## What is routing

Between a client and a server, or between one server and another, there are always multiple hidden hops in between. Those hops used to be called routers. Today, in modern data centers, we often call them switches. The distinction is less important than it used to be, because modern switches are powerful enough to perform routing, forwarding, filtering, and policy enforcement at scale. 

From this point forward, I will use routers and switches interchangeably. What matters is not the name of the box, but the role it plays in moving packets from one place to another.

For these devices to communicate with each other, they need a shared language. That language is called **routing**.

Routing is simply the process by which network devices decide where traffic should go next. But like human languages, there isn’t just one. Different environments require different routing behaviors. The “language” chosen depends on the size of the network, the scale of growth, the desired convergence speed, and the operational philosophy.

If the network is very small - perhaps a lab environment, a small office with a few VLANs, or a simple topology with only a handful of routers and a few dozen hosts - you can configure everything manually. In such cases, **static routing** is perfectly sufficient. You explicitly tell each router where to send traffic for specific destinations. Nothing changes unless you change it. It is predictable, simple, and easy to understand.

But static routing does not scale. The moment the network grows - more subnets, more racks, more links, more devices - manually updating routes becomes operationally fragile. A single missed configuration can blackhole traffic. A link failure requires human intervention. Complexity grows faster than you expect.

This is where **dynamic routing protocols** enter the picture.

Dynamic routing allows routers to automatically exchange reachability information. They discover paths, react to failures, and adapt to topology changes without manual reconfiguration. Instead of hardcoding every path, devices learn from each other.

Among the many routing protocols that exist, two have become especially important in modern networks: **OSPF** and **BGP**. OSPF has traditionally dominated enterprise and campus environments. BGP, originally built to power the internet, has now become the backbone of hyperscale data center fabrics.

The rest of this chapter will focus on these two protocols — not just how they work, but why they are used in different scenarios, and how their behavior changes inside modern data center architectures.
