# Symmetric vs Asymmetric IRB in EVPN

Once EVPN handles Layer 2 forwarding within a segment, the next question is inter-subnet routing — what happens when a host in VNI 10010 (subnet 10.1.1.0/24) needs to reach a host in VNI 10020 (subnet 10.1.2.0/24)?

In a classical three-tier architecture, this traffic would travel up to a centralized core router and back down. In a spine-leaf EVPN fabric, the design goal is to route at the leaf — distributing the routing function across every leaf switch instead of concentrating it. This is **Integrated Routing and Bridging (IRB)**, and there are two fundamentally different approaches to implementing it: asymmetric and symmetric.

Choosing between them is one of the most common design decisions in any EVPN fabric deployment.

## Asymmetric IRB

In asymmetric IRB, routing and bridging happen at different points on the path depending on direction — hence "asymmetric."

**Ingress leaf does everything.** When a host on Leaf-1 in VNI 10010 sends traffic to a host on Leaf-2 in VNI 10020:

1. Leaf-1 receives the frame from the source host.
2. Leaf-1 routes the packet: looks up the destination IP (10.1.2.50) in its IP routing table, identifies it belongs to VNI 10020, rewrites the MAC header.
3. Leaf-1 encapsulates the packet in VXLAN using **VNI 10020** — the destination VNI, not the source VNI.
4. Leaf-2 receives the packet on VNI 10020, bridges it locally to the destination host. No routing needed on Leaf-2 for this direction.

For the return traffic — host on Leaf-2 sending back to host on Leaf-1:

1. Leaf-2 routes the packet at ingress, encapsulates in **VNI 10010**.
2. Leaf-1 receives and bridges locally.

The asymmetry is that **each leaf routes at ingress and bridges at egress**, but the two directions use different VNIs.

**What this requires:** For asymmetric IRB to work, **every leaf must have all VNIs configured locally** — even VNIs for subnets that have no locally attached hosts. Leaf-1 needs VNI 10020 configured in order to route into it. Leaf-2 needs VNI 10010 configured in order to route into it on return traffic. In a fabric with hundreds of VNIs, this means every leaf carries the full VNI configuration of the entire fabric.

**The tradeoff:** Asymmetric IRB is simpler conceptually and performs well. But requiring every leaf to hold every VNI creates a scaling problem. In a large multi-tenant environment where each tenant has dozens of VNIs, the configuration and state on each leaf becomes enormous. It also makes VNI management operationally complex — adding a new VNI means touching every leaf.

## Symmetric IRB

Symmetric IRB solves the scaling problem by introducing a shared Layer 3 VNI — called the **L3VNI** or **routing VNI** — that is used specifically for inter-subnet traffic.

**How it works:**

When a host on Leaf-1 in VNI 10010 sends traffic to a host on Leaf-2 in VNI 10020:

1. Leaf-1 receives the frame, routes the packet.
2. Leaf-1 encapsulates in the **L3VNI** (not the destination VNI). The L3VNI is associated with a VRF — a virtual routing table shared across all subnets for a given tenant.
3. Leaf-2 receives the packet on the L3VNI, identifies it belongs to the tenant VRF, routes locally to VNI 10020, bridges to the destination host.

For the return traffic:

1. Leaf-2 routes at ingress, encapsulates in the same L3VNI.
2. Leaf-1 receives on the L3VNI, routes to VNI 10010, bridges locally.

Both directions use the same VNI for inter-subnet transit — the L3VNI — which is where "symmetric" comes from.

**What this requires:** Each leaf only needs the L3VNI and the specific L2 VNIs for subnets with locally attached hosts. Leaf-1 does not need to know about VNI 10020 unless it has hosts in subnet 10.1.2.0/24. The full VNI configuration is distributed — each leaf carries only what is relevant to it.

**EVPN Type 5 routes carry the inter-subnet reachability.** When Leaf-2 has hosts in VNI 10020, it advertises a Type 5 route for subnet 10.1.2.0/24 into BGP. Leaf-1 receives this and knows: to route to 10.1.2.0/24, send to Leaf-2's VTEP using the L3VNI. It does not need VNI 10020 configured locally.

## Comparing the Two

| | Asymmetric IRB | Symmetric IRB |
|---|---|---|
| VNI scope on each leaf | All VNIs in fabric | Only local L2 VNIs + L3VNI |
| Route type used | Type 2 only | Type 2 + Type 5 |
| Configuration complexity | High (full VNI mesh) | Lower (distributed) |
| Scale | Limited by VNI count per leaf | Scales to large VNI counts |
| Operational model | Simpler to understand | More moving parts (L3VNI, VRF, Type 5) |

## Which One Is Used in Practice

In hyperscale and large enterprise deployments, **symmetric IRB is the dominant model** — specifically because it solves the VNI scaling problem. Requiring every leaf to hold every VNI becomes operationally untenable as a fabric grows. Symmetric IRB, combined with EVPN Type 5 routes, allows VNI configuration to stay local to the leaves where hosts actually reside.

Hyperscale DC fabrics typically use symmetric IRB for exactly this reason: tenant isolation requires per-tenant VRFs and L3VNIs, and the number of distinct tenant segments in a single availability zone is far too large to require every leaf to hold every segment.

The mental model: asymmetric is simpler but doesn't scale. Symmetric is more complex but designed for large, multi-tenant fabrics. Any design interview question about EVPN inter-subnet routing is really asking you to know this distinction.
