## OSPF Overview

OSPF, or Open Shortest Path First, is a dynamic routing protocol. Unlike static routing, where paths are manually defined, OSPF allows routers to discover the network topology automatically. When the network first comes up, OSPF builds a map of the entire topology. If something changes - a link fails or a device goes down - OSPF recalculates and reconverges.

But how does that actually happen?

For OSPF to work, routers must first talk to each other. And before they can exchange meaningful routing information, they must become neighbors.

Neighbor formation is the starting point of everything in OSPF. Routers send periodic hello packets out of their interfaces. If two routers agree on certain parameters — such as area ID, subnet, hello/dead timers, and authentication settings — they form a neighborship. Only after this relationship is established do they begin exchanging deeper information.

Once routers become neighbors, they start sharing information about their directly connected interfaces. Each router describes its links, its interface states, and the cost associated with each link. This information is collected into a structure called the Link-State Database (LSDB). The key idea behind OSPF is that every router within the same area should have an identical view of this database.

In other words, OSPF routers inside an area share a synchronized map of the network.

After building this shared map, each router independently runs the Shortest Path First (SPF) algorithm - commonly known as Dijkstra’s algorithm. Using the link costs (which are typically derived from interface bandwidth), the router calculates the shortest path to every destination in the topology. The result of this calculation is the routing table.

Now consider what happens when the network changes.

Suppose a link fails or a router goes down. How does OSPF detect it? This is where the hello and dead timers come into play. Hello packets are sent periodically on each OSPF-enabled interface. If a router stops receiving hello packets from a neighbor within the configured dead interval, it assumes that neighbor is no longer reachable.

The router that detects the failure generates a Link-State Advertisement (LSA) describing the change. This update is flooded to all other routers in the same area. Each router updates its link-state database and reruns the SPF algorithm. This process is called convergence.

Because OSPF uses flooding and maintains a synchronized database, convergence is typically fast and consistent across the network.

Now an important question arises: as the network grows, does every router need to form a neighbor relationship with every other router?

Overall, it is a system of multiple components working together - hello packets, LSAs, SPF calculations, area hierarchy, and database synchronization - all operating quietly in the background.

In the upcoming sections, we will peel back each of these layers and examine how OSPF truly functions under the hood.
