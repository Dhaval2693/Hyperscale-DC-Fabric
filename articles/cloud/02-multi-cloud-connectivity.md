# Multi-Cloud Connectivity

Most large organizations now span multiple clouds — AWS for general compute, GCP for AI/ML, sometimes Azure for enterprise. Connecting them efficiently is a real problem with real cost implications. This article covers the connection options, the billing model, and the failure modes you should be ready to discuss in interviews.

## Why Multi-Cloud Is Hard

Each cloud is its own walled garden:
- Different IP space, different routing models, different naming conventions
- **Egress fees from each cloud apply** when traffic leaves
- BGP semantics differ across providers
- Latency between clouds isn't always predictable
- Single management plane doesn't exist

The naive answer ("just VPN them together") quickly hits bandwidth, latency, and cost walls.

## The Three Connection Options

### Option 1: Public Internet (VPN or Direct)

Cheapest to start, worst at scale.

- Site-to-site VPN between cloud regions
- Or plain internet-routed traffic (no encryption)
- **Pros:** instant, cheap setup
- **Cons:** egress fees from BOTH clouds, unpredictable latency, no SLA

### Option 2: Direct Cloud Interconnect (via Carrier)

The standard for production-scale traffic.

- AWS Direct Connect + GCP Partner Interconnect (or equivalent combinations)
- Common pattern: terminate DX and Partner Interconnect at the **same colocation facility** (Equinix, CoreSite), then cross-connect inside
- **Pros:** dedicated bandwidth, lower per-GB cost, predictable latency
- **Cons:** monthly port fees, setup complexity, still pay egress per cloud

### Option 3: Cloud-to-Cloud via Intermediary

Software-defined interconnect platforms (Megaport, Equinix Fabric, PacketFabric).

- Pay one provider; virtual circuits to all your clouds
- Often simplest at multi-cloud scale
- **Pros:** single management plane, easy to add new clouds
- **Cons:** monthly cost, throughput tiers can be limiting

## The Egress Cost Trap

**Both sides charge for traffic leaving their cloud.** This is the #1 cost surprise in multi-cloud.

### Worked Example: 100 TB/month between AWS and GCP

**Via direct interconnect (DX + Partner Interconnect):**
- AWS egress via DX: ~$0.02/GB × 100,000 GB = $2,000
- GCP egress via Interconnect: ~$0.02/GB × 100,000 GB = $2,000
- DX port (10 Gbps): ~$200/month
- Partner Interconnect attachment: ~$200/month
- **Total: ~$4,400/month**

**Via public internet (VPN):**
- AWS internet egress: $0.09/GB × 100,000 = $9,000
- GCP internet egress: $0.08/GB × 100,000 = $8,000
- **Total: $17,000/month**

Direct interconnect saves ~75% — but only if you actually move enough traffic to justify the fixed port costs. Below a certain volume, public internet wins on TCO.

## BGP Across Clouds

When you connect via DX + Partner Interconnect, you're running BGP between cloud routers (AWS Cloud Router on AWS side, GCP Cloud Router on GCP side) and a router in the carrier's facility.

Key concepts to know:

| Concept | Use |
|---|---|
| **AS numbers** | Each cloud has its own ASN for BGP peering |
| **BGP communities** | Tag routes for traffic engineering hints |
| **Local preference** | Control outbound path selection |
| **MED (Multi-Exit Discriminator)** | Hint to neighbors about preferred inbound path |
| **AS path prepending** | Make a path "look worse" to discourage its use |

In multi-cloud, BGP typically runs at the intermediary (Megaport, Equinix), advertising routes between clouds with route policy you control.

## Failure Modes to Discuss in Interviews

1. **Single interconnect failure.** Design with redundant connections at different colocation facilities. The classic 1+1 protection pattern.
2. **BGP flap from one side.** Can drain a region; need BGP dampening and alerting on flap counters.
3. **Asymmetric routing.** Traffic exits via one path, returns via another. Breaks stateful firewalls and complicates debugging.
4. **Bandwidth exhaustion.** A single 10G port can max out; need utilization monitoring + capacity planning.
5. **Asymmetric billing.** One cloud might bill heavier than the other even on the same path. Always model both sides.

## The Standard Multi-Cloud Architecture

At scale, the pattern is:

1. **Hub-and-spoke per cloud** — TGW (AWS), NCC / Cloud Router (GCP) as regional hubs
2. **Connect hubs via carrier** — Equinix/Megaport for direct interconnect
3. **Run BGP** at the intermediary — protocol handles failover
4. **Tag traffic with BGP communities** — direct to cheap or fast path based on workload
5. **Monitor cost AND utilization** — per-link metrics to know when to buy more capacity

## How to Talk About It

> "For multi-cloud at scale, public internet hits cost and latency walls quickly. I'd use direct interconnect at a colocation facility — Direct Connect from AWS and Partner Interconnect from GCP terminating at the same Equinix campus, cross-connected. Both clouds charge egress, so the savings come from per-GB rates being lower on dedicated links. BGP at the intermediary handles routing and failover. The trap to watch: egress costs apply on both sides, so when sizing the interconnect, model per-GB savings against the fixed port cost."

## A Sample Interview Scenario

> "We move 500 TB/month of training data between AWS and GCP. Currently via public internet. What's the right architecture?"

**Sample answer (quantitative, structured):**

1. **Quantify current cost:**
   - 500 TB × ($0.09 + $0.08) = ~$85,000/month, ignoring tier discounts
2. **Propose direct interconnect:**
   - Port cost: 2 × $200 = $400/month (for redundancy)
   - Egress at $0.02/GB on each side: 500 TB × $0.04 = $20,000/month
   - **Total: ~$20,400/month**
3. **ROI:** ~$65k/month savings; payback in days, ongoing
4. **Caveats:**
   - Redundancy required — 2 ports at 2 colos, BGP for failover
   - Transition plan: cut over gradually to avoid disruption
   - Monitor: per-link utilization, BGP session health, egress cost monthly

That quantitative, cost-aware answer is exactly what senior infrastructure roles look for.

## What to Memorize

- The three connection options (internet/VPN, DX+PI, intermediary)
- The egress-on-both-sides cost trap
- BGP communities and prepending as TE levers
- Standard architecture: hub per cloud + carrier interconnect
- Common failure modes (asymmetric routing, BGP flap, single-point capacity)
