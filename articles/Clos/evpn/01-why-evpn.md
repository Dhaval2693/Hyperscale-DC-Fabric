# Why EVPN Exists

You have built a VXLAN fabric. Spine and leaf switches are cabled, VNIs are assigned, VTEPs are configured. Traffic can flow between hosts on the same segment across the underlay. The overlay works.

Now ask a simple question: how does Leaf-A know which VTEP to send a frame to when it has never seen the destination MAC address before?

The honest answer, in a basic VXLAN deployment, is that it does not know. So it floods the frame — sends it to every VTEP in the fabric simultaneously. Every leaf receives it. Every leaf processes it. Only the correct one actually delivers it to the destination. This is called **flood and learn**, and it is the default behavior of VXLAN when deployed without a control plane.

Flood and learn works in small environments. In a hyperscale fabric with hundreds of leaf switches and tens of thousands of hosts, it is a disaster.

Every unknown unicast frame becomes a broadcast storm across the entire fabric. Every ARP request from every host gets replicated to every VTEP. Every new VM that comes up — in a cloud environment, that happens thousands of times per day — triggers a wave of flooding until every switch has learned its MAC address through data-plane observation. The BUM traffic (Broadcast, Unknown unicast, Multicast) grows proportionally with the number of VTEPs, and it never stops because the data plane is always chasing state it does not have ahead of time.

The fabric becomes increasingly inefficient as it scales. More hosts mean more flooding. More VTEPs mean more replication. The underlay carries traffic that carries no useful payload — just control signals dressed up as data frames.

VXLAN needed a control plane.

## The Insight: Separate the Learning from the Forwarding

The fundamental problem with flood and learn is that it conflates two things: **learning where hosts are** and **forwarding traffic to them**. In flood and learn, the fabric can only learn a host's location by sending traffic at it and watching where the reply comes from. The data plane is doing the job that a control plane should do.

**EVPN — Ethernet VPN** — separates these concerns. It provides a control plane for VXLAN fabrics: a mechanism for VTEPs to advertise what they know about locally attached hosts to every other VTEP in the fabric, before any data traffic is sent.

The control plane EVPN chose to build on is BGP — specifically, MP-BGP with a new address family. This was not an arbitrary choice. BGP was already the proven mechanism for distributing reachability information at scale across distributed systems. It was running in every data center fabric worth talking about. It had all the policy knobs, the route reflection mechanisms, the filtering primitives, and the operational familiarity that network engineers already possessed. Building EVPN on top of BGP meant inheriting all of that for free.

The result: VTEPs establish BGP sessions with route reflectors (usually the spines). When a host connects to a leaf switch, the leaf immediately advertises that host's MAC address and IP address into BGP. Every other VTEP in the fabric receives this advertisement and builds its forwarding table proactively — before it ever needs to send traffic to that host. Unknown unicast flooding drops to near zero. ARP suppression becomes possible because the leaf already knows the MAC-to-IP binding and can answer ARP requests locally without flooding the fabric.

## What EVPN Actually Does

EVPN is an address family for BGP — specifically **AFI 25, SAFI 70** in BGP terminology. It introduces a new type of BGP route called an **EVPN route**, and defines several route types, each carrying a different category of reachability information.

The three route types you need to know cold for any hyperscale DC interview:

**Type 2 — MAC/IP Advertisement Route.** This is the core of EVPN. When a host connects to a leaf, the leaf advertises a Type 2 route containing the host's MAC address, its IP address, and the VTEP IP of the originating leaf. Every other VTEP receives this and knows: "to reach this MAC/IP, encapsulate in VXLAN and send to that VTEP." No flooding needed. No ARP needed. The control plane has already distributed the information.

**Type 3 — Inclusive Multicast Ethernet Tag Route.** This handles BUM traffic — the broadcast, unknown unicast, and multicast frames that still need to be delivered to all VTEPs in a segment. A Type 3 route is how a VTEP advertises "I have hosts in VNI X — please include me in the BUM flood list for that VNI." Instead of a static ingress replication list configured per VTEP, the fabric builds it dynamically from Type 3 route advertisements.

**Type 5 — IP Prefix Route.** This extends EVPN beyond Layer 2. A Type 5 route advertises an IP prefix — a subnet or a host route — without requiring an associated MAC address. This is how EVPN handles inter-subnet routing at scale and how it integrates with external networks. Where Type 2 is the Layer 2 control plane, Type 5 is the Layer 3 control plane.

## In a Hyperscale Context

At AWS scale — where a single Availability Zone may have hundreds of leaf switches and tens of thousands of servers — flood and learn is simply not an option. The BUM traffic alone would consume meaningful bandwidth on every inter-switch link. ARP flooding from virtualized workloads, where VMs spin up and down constantly, would create continuous noise across the fabric.

EVPN with BGP route reflection gives every leaf switch an accurate, proactively populated forwarding table. ARP suppression at the leaf means the server never even sees the ARP request — the switch answers it locally from its BGP-populated table. Unknown unicast flooding becomes a rare exception rather than the normal operating mode.

This is why every modern hyperscale DC fabric runs EVPN. Not because it is the only way to build a VXLAN fabric, but because it is the only way to build one that scales.

In the next article, we will go deeper into each EVPN route type and what information each one carries.
