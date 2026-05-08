# EVPN Route Types

EVPN communicates through BGP using a set of structured route types. Each type carries a specific category of reachability information. Understanding what each route type contains and when it is generated is the foundation for understanding any EVPN-based fabric.

The full EVPN specification defines five route types. In data center fabrics, three matter most. One — Type 2 — is the heart of the entire system.

## Type 2 — MAC/IP Advertisement Route

When a host connects to a leaf switch and becomes reachable, the leaf generates a Type 2 route. This advertisement carries:

- The **MAC address** of the host
- Optionally, the **IP address** of the host (when ARP/ND suppression is in use)
- The **VTEP IP** of the originating leaf — so receiving VTEPs know where to send encapsulated traffic
- The **VNI** (Virtual Network Identifier) that maps to the host's segment
- An **Ethernet Tag** identifying the broadcast domain

When a remote leaf receives a Type 2 route, it installs a forwarding entry: "MAC address X is reachable via VTEP Y on VNI Z." From that point forward, any frame destined for that MAC address is encapsulated and sent directly to the correct VTEP without flooding.

The IP address component of a Type 2 route is what enables **ARP suppression**. When a host sends an ARP request looking for the MAC address of a known IP, the local leaf can intercept that ARP, look up the IP in its BGP-populated table, and reply directly with the correct MAC — without ever flooding the ARP request across the fabric. The host gets an answer instantly. The fabric sees zero BUM traffic for that ARP exchange.

This is the difference between a fabric that generates constant background noise and one that is nearly silent under normal operation.

**Key point for interviews:** A Type 2 route with both MAC and IP is the signal that ARP suppression is possible. A Type 2 with only a MAC means the leaf knows the host is there but does not know its IP — perhaps because it learned the MAC through a data-plane event rather than a control-plane event.

## Type 3 — Inclusive Multicast Ethernet Tag Route

Not all traffic can be eliminated through MAC/IP learning. BUM traffic — **B**roadcast, **U**nknown unicast, and **M**ulticast — still needs to reach all VTEPs participating in a given VNI. ARP suppression handles most of the ARP broadcast problem, but there are still legitimate cases where a frame must be delivered to every endpoint in a segment: Layer 2 broadcasts, multicast streams, and cases where a MAC genuinely is unknown.

Before EVPN, the ingress replication list — the list of VTEP IPs that should receive BUM traffic for a given VNI — was statically configured on every leaf. In a fabric with fifty leaf switches, every leaf needed a manually maintained list of the other forty-nine. As the fabric grew, this became an operational burden and a source of configuration drift.

Type 3 routes automate this. When a leaf switch has locally attached endpoints in a VNI, it advertises a Type 3 route containing:

- The **VNI** it is participating in
- Its own **VTEP IP address** (the source of BUM traffic for this VNI)

Every other VTEP in the fabric receives this advertisement and automatically adds the originating VTEP to its ingress replication list for that VNI. When the fabric needs to flood a BUM frame, it has a dynamically maintained, always-accurate list of destinations — built entirely from BGP. No manual configuration, no drift.

As VTEPs join and leave the fabric, the Type 3 advertisements appear and withdraw automatically. The ingress replication list self-heals.

## Type 5 — IP Prefix Route

Type 2 routes handle Layer 2 — they distribute MAC and IP bindings within a segment. But what about routing between segments, or connecting the fabric to external networks?

Type 5 routes carry **IP prefixes** without an associated MAC address. This makes them useful in two specific scenarios:

**Inter-subnet routing in the fabric.** In a VXLAN/EVPN fabric with Integrated Routing and Bridging (IRB), each leaf acts as a default gateway for locally attached subnets. When a host in subnet A needs to reach a host in subnet B, the traffic needs to be routed at the leaf level. Type 5 routes allow leaves to advertise their locally connected subnets and learned routes to each other through BGP, enabling distributed routing across the fabric without a centralized gateway.

**External connectivity.** Border leaves — the leaves that connect the fabric to WAN routers, external BGP peers, or other fabrics — use Type 5 routes to redistribute external prefixes into the EVPN control plane, and to advertise internal fabric prefixes outward. A Type 5 route might carry the default route learned from an upstream ISP, or a specific subnet belonging to another data center reachable over DCI.

**The distinction that matters:** Type 2 is host-specific (a /32 or /128, tied to a MAC). Type 5 is prefix-level (a subnet or aggregate, with no MAC binding). If you hear "EVPN Type 5" in a DCI context, the conversation is about routing prefixes across data centers — not about individual host MAC addresses.

## Types 1 and 4 — Ethernet Auto-Discovery and ES Routes

These two types exist primarily for **multi-homing** scenarios — where a host or rack is connected to two leaf switches simultaneously for redundancy.

**Type 1 — Ethernet Auto-Discovery Route** signals that a VTEP is a member of a given Ethernet Segment (ES). It is used to signal aliasing — the ability for traffic destined to a multi-homed host to be load-balanced across both VTEPs rather than always going to just one.

**Type 4 — Ethernet Segment Route** is used to elect a **Designated Forwarder (DF)** among the VTEPs connected to the same Ethernet Segment. The DF is responsible for forwarding BUM traffic toward multi-homed hosts, preventing duplicate delivery.

In a simple single-homed spine-leaf fabric, you may not encounter Type 1 and 4 in day-to-day operation. But in any design that includes server multi-homing to multiple leaf switches — which is common in high-availability designs — understanding Types 1 and 4 is essential.

## How They Work Together

A complete EVPN fabric uses all of these route types simultaneously:

- Type 3 establishes which VTEPs participate in each VNI
- Type 2 distributes MAC/IP bindings so traffic is forwarded without flooding
- Type 5 handles inter-subnet and external routing
- Types 1 and 4 manage multi-homed attachment points

The result is a fabric where every VTEP has a complete, proactively populated picture of the entire overlay — built through BGP, updated in real time, and requiring no data-plane flooding to maintain.
