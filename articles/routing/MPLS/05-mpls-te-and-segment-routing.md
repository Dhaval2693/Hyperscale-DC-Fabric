# MPLS-TE and Segment Routing

Basic MPLS (covered in the earlier MPLS articles) sets up label-switched paths via IGP-derived routing. **MPLS-TE (Traffic Engineering)** lets you steer traffic along *engineered* paths that don't necessarily match the IGP shortest path. **Segment Routing** is the modern evolution — same idea, simpler control plane.

For backbone and WAN roles, this is core technology. For DC roles, it's worth knowing exists.

## Why Traffic Engineering Exists

The IGP (OSPF, IS-IS) picks the shortest path. But "shortest" doesn't always mean "best":

- The shortest path may be congested
- Different traffic classes need different paths (latency-sensitive vs bulk)
- Failover paths must be pre-computed for fast convergence
- Some links have higher cost ($) per bit and should be avoided

Traffic engineering = picking the path explicitly, based on operator-defined criteria, not just topology.

## MPLS-TE (Classic, RSVP-TE Based)

The original MPLS traffic engineering, standardized as RSVP-TE.

**How it works:**
1. **TE topology database** — IGP (OSPF-TE or IS-IS-TE) carries link attributes: bandwidth, color/admin groups, etc.
2. **Path computation** — head-end router runs CSPF (Constrained Shortest Path First) on the TE database to find a path that meets constraints
3. **Signaling** — RSVP-TE signals the path, installing labels at each hop
4. **Resource reservation** — each hop reserves bandwidth for the LSP
5. **Forwarding** — packets steered into the LSP follow the engineered path

**Strengths:**
- Per-LSP bandwidth reservation
- Strict path control (explicit hops)
- Fast Reroute (FRR) for sub-50ms failover

**Weaknesses:**
- Heavy control plane (RSVP state per hop, refresh messages)
- Scales poorly with thousands of LSPs
- Complex to operate

## Segment Routing (Modern Alternative)

Segment Routing (SR) accomplishes the same goal with a fundamentally simpler control plane.

**The core idea:** the source router prepends a **list of "segments"** (instructions) to the packet. Each segment is either a node (go to this router) or an adjacency (use this specific link). Transit routers just follow the segment list — no per-LSP state.

### Two Flavors

| | SR-MPLS | SRv6 |
|---|---|---|
| Data plane | MPLS labels | IPv6 addresses |
| Header | Label stack | IPv6 Segment Routing Header (SRH) |
| Adoption | Mature, widely deployed | Newer, growing |
| Use case | Existing MPLS networks | Greenfield IPv6 backbones |

### How SR Differs from RSVP-TE

| | RSVP-TE | Segment Routing |
|---|---|---|
| Path state | Held at every hop (RSVP soft state) | Held only at source (segment list in header) |
| Control plane | Heavy (RSVP) | Light (IGP carries segment info) |
| Scaling | Limited by LSP count | Scales to millions of paths |
| Failover | FRR via pre-signaled backup LSPs | TI-LFA (topology-independent loop-free alternates) |
| Operational complexity | High | Lower |

**The pitch for SR:** stateless mid-network, source-routed, no RSVP. Much simpler at scale.

## When Traffic Engineering Is Worth It

**Yes, use TE when:**
- Multiple equal-cost paths exist and you need to distribute load
- Different traffic classes need different paths (latency vs bulk)
- You need sub-50ms failover (FRR or TI-LFA)
- You're a service provider with SLA commitments
- The backbone has expensive links that shouldn't carry overflow traffic

**No, skip TE when:**
- IGP shortest path is fine
- The complexity isn't justified by measurable wins
- Small networks (<10 backbone routers)

The JD line "**operational judgment to know when TE is worth the complexity**" is calling out exactly this — TE is powerful but expensive in operational overhead. Don't deploy it because it's cool; deploy it because data shows ECMP is inadequate.

## Common Use Cases

1. **Differentiated services backbones** — different paths for voice/video vs bulk
2. **Bandwidth optimization** — fill up cheap paths before expensive ones
3. **Latency-sensitive routing** — strict path for low-latency apps
4. **Avoidance routing** — steer around a known-flaky link without removing it
5. **Capacity arbitrage** — move traffic to off-peak paths

## Fast Reroute (FRR) and TI-LFA

Both MPLS-TE FRR and SR's TI-LFA solve the same problem: when a link or node fails, switch to a backup path in <50ms (faster than IGP reconvergence).

- **MPLS-TE FRR:** pre-signal a backup LSP via RSVP-TE; on failure, swap to it immediately
- **TI-LFA (SR):** pre-compute a backup path for every link, stored at each node; on failure, packets are encapsulated to follow the backup segment list

TI-LFA is generally easier to operate at scale — no RSVP state, no pre-signaled tunnels to maintain.

## How to Talk About It

For a "tell me about TE" question:
> "Traffic engineering is about steering traffic along paths other than IGP shortest. Classic MPLS-TE uses RSVP-TE — heavy control plane, per-LSP state. Segment Routing is the modern simplification: source routing with a segment list in the header, no per-LSP state in the mid-network. SR-MPLS is widely deployed; SRv6 is the IPv6-native version. The operational judgment is knowing when TE is worth the complexity — usually only for differentiated services, bandwidth-constrained backbones, or sub-50ms failover requirements."

## What to Memorize

| Concept | Key idea |
|---|---|
| **MPLS-TE / RSVP-TE** | Per-LSP signaled paths, bandwidth reservation, heavy control plane |
| **CSPF** | Path computation respecting constraints (bandwidth, color, etc.) |
| **Segment Routing** | Source-routed via segment list, no per-LSP mid-network state |
| **SR-MPLS vs SRv6** | Data plane is labels vs IPv6 |
| **FRR / TI-LFA** | <50ms failover via pre-computed backups |
| **TE database** | Extension to OSPF/IS-IS that carries link attributes |

## Connection to Other Topics

- **Builds on:** [01-why-mpls-exists.md](01-why-mpls-exists.md), [02-lsp-and-label-operations.md](02-lsp-and-label-operations.md)
- **Bridges to:** backbone WAN design, cost optimization (route around expensive links)
- **Relevant for:** any backbone-focused role, service provider work, hyperscaler WAN team
