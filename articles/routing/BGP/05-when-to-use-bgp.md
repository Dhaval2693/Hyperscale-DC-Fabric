# When Do You Really Need BGP?

There is a common misconception in networking that the moment you connect to an ISP, you must run BGP. That is not true.

Many small and even medium-sized networks run perfectly well without it. Imagine a company connected to a single ISP. One public prefix. Basic internet access for employees and a website to host. There is no need to influence traffic, no need to manipulate paths, no need to receive a full internet routing table. In this case, a static default route pointing toward the ISP is all you need. The ISP statically routes your prefix back to you. Traffic flows. No dynamic sessions. No path attributes. No state machine to maintain. It simply works.

Static routing is quiet, predictable, and lightweight. It consumes almost no CPU, requires no session maintenance, and introduces no risk of a routing protocol misconfiguration taking down your connectivity. When the design is simple, the protocol should be too.

The moment your design stops being simple, the calculus changes. Now imagine you are connected to two ISPs. Suddenly, you care about which provider should handle outbound traffic, what happens if one goes down, whether you can prefer one ISP for certain destinations, and how you influence which provider inbound traffic uses to reach you. You want to filter what routes you receive, and you want failover to happen automatically — not because an engineer noticed the outage and updated a static route.

Static routing can approximate very basic failover using floating routes with higher administrative distance. But the moment policy matters, static routing becomes rigid. It has no mechanism to withdraw your prefix from a failed provider, no way to express preference across multiple upstream paths, and no ability to react dynamically to what your providers are advertising.

BGP exists for policy. It lets you advertise selectively, filter what you receive, manipulate path preference, and scale cleanly across multiple providers — all expressed in the routing protocol itself, enforced dynamically as the network changes. The protocol does not define what optimal means. It gives you the mechanisms to define it on your own terms.

Even once BGP is running, a separate decision remains: what routing information to actually receive from your upstream providers. At the most conservative end, you accept only a **default route** — the ISP says "send everything unknown to me," and your router holds no internet prefixes at all. This works well with a single upstream and no path decisions to make. A step up is a **partial table** — your ISP advertises the routes it can reach more efficiently, plus a default for everything else. Your router makes smarter forwarding decisions for a subset of destinations without the cost of holding the full table. At the far end is the **full routing table** — the complete BGP table of over a million prefixes, giving your router total visibility into every path on the internet. Full tables are justified only when you need to make precise path decisions across multiple providers, and they demand significant memory and CPU on every router that holds them.

The threshold for needing BGP is not about the size of your network. It is about whether control and redundancy are requirements. A small network with two ISPs and real failover needs BGP. A large enterprise with a single, well-connected upstream may not. Once you know what your network needs to do, the answer is usually clear.

Modern data centers have taken BGP even further, using it as the internal routing protocol of choice inside large Clos fabrics where scale and clear failure domains matter more than simplicity. But that story comes later, after the protocol mechanics are fully on the table.

Once the design calls for BGP, the next question is what happens when you connect to more than one provider. That is where multihoming comes in — the decision to connect your AS to multiple external networks for redundancy, path diversity, and policy control. In the next article, we will look at what multihoming means and why it shapes so much of how BGP is actually deployed.
