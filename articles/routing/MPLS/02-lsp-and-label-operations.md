# LSPs and Label Distribution

An MPLS label on its own does nothing. What makes MPLS work is the **Label Switched Path (LSP)** — a predetermined, unidirectional path through the network along which all packets with a given label are forwarded.

An LSP connects an ingress router (where labels are pushed onto packets) to an egress router (where labels are popped and the packet re-enters normal IP forwarding). Every router along the path holds a label binding: "when I receive a packet with label X on interface A, swap it for label Y and forward it out interface B." The chain of these bindings across every hop in the path constitutes the LSP.

Building an LSP requires distributing label bindings across all routers in the path. Two protocols do this: **LDP** and **RSVP-TE**. They have fundamentally different philosophies.

## LDP — Label Distribution Protocol

LDP is the simpler of the two. Its job is straightforward: for every route that exists in the IP routing table, automatically create a corresponding label binding and distribute it to neighboring routers.

**How LDP works:**

1. LDP neighbors discover each other using multicast hellos on each link (UDP port 646).
2. Once neighbors are discovered, they establish a TCP session and begin exchanging label bindings.
3. Each router advertises a label for every prefix in its IP routing table to its LDP neighbors.
4. Neighbors install those bindings in their LFIB, chaining them to create end-to-end LSPs.

The LSP that LDP builds follows the exact same path as the underlying IGP (IS-IS or OSPF). If OSPF routes traffic from A to B via the path A → C → D → B, the LDP-established LSP follows the same path. LDP does not have the ability to steer traffic differently from the IGP — it just adds label switching on top of whatever path IGP has already computed.

**Where LDP is used:** LDP is the right choice when you simply want the efficiency of label switching across a backbone without needing traffic engineering. It is operationally simple — configure LDP on all backbone interfaces and it builds LSPs automatically. No path computation. No reservation state. For basic MPLS VPN deployments where traffic engineering is not required, LDP is sufficient.

**LDP's limitation:** Because LDP LSPs follow IGP paths, you have no ability to route traffic differently based on bandwidth availability, administrative preference, or SLA requirements. If a path is congested, LDP cannot shift traffic to an alternate path. For that, you need RSVP-TE.

## RSVP-TE — Resource Reservation Protocol with Traffic Engineering Extensions

RSVP-TE takes a fundamentally different approach. Instead of automatically distributing labels for IGP routes, RSVP-TE establishes LSPs along **explicitly specified paths** and **reserves bandwidth** along the way.

**How RSVP-TE works:**

1. A path computation — either by the ingress router using CSPF (Constrained Shortest Path First) or by a centralized PCE (Path Computation Element) — determines the explicit route the LSP should follow. This route may differ from the IGP shortest path.
2. The ingress router sends a **Path message** along the specified route, hop by hop. Each router along the path notes the bandwidth reservation request and reserves resources.
3. The egress router responds with a **Resv message** that travels back upstream. As the Resv message traverses each hop, that hop allocates the requested bandwidth and assigns a label binding.
4. The labels carried in the Resv message chain together to form the LSP. By the time the Resv message returns to the ingress, the end-to-end LSP is established with bandwidth reserved at every hop.

**What this gives you:** Traffic on this LSP is guaranteed the reserved bandwidth. You can run multiple RSVP-TE tunnels across your backbone, each following a different path, distributing load based on explicit engineering decisions rather than IGP metric convergence. When a link fails, RSVP-TE can pre-compute alternate paths (Fast Reroute) and switch traffic in under 50ms.

**Where RSVP-TE is used:** Service providers with SLA commitments — guaranteed bandwidth, latency bounds — rely on RSVP-TE traffic engineering. It is also common in large enterprise WAN backbones. The tradeoff is operational complexity: you are now managing explicit tunnel configurations, bandwidth reservations, and path computation in addition to the underlying IGP.

## Penultimate Hop Popping (PHP)

One operational detail that matters in practice: MPLS labels are typically popped not at the egress PE but at the **penultimate hop** — the router one hop before the egress.

Why? Consider what happens at the egress PE without PHP. The PE receives a packet with an MPLS label. It pops the label, sees the IP header, and makes an IP forwarding decision. That is two lookups — one to pop the label and one to look up the IP destination. With PHP, the penultimate hop pops the label before forwarding to the egress PE. The egress PE receives a raw IP packet (or a packet with only the inner VPN label if this is a VPN scenario), makes a single IP lookup, and forwards it. One lookup instead of two.

PHP is enabled by the egress PE signaling a special label value — **Implicit NULL (label 3)** — to its upstream neighbor. When the upstream router receives Implicit NULL as the label binding for a prefix, it knows to pop its label before forwarding rather than swapping it.

## The Label Stack

MPLS supports multiple labels stacked on a single packet. Each label has its own S-bit — the stack-bottom bit — with only the innermost label having S=1. Routers process only the top of stack.

This stacking is what enables hierarchical MPLS. In an MPLS L3VPN, a packet typically carries two labels:

- **Outer label (transport label):** Swapped at every P router across the backbone. Identifies the LSP from ingress PE to egress PE.
- **Inner label (VPN label):** Not touched by P routers. Popped at the egress PE to identify which VRF and which customer interface the packet belongs to.

P routers never see the inner VPN label. They only process the outer transport label and forward. The egress PE processes both — pops the transport label (already done by PHP), reads the VPN label, and delivers to the correct customer context.

This two-label design is what keeps P routers free of customer routing state — the entire customer context is encoded in the inner label, processed only at the edge. The backbone remains simple and scalable regardless of how many customers or prefixes the VPN service carries.
