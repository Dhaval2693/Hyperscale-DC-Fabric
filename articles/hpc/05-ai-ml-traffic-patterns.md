# AI/ML Network Traffic Patterns

AI/ML workloads put fundamentally different stress on networks than traditional cloud or enterprise traffic. This article covers the traffic patterns, why they're hard, and how to think about them as a network engineer — especially relevant for any role at an AI lab or hyperscaler with AI infrastructure.

## The Two Workload Types

### Training
Many GPUs working together on a single model. Communication is:
- **Collective** (everyone-to-everyone)
- **Synchronized** (no one moves until all are done)
- **High-volume** (gradient or parameter exchange every step)

### Inference
A trained model serving predictions. Communication is:
- **Point-to-point** (client → model server)
- **Asynchronous** (each request independent)
- **Low-volume per request** but high QPS

These have **completely different network characteristics**, and a single fabric often has to serve both.

## Training: Collective Communication Patterns

When N GPUs train together, they synchronize after each step. The "collective" operations:

### All-Reduce

Every GPU has a gradient. All GPUs need to end up with the SUM (then divide by N to average).

**Naive:** send everyone's data to one node, sum, broadcast back. O(N) bottleneck on the central node.

**Ring all-reduce** (what NCCL uses): arrange GPUs in a ring; each sends to its right neighbor. After N-1 steps, every node has the sum. Bandwidth per link is roughly `2 × (gradient_size / N)` — scales nicely with N.

**Tree all-reduce:** binary tree, log(N) hops.

**Network implication:** sustained, high-bandwidth, all-to-all traffic during gradient sync. Bursts can be hundreds of GB/s on a single fabric.

### All-Gather

Each GPU has a piece of data. All GPUs need to have ALL pieces (concatenated).

Used in tensor-parallel models and FSDP (Fully Sharded Data Parallel).

### Reduce-Scatter

Inverse of all-gather. Each GPU sends its piece; each ends up with the sum of one specific slice.

### Broadcast

One GPU sends data to all others. Used for parameter init or distributing a value.

## What Makes Training Traffic Hard

1. **Synchronous → microbursts.** All GPUs send at the same instant. Total traffic can saturate fabric in microseconds.

2. **Symmetric bandwidth.** Traffic is bidirectional and balanced — not the asymmetric pattern of client-server workloads.

3. **Latency-sensitive.** If even one GPU's communication stalls, all GPUs wait. The "stragglers" effect — the slowest link sets the pace.

4. **Lossless required.** TCP retransmit latency would catastrophically slow training. Hence RoCEv2 + PFC + ECN (covered in the previous HPC articles).

5. **Predictable scale.** You know in advance how many GPUs, what model size, what gradient size per step. Capacity planning is more deterministic than enterprise traffic.

## Inference: A Different Beast

Inference traffic:
- **Request/response** — asymmetric (small request, larger response)
- **Bursty at the QPS level**, but each request is small
- **Latency-bounded** — p99 latency matters
- **No collective** — each request is independent

The network demands are more like a web service than HPC. But on a shared fabric, **inference latency can be ruined by a training all-reduce burst** — hence QoS classification matters.

## Checkpoint and Weight Sync

Training jobs save model state periodically (checkpoints) and load pre-trained weights (initialization):

- **Checkpoint write:** large bulk transfer to storage (often cross-region). Tens of TB per checkpoint for large models.
- **Weight load:** read from storage at job start, distribute to all GPUs.

This is **bulk traffic** — high volume but latency-insensitive. The classic conflict: bulk checkpoint transfer starves latency-sensitive inference.

**QoS solution:** mark checkpoint traffic AF11 (low priority), inference EF (high priority). Schedule large checkpoints during off-peak windows when possible.

## Bandwidth Symmetry Matters

Traditional enterprise: heavy downstream (users pulling data), lighter upstream. Fabric and links can be sized asymmetrically.

AI training: **symmetric**. All-to-all means equal traffic in both directions on every link. Fabrics must be sized for **full bisection bandwidth** — which is expensive at scale.

Non-blocking fabrics (full bisection) are the norm for AI training. The fat-tree / Clos topology with 4:1 oversubscription that works for cloud workloads will throttle training.

## Job Placement Matters

