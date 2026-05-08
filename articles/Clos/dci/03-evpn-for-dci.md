# EVPN for DCI

Once you have a physical transport between data centers — dark fiber, leased wavelengths, or MPLS circuits — you need a network architecture that runs over it. For modern DC fabrics built on VXLAN and EVPN, the natural extension is to use the same control plane across the DCI link.

EVPN/VXLAN for DCI extends the same technology used within the DC to connect two separate fabrics, giving you both Layer 2 extension and Layer 3 routing across the DCI link — using the same BGP control plane you already operate.

## The Architecture: Two Fabrics, One Control Plane

In a typical two-DC EVPN DCI design, each data center runs its own spine-leaf fabric with EVPN/BGP as the overlay control plane. At the edge of each fabric are **Border Leaf** switches (sometimes called DCI gateways or border routers) — the leaf switches that connect to the DCI transport network.

The BGP topology extends from within each DC across the DCI link:

```
DC-A: Leaf → Spine (Route Reflector) → Border Leaf
                                              ↕ (DCI link)
DC-B: Border Leaf → Spine (Route Reflector) → Leaf
```

The Border Leaf switches peer BGP across the DCI link, exchanging EVPN routes between the two fabrics. EVPN route types carry different information:

- **Type 2 (MAC/IP routes):** Allow each DC's leaves to know about hosts in the other DC. With this, a host in DC-A can reach a host in DC-B with direct VXLAN encapsulation, without traffic going through a central gateway.
- **Type 3 (BUM routes):** Build the inter-DC BUM replication list — which VTEPs in DC-B should receive broadcast/unknown unicast/multicast traffic for a given VNI.
- **Type 5 (IP Prefix routes):** Carry subnet-level reachability between DCs, enabling inter-DC Layer 3 routing without requiring MAC-level host advertisements for all hosts.

## Layer 2 Extension: Stretched VNIs

Some applications require the same Layer 2 segment to span both data centers. In EVPN DCI, this is implemented by stretching a VNI across the DCI link — configuring the same VNI in both DCs and allowing EVPN Type 2 routes to propagate between them.

A host in DC-A at 10.1.1.5 and a host in DC-B at 10.1.1.7 can be in the same /24 subnet, on the same VNI, reachable from each other via VXLAN encapsulation across the DCI link.

This enables:
- **VM live migration** (vMotion): A VM migrates from a host in DC-A to DC-B. The new leaf in DC-B advertises a Type 2 route for the VM's MAC/IP. Traffic from DC-A that was previously going to the DC-A VTEP is redirected to the DC-B VTEP. The migration is transparent to the application — the IP address does not change.
- **Active-active clustering:** Some applications (database clusters, NFS clusters) require Layer 2 adjacency between nodes. Stretched VNIs allow cluster nodes to reside in separate DCs with full Layer 2 visibility.

**The danger of Layer 2 extension:** Extending a broadcast domain across data centers means that problems in one DC can propagate to the other. A broadcast storm in DC-A's VNI 10010 will cross the DCI link and impact DC-B's VNI 10010. EVPN's ARP suppression mitigates this (reducing broadcast traffic significantly), but the risk does not disappear entirely.

Best practice: extend Layer 2 across DCI only for VNIs where the application genuinely requires it. Do not stretch VNIs by default. Use Layer 3 routing for everything that does not require Layer 2 adjacency.

## Layer 3 Routing: Type 5 Routes Across DCI

For applications that communicate using IP routing (the majority of modern applications), EVPN Type 5 routes provide inter-DC reachability without extending Layer 2.

DC-A's Border Leaf advertises Type 5 routes for all subnets in DC-A into the BGP session with DC-B's Border Leaf. DC-B installs these routes pointing to DC-A's Border Leaf VTEP. Traffic from DC-B destined for a subnet in DC-A is encapsulated in VXLAN and sent to DC-A's Border Leaf, which routes it into the correct VNI within DC-A.

This provides inter-DC IP routing while keeping Layer 2 domains completely separate — no broadcast domain extension, no spanning-tree risk, no storm propagation across the DCI link.

**The active-active vs active-standby question:** When two DCs both host the same subnets (for high availability), both DCs advertise Type 5 routes for the same prefixes. The BGP path selection and community tagging on those routes determines how inter-DC traffic is load-balanced. This is where EVPN route targets and BGP communities become policy tools — not just control-plane identifiers.

## Anycast Gateways at the DCI Boundary

Modern EVPN fabrics use **Anycast IRB gateways** — every leaf switch is configured as the default gateway for its locally attached subnets, with the same IP and MAC address. A host in DC-A that sends traffic to its default gateway reaches any leaf in DC-A — they all respond identically.

At the DCI boundary, the anycast gateway concept extends to the border leaves. DC-B traffic destined for DC-A's subnets is routed to DC-A's border leaf, which acts as the entry point for that traffic into DC-A's fabric. The border leaf performs the final routing and VXLAN encapsulation to deliver to the correct leaf within DC-A.

This avoids the tromboning problem (traffic going to DC-A's core router, back to DC-B, and then to the correct DC-B leaf) by making routing decisions at the closest point to the traffic source.

## Failure Modes and Split-Brain

The most serious operational concern for DCI is **split-brain**: the DCI link fails, both DCs continue operating independently, and the two halves of the network diverge. When the DCI link is restored, the two fabrics must reconcile potentially conflicting state — MAC address conflicts, overlapping IP assignments, routing divergence.

Mitigation strategies:
- **Prioritize Layer 3 over Layer 2 extension:** A split-brain in a pure Layer 3 DCI design means each DC can continue serving its local users independently. Traffic that was crossing the DCI is lost, but neither DC fails catastrophically.
- **Active-standby for stretched VNIs:** Rather than running stretched VNIs in active-active mode, prefer active-standby: one DC is the primary for a given VNI, the other is standby. This eliminates the MAC conflict risk during split-brain.
- **Fast detection:** DCI link failures should be detected in milliseconds (BFD, link-layer failure detection) so that routing can converge quickly and traffic is redirected rather than blackholed.
- **Out-of-band management path:** Ensure the DCI management plane (BGP sessions, telemetry, configuration management) has an out-of-band path that survives a DCI data-plane failure. You need to see what happened even if the main DCI link is down.

DCI failure management is where operational maturity is demonstrated. Anyone can build a DCI that works under normal conditions. The design quality shows in how gracefully it handles failures — and how quickly and completely it recovers.
