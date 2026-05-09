# DCI Transport Options

The physical transport between data centers sets the ceiling for everything built on top. The bandwidth available, the latency achievable, the failure modes to plan for — all of these are determined by the transport layer. Getting the transport wrong means that no amount of clever overlay design can fix the resulting constraints.

There are four main transport options for DCI, each with a distinct cost, performance, and operational profile.

## Dark Fiber

Dark fiber is unlit optical fiber — physical glass, leased from a telecom provider, between two points. "Dark" means no electronics: you get fiber strands, and you provide the transceivers, amplifiers, and any multiplexing equipment on both ends.

**Advantages:**
- Maximum control — you provision your own wavelengths, manage your own amplification, run your own DWDM equipment
- No per-bandwidth pricing from the carrier — you pay a flat lease rate for the fiber, then run as many wavelengths as the fiber supports
- Lowest latency — only the inherent fiber delay (roughly 5 microseconds per kilometer), no carrier switching or mux/demux overhead
- Long-term economics favor dark fiber for very high-bandwidth requirements

**Disadvantages:**
- High upfront cost — dark fiber leases are expensive, and you must provide all equipment
- Carrier expertise required — managing optical amplification, dispersion compensation, and DWDM channel provisioning requires optical engineering skill sets that most network teams do not have
- Longer provisioning time — new dark fiber takes months to provision; adding capacity requires either additional fiber or changing the DWDM channel plan

**When to use:** Hyperscalers (Google, Meta, Amazon, Microsoft) with very high, consistent bandwidth requirements between owned or leased DCs typically use dark fiber for their most critical DC pairs. The economics make sense at scale; the operational complexity is manageable with a dedicated optical engineering team.

## DWDM Leased Wavelengths

DWDM (Dense Wavelength Division Multiplexing) allows multiple optical channels to be carried simultaneously on a single fiber by using different wavelengths of light. Leasing a wavelength from a carrier means the carrier provides the fiber and the DWDM infrastructure; you get a point-to-point optical connection of defined capacity (typically 10G, 100G, or 400G per wavelength).

**Advantages:**
- No optical engineering required — the carrier manages the DWDM plant
- Faster provisioning than dark fiber for new capacity
- Pay per wavelength — better economics than dark fiber for moderate bandwidth requirements
- Carrier provides SLAs for uptime and latency

**Disadvantages:**
- Per-wavelength cost adds up at very high bandwidth
- Less flexibility — you cannot easily change channel parameters
- Carrier dependency for troubleshooting optical layer issues
- Latency slightly higher than dark fiber due to carrier switching equipment

**When to use:** The most common choice for mid-to-large organizations that need high-bandwidth DCI without the operational overhead of managing their own optical plant. A 100G or 400G leased wavelength per DCI path, with redundant paths via different carriers, is a standard enterprise and smaller hyperscaler design.

## MPLS Circuit (L2 or L3 WAN Service)

Carriers sell Layer 2 (Ethernet circuit, VPLS) and Layer 3 (IP/MPLS VPN) WAN services over their MPLS backbone. You connect your DC routers to the carrier's PE, and the carrier transports your traffic across their network.

**Advantages:**
- Simplest to provision — carrier manages all transport
- Geographic flexibility — carrier networks connect many locations; adding a new DC to the service is faster than deploying dark fiber
- Built-in redundancy — MPLS providers offer 99.99% or higher uptime SLAs

**Disadvantages:**
- Higher latency than fiber — carrier network has switching hops and queuing
- Bandwidth limits — gigabit-level MPLS circuits are common; tens-of-gigabits per DCI path requires either many circuits or a move to wavelength services
- Less control — you cannot engineer the path your traffic takes through the carrier network
- Cost per Mbps is significantly higher than dark fiber at scale

**When to use:** Smaller organizations, branch-to-DC connectivity, or as a backup path when dark fiber is the primary. Not appropriate as the primary DCI transport for hyperscale environments because bandwidth economics do not scale.

## Internet-Based Overlay (IPSec VPN)

The lowest-cost option: build an encrypted VPN tunnel between two DC routers using the public internet as the underlying transport.

**Advantages:**
- Near-zero transport cost — internet transit is commodity
- Very fast to provision
- Can connect nearly anywhere with internet access

**Disadvantages:**
- Highly variable latency and bandwidth — the internet is not engineered for predictability
- No SLAs from internet — outages on internet paths are handled by your routing, not a carrier guarantee
- Encryption overhead — IPSec processing at high line rates requires dedicated hardware (or hardware offload NICs)
- Security complexity — managing IPSec certificates, IKE sessions, and key rotation at scale

**When to use:** Backup path only, or for locations with no viable private circuit options. Never as the primary DCI transport for production workloads requiring consistent performance. Sometimes used for management plane connectivity between DCs as a secondary path.

## The Practical Reality: Multiple Layers

In production, DCI transport is almost never a single option. A well-designed DCI uses:

- **Primary path:** Dark fiber or leased DWDM wavelengths — maximum bandwidth, minimum latency
- **Secondary path:** A different carrier's leased wavelength or MPLS circuit — diverse routing for carrier redundancy
- **Tertiary path (optional):** Internet VPN — available for management traffic if both primary and secondary fail

The network design must ensure that a single carrier failure, a fiber cut on one path, or a data center peering failure does not cause a complete DCI outage. This requires routing protocols (BGP) at the DCI layer that can detect path failures and shift traffic to the remaining available paths — with monitoring tight enough to detect and alert on any single path failure before a second failure can create a complete outage.

This is the operational context for any DC network role focused on DCI: it is not just "connecting buildings" — it is engineering a resilient, high-bandwidth interconnect that is itself a critical piece of a hyperscaler's availability story.
