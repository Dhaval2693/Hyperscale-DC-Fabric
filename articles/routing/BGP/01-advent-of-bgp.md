# Why the Internet Needed BGP

Imagine for a moment that the entire Internet ran on OSPF.
Every subnet.
Every router.
Every link.
Every failure.

Flooded everywhere. It sounds simple at first - until you think about scale.
An Interior Gateway Protocol (IGP) like OSPF assumes that all routers belong to the same administrative authority. They trust each other. They freely exchange topology information. They build a synchronized database of the network.

That works well inside a company. It would be catastrophic across the world.

If every ISP, enterprise, government network, and academic backbone shared full link-state information globally:
- Stability would collapse.
- Convergence storms would ripple worldwide.
- A single configuration mistake could impact the entire Internet.
- A malicious attack against the routing protocol could propagate instantly.

The Internet needed something different. It needed a protocol that does not expose topology. A protocol that does not flood. A protocol built around control and policy.
That protocol became **BGP**. 

In BGP, two routers running BGP directly over a session are **neighbors**. Once that session is established and they begin exchanging reachability information, they become **peers**.
BGP establishes a unique, unicast TCP connection (port 179) to each neighbor. There is no multicast. No flooding. Every session is deliberate. When two BGP neighbors first establish a session, they exchange their entire routing tables. After that, they only exchange incremental updates - only what changes. This design is what makes BGP scalable.It shares reachability. Not topology. Not internal design. Not link-state. And that difference is why the Internet survived exponential growth.
