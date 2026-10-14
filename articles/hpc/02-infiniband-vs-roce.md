# InfiniBand vs RoCEv2

Both InfiniBand and RoCEv2 deliver RDMA. They use different physical networks, different switch fabrics, and have different operational characteristics. Understanding the tradeoffs is essential for any network engineer working with or designing AI/ML infrastructure.

## InfiniBand: Purpose-Built for RDMA

InfiniBand is not Ethernet. It is a completely separate network technology with its own:
- Physical layer (different cable types, transceivers, and signaling)
- Link layer (IB link protocol, not 802.3)
- Network layer (IB addressing — Local Identifiers (LIDs) and Global Identifiers (GUIDs), not IP addresses)
- Transport layer (IB transport, including Reliable Connected, Unreliable Connected, Unreliable Datagram)
- Switch hardware (InfiniBand switches — Mellanox/NVIDIA Quantum, Cornelis Omni-Path)
- Subnet Manager (software that configures the IB fabric, assigns LIDs, and manages routes)

**How InfiniBand Handles Congestion**

InfiniBand is inherently lossless: credit-based flow control ensures that a sender never transmits more data than the receiver has buffer for. No packet is ever dropped due to buffer overflow in a correctly operating IB fabric. This is the fundamental reason IB can support RDMA without the complex PFC/ECN machinery required for RoCEv2.

The subnet manager maintains full topology knowledge and computes optimal paths (linear forwarding tables for each switch). InfiniBand fabrics typically use fat-tree or dragonfly topologies — the subnet manager programs switch forwarding tables to achieve full bisection bandwidth.

**Performance**

InfiniBand's latest generation (NDR — Next Data Rate) delivers 400 Gbps per port, with latency under 500 nanoseconds port-to-port. HDR (High Data Rate) delivers 200 Gbps. For AI training jobs that require maximum bandwidth and minimum latency for gradient synchronization, InfiniBand's performance advantage over RoCEv2 is measurable.

**The Operational Difference**

InfiniBand requires a **Subnet Manager (SM)** — typically running as software on a dedicated server or embedded in a switch. The SM discovers the fabric topology, assigns LIDs (16-bit local addresses) to every node and switch port, and computes forwarding tables. Without a functioning SM, the IB fabric does not forward traffic.

This centralized management is both a simplicity and a risk: the SM is the single point of operational control, and SM failures can take down the entire IB fabric. Production IB deployments use redundant SM instances (one active, one standby) and careful SM placement.

For the network engineering team: InfiniBand is managed entirely within the IB domain. The IP network only connects the management servers and out-of-band management; all RDMA traffic runs over IB switches and does not touch the Ethernet fabric.

## RoCEv2: RDMA over Ethernet

RoCEv2 runs RDMA over Ethernet and UDP/IP. The RDMA verbs (Send, Receive, Read, Write) are the same as InfiniBand, but the packets are standard Ethernet frames with UDP headers (port 4791 is the well-known port for RoCEv2).

**What stays the same from the application's perspective:**
- The same RDMA API (ibverbs)
- The same communication patterns (Send/Receive, Read/Write)
- The same performance libraries (NCCL, OpenMPI with UCX)

**What is different:**
- The network is Ethernet — the same switches, cables, and transceivers used for general compute
- IP addresses (not IB LIDs) identify endpoints
- No Subnet Manager — standard IP routing and Ethernet forwarding
- No inherent losslessness — Ethernet drops packets under congestion, which RDMA cannot tolerate

**The Losslessness Problem**

This is the crux of why RoCEv2 is a network engineering problem: **Ethernet drops packets. RDMA cannot tolerate drops.**

A dropped RoCEv2 packet triggers a Go-Back-N retransmission by default — the sender must retransmit from the dropped packet's sequence number forward. In a high-bandwidth RDMA flow, a single dropped packet causes a massive retransmission that can stall the flow for hundreds of milliseconds. At the scale of thousands of GPU-to-GPU flows in a training job, occasional drops cascade into complete training throughput collapse.

The solution is lossless Ethernet via **PFC (Priority Flow Control)** and **ECN (Explicit Congestion Notification)** — covered in the congestion control articles. The network must be engineered so that:
1. ECN marks packets early enough that the RDMA sender reduces its rate before any buffer overflows (DCQCN algorithm)
2. PFC pauses the upstream sender if ECN is insufficient and the buffer is about to overflow
3. PFC deadlock never occurs (requires careful topology design)

RoCEv2 and QoS/ECN are inseparable — anyone operating RoCEv2 infrastructure must understand both together.

## The Comparison

| | InfiniBand (NDR) | RoCEv2 (100GbE) |
|---|---|---|
| Port bandwidth | 400 Gbps | 100 Gbps (per port) |
| Latency | ~500ns | 1-2 µs (with good tuning) |
| Lossless | Native (credit-based) | Requires PFC + ECN |
| Network infrastructure | Dedicated IB switches | Shared Ethernet fabric |
| Management | Subnet Manager (IB-specific) | Standard IP/BGP operations |
| Cost | Higher (dedicated IB switches) | Lower (shared fabric) |
| Operational complexity | IB expertise required | Ethernet expertise + PFC/ECN |
| Vendor ecosystem | Primarily NVIDIA/Mellanox | Multiple vendors (Mellanox, Broadcom, Cisco) |

