# Network SLOs and SLIs

SRE practices (Service Level Objectives, Service Level Indicators, error budgets) are well-established for application services. Applying them to **network infrastructure** is newer and harder — but it's exactly what hyperscaler network teams now do, and what senior network engineering roles increasingly expect (defining SLOs/SLIs for network services, capacity planning with error budgets).

This article covers how to think about SLOs for network services, the SLI types that matter, and how error budgets shape operational decisions.

## The Core Vocabulary

| Term | Definition |
|---|---|
| **SLI** | Service Level Indicator — a measurable metric (e.g., "% of pings under 5ms latency") |
| **SLO** | Service Level Objective — a target for the SLI over a time window (e.g., "99.9% over 30 days") |
| **SLA** | Service Level Agreement — a contractual commitment, usually weaker than the internal SLO |
| **Error budget** | The allowed "bad" time/events = (1 - SLO) × time window |

**The relationship:** SLI is what you measure. SLO is the target. Error budget is what you spend when SLO is violated. SLA is what you promise to customers (with a comfortable margin over your internal SLO).

## The Four SLI Types for Networks

### 1. Availability

"What % of the time is the network usable?"

- **For a link:** % of time the interface is up and forwarding
- **For a path:** % of time end-to-end connectivity exists
- **For a fabric:** % of time bisection bandwidth meets demand

Measurement: synthetic probes (ICMP, TCP connect) every N seconds, count successful checks.

### 2. Latency

"How fast does traffic get there?"

- p50, p95, p99 latencies — never just averages
- Often broken down by path or class (intra-DC, intra-region, inter-region)

Measurement: synthetic probes, in-band one-way delay (1588 PTP if you have it), or sampled flow telemetry.

### 3. Throughput

"How much can it move?"

- Available bandwidth on a link
- Goodput end-to-end (after retransmits)
- Tail throughput (worst per-flow throughput at high utilization)

Measurement: interface counters (utilization), iperf-style probes, or app-reported.

### 4. Loss / Error

"How clean is the path?"

- Packet loss rate
- Interface error counters (CRC, drops)
- RDMA retransmits (for HPC fabrics)
- TCP retransmit rate (host-side)

Measurement: interface counters, host-side stats, flow telemetry.

**Most network SLOs use a combination of all four.** Availability tells you "is it on?", latency/throughput/loss tell you "is it good?"

## Defining Good SLOs

### Rule 1: Pick SLIs your users actually feel

A "100% interface availability" SLO sounds great but tells you nothing — what users feel is "can my packets get from A to B in time?" Measure the user-facing path, not isolated devices.

### Rule 2: Choose SLO targets carefully

99% = 7.2 hours of "bad time" per month. 99.9% = 43 minutes. 99.99% = 4.3 minutes.

Higher SLOs cost exponentially more to deliver (more redundancy, faster failover, more on-call). Set the target by what users *need*, not what sounds impressive.

### Rule 3: Window matters

A 99.9% SLO over 30 days is very different from 99.9% over 5 minutes. Long windows tolerate transient blips; short windows catch them.

For infrastructure, **rolling 30-day windows** are common — gives you flexibility to absorb a bad day without missing the quarter's target.

## Error Budgets in Practice

The error budget is what makes SLOs useful operationally.

**Example:** 99.9% availability SLO over 30 days → 43 minutes of allowed downtime per month.

- **Budget remaining > 50%** → safe to ship risky changes, drain links for maintenance
- **Budget remaining 10-50%** → caution, prefer low-risk changes
- **Budget remaining < 10%** → freeze; only critical fixes, focus on reliability
- **Budget exhausted** → all hands on reliability work until next window starts

This turns SLOs from "abstract goal" into "operational decision-making framework." The error budget is what gives you the data to say "we can't ship this risky change this week."

## SLOs for Specific Network Services

### Backbone / WAN

- **Availability:** 99.99% (4.3 min/month) for the backbone overall
- **Latency:** p99 inter-region latency under [N] ms, measured by 1s probes
- **Loss:** < 0.001% per path

### DCN Fabric

- **Availability:** 99.999% (5 min/year) for the fabric (you have redundancy)
- **PFC pause events:** < N pause frames per minute per link
- **ECN marking rate:** < X% on training fabric

### Inference Service Network Path

- **p99 round-trip latency** from client to model: < [N] ms
- **Tail throughput:** sustained Gbps per session

The point: pick SLIs that match the *workload's actual need*, not generic platitudes.

## Common Pitfalls

1. **SLO too strict, no budget to ship.** If the SLO is 99.999% but you can only deliver 99.9%, you're permanently in "no changes" mode. Set realistic targets.

2. **Measuring the wrong layer.** "Interface up" doesn't mean "packets arrive." Use end-to-end probes when possible.

3. **No error budget enforcement.** If you don't actually freeze changes when budget is gone, the SLO is decorative.

4. **Window too short.** 5-minute SLOs mean every brief blip is a violation. 30-day rolling windows are usually better for infrastructure.

5. **Confusing SLO with SLA.** SLA = customer-facing promise (with margin). SLO = internal target (tighter). Never write an SLA at your SLO — you have no margin for error.

## The Operational Workflow

A mature network SRE practice runs like this:

1. **Define SLIs** for each user-facing service (DCN, backbone, inference path)
2. **Set SLOs** based on what users need + what you can deliver
3. **Instrument continuously** — synthetic probes + flow telemetry + interface counters
4. **Dashboard the error budget** — make it visible to operators and partner teams
5. **Use it for change decisions** — high budget = ship risky changes; low budget = freeze
6. **Post-incident** — review SLO impact, update target if learning warrants

## How to Talk About It

For "how do you measure network reliability":
> "I use SRE practices — SLIs for the four dimensions (availability, latency, throughput, loss), each tied to a user-facing service path. SLOs are 30-day rolling windows. The error budget governs how aggressive we can be with changes — high budget means we can experiment, low budget means we freeze and focus on reliability. The point isn't decorative numbers; it's a framework for making operational decisions backed by data."

For "tell me about a network outage":
> "Use STAR format and explicitly call out: which SLO did this impact? How much of the error budget did it consume? What did you change to prevent recurrence?"

## What to Memorize

- The four SLI types (availability, latency, throughput, loss)
- The math: 99.9% / 30 days = 43 min budget
- The use of error budgets for change decisions
- Why end-to-end measurement beats device-level
- SLO is internal, SLA is contractual (and weaker)
