# Understanding BGP Peering: EBGP vs IBGP

At first glance, BGP peering seems simple. Two routers connect. They exchange routes. Traffic flows. But the type of peering defines the behavior of the entire system.

If two BGP neighbors belong to different Autonomous Systems, the session is called **External BGP (EBGP)**. If two neighbors belong to the same AS, the session is called **Internal BGP (IBGP)**.
That distinction is small in configuration. It is enormous in design.
EBGP operates across trust boundaries. IBGP operates inside a single administrative domain.


Inside an AS, routers must share external routes with each other. But BGP has a built-in loop prevention rule - If a router sees its own ASN in the AS_PATH, it rejects the route. This works perfectly across different ASes.
Inside the same AS, however, all routers share the same ASN. So how do they share routes without breaking loop prevention?
In IBGP, the rule becomes - do not re-advertise routes learned from one IBGP peer to another IBGP peer. That prevents loops - but it creates a scaling issue.
To ensure every router knows every external route, a **full mesh of IBGP sessions** must exist. If you have 10 BGP routers inside an AS, each must peer with the other 9.
As the number of routers increases, the number of sessions grows rapidly. This is one of the reasons IBGP does not scale linearly without additional design tools like route reflectors or BGP confederations. More about this in the later chapter.

But why we need BGP protocol inside AS if we have IGP like OSPF? Why not redistribute EBGP routes into OSPF? The answer is simple. Disaster.
If you inject thousands (or hundreds of thousands) of Internet routes into an IGP:
- SPF calculations explode.
- CPU utilization spikes.
- Memory consumption increases dramatically.
- Convergence events become catastrophic.
- A single routing issue could collapse the internal network.

IGPs were not designed to carry Internet-scale routing tables. BGP exists to protect the stability of the internal routing domain.
