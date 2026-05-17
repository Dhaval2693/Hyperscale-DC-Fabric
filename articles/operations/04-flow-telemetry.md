# Flow Telemetry: sFlow, IPFIX, NetFlow

Streaming telemetry (gNMI) tells you about **device state** — interface counters, BGP sessions, CPU. Flow telemetry tells you about **traffic** — who is talking to whom, with what protocol, in what volume. Both are necessary; they answer different questions.

This article covers the three main flow telemetry protocols, when to use each, and the design tradeoffs (sampling, cardinality, storage) that come up when you build a telemetry pipeline at scale.

## Why Flow Telemetry Matters

You can't optimize what you can't see. For cost attribution, capacity planning, and DDoS detection, you need to know:
- Which source IP sent how many bytes to which destination IP?
- Over what protocol/port?
- Through which interface?
- At what time?

Interface counters (from SNMP or gNMI) tell you the AGGREGATE — "this link saw 50 Gbps last hour." Flow telemetry tells you WHO and WHAT — "10.0.0.5 sent 30 Gbps to 10.1.0.5 on TCP/443 for the last 10 minutes."

## The Three Protocols

### NetFlow (Cisco, v5 and v9)

The original. Each "flow" is a unidirectional sequence of packets with the same {src IP, dst IP, src port, dst port, protocol, ToS, interface}. The router buffers flow records and exports them when the flow ends or times out.

- **v5**: fixed format, limited fields
- **v9**: template-based, extensible

Primarily Cisco-native. Replaced by IPFIX as a standard.

### IPFIX (RFC 7011 — the IETF standard)

Essentially "NetFlow v10" — standardized, vendor-neutral, template-based. Most modern routers export IPFIX.

- More flexible field set than NetFlow v9
- Supports variable-length fields
- Can carry custom information elements

**Use IPFIX when:** you need a vendor-neutral flow protocol on modern gear. This is the default in most new deployments.

### sFlow (RFC 3176)

Packet sampling, not flow records. Router takes every Nth packet and sends the **packet header itself** (or a portion) to a collector.

- **Pros:** simpler implementation (no flow state on router); works for any protocol; sees layer 2 info; minimal router CPU
- **Cons:** statistical only — small flows may be missed entirely; requires more collector-side processing to reconstruct flows

**Use sFlow when:** you want low router overhead, broad visibility, and don't need exact byte accounting per flow (statistical inference is fine).

## When to Use What

| Need | Use |
|---|---|
| Exact byte/packet counts per flow | NetFlow/IPFIX with no sampling (expensive!) |
| Cost attribution at scale | IPFIX with sampling, statistical estimation |
| Low-overhead visibility | sFlow |
| Layer 2 info (MAC, VLAN) | sFlow |
| Multi-vendor environment | IPFIX (standardized) |
| DDoS detection (volumetric) | sFlow or sampled IPFIX |
| Application-level analysis | IPFIX with extended fields |

## Sampling: The Cardinality Problem

At hyperscaler scale, **unsampled flow export will crush your router and your collector**.

A 10G link at line rate is ~14.8M packets/second. Exporting a flow record for every flow generates millions of records per second per router. Multiply by a fleet of thousands.

**Sampling solves this.** Pick a sampling rate (e.g., 1 in 1000) and export only sampled flows. The collector multiplies up to estimate true volume.

| Sampling rate | Accuracy | Volume |
|---|---|---|
| 1:1 (no sample) | Exact | Crushing |
| 1:100 | Good for top-talkers, weak for rare flows | High |
| 1:1000 | Statistical only | Moderate |
| 1:10000 | Top-talkers only | Manageable |

**Rule of thumb:** start at 1:1000, dial up sampling for hot spots, accept that small flows are statistically inferred (not exact).

## Cardinality: The Storage Problem

Even with sampling, the number of **unique flow keys** can explode. Every {src, dst, sport, dport, proto} combination is a row.

- 1M unique src/dst pairs × 100 ports = 100M flows/hour
- Multiply across the fleet → billions of rows per day

**Strategies:**
1. **Pre-aggregate** at the collector — roll up to source-IP-only, or destination-prefix, before storing
2. **Tiered storage** — hot (last hour) on fast columnar store, warm (days) compressed, cold (months) downsampled
3. **Drop low-volume flows** below a noise floor
4. **Time-based bucketing** — 1-minute summaries instead of per-flow timestamps

## Architecture: A Flow Telemetry Pipeline

The typical pipeline:

```
[Router (sFlow/IPFIX)] → [Collector (goflow2, pmacct)]
                       → [Stream processor (Kafka + Flink)]
                       → [Enrichment (IP → workload, prefix → team)]
                       → [Storage (ClickHouse, BigQuery, Elastic)]
                       → [Dashboards (Grafana, internal BI)]
```

**Critical:** the enrichment step. Raw IPs are meaningless. You need to join against source-of-truth data (CMDB, IPAM, service registry) to attribute traffic to teams/workloads.

The hard part isn't the protocol — it's the pipeline design, especially the **identity mapping** at the enrichment stage.

## Comparison: Flow vs Streaming Telemetry

| | Flow telemetry (sFlow/IPFIX) | Streaming telemetry (gNMI) |
|---|---|---|
| What it tells you | Traffic (who/what/how much) | Device state (counters, sessions, CPU) |
| Granularity | Per-flow (sampled) | Per-interface, per-protocol |
| Data volume | High (every flow) | Lower (configurable subscriptions) |
| Use case | Cost attribution, DDoS, capacity planning | Health monitoring, alerting |

**You need both.** They answer different questions. A complete observability pipeline ingests both.

## How to Talk About It

> "Flow telemetry covers the 'who-talked-to-whom' question that interface counters can't answer. IPFIX is the standard; sFlow is the lower-overhead alternative. At scale you have to sample — 1:1000 is a reasonable default. The hard engineering is the pipeline: collector, enrichment (IP → workload), tiered storage with aggregation. The protocols are the easy part."

## Applied Example: Cost Attribution Pipeline

> "Per-flow cost attribution is a flow telemetry problem at heart. I'd export IPFIX from backbone routers, sample at 1:1000 to manage volume, enrich at ingest time with source-of-truth identity mapping (IP → team → workload), join against the per-path cost model, store in a columnar warehouse. The pipeline becomes the source of truth for 'who's spending what on egress.'"

## What to Memorize

- The three protocols: NetFlow (Cisco original), IPFIX (standard), sFlow (sampled headers)
- Sampling rate as the volume lever
- Cardinality as the storage lever
- The pipeline pattern: collector → enrichment → tiered storage → dashboards
- "Flow telemetry tells you about traffic; streaming telemetry tells you about devices"
