# Why Observability Matters in Networks

You cannot fix what you cannot see.

This is obvious in theory. In practice, many network operations teams have spent years in a model where observability was an afterthought — devices were managed, changes were made, and problems were discovered when customers called. The tools for understanding what the network was doing in real time were limited: SNMP polling every five minutes, CLI commands run during incidents, and logs that were only examined after something broke.

Hyperscale data center networking has made this model obsolete. At the scale of thousands of devices, tens of thousands of interfaces, and millions of traffic flows, you need to know what is happening before customers notice — and you need enough instrumentation to diagnose complex issues without guessing.

This is what **observability** means in a network context: the ability to infer the internal state of the network from external signals, in real time, at scale.

## The Three Pillars of Network Observability

**Metrics:** Numerical measurements of network state over time. Interface counters (bytes in/out, errors, drops), CPU and memory utilization, BGP prefix counts, packet loss rates, latency measurements. Metrics answer "how much" and "how fast."

**Logs:** Discrete events recorded with timestamps. A BGP neighbor going up or down. An interface changing state. A configuration change. A routing table update. OSPF adjacency forming or failing. Logs answer "what happened and when."

**Traces:** The path of a specific transaction or flow through the network. Which switch did this packet traverse? What happened at each hop? Was it dropped? Was it delayed? Traces answer "why did this specific thing fail."

Most network observability systems are strong on metrics, moderate on logs, and weak on traces. Full distributed tracing at the network layer (following a specific flow hop-by-hop) is still an emerging capability in network tooling.

## Why SNMP Is No Longer Enough

SNMP (Simple Network Management Protocol) has been the dominant network monitoring protocol for three decades. SNMP v2c polling works: connect to a device, query specific MIB OIDs, receive the current value. Poll every 5 minutes. Graph the results.

The limitations at hyperscale are significant:

**Polling interval:** A 5-minute polling interval means you can only detect events that persist for longer than 5 minutes. A 30-second traffic spike that causes packet loss and triggers a BGP neighbor flap, then recovers — you will see in the counters that something happened, but you will not know when or at what rate. At hyperscale, many important events are sub-minute.

**Scale:** Polling thousands of devices via SNMP creates significant load on the network management system and on the devices being polled. SNMP polling is CPU-intensive on the device; at scale, SNMP storms during outages (when everything is being checked simultaneously) can worsen device performance at exactly the wrong time.

**Structured data:** SNMP MIBs are the schema for SNMP data — but MIBs are vendor-specific, often incomplete, and painful to parse. Getting a consistent, normalized view of network state across a multi-vendor environment via SNMP requires significant data transformation work.

**No push model:** SNMP polling is pull-based — you ask, the device answers. If you are not polling at the moment something interesting happens, you miss it. SNMP traps (push-based alerts) exist but are unreliable (UDP, no delivery guarantee) and coarse-grained.

## Streaming Telemetry: The Modern Alternative

Modern network observability is built on **streaming telemetry** — a push-based model where network devices continuously stream state to a telemetry collector, rather than waiting to be polled.

The protocol stack:
- **gNMI (gRPC Network Management Interface):** The transport protocol. Devices stream structured data to collectors over persistent gRPC connections.
- **YANG models:** The data schema. The telemetry data is structured according to the same YANG models used for configuration management (OpenConfig, vendor-native YANG). The collector knows exactly what each field means without parsing unstructured text.
- **Subscriptions:** The collector subscribes to specific data paths it wants to receive. A subscription to `/interfaces/interface/state/counters` delivers interface counter updates continuously. Subscriptions can be sample-based (every N milliseconds) or on-change (whenever the value changes).

The result: sub-second visibility into interface counters, BGP state, routing table changes, and any other YANG-modeled state on the device — with structured, machine-readable data that can be directly ingested into a time-series database.

**The telemetry pipeline:**

```
Network Devices
    │ gNMI stream
    ▼
Telemetry Collector
(gNMI Dial-in or Dial-out)
    │ normalized metrics
    ▼
Time-series Database
(InfluxDB, Prometheus, TimescaleDB)
    │ queries
    ▼
Dashboard / Alerting
(Grafana, PagerDuty, custom)
```

At AWS, I built QuickSight dashboards that consumed network telemetry data to drive operational visibility for the deployment and fleet management workflows. The specific toolchain was AWS-internal, but the architecture is the same: devices emit structured data, a pipeline normalizes and stores it, dashboards make it actionable.

## What Good Observability Enables

**Proactive incident detection.** Instead of waiting for a customer complaint, the monitoring system detects anomalies — a BGP neighbor that is flapping, interface error counters that are climbing, a routing table that has lost prefixes — and alerts the on-call engineer before the impact becomes visible to users.

**Faster diagnosis.** During an incident, good observability means the answer to "what is happening" is available in seconds, not hours of manual CLI investigation. The timeline of events is already in the telemetry database; correlating a traffic drop with a BGP withdrawal with an interface error is a query, not a manual log search across dozens of devices.

**Capacity planning.** Historical telemetry data shows traffic growth trends, identifies bottlenecks before they become incidents, and provides the factual basis for infrastructure investment decisions. At AWS, the QuickSight dashboards I built were used for exactly this — tracking fabric utilization trends and informing decisions about DC expansion timing.

**Change validation.** After a configuration change, telemetry data confirms whether the change had the intended effect. Did the BGP session come up? Did traffic shift to the new path? Did error rates change? Validation through telemetry is faster and more reliable than manual CLI verification across many devices.

The next article covers streaming telemetry and gNMI in more depth. The article after covers the dashboards I built at AWS and what metrics I tracked for DC fabric health.
