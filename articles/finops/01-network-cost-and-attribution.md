# Network Cost and Attribution

For most engineers, network cost is "someone else's problem." For roles like Anthropic's Capacity & Efficiency, it **is** the problem. This article covers where the money goes in modern cloud + DC networks, how to attribute spend to teams and workloads, and how to make cost a first-class input to design decisions.

## Where the Money Actually Goes

Network spend breaks down into roughly four buckets:

| Bucket | What it covers | Typical % of spend |
|---|---|---|
| **Egress / data transfer** | Bytes leaving a cloud region or AZ | **40-60% (usually dominant)** |
| **Interconnect / transit** | DX, Interconnect, IP transit, peering | 15-25% |
| **Optical / colo / leases** | Dark fiber, DWDM wavelengths, rack space | 10-20% |
| **Hardware + software** | Switches, routers, NOS licenses, controllers | 10-20% |

**Egress dominates.** In multi-region or multi-cloud architectures, egress can easily exceed all other line items combined. This is why the role mentions "every byte of cross-region egress" — that's where the leverage is.

## The Egress Cost Hierarchy (AWS Example)

Cheapest → most expensive:

| Path | Approx. cost (per GB) |
|---|---|
| Intra-AZ (same VPC) | Free |
| Inter-AZ (same region) | $0.01-0.02 each way |
| Inter-region within AWS | $0.02-0.09 |
| Egress to internet | $0.05-0.09 (tiered; first-GB rates can be higher) |
| Egress to another cloud | Same as internet |
| Direct Connect transfer | $0.02-0.03 (much cheaper) |

**The economic levers are obvious:**
1. Keep traffic intra-AZ when possible (free)
2. Avoid cross-region for high-volume workloads
3. Use DX for predictable hybrid traffic
4. Co-locate chatty services in the same AZ

## Cost Attribution: The Three Levels

### Level 1: Tag-Based Attribution

Every resource tagged with team/workload. Cloud bill rolled up by tag.

- **Pros:** easy to set up; works with native cloud cost tools
- **Cons:** misses traffic-level cost — you know what each VPC cost but not which **flow** within it

### Level 2: VPC Flow Logs + Pricing Join

Enable VPC flow logs (records every accepted/denied connection). Join against the AWS pricing API to compute cost per flow.

- **Pros:** per-flow attribution; reveals chatty source-destination pairs
- **Cons:** flow logs cost money themselves; sampling needed at scale

### Level 3: sFlow/IPFIX + Streaming Pipeline

For DC fabric and hybrid environments, export flow telemetry from routers, ingest into a streaming pipeline, attribute every byte to source/destination workload via a service registry.

- **Pros:** covers traffic the cloud bill doesn't see (DCN, backbone)
- **Cons:** building the pipeline is real engineering work

**At hyperscaler scale, you need Level 3.** Cloud bills + tags don't capture inter-fabric or inter-DC traffic.

## Building a Chargeback Model

The output of attribution is a model that says: *"Team X consumed Y bytes, costing $Z."*

**Components:**

1. **Traffic data** — bytes per flow (sFlow/IPFIX/VPC flow logs)
2. **Source/destination identity** — workload tags, service registry lookup
3. **Path cost model** — per-GB cost for each path (intra-AZ, cross-region, egress, DX, etc.)
4. **Aggregation** — bytes × cost per path, rolled up by team/workload
5. **Dashboard** — Grafana / internal BI tool

The hard part isn't the math; it's the **identity mapping**. "This IP at this timestamp belonged to which workload?" requires good source-of-truth data and time-correlated lookups.

## Show-Back vs Charge-Back

| | Show-back | Charge-back |
|---|---|---|
| **Financial impact** | None — visibility only | Team's budget is actually debited |
| **Drives** | Awareness, voluntary optimization | Hard tradeoffs |
| **Politically** | Easy to roll out | Requires org buy-in |
| **Data quality** | Can tolerate gaps | Must be airtight (legal/financial implications) |

Most large companies start with show-back. Charge-back requires organizational buy-in and clean attribution data.

## Cost Optimization Playbook

Once you have visibility, common wins:

1. **Cross-AZ traffic killers** — load balancers ignorant of AZ affinity, replicas in wrong AZ
2. **Cross-region replication overuse** — does this dataset really need 3-region replication?
3. **Egress to image registries** — pulling Docker images from a different region/cloud
4. **NAT Gateway overuse** — high-volume outbound from private subnets at $0.045/GB
5. **Old TGW attachments** — unused VPCs still attached, charging port fees
6. **Egress-heavy services on wrong path** — moving to DX can cut per-GB rate by ~75%

## The "Build vs Buy" Question

This comes up constantly: *"Should we buy more capacity, or move the workload to existing capacity?"*

**The model:**
- **Buy capacity** — fixed cost (port + monthly recurring), unlocks future flexibility
- **Move workload** — engineering time cost (one-time), saves variable cost forever

A clean answer requires:
- Current utilization on existing capacity
- Projected growth
- Engineering cost to move (person-months)
- Time value of money (capacity bought today costs less than tomorrow's outage)

This is exactly the "model whether it's cheaper to buy an additional 1.6Tb interconnect tranche or to re-route traffic" question from the JD — **answer with a spreadsheet, not an opinion.**

## A Sample Cost Model Sketch

A useful framework on a whiteboard:

```
For each candidate solution:
  TCO_12mo = Fixed_setup + (Variable_per_month × 12)
                          + Risk_adjustment

Compare TCO across:
  - Buy more capacity
  - Move workload to existing capacity
  - Do nothing (baseline)

Sensitivity: ±20% growth assumption
```

The numbers may be approximate; the **discipline** of writing it down is what matters in an interview.

## How to Talk About It

**For "tell me about cost optimization":**
> "Most network cost is data transfer, dominated by egress. I'd start with attribution — flow telemetry tagged back to workload via source-of-truth lookup, joined against the per-path pricing model. Once I can show per-team cost per workload, optimization wins follow: cross-AZ killers, cross-region replication overuse, egress to wrong destinations. The pattern is always: instrument first, attribute second, optimize third."

**For "build vs buy":**
> "Quantitative answer only. I'd model: current utilization, projected growth, cost of new capacity (one-time + recurring), cost of re-routing (engineering time + recurring savings). Whichever has lower 12-month TCO at the projected growth rate. Sensitivity check at ±20% growth."

## What to Memorize

- The egress cost hierarchy (intra-AZ < inter-AZ < inter-region < internet)
- The three attribution levels (tags → flow logs → full pipeline)
- Show-back vs charge-back distinction
- The five common cost wins (cross-AZ, replication, image pulls, NAT, idle attachments)
- The "build vs buy" framework

## Anthropic-Specific Framing

This role is about **making cost a first-class engineering input.** Frame answers as:

1. **Show the data** — per-flow attribution, dollar quantification
2. **Quantify the impact** — dollars/month at current rate
3. **Propose the change** — specific architecture or policy
4. **Project savings + risks** — 12-month TCO model
5. **Land it through influence** — convince the team that owns the workload

That sequence is what "drive cost attribution" looks like in practice. The JD explicitly calls out influence-without-authority — being able to make a quantitative case to a research or finance team is the differentiator.
