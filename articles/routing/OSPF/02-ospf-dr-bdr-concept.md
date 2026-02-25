## DR/BDR: Why Not Everyone Talks to Everyone

Does OSPF need to form a neighborship with every router in the network?

On a point-to-point link, that makes perfect sense. There are only two routers, so forming a full adjacency is simple and efficient. But in a broadcast domain, things look very different.

Imagine a shared Ethernet segment with 20 routers connected to the same network. If every router formed a full adjacency with every other router, the control-plane overhead would grow quickly. Each router would maintain state for every neighbor and process every topology change individually.

The number of adjacencies in such a setup is calculated using the formula n(n − 1) / 2. With 10 routers, that already results in 45 adjacencies. With 20 routers, that becomes 190 adjacencies. Now imagine scaling that further.

That amount of adjacency formation and link-state flooding is unnecessary and inefficient.

This is where the concept of the **Designated Router (DR)** and **Backup Designated Router (BDR)** comes into play.

The DR exists to centralize adjacency formation and flooding. Instead of every router forming a full adjacency with every other router, all routers form full adjacencies only with the DR and the BDR. The DR becomes the representative of the multi-access network and advertises that segment’s state to the rest of the OSPF area.

The BDR exists for stability. It forms full adjacencies just like the DR and keeps its database synchronized. If the DR fails, the BDR immediately takes over without forcing the entire segment to restart the election process.

All other routers on that segment — the ones that are neither DR nor BDR — are called **DROther** routers. They still participate fully in OSPF, but they form full adjacencies only with the DR and BDR, not with every router on the segment. This is what keeps adjacency growth under control.

To understand how this works, let’s walk through a simple example.

Imagine four routers connected to the same broadcast network:

- R1 with priority 1 and router ID 1.1.1.1  
- R2 with priority 5 and router ID 2.2.2.2  
- R3 with priority 10 and router ID 3.3.3.3  
- R4 with priority 0 and router ID 4.4.4.4  

First, OSPF determines which routers are eligible. Any router whose interface priority is set to 0 is ineligible to become DR or BDR. That immediately removes R4 from consideration.

Now among the remaining eligible routers — R1, R2, and R3 — the election begins.

OSPF elects the BDR first. The router with the highest interface priority wins. In this case, R3 has the highest priority of 10, so R3 becomes the BDR.

Next, OSPF elects the DR from the remaining eligible routers — R1 and R2. Between those two, R2 has the higher priority (5 vs 1), so R2 becomes the DR.

The final result looks like this:

- R2 → DR  
- R3 → BDR  
- R1 → DROther  
- R4 → DROther (ineligible for DR/BDR)

Notice something important: DR and BDR are properties of the interface, not the router itself. A router could be a DR on one interface and a regular participant on another.

Also, the election is non-preemptive. If a new router later joins with a higher priority, it does not automatically replace the current DR. Stability is preferred over constant role changes. A new election only happens if the DR or BDR fails.

OSPF uses multicast addresses to coordinate this behavior efficiently. Hello packets are sent to 224.0.0.5 (All OSPF Routers). Updates specifically destined for the DR and BDR are sent to 224.0.0.6. This structure ensures controlled flooding rather than chaotic message exchange.

Once you understand DR, BDR, and DROther roles, you begin to see OSPF as a carefully engineered system designed to prevent adjacency explosion while maintaining database consistency and fast failover.