## What Is Used in Practice

**Pure InfiniBand clusters:** Large AI training facilities (hyperscalers with dedicated ML clusters, cloud provider GPU pods) often use InfiniBand for the highest-performance training workloads. The dedicated fabric, purpose-built for RDMA, delivers the best all-reduce performance for extremely large model training where every microsecond of synchronization latency multiplies across thousands of GPUs.

**RoCEv2 clusters:** Organizations that want to leverage existing Ethernet infrastructure, or that are building GPU clusters at smaller scale where absolute peak RDMA performance is less critical, often choose RoCEv2. Cloud providers offering GPU instances to tenants sometimes use RoCEv2 because it allows the RDMA traffic to share the general-purpose DC fabric with other workloads — important for multi-tenant environments.

**Hybrid:** Some large-scale deployments use InfiniBand for GPU-to-GPU RDMA (the training fabric) and Ethernet for storage, management, and general compute traffic. The GPU servers have two NICs: an IB HCA for RDMA and an Ethernet NIC for everything else.

## The third option: where EFA/SRD fits

The comparison above is the classic two-way choice, but on the public cloud there is a third answer: **AWS EFA**, running the **SRD** transport (covered in the RDMA article). It belongs in this comparison because it makes a fundamentally different bet than either InfiniBand or RoCEv2. InfiniBand builds a bespoke lossless fabric; RoCEv2 forces commodity Ethernet to behave losslessly with PFC and ECN; EFA/SRD gives up on in-order, lossless delivery entirely and instead sprays packets across many paths, tolerates reordering, and reassembles in the NIC — which lets it sidestep the PFC fragility that makes RoCEv2 hard to operate at scale. EFA is AWS-proprietary (EC2 only), so it is not a fabric you choose on a spec sheet against the other two — it is the one you get when you train on AWS.

| | InfiniBand (NDR) | RoCEv2 (100GbE) | AWS EFA / SRD |
|---|---|---|---|
| Latency | ~500ns (lowest) | 1-2 µs (tuned) | low, consistent tail |
| Losslessness | Native (credit-based) | Requires PFC + ECN | Not required (tolerates loss/reorder) |
| Multipath | Limited (in-order) | Limited (in-order, PFC) | Native packet spray |
| Fabric | Dedicated IB switches | Shared Ethernet | AWS Nitro / EC2 only |
| Portability | On-prem & some clouds | On-prem & multi-vendor | AWS only (proprietary) |
| Operational burden | Subnet Manager, IB skills | PFC/ECN/DCQCN tuning | Managed by AWS |

## Which one, and when

For a network engineer being asked "which should we deploy," the decision is less about raw numbers and more about constraints:

- **Choose InfiniBand** when you are building a dedicated, tightly-coupled training cluster, performance is the top priority, and the budget supports a bespoke fabric and the specialized operations it demands. Every microsecond of synchronization latency multiplies across thousands of GPUs, so for the largest, most latency-sensitive training jobs IB's co-designed fabric still wins on pure performance.

- **Choose RoCEv2** when you want to run RDMA on the Ethernet fabric and skills you already have, when the cluster shares infrastructure with other workloads or is multi-tenant, or when cost and vendor flexibility matter more than squeezing out the last microsecond. The tradeoff you are accepting is operational: you must engineer and monitor losslessness (PFC, ECN, DCQCN) correctly, because a misconfigured lossless fabric fails in subtle, hard-to-diagnose ways. The industry has been steadily voting this way — a growing majority of new AI fabric deployments now choose Ethernet-based RDMA over InfiniBand, as Ultra Ethernet matures and hyperscalers validate RoCE at scale.

- **Choose EFA/SRD** when you are training on AWS — which effectively makes the choice for you, since it is the RDMA fabric AWS offers. Its multipath, loss-tolerant design is genuinely well-matched to large, elastic cloud clusters where links fail and congestion shifts, and it removes the PFC-tuning burden entirely. You give up the absolute lowest latency of a dedicated IB fabric in exchange for cloud elasticity and a transport AWS operates for you.

The honest one-line summary: **InfiniBand** for a dedicated performance-first cluster you own and operate; **RoCEv2** to run RDMA on commodity Ethernet you already know; **EFA/SRD** because you are on AWS. All three solve the same problem — move gradients between thousands of GPUs faster than the GPUs can notice they are waiting — and the right answer is dictated by where you are deploying and what you are optimizing for.

## What a Network Engineer Needs to Know

For a network engineer working with AI/ML infrastructure, the foundational knowledge that matters:
- RDMA principles (covered in the previous article)
- Lossless Ethernet (PFC + ECN + DCQCN — covered in the congestion control articles)
- Fat-tree and dragonfly topologies (covered in the HPC topology article)
- The operational model for RDMA monitoring: tracking CNP rates, PFC pause counts, RDMA retransmit counters

Understanding why each technology exists, what problem it solves, and what the network engineering constraints are is more transferable than hands-on experience with any specific vendor's implementation. The underlying principles — lossless fabric, RDMA semantics, congestion signaling — are consistent across InfiniBand and RoCEv2.
