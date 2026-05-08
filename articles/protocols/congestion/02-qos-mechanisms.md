# QoS Mechanisms: Classification, Marking, Queuing, and Scheduling

QoS is not a single feature — it is a pipeline of mechanisms that work together. Understanding each mechanism in isolation is necessary but not sufficient. What matters operationally is understanding how they compose: where classification happens, how markings propagate, what queuing model applies at each device, and what the scheduler does when multiple queues are competing for bandwidth.

## Classification: The First Decision

Every packet that enters a QoS-enabled device must be classified — placed into one of a set of traffic classes that determine how it will be handled.

Classification can happen at multiple layers:

**L4 classification** (most common at the edge): Match on source/destination IP, protocol, and TCP/UDP port numbers. A packet from a storage controller to port 3260 (iSCSI) is classified as storage I/O. A packet to port 179 (BGP) is classified as control plane. A packet from a bulk backup process is classified as best-effort.

**DSCP trust** (common at the core): Rather than re-classifying at every hop, trust the DSCP marking already on the packet. The edge device classifies and marks once; every downstream device reads the mark and queues accordingly. This is how QoS scales in large networks — classification is expensive, marking is cheap.

**802.1p / CoS** (for Layer 2 segments): The 3-bit Class of Service field in the 802.1Q VLAN tag carries priority information within a switched Ethernet domain. Typically remapped to DSCP at Layer 3 boundaries.

The rule for large fabrics: **classify at the ingress edge, trust markings everywhere else.** Re-classifying at every hop is operationally complex and inconsistent. Define classification policy once at the access layer or the first-hop switch, mark the packet, and let the marking propagate.

## DSCP: The Marking Standard

**DSCP (Differentiated Services Code Point)** occupies the upper 6 bits of the IP header's TOS (Type of Service) byte, giving 64 possible values. In practice, the industry has converged on a smaller set of well-known Per-Hop Behaviors (PHBs):

**EF — Expedited Forwarding (DSCP 46):** Intended for real-time, low-latency traffic. A device that sees EF-marked traffic is expected to give it strict priority — forward it immediately, with minimal queuing delay. Used for VoIP, latency-sensitive control plane traffic, and some storage I/O.

**AF — Assured Forwarding (DSCP 10, 12, 14, 18, 20, 22, 26, 28, 30, 34, 36, 38):** Four classes (AF1 through AF4), each with three drop precedences (low, medium, high). AF traffic gets a bandwidth guarantee but is subject to dropping when congestion occurs — higher drop precedence packets are dropped first. Used for important but not time-critical traffic.

**CS — Class Selector (DSCP 8, 16, 24, 32, 40, 48, 56):** Backwards-compatible with the old IP Precedence field. CS6 and CS7 are typically reserved for network control plane traffic (routing protocols, ICMP from network devices).

**Default/BE (DSCP 0):** Best-effort. No guarantees. Internet traffic, bulk transfers, anything not explicitly classified.

**In practice for DC environments:**
- Control plane (BGP, OSPF): CS6 or EF
- Storage I/O: EF or AF41
- Latency-sensitive application traffic: AF31 or AF41
- General compute traffic: AF11 or default
- Bulk/backup: default or explicit low-priority marking

## Queuing Models

Once packets are classified and marked, they enter queues. The queuing model determines how many queues exist per interface and how they are organized.

**Single Queue (no QoS):** All packets enter one FIFO queue. Processed in arrival order. Any congestion affects all traffic equally. This is best-effort — functional but offering no differentiation.

**Multiple Queues with Strict Priority:** Multiple queues ranked by priority. The scheduler always serves the highest-priority non-empty queue. Lower-priority queues only get service when all higher-priority queues are empty.

The problem with strict priority alone: a high-priority queue that is always busy can starve lower-priority queues completely. If control plane traffic and real-time traffic always have packets waiting, bulk traffic queues may never be served — **queue starvation**.

**Weighted Queuing (WFQ / DWRR):** Each queue is assigned a weight. The scheduler distributes bandwidth proportionally to weights. A queue with weight 60 gets 60% of available bandwidth; a queue with weight 20 gets 20%. No queue starves — every queue is guaranteed its minimum share.

**Hybrid — Strict Priority + Weighted Queuing:** The most common model in modern DC switches. One or two queues are strict priority (for control plane and latency-critical traffic). Remaining queues use weighted scheduling among themselves. This gives critical traffic guaranteed low latency while preventing best-effort traffic from being completely starved.

**In Arista, Cisco NX-OS, and similar DC platforms:** Typically 8 queues per interface. Queue 7 (or equivalent) is strict priority for control plane. Queues 4-6 for high-priority application traffic with assigned weights. Queues 1-3 for general traffic. Queue 0 for bulk/scavenger.

## Tail Drop vs WRED

When a queue fills, the device must decide what to do with new arriving packets. The default behavior is **tail drop**: when the queue is full, every new packet is dropped until space becomes available. Tail drop works but has a known pathology called **TCP global synchronization**.

TCP uses packet loss as a congestion signal and reduces its sending rate when it detects drops. In a network with tail drop, when a queue fills, many TCP flows simultaneously detect loss at the same moment. They all reduce their sending rate simultaneously. The queue drains. All flows simultaneously ramp back up. The queue fills again. They all drop simultaneously again. This oscillation — all flows synchronizing on the same congestion signal — causes periodic throughput collapse.

**WRED (Weighted Random Early Detection)** solves this by dropping packets probabilistically before the queue is full. As queue depth grows, WRED increases the probability that an incoming packet is dropped. Different traffic classes (differentiated by DSCP or drop precedence) have different drop thresholds — AF low-drop-precedence packets are dropped later than AF high-drop-precedence packets.

By dropping packets early and randomly (affecting different flows at different times), WRED desynchronizes TCP flows. They reduce rates at different moments, preventing the simultaneous collapse. Average queue depth stays lower. Throughput stays higher.

WRED is effective for TCP traffic. It is **not appropriate for UDP traffic** (such as real-time streaming) because UDP does not respond to drops by reducing its rate — it just loses the packet.

## Shaping vs Policing

Both shaping and policing enforce a rate limit on traffic, but they handle excess differently.

**Policing:** Drops (or re-marks) packets that exceed the defined rate immediately. Hard enforcement. No buffering. Excess traffic is gone. Useful at network ingress points where you need to enforce a customer's committed rate without allowing burst.

**Shaping:** Buffers excess traffic and releases it at the defined rate. Smoothes bursts. Traffic is delayed, not dropped. Useful when the downstream path can handle the average rate but not the peak burst, and when delay is preferable to loss.

For most intra-DC traffic, shaping is rarely applied — links are fat enough that shaping would introduce unnecessary latency. Policing is used at specific points: ingress to a spine-leaf fabric from external sources, or enforcement of tenant bandwidth commitments in cloud environments.

The practical takeaway: QoS in a DC is primarily about queuing and scheduling, not shaping. The goal is to handle congestion when it happens — not to artificially constrain flows.
