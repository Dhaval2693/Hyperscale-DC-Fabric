# PIM-SM Mechanics

PIM Sparse Mode is built around a specific sequence: receivers join a shared tree rooted at the Rendezvous Point (RP), traffic initially flows down that shared tree, and then — optionally — individual routers switch to a source-specific shortest-path tree for optimal delivery. Understanding this sequence, step by step, is what matters for both interview discussions and production operations.

## The Rendezvous Point

The RP is a designated router in the network that acts as the meeting point between sources and receivers. Both sides independently discover the RP (via static configuration, Auto-RP, or PIM Bootstrap Router — BSR), and this shared knowledge is what allows sources and receivers to find each other without direct coordination.

**RP as a single point of failure:** In a network with a single RP, the RP's failure means multicast stops working for all groups using that RP. Production networks use **Anycast RP** or **RP redundancy via PIM BSR** to eliminate this. With Anycast RP, multiple routers share the same RP address (using MSDP — Multicast Source Discovery Protocol to synchronize source state between them). Receivers join whichever RP is closest; if one RP fails, traffic fails over to the nearest surviving RP.

## Phase 1: Receiver Joins the Shared Tree

When a host sends an IGMP membership report for group G, the first-hop router (FHR from the receiver's perspective) creates a multicast route state entry and sends a **PIM Join message** upstream toward the RP.

The Join message travels hop-by-hop toward the RP, following the unicast route. Each router along the path:
1. Receives the Join
2. Creates a `(*, G)` state entry — "I have downstream receivers for group G, regardless of source"
3. Forwards the Join upstream toward the RP
4. Begins forwarding multicast traffic for group G downstream when it arrives

The path of Join messages from the receiver's FHR to the RP forms the **Shared Tree (RPT)** — rooted at the RP, with branches extending toward all receivers. When traffic for group G arrives at the RP, it flows down this shared tree to all receivers.

## Phase 2: Source Registers with the RP

When a source begins transmitting multicast traffic for group G, the first-hop router of the source (the DR — Designated Router on the source's subnet) encapsulates the multicast traffic in **PIM Register messages** and sends them unicast to the RP.

The RP receives the Register message, decapsulates the multicast data, and forwards it down the shared tree to all receivers. At the same time, the RP sends a **PIM Join toward the source** — building a source-specific branch of the tree from the RP back to the source, called the **Source Path Tree (SPT)**.

Once the SPT branch from the RP to the source is established, the RP receives the multicast traffic natively (not encapsulated) and the source's DR receives a **Register-Stop** message from the RP — "stop encapsulating, the tree is built."

## Phase 3: Receiver Switches to Source Tree (SPT Switchover)

The shared tree rooted at the RP may not be the optimal path from source to receiver. Traffic might travel from the source to the RP and back down through the same router on its way to the receiver — a suboptimal, traffic-engineering-unfriendly path.

PIM-SM allows individual receivers to switch to the **Shortest-Path Tree (SPT)** — a tree rooted at the source itself, not the RP. This eliminates the RP as a waypoint and delivers traffic via the shortest path from source to receiver.

**SPT switchover is triggered by a bandwidth threshold** (configurable per platform; by default in Cisco/Arista, switchover happens immediately on the first packet). When the receiver's FHR sees multicast traffic arriving from the RP for group G from source S, it sends a **PIM Join toward the source (S,G Join)** — following the unicast route directly to the source's network.

The Join builds an (S,G) entry — source-specific, not shared. Traffic begins arriving on the new, shorter path. The FHR then sends a **PIM Prune toward the RP** — "stop sending traffic for (S,G) down the shared tree; I'm now on the source tree." The RP removes the FHR from the shared tree's downstream interface list for that (S,G).

The final state: traffic flows from the source directly to the receiver via the optimal path, with no RP in the traffic path. The RP remains only for state maintenance — signaling, not forwarding.

## PIM State Entries

Understanding the two types of PIM state entries is essential for troubleshooting:

**`(*, G)` — Wildcard, Group:** State for "any source sending to group G." Created when a receiver joins. Indicates a downstream interest in group G regardless of which source is sending. Traffic arrives from the RP direction.

**`(S, G)` — Source, Group:** Source-specific state. Created after SPT switchover. Traffic arrives from the specific source S direction. More specific than `(*, G)`.

When both `(*, G)` and `(S, G)` state exist on a router, the more specific `(S, G)` takes precedence for traffic from source S.

## The Assert Mechanism

In a multi-access network (a LAN segment with multiple PIM routers), multiple routers may be connected to the same downstream receivers and may all try to forward multicast traffic onto the segment. This would result in duplicate delivery.

PIM's **Assert mechanism** resolves this. When a router receives multicast traffic on an interface from which it would normally forward (because it has downstream receivers there), and it also sees that traffic on the same interface from another PIM router, it sends a PIM Assert message. The Assert contains the router's metric toward the source. The router with the **lower administrative distance / better metric wins** and becomes the sole forwarder. The losing router removes the downstream interface from its OIL (Outgoing Interface List) and stops forwarding.

This is the mechanism that prevents duplicate delivery on shared LAN segments and designates a single forwarder in cases of topology ambiguity.

## Join/Prune Timers and Convergence

PIM Join/Prune messages are sent periodically (every 60 seconds by default) to refresh state. This is important: PIM state is **soft state** — it times out if not refreshed. A downstream router that loses connectivity to the upstream and stops sending Joins will eventually have its state expire at the upstream, which will prune the branch.

This soft-state model means PIM is self-healing but has a convergence time proportional to the timer values. For production networks with strict multicast availability requirements, Refresh Interval timers should be tuned to converge quickly after a failure. BFD can also be run on PIM-enabled interfaces to detect neighbor failures much faster than the default PIM hello timer allows.

## What I Tested at Arista

At Arista Networks, I validated PIM-SM behavior across multiple hardware platforms:

- **RP election and failover:** Testing Anycast RP behavior with MSDP — confirming that when one RP failed, receivers transitioned to the surviving RP and traffic resumed within the expected convergence time.
- **SPT switchover:** Validating that (S,G) state was correctly built and that the subsequent RP Prune was sent, verifying the traffic path transitioned from shared tree to source tree correctly.
- **Failure scenarios:** Simulating upstream link failures mid-stream and confirming that the router correctly re-joined via an alternate path and that receivers did not see traffic loss beyond the expected convergence window.
- **Scalability:** Testing multicast forwarding at high group counts to verify that hardware TCAM utilization remained within bounds and that forwarding rates did not degrade as group count increased.

This hands-on validation work is what gives real credibility to discussing PIM-SM in interview settings — the ability to speak not just about how it works conceptually but about what it looks like when it does not work and how you verify it.
