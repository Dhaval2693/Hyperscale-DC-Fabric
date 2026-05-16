# Why Multicast Exists

Most network traffic is unicast: one sender, one receiver. A packet has a source IP and a destination IP, and the network delivers it from the source to that specific destination. This model works for the vast majority of applications — web requests, API calls, database queries, file transfers.

But consider a different problem: one source that needs to deliver the same data to a large number of receivers simultaneously.

A live video stream. A financial market data feed. A network management system pushing configuration to hundreds of devices. A distributed storage system replicating data to multiple nodes. In all of these cases, the naive approach — unicast to each receiver individually — produces a fundamental inefficiency.

If 1,000 servers need to receive the same 1 Gbps video stream, and the sender unicasts to each one, the sender must transmit 1,000 Gbps of traffic. Its uplink is saturated. Every switch on the path to the receivers duplicates the traffic at each hop. The network carries 1,000 copies of identical data simultaneously.

Multicast solves this by delivering one copy of the data into the network and having the network replicate it — only at the points where the traffic must diverge to reach different receivers. The sender transmits 1 Gbps once. The network replicates it at routers that have multiple branches going to receivers, and only there.

## The Fundamental Design

Multicast uses a specific address range: **224.0.0.0/4** — the Class D address space, from 224.0.0.0 to 239.255.255.255. These addresses are group identifiers, not host addresses. A receiver "joins" a multicast group by signaling its interest to the network; the sender transmits to the group address, and the network delivers to all current group members.

The key contrast with unicast: the sender does not know who is listening. The sender transmits to 239.1.1.1 and relies on the network to deliver to every host that has joined that group. As receivers join and leave, the network's delivery tree adapts — without any action required by the sender.

This decoupling of sender from receivers is multicast's fundamental design property and the source of both its power and its complexity.

## IGMP: How Receivers Join Groups

When a host wants to receive traffic for a multicast group, it sends an **IGMP (Internet Group Management Protocol)** message to its local router. This is called a **membership report** — "I want to receive traffic for group 239.1.1.1."

The router records this membership and begins forwarding traffic for that group to the interface where the host is connected. When the host no longer wants the traffic, it sends an IGMP **leave** message. The router confirms no other host on that interface still wants the group and, if confirmed, stops forwarding.

IGMP is entirely local — between the host and its first-hop router. It does not propagate across the wider network. The router uses IGMP to know which of its local interfaces have interested receivers; it uses **PIM (Protocol Independent Multicast)** to signal this interest upstream toward the source and to build the delivery tree across the network.

## PIM: Building the Delivery Tree

**PIM (Protocol Independent Multicast)** is the protocol that multicast routers use to build the tree of paths from a source to all receivers. PIM does not discover routes itself — it is "protocol independent" because it uses the existing unicast routing table (BGP, OSPF, IS-IS) for path information. PIM decides which direction is "upstream" (toward the source) and which is "downstream" (toward receivers) based on the unicast routing table.

There are two main variants of PIM:

**PIM Dense Mode (PIM-DM):** Assumes most routers in the network have interested receivers. Floods multicast traffic everywhere first, then prunes branches where there are no receivers. Operationally simple but creates significant unnecessary traffic in sparse receiver environments. Not appropriate for large networks.

**PIM Sparse Mode (PIM-SM):** Assumes receivers are sparse — most routers do not have interested receivers. Uses an explicit join model: routers send explicit join messages upstream only when they have local receivers. Traffic is not flooded unless a receiver exists. PIM-SM is the standard for production multicast networks.

PIM-SM introduces the concept of a **Rendezvous Point (RP)** — a router that serves as the meeting point between sources and receivers. This is the mechanism that connects sources to receivers without requiring the source to know who is listening, and without requiring receivers to know where the source is.

## Where Multicast Is Used

**Financial services / market data:** Stock exchanges and trading platforms distribute real-time price feeds to thousands of trading systems simultaneously. Unicasting to each is not feasible at the required rate. Multicast is the only scalable solution.

**IPTV and video distribution:** Content delivery within a carrier or enterprise network distributes live video as multicast streams. Set-top boxes and video clients join the group for the channel they want to watch.

**Network management:** Routing protocols themselves use multicast. OSPF uses 224.0.0.5 (all routers) and 224.0.0.6 (all DR/BDR). EIGRP uses 224.0.0.10. These are link-local multicast addresses that do not traverse routers — they are the protocol's mechanism for adjacent router discovery.

**Distributed storage and databases:** Some distributed database systems use multicast for cluster membership announcements and data replication to multiple replicas simultaneously.

**DC fabrics (limited use):** In VXLAN fabrics without EVPN, multicast is used for BUM traffic replication — each VNI is mapped to a multicast group, and BUM frames are flooded via multicast to all VTEPs in that VNI. EVPN replaced this with unicast ingress replication in modern designs, but understanding multicast-based VXLAN is still relevant for operating older deployments.

The next article goes deeper into PIM-SM mechanics — how the protocol actually builds and maintains multicast distribution trees.
