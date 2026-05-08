# Why MPLS Exists

In the early days of the Internet, routing was straightforward in concept if not in scale. Every router received a packet, examined the destination IP address, performed a longest-prefix match lookup against its routing table, and forwarded the packet out the appropriate interface. Repeat at every hop until the packet reached its destination.

This worked. And as the Internet grew, the routers that made up its backbone became faster, the routing tables became larger, and the engineers maintaining those routers began to notice a problem.

The problem was not the forwarding itself — hardware was improving. The problem was the **inflexibility** of pure IP routing. Every forwarding decision was made independently, at every hop, based solely on the destination IP address. You could not engineer traffic paths. You could not create virtual private networks efficiently. You could not guarantee that two packets from the same flow would take the same path through the network. And for service providers building shared infrastructure that needed to carry traffic for multiple customers with different SLAs, best-effort IP routing was increasingly inadequate.

MPLS — **Multiprotocol Label Switching** — was designed to solve these problems. Not by replacing IP routing, but by adding a layer of engineered control on top of it.

## The Insight: Decide Once, Switch Many Times

The fundamental insight behind MPLS is that the expensive routing decision — the longest-prefix match lookup — only needs to happen once, at the edge of the network. Interior routers should not have to perform IP lookups at all. They should just switch packets based on a simple, fixed-length label.

This maps to a real operational boundary in service provider networks. A service provider has edge routers — called **Provider Edge (PE) routers** — where customer traffic enters and exits the network. Inside the network, there are **Provider (P) routers** that carry transit traffic across the backbone.

In pure IP routing, every P router needs to maintain full BGP routing tables — potentially millions of routes — to forward packets correctly. In MPLS, the PE router at the ingress performs the IP lookup once, assigns a **label**, and pushes the packet into the MPLS network. Every P router along the path just reads the label and switches — no IP lookup, just a table lookup that maps a label to an outgoing interface and a new label.

This is **label switching**: fast, simple forwarding at every interior hop, with all the intelligence concentrated at the edges.

## What a Label Is

An MPLS label is a 32-bit field inserted between the Layer 2 header and the Layer 3 (IP) header. It has four components:

- **Label value** (20 bits): The actual label, locally significant between adjacent routers. Label values are not globally meaningful — the same label value can mean different things on different routers and different interfaces.
- **TC (Traffic Class)** (3 bits): Used for QoS marking — maps to CoS/DSCP values for priority handling.
- **S (Bottom of Stack)** (1 bit): Indicates whether this is the last label in a stack. MPLS supports a stack of labels — multiple labels stacked on a single packet — which enables hierarchical tunneling.
- **TTL** (8 bits): Functions like IP TTL, preventing loops.

Because the label is locally significant, each router along the path has its own label for the same forwarding path. A router receives a packet with label X, looks up X in its **Label Forwarding Information Base (LFIB)**, and knows: swap label X for label Y and forward out interface eth0. The next router does the same with its own table.

## The Three Label Operations

Every MPLS router performs exactly one of three operations on each packet:

**Push:** Add a new label to the top of the stack. This is what the ingress PE does when a packet enters the MPLS network — it pushes a label that corresponds to the forwarding path through the backbone.

**Swap:** Replace the top label with a new one. This is what every P router in the backbone does — swap the incoming label for the outgoing label defined in the LFIB for the next hop.

**Pop:** Remove the top label. This happens at the penultimate hop before the egress PE — a mechanism called **Penultimate Hop Popping (PHP)** — so the egress PE receives a packet with the IP header exposed and can make its final IP forwarding decision efficiently.

These three operations are the entire operational vocabulary of an MPLS label switch. No IP lookup. No routing table. Just a label, an LFIB lookup, a swap or pop, and a forward.

## Why Service Providers Adopted It

For a service provider, MPLS solved three problems that pure IP could not:

**Traffic Engineering.** With IP, you cannot control which path traffic takes through the network. BGP picks the best path based on attributes, and all traffic to a destination follows the same path. If that path is congested while another is idle, you cannot shift load without changing routing policy globally. MPLS with RSVP-TE (Resource Reservation Protocol - Traffic Engineering) lets you create explicit Label Switched Paths that follow any route you specify — routing around congestion, optimizing utilization, and meeting SLA commitments.

**VPN Services.** Selling network services to multiple customers over shared infrastructure requires isolation. With MPLS, a service provider can build L3VPN and L2VPN services where each customer's traffic is isolated in its own forwarding context. Customer routes never appear in the provider's backbone routing table. The backbone P routers have no knowledge of customer prefixes at all.

**Scalability.** P routers in an MPLS backbone only need to hold MPLS labels in their LFIB — not the full BGP routing tables of every customer. This dramatically reduces the routing state at the core, allowing backbone routers to be optimized for high-speed switching rather than complex routing lookups.

At ECI Telecom, where I supported service provider customers running MPLS backbones, these were the exact operational reasons MPLS was deployed: selling L2VPN and L3VPN services over a shared backbone while keeping customer traffic isolated and giving operators the ability to engineer traffic across specific paths.

MPLS did not replace IP — it built a programmable forwarding layer on top of it. The next article covers how Label Switched Paths are built and how labels are distributed.
