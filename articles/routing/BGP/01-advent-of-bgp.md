# Why the Internet Needed BGP

Imagine for a moment that the entire Internet ran on OSPF. Every subnet. Every router. Every link. Every failure — flooded everywhere.

That thought experiment falls apart quickly. An **Interior Gateway Protocol (IGP)** like OSPF assumes that all routers belong to the same administrative authority. They trust each other completely. They exchange full topology information without hesitation. They build a synchronized database of every link, every cost, every path — and every router in the domain holds an identical copy of that database.

That model works beautifully inside a company. At the scale of the Internet, it would be catastrophic. Imagine thousands of organizations — ISPs, enterprises, governments, academic backbones — all sharing complete link-state information globally. Stability would collapse under convergence storms that never settle. A single misconfigured router in one country could trigger a topology change that flooded the entire world. A malicious attack on the routing protocol, or even an innocent operator mistake, could propagate instantly across every network on earth. And because every router would need to hold the full global topology, the routing database would grow beyond anything hardware could handle.

The Internet needed something different.

Before **BGP** existed, a protocol called **EGP (Exterior Gateway Protocol)** tried to fill that role. EGP could announce reachability — "I can reach these networks" — but that was the extent of its capability. It had no understanding of path attributes, no ability to express routing policy, and no reliable mechanism to prevent routing loops as the network grew. The attempts to build something better on top of EGP failed. EGP was a reachability protocol, not a true routing protocol. The Internet outgrew it.

BGP was designed to replace it — and to solve a fundamentally harder problem.

The first thing BGP introduced was a concept that OSPF has no equivalent for: the **Autonomous System**. An **AS** is a collection of IP prefixes under a single administrative authority, identified by a globally unique **AS number (ASN)**. An ISP is an AS. A large enterprise is an AS. A hyperscaler like Google or Meta is an AS — sometimes several. Inside an AS, you manage your own routing however you choose: OSPF, IS-IS, or whatever fits your architecture. Outside an AS is a boundary of trust. Your routers do not automatically trust another organization's routers, and you do not expose your internal topology to them.

BGP operates at that boundary. It does not flood topology. It shares reachability.

When a BGP router establishes a session with another router, they are initially called **neighbors** — two routers connected by a deliberate, configured session. Once that session is up and they begin exchanging routing information, they become **peers**. That exchange happens over a direct, unicast TCP connection on port 179. There is no multicast. No flooding. No automatic discovery. Every session is intentional. The engineer decides who to peer with, and the protocol opens a dedicated TCP connection to that specific neighbor.

When two BGP peers first connect, they exchange their entire routing tables. After that initial exchange, BGP sends only what changes — incremental, partial updates. A prefix is withdrawn, or a new one is announced, and that delta propagates. Nothing more. This design is what allows BGP to scale where OSPF cannot: it never floods the network; it only informs the peer of what changed.

Two distinct flavors of BGP emerge directly from the AS model. When two routers belong to *different* autonomous systems, the session between them is called **eBGP** — external BGP. This is the BGP of the Internet: ISPs peering with other ISPs, enterprises connecting to upstream providers, hyperscalers exchanging routes at Internet exchange points. When two routers belong to the *same* autonomous system, the session is called **iBGP** — internal BGP. iBGP exists to carry external routing information across an AS without leaking internal topology to anyone outside it.

That separation between eBGP and iBGP looks simple on the surface. In practice, it creates a set of constraints and behaviors that shape how every BGP network is designed. In the next article, we will look at exactly how eBGP and iBGP differ — and why those differences matter.
