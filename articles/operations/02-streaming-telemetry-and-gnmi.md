# Streaming Telemetry and gNMI

The shift from SNMP polling to streaming telemetry is one of the most significant changes in how production networks are operated at scale. This article covers how streaming telemetry works, how gNMI implements it, and what it looks like in practice.

## How Streaming Telemetry Works

In the streaming telemetry model, the relationship between the network device and the monitoring system is inverted from SNMP:

**SNMP (pull model):** Monitoring system → asks the device → device responds → monitoring system stores the answer → repeats every N minutes.

**Streaming telemetry (push model):** Device → continuously streams updates → monitoring system stores every update.

In the push model:
- The device does not wait to be asked — it sends updates as fast as the configured sample interval (sub-second is common for critical counters)
- The monitoring system receives a continuous stream of structured updates
- If the monitoring system misses an update (TCP retransmits it), not an interval — critical events are not lost
- The device's telemetry agent runs independently of the CLI and SNMP agent, reducing interference between monitoring load and device operations

## gNMI: The Protocol

**gNMI (gRPC Network Management Interface)** is the protocol that implements streaming telemetry. It is defined in an OpenConfig specification and implemented by most major network vendors.

gNMI defines four RPCs:

**Capabilities:** The collector asks the device what YANG models and encodings it supports. This is the discovery step — before subscribing to data, confirm the device supports the paths you want.

**Get:** A synchronous, single-response query. Equivalent to SNMP Get — request a value, receive it. Used for one-time state retrieval, not continuous monitoring.

**Set:** Push configuration to the device. This is gNMI's configuration management function — replacing or merging YANG model instances on the device. Combined with NETCONF's candidate/commit model, gNMI Set enables atomic configuration deployment.

**Subscribe:** The streaming telemetry function. The collector sends a subscription request specifying which data paths it wants and at what rate. The device sends a continuous stream of updates.

## Subscription Modes

**ONCE:** The device sends the current value of the subscribed paths and then closes the subscription. Equivalent to a single Get but for potentially many paths simultaneously.

**POLL:** The collector explicitly triggers each update by sending a poll request. The device responds with the current values. Comparable to SNMP polling but using the gNMI/YANG structured format.

**STREAM:** The device sends updates continuously according to the configured interval or on-change trigger. This is the primary mode for network monitoring.

Stream subscriptions have two sub-modes:

**SAMPLE:** The device sends the value at a fixed interval, regardless of whether it has changed. Used for counters and metrics where you want regular snapshots even when stable. Typical intervals: 1 second for interface counters, 5 seconds for routing table size, 10-30 seconds for BGP session state.

**ON_CHANGE:** The device sends an update only when the value changes. Ideal for state data — BGP session up/down, interface operational state, alarm state. You receive an event exactly when something changes, not on a fixed schedule.

## Data Paths and YANG

The data paths in a gNMI subscription correspond to paths in a YANG model. The path syntax follows a hierarchical structure similar to XPath:

```
/interfaces/interface[name=Ethernet1]/state/counters/in-octets
/network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP]/bgp/neighbors/neighbor[neighbor-address=192.168.1.1]/state/session-state
/components/component[name=CPU]/state/memory/utilized
```

Each path segment is a YANG container, list, or leaf. List elements are addressed by their key, as shown with `[name=Ethernet1]` or `[neighbor-address=192.168.1.1]`.

Subscribing to a path that includes a list without a specific key subscribes to all instances: `/interfaces/interface/state/counters/in-octets` subscribes to in-octets for all interfaces simultaneously. This wildcard subscription is how you efficiently monitor all interfaces on a device in a single subscription.

## The Telemetry Pipeline in Practice

**Collectors:** Tools that receive gNMI streams and normalize them. Common open-source collectors: gNMIc (a gNMI CLI tool and collector), Telegraf (with gNMI input plugin), OpenConfig's reference collector. Commercial options include those from Arista (CloudVision), Cisco (Crosswork), and Juniper (Paragon).

**Time-series databases:** Store the normalized telemetry data with timestamps. Common choices: InfluxDB (purpose-built for time-series), Prometheus (pull-based but widely used with pushgateways), TimescaleDB (PostgreSQL extension for time-series).

**Visualization and alerting:** Grafana is the standard dashboard tool for network telemetry — connects to InfluxDB, Prometheus, and other data sources; rich time-series graphing; threshold-based alerting. PagerDuty or OpsGenie integrates with alerting to trigger on-call notifications.

**A minimal working pipeline:**

```
switch → gNMI stream → Telegraf (collector) → InfluxDB → Grafana
```

Telegraf's gNMI plugin subscribes to configured paths on each device, receives the stream, tags each metric with device name and relevant labels, and writes to InfluxDB. Grafana queries InfluxDB with InfluxQL or Flux and renders dashboards with configurable time ranges and refresh rates.

## What to Monitor: The Critical Metrics

For a spine-leaf fabric, the minimum viable telemetry coverage:

**Interface health:**
- `in-octets`, `out-octets`: Traffic rates (compare to interface bandwidth for utilization %)
- `in-errors`, `out-errors`: Non-zero error rates indicate hardware or cable issues
- `in-discards`, `out-discards`: Non-zero discard rates indicate buffer overflow (congestion) or policy drops
- `oper-status`: Interface operational state changes — any flap should trigger an alert

**BGP:**
- `session-state`: Up/Down state for every BGP peer
- `prefixes-received`: Number of prefixes received from each peer — unexpected drops indicate a withdrawn route or routing policy change
- `messages-received`, `messages-sent`: Rapid message rates indicate instability

**Routing table:**
- Route count in each VRF — unexpected drops indicate a routing event

**Device health:**
- CPU utilization — spikes above 70% indicate the control plane is under stress
- Memory utilization — approaching 90% warrants investigation
- Temperature and fan status — hardware health signals

**ECMP load balancing:**
- Per-member traffic rates in ECMP groups — significant imbalance indicates a load-balancing hash problem

## Alerting Philosophy

Good alerts are specific and actionable. Bad alerts are vague and noisy. The operational principle:

- An alert should tell the engineer exactly what is wrong, on which device, and what the current value vs. expected value is
- An alert should only fire when the condition requires human action — not as an informational notification
- Alert fatigue (too many false-positive or informational alerts) causes engineers to start ignoring alerts — which leads to missing the real ones

Well-designed hyperscale telemetry dashboards follow this principle: surface the data that supports proactive decisions (when should we expand capacity?) and reactive diagnosis (which device is causing this incident?) — not to generate noise.
