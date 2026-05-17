# Telemetry Pipeline Design

Knowing the protocols (gNMI, sFlow, IPFIX, eBPF) is the easy part. The hard part is designing the **pipeline** that ingests, enriches, stores, and visualizes that telemetry at scale — at acceptable cost, with the right cardinality and sampling strategy.

This article covers the architecture patterns, the three big tradeoffs (sampling, cardinality, storage), and the design decisions a senior engineer is expected to reason about.

## The Standard Pipeline Architecture

```
┌──────────┐    ┌───────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────┐
│  Sources │ →  │ Collector │ →  │ Enrichment   │ →  │  Storage │ →  │ Dashboards│
│ (router, │    │ (goflow2, │    │ (IP→workload │    │(ClickHouse│    │ (Grafana, │
│  host)   │    │  pmacct,  │    │  prefix→team)│    │ BigQuery, │    │  internal)│
│          │    │  Telegraf)│    │              │    │   Loki)   │    │           │
└──────────┘    └───────────┘    └──────────────┘    └──────────┘    └───────────┘
        │
        └─ Hot path (alerting): Kafka → Flink → on-call
```

**Two paths matter:**
- **Cold path** — to storage for analysis and dashboards
- **Hot path** — stream processor for real-time alerting

Most pipelines fork at the collector: one branch to storage, another to a stream processor for alerting on anomalies as they happen.

## The Three Big Tradeoffs

### Tradeoff 1: Sampling

You can't store every event at hyperscaler scale. **Sample to reduce volume.**

| Strategy | Pros | Cons |
|---|---|---|
| Fixed-rate sampling (1 in N) | Simple, predictable | Misses rare flows entirely |
| Adaptive sampling | More accurate for low-volume flows | Complex, harder to reason about |
| Stratified (per-prefix or per-app) | Better coverage of important traffic | Configuration overhead |

**Rule of thumb:** start with 1:1000 fixed-rate. Tune up for hot spots, accept statistical inference for the rest.

### Tradeoff 2: Cardinality

**Cardinality** = number of unique time-series (or rows) you store.

A label like `source_ip` has near-infinite cardinality. A label like `region` has ~10. Cardinality drives storage cost, query latency, and ingest CPU.

**Strategies to control cardinality:**

1. **Drop high-cardinality labels** at ingest if not needed for queries
2. **Aggregate to coarser keys** — store per-prefix instead of per-IP
3. **Use sampling** — only keep records for hot keys
4. **Time-aggregate** — 1-minute summaries instead of per-packet timestamps
5. **Tiered retention** — keep high-cardinality data for short windows only

### Tradeoff 3: Storage

A single hot store fits no use case at scale. **Use tiered storage.**

| Tier | Purpose | Tech | Retention |
|---|---|---|---|
| **Hot** | Real-time queries, dashboards | ClickHouse, Druid, Prometheus | 1-7 days, full fidelity |
| **Warm** | Analytics, capacity planning | ClickHouse with longer retention, BigQuery | 30-90 days, downsampled |
| **Cold** | Compliance, post-incident forensics | Object storage (S3, GCS) + Parquet | 1+ years, aggregated |

**The query pattern matters.** Recent + frequent = hot. Old + occasional = cold. Don't put cold-path data in your hot store — your storage bill will explode.

## Enrichment: The Hardest Part

The protocols give you IPs, ports, and counters. Your dashboards need workloads, teams, and dollars. **Enrichment closes that gap.**

Sources of enrichment data:
- **IPAM / CMDB** — IP → device, IP → subnet → workload
- **Service registry / Consul** — service name → IPs
- **K8s metadata** — Pod IP → namespace → team
- **Cloud tags** — VPC ID → owning team
- **BGP communities / labels** — for path identification

**The hardest engineering challenge:** time-correlated lookups. "This IP at this timestamp belonged to which workload?" requires either:
- Snapshot the mapping at ingest time (and store with the record)
- Or maintain a time-versioned mapping store (e.g., temporal table)

Most pipelines snapshot at ingest. The mapping is "close enough" for time scales of minutes, less reliable for forensic work spanning weeks.

## Hot Path vs Cold Path

