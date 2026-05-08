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

This is why LinkedIn's JD specifically lists both RoCEv2 and QoS/ECN as basic qualifications — the two are inseparable for anyone operating RoCEv2 infrastructure.

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

## What This Means for a Network Engineer at LinkedIn

LinkedIn's JD mentions "AI/ML network infrastructure, e.g. InfiniBand and RoCEv2 networking" as a preferred qualification. The honest admission: if you have not operated production InfiniBand or RoCEv2 fabric, that is a gap.

The foundational knowledge that bridges the gap:
- RDMA principles (covered in the previous article)
- Lossless Ethernet (PFC + ECN + DCQCN — covered in the congestion control articles)
- Fat-tree and dragonfly topologies (covered in the HPC topology article)
- The operational model for RDMA monitoring: tracking CNP rates, PFC pause counts, RDMA retransmit counters

You do not need to have designed and operated an NVIDIA Quantum InfiniBand fabric to have a productive conversation about it in an interview. You need to understand why it exists, what problem it solves, and what the network engineering constraints are. That depth — combined with honesty about hands-on experience — is the right posture.
