# PFC and Lossless Ethernet

TCP was designed with loss in mind. When a packet is dropped, TCP detects the loss, retransmits, and adjusts its sending rate. The entire congestion control architecture of the modern Internet is built around the assumption that packet loss is a normal, expected event that carries information.

RDMA (Remote Direct Memory Access) operates under a completely different assumption: **there are no packet drops.** RDMA protocols — including InfiniBand and RoCEv2 (RDMA over Converged Ethernet) — have no reliable retransmission at the transport layer. A dropped packet in an RDMA flow causes the flow to stall until an application-level timeout expires, which can take hundreds of milliseconds or longer. For GPU-to-GPU communication in a distributed training job where every microsecond of stall time accumulates across thousands of operations, this is catastrophic.

To run RDMA over Ethernet, you need Ethernet to behave like InfiniBand: **zero packet loss**. This requirement defines everything about how lossless Ethernet is designed.

## Why Standard Ethernet Drops Packets

Before discussing the solution, it is worth being precise about why Ethernet drops packets at all.

The answer is buffer overflow. When more traffic arrives at a switch port than can be immediately transmitted — because the egress link is busy or because multiple ingress ports are all sending to the same egress — packets queue in the switch's on-chip buffers. When those buffers fill, new arriving packets are dropped. This is tail drop.

The solution to zero-loss Ethernet is to prevent buffers from ever overflowing. There are two mechanisms for this: **PFC (Priority Flow Control)** and **ECN-based congestion notification** (discussed in the previous article). PFC is the foundational mechanism for lossless behavior.

## PFC: Priority Flow Control

PFC is defined in the IEEE 802.1Qbb standard. It extends the older 802.3x flow control (which could pause an entire link) by allowing **per-priority pause** — pausing traffic of a specific priority class without affecting other priority classes on the same link.

**How PFC works:**

1. A switch's ingress buffer for a given priority class starts filling. When the buffer occupancy reaches a configured **pause threshold** (set well below the buffer maximum to account for packets already in flight), the switch sends a **PAUSE frame** to the upstream device on that link.
2. The PAUSE frame specifies which priority class to pause and for how long (expressed in pause quanta — units of 512 bit-times).
3. The upstream device receives the PAUSE frame and immediately stops transmitting packets of that priority class for the specified duration.
4. The downstream switch drains its buffer.
5. When the buffer drops below a **resume threshold**, the switch sends another PAUSE frame with a duration of zero — "you may resume."
6. The upstream device resumes transmitting.

The key property: traffic of other priority classes is not affected. If you have 8 priority classes (0-7) and PFC is configured for class 3 (your RDMA traffic), a PAUSE on class 3 does not affect class 7 (your control plane traffic) or class 0 (your best-effort traffic). Each priority class is independently pausable.

**The lossless property:** If PFC parameters are tuned correctly — pause threshold accounts for in-flight packets (the bandwidth-delay product of the link) — no packet should ever be dropped due to buffer overflow in the RDMA priority class. When a switch's buffer fills, it pauses the upstream before the buffer overflows. The upstream holds the packets in its own buffers. The flow is slowed, not lost.

## PFC Deadlock: The Dark Side of Lossless Ethernet

PFC introduces a serious risk: **deadlock**. 

Imagine four switches in a ring topology: A → B → C → D → A. Each is pausing the one upstream:
- D's buffer fills, D pauses C
- C's buffer fills (because D is paused), C pauses B
- B's buffer fills, B pauses A
- A's buffer fills, A pauses D

Every switch is paused. No traffic can move. The network is frozen — a circular dependency of PAUSE frames. This is PFC deadlock, and it is a real operational risk in RDMA fabrics.

Avoiding PFC deadlock requires careful network design:
- Ensure the network topology has no cyclic buffer dependencies — in a spine-leaf fabric with no east-west traffic among spines, deadlock loops cannot form because traffic only flows up from leaf to spine and down from spine to leaf.
- Use **Deadlock Detection and Recovery** mechanisms available on some switch platforms.
- Apply PFC only on specific priority classes used for RDMA, using other classes (without PFC) for general traffic — this limits the scope of potential deadlock to the RDMA priority.

## ECN as the First Line of Defense

In a well-operated RDMA fabric, PFC should be a backstop — an emergency brake that engages rarely, not a normal operating condition. If PFC is pausing constantly, that indicates chronic congestion that will eventually cause latency problems or, in a degenerate case, contribute to deadlock conditions.

The preferred first line of defense is **ECN (Explicit Congestion Notification)** with RDMA-aware congestion notification. RoCEv2 uses a mechanism called **CNP (Congestion Notification Packet)**: when an RDMA receiver detects CE-marked packets, it sends a CNP back to the sender. The sender implements a rate-reduction algorithm (typically DCQCN — Data Center Quantized Congestion Notification) that reduces its sending rate proportionally.

DCQCN is the RDMA equivalent of DCTCP: rate-proportional congestion response using ECN signals, designed to keep queue depths low enough that PFC is rarely triggered.

The target operating model: **ECN handles normal congestion. PFC handles extraordinary bursts. Neither should be chronic.**

## The Priority Classes in Practice

A typical lossless Ethernet DC fabric allocates priority classes roughly as follows:

| Priority | Traffic | PFC Enabled | ECN Enabled |
|---|---|---|---|
| 7 | Network control (BGP, OSPF, PFC frames) | No | No |
| 6 | Latency-sensitive application | No | Yes |
| 4-5 | General compute / TCP | No | Yes |
| 3 | RDMA (RoCEv2) | **Yes** | Yes |
| 0-2 | Best-effort | No | No |

PFC is enabled only on the RDMA priority class. Control plane traffic is never paused — if PFC were enabled on control plane priority, a congested RDMA flow could indirectly cause BGP sessions to drop, which would be catastrophic.

## What "Lossless" Actually Means in Operations

Lossless Ethernet does not mean zero packet loss under all conditions. It means zero packet loss due to buffer overflow in the PFC-protected priority class, under normal operating conditions. Loss can still occur due to:
- Hardware errors (bit flips, CRC failures)
- Software bugs in RDMA stacks
- PFC deadlock (if it occurs)
- Configuration errors that allow PFC-protected traffic to mix with non-PFC traffic

Monitoring a lossless RDMA fabric requires tracking PFC pause frame counts, buffer utilization, CNP rates, and RDMA retransmit counters. A well-operated fabric should show near-zero RDMA retransmits and PFC pause frames as a rare event rather than a continuous background condition.

This is the foundation of what the LinkedIn JD means by "AI/ML network infrastructure, e.g. InfiniBand and RoCEv2 networking." The networking knowledge underneath these technologies is PFC, ECN, DCQCN, and lossless fabric design — and that knowledge starts here.