**Cold path** = storage and dashboards. Latency: minutes to hours.
**Hot path** = real-time alerting. Latency: seconds.

**Hot path stack:**
- Kafka (or equivalent) ingests events
- Stream processor (Flink, Materialize, ksqlDB) computes rolling metrics
- Alerting rules fire on threshold breach
- PagerDuty or similar dispatches

Don't try to do real-time alerting on a cold store. Queries will be too slow.

## What Lives at Each Layer

### Source layer
- gNMI subscriptions on devices
- sFlow/IPFIX export config
- eBPF probes on hosts

**Decision:** which fields to export. More fields = more storage and ingest cost.

### Collector layer
- Receives, decodes, normalizes
- Optionally pre-aggregates (1-minute rollups before sending downstream)

**Tools:** goflow2 (IPFIX/sFlow), Telegraf, custom Go/Python collectors.

### Enrichment layer
- Joins raw telemetry against source-of-truth data
- Adds workload, team, region labels

**Implementation:** stream processor (Flink) or batch (Spark) for cold path; in-memory lookup table refreshed periodically.

### Storage layer
- Hot: columnar OLAP store (ClickHouse, Druid)
- Warm: data warehouse (BigQuery, Snowflake)
- Cold: object storage with Parquet

### Visualization layer
- Grafana for engineer dashboards
- Internal BI tools (Looker, Mode) for cost reports
- Custom apps for tools like cost attribution dashboards

## Common Failure Modes

1. **Cardinality explosion.** A single new label (e.g., `request_id`) creates millions of unique time-series. Bill jumps 10x.

2. **Storage cost overrun.** Hot store retention extended "just in case" eats budget. Tier discipline matters.

3. **Stale enrichment.** IP→workload mappings get out of date; attribution becomes wrong. Fix: monitor lookup failure rate.

4. **Dashboard query timeouts.** Pre-aggregate. Don't make Grafana scan raw flows at query time.

5. **Hot path overload.** Stream processor backs up during traffic surges; alerts delay. Fix: backpressure handling.

## Sampling Math (Worked Example)

100 routers, each exporting IPFIX, each seeing 10G of traffic at line rate (~14.8M pps):
- Unsampled: 100 × 14.8M = 1.48B records/second. Infeasible.
- Sampled 1:1000: 1.48M records/second. Still a lot but manageable.
- After 1-minute aggregation at collector: ~24k records/minute per router → 2.4M records/minute total. Storable.

The math is "what does my hot store ingest budget look like?" Work backwards from there.

## How to Talk About It

> "Telemetry pipeline design is about three tradeoffs: sampling rate, cardinality, and storage tier. At scale you sample (1:1000 IPFIX is a reasonable default). You control cardinality by dropping or aggregating high-cardinality labels at ingest. You tier storage — hot for dashboards (days), warm for analytics (weeks), cold for forensics (months+). The hardest engineering is enrichment: joining raw IPs against source-of-truth identity data, time-correlated. That's what turns raw telemetry into 'team X spent $Y on workload Z'."

## Anthropic-Specific Framing

The role's representative project — "instrument DCN fabric utilization with streaming telemetry and build the Grafana dashboards that become the team's source of truth" — is exactly this article. The answer to "how would you build this":

1. **Source layer:** gNMI subscriptions for utilization + interface counters; IPFIX for flow attribution
2. **Collector:** goflow2 + Telegraf, pre-aggregating to 1-minute summaries
3. **Enrichment:** join with topology DB and service registry; output (link, workload, bytes, $)
4. **Storage:** ClickHouse hot (7 days), BigQuery warm (90 days), S3+Parquet cold (1+ year)
5. **Dashboards:** Grafana with pre-aggregated tables for sub-second query latency
6. **Hot path:** Kafka + Flink for anomaly detection (sudden burst, unexpected drop)

That's a complete answer. Memorize the shape; the specific tools vary by org.

## What to Memorize

- Three tradeoffs: sampling, cardinality, storage tier
- Two paths: hot (alerting) vs cold (analysis)
- Pipeline shape: source → collector → enrichment → storage → dashboards
- Enrichment is the hardest part — IP→workload mapping
- Tier storage: hot/warm/cold with different fidelity and retention