The same model trained on the same GPUs can have wildly different network behavior depending on **placement**:

| Placement | Network path |
|---|---|
| All GPUs on one node | NVLink only — no fabric traffic |
| GPUs across nodes in same rack | Top-of-rack switch |
| GPUs across racks | Spine traffic |
| GPUs across DCs | DCI / WAN |

Modern AI training schedulers (Slurm with topology-aware placement, K8s with topology-aware scheduling) consider this. If they don't, network performance dies.

## The Numbers (Order of Magnitude)

A modern AI training cluster:
- ~1000 GPUs, each with 400 Gbps fabric NIC
- Gradient sync every step (~100s of ms per step)
- Per-step traffic: easily 10s of TB across the fabric
- Sustained bandwidth: hundreds of Tb/s aggregate

This is why these networks use 400 Gbps+ links, lossless fabrics, and dedicated topologies.

## How to Talk About It

**For "tell me about AI/ML traffic" question:**
> "Training traffic is collective and synchronous — all-reduce after every step, microbursts that can saturate fabric in microseconds. Symmetric bandwidth, latency-sensitive because stragglers slow everyone. That's why you see RoCEv2 + PFC + ECN for lossless behavior. Inference is the opposite: request/response, asymmetric, independent. On shared fabrics, QoS keeps inference latency safe from training bursts. Checkpoint traffic is bulk and gets lowest priority."

**For "how does this differ from cloud workloads":**
> "Cloud workloads are typically asymmetric and tolerant of TCP retransmits. Training is symmetric and lossless-required. The fabric sizing changes — you need full bisection bandwidth, not 4:1 oversubscription. Topology-aware job placement becomes critical because placement determines whether traffic stays on NVLink, in-rack, or hits the spine."

## Likely Interview Questions

**Q: "How would you design the fabric for a 5000-GPU training cluster?"**

Walk through:
- Spine-leaf or full mesh; high-radix switches at the spine
- 400G+ links, RoCEv2 with PFC + ECN
- Full bisection bandwidth (or close)
- Topology-aware placement integration with the scheduler
- Separate fabric or VLAN for storage (checkpoints)
- Telemetry: per-link utilization, PFC pause counters, ECN marks, RDMA retransmits

**Q: "Inference latency spiked at 9 AM every day. What do you check?"**

Diagnostic checklist:
- Correlate with training jobs — checkpoint writes? all-reduce bursts?
- Check QoS classification — is inference actually marked correctly?
- Look at PFC pause frames on inference path
- Look at ECN marking rates
- Verify topology — is inference traffic crossing busy spine paths?
- Check for noisy-neighbor effects on shared links

**Q: "We need to scale our cluster from 1000 to 5000 GPUs. What changes for the network?"**

- Bisection bandwidth requirement scales linearly with GPU count
- May need new spine tier or higher-radix switches
- Collective communication time scales with N — ring all-reduce per-link bandwidth drops
- Checkpoint storage path may need parallelization
- Telemetry pipeline cardinality grows 5x — sampling/aggregation strategy matters

## What to Memorize

| Concept | Key idea |
|---|---|
| **All-reduce** | Collective sum, ring-based at scale |
| **All-gather** | Collective concatenation (FSDP, tensor-parallel) |
| **Synchronous collective** | Everyone sends at the same instant → microbursts |
| **Bisection bandwidth** | Sum of bandwidth between any two halves of the network |
| **Stragglers** | Slowest GPU/link sets the pace for everyone |
| **Lossless required** | TCP retransmit latency kills training; hence RoCEv2 |
| **Topology-aware placement** | Schedule jobs based on network locality |

## Connection to the Rest of the Repo

This article builds on the HPC sequence:
- [01-why-rdma.md](01-why-rdma.md) — why kernel-bypass is needed
- [02-infiniband-vs-roce.md](02-infiniband-vs-roce.md) — the IB vs RoCE choice
- [03-lossless-ethernet-for-rdma.md](03-lossless-ethernet-for-rdma.md) — PFC, ECN, DCQCN mechanics
- [04-hpc-topology.md](04-hpc-topology.md) — bisection bandwidth, fat-tree designs

If those clicked, this should feel like the "so what does the traffic actually look like" follow-up — the workload patterns that make all that lossless, full-bisection infrastructure necessary.
