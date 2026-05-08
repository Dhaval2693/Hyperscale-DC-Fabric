# MPLS L3VPN and L2VPN

MPLS enables two fundamentally different ways to sell connectivity as a service: L3VPN, where the provider participates in the customer's routing, and L2VPN, where the provider transparently transports Layer 2 frames as if the customer had a direct Ethernet connection between sites. Both use MPLS for transport, but the boundary of responsibility — and the complexity — differs significantly.

## MPLS L3VPN

In an MPLS L3VPN, the service provider takes on routing responsibility. The provider's PE routers maintain per-customer routing tables, exchange routing information with customer CE routers, and route customer traffic across the backbone.

**The VRF: Virtual Routing and Forwarding**

The key mechanism that makes L3VPN possible is the **VRF**. Every PE router maintains a separate routing table — a VRF — for each customer or each logical VPN. Customer A's routes are in VRF-A. Customer B's routes are in VRF-B. These routing tables are completely isolated from each other and from the provider's global routing table. Customer A's routes never appear in Customer B's VRF, and neither customer's routes appear on P routers at all.

This isolation is what allows a provider to sell VPN service to multiple customers simultaneously over the same physical infrastructure without any risk of routing information leaking between them.

**Route Distinguisher (RD)**

A problem arises immediately: two different customers may use the same IP address space. Customer A has a site at 10.1.0.0/24 and Customer B also has a site at 10.1.0.0/24. When these routes are distributed via MP-BGP between PE routers, they must be kept distinct even though the IP prefixes are identical.

The **Route Distinguisher** solves this. An RD is a 64-bit value prepended to an IP prefix to create a unique **VPNv4 prefix** in the format RD:prefix. Customer A's route might be 100:1:10.1.0.0/24 and Customer B's route might be 100:2:10.1.0.0/24. These are distinct in the BGP control plane even though the IP portions are identical.

The RD is purely a BGP identifier. It is not used for forwarding.

**Route Target (RT)**

How does a PE know which VRFs should import which BGP VPNv4 routes? This is where **Route Targets** come in.

Route Targets are BGP communities attached to VPNv4 routes. Each VRF has:
- An **export RT**: attached to every route it exports into MP-BGP
- An **import RT**: defines which RT values the VRF will import from MP-BGP

When a PE advertises a VPNv4 route, it attaches the export RT. When a remote PE receives the route, it checks all local VRFs: does any VRF's import RT match this route's export RT? If yes, import the route into that VRF. If no, discard.

This flexible import/export model allows service providers to build different VPN topologies:
- **Full mesh**: all sites share the same RT, so every site can reach every other site
- **Hub and spoke**: remote sites export to one RT, import from another; the hub site imports from all spokes and exports to all spokes
- **Extranet**: two different customers share specific routes by configuring matching RTs on specific VRFs

**Data Plane: Two Labels**

When customer traffic crosses the backbone, it carries two MPLS labels:

1. **Transport label** (outer): Identifies the RSVP-TE or LDP LSP from ingress PE to egress PE. Swapped at every P router. Popped at the penultimate hop via PHP.
2. **VPN label** (inner): Assigned by the egress PE and advertised via MP-BGP along with the VPNv4 prefix. Identifies which VRF and which CE interface to deliver the traffic to on the egress PE.

P routers only process the transport label. The VPN label is completely opaque to them. The egress PE, after PHP has removed the transport label, reads the VPN label to determine the correct VRF and customer interface. Then it makes a normal IP lookup within that VRF and forwards to the CE.

## MPLS L2VPN

L2VPN takes a different approach. Instead of routing customer traffic, the provider transparently delivers Ethernet frames. From the customer's perspective, it is as if their sites are connected by a direct Ethernet link, even though the actual transport is an MPLS backbone.

There are two main L2VPN service types:

**VPWS (Virtual Private Wire Service) — Point-to-Point**

VPWS, sometimes called a pseudowire, creates a point-to-point Ethernet connection between exactly two customer sites. The PE at each end has a local attachment circuit (an interface connected to the customer CE). Any frame arriving on one attachment circuit is encapsulated in MPLS and delivered to the attachment circuit at the remote end — unchanged, bit-for-bit.

The customer CE devices at both ends believe they have a direct Ethernet connection. They can run any protocol they want — OSPF, BGP, their own proprietary signaling — and the provider network is invisible. The provider does not participate in any Layer 3 routing.

This is the simplest L2VPN service and the one I most commonly worked with at ECI Telecom. Provisioning it requires:
- Configuring the attachment circuit on both PE routers
- Establishing a pseudowire (a signaled or static MPLS label pair) between the two PEs
- Optionally, running LDP-based pseudowire signaling to automate label exchange

**VPLS (Virtual Private LAN Service) — Multipoint**

VPLS extends the concept to multiple sites. Instead of a point-to-point wire, the provider creates a virtual LAN that all customer sites share. Any frame sent by a CE at one site can be delivered to any or all other CE devices in the VPLS instance.

VPLS introduces MAC learning in the provider network: PE routers maintain MAC address tables per VPLS instance and learn which CEs are reachable via which pseudowires — mirroring how a Layer 2 switch works, but distributed across the MPLS backbone.

Unknown unicast and broadcast frames are flooded to all pseudowires in the VPLS instance, exactly as a real Ethernet switch would do.

## L3VPN vs L2VPN: Choosing the Right Service

| | L3VPN | L2VPN (VPWS/VPLS) |
|---|---|---|
| Provider involvement | Participates in customer routing | Transparent — no routing |
| Customer control | CE-PE routing protocol required | Customer controls all routing |
| Address overlap | Handled via RD/RT | Customer manages |
| Complexity | High (VRFs, RD, RT, BGP) | Lower (pseudowire + labels) |
| Use case | Managed WAN, multi-site enterprise | Extending Layer 2, migrating legacy protocols |

At ECI Telecom, both were in production simultaneously. Customers with complex multi-site routing requirements and the resources to manage their own CE routers often preferred L3VPN — they got the routing expertise of the provider team. Customers migrating legacy applications that required Layer 2 adjacency between sites, or customers who wanted full control of their own routing, used L2VPN pseudowires.

The ability to understand which service fits which customer requirement — and to troubleshoot each one when it breaks — is what makes MPLS operational experience genuinely valuable.
