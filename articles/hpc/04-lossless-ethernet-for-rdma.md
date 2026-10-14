# Lossless Ethernet for RDMA: Making It Work in Practice

The theory of lossless Ethernet for RoCEv2 is covered in the PFC and ECN articles. This article focuses on what it looks like to actually deploy and operate a lossless Ethernet fabric for RDMA — the configuration, the monitoring, and the failure modes that matter in production.

## The Target Operating State

A correctly operating lossless RDMA fabric should exhibit:

- **Near-zero RDMA retransmits.** If DCQCN and ECN are working correctly, senders reduce their rate before queue depths reach PFC threshold. PFC should rarely trigger. RDMA retransmits should be essentially zero in steady state.
- **Low, stable PFC pause frame counts.** Some PFC activity is expected during sudden burst events. Continuous, high PFC pause rates indicate chronic congestion that ECN/DCQCN is not managing. This needs investigation.
- **ECN marks on 5-20% of packets during peak load.** ECN is working as designed if marks appear under load but queue depths stay below PFC threshold. Zero ECN marks under load suggests ECN threshold is set too high.
- **Zero packet drops in the RDMA priority class.** Any discard counters in the RDMA QoS class should alarm immediately — this indicates PFC is failing to prevent drops.

## Configuration Components

**Step 1: Define QoS classes and DSCP markings**

RDMA traffic must be marked with a specific DSCP value so switches can classify it into the correct QoS queue. Common choice: DSCP 26 (AF31) or a vendor-recommended value. All RNICs must be configured to mark RDMA traffic with this DSCP value at the source.

```
# RDMA traffic: DSCP 26 → CoS 4 → RDMA queue with PFC enabled
```

**Step 2: Enable PFC on the correct priority**

PFC is enabled per-priority-class (0-7). Enable PFC only on the RDMA priority:

```
# Arista EOS example
priority-flow-control mode on
priority-flow-control priority 4 no-drop  # CoS 4 = RDMA, lossless
```

PFC must be enabled end-to-end: on every switch port in the RDMA traffic path, including server-facing ports, spine uplinks, and spine ports. A single switch port in the path without PFC enabled breaks the lossless guarantee.

**Step 3: Configure ECN thresholds**

ECN marking begins when queue depth exceeds the configured threshold. The threshold must be below the PFC pause threshold (otherwise ECN signals too late and PFC must trigger):

```
# Typical values for a 100GbE port with 4MB buffer
ECN marking threshold: 800KB (20% of buffer)
PFC pause threshold: 1.5MB (37.5% of buffer)
Headroom (in-flight packets at 100GbE × RTT): ~200KB
```

These values depend on link speed, RTT, and switch buffer size. They require tuning based on measured queue depth under representative load.

**Step 4: Enable DCQCN on the RNICs**

DCQCN (Data Center Quantized Congestion Notification) is the congestion response algorithm on the RDMA NIC. When the NIC receives a CNP (Congestion Notification Packet — sent by the receiver when it sees CE-marked packets), it reduces its sending rate proportionally.

DCQCN parameters are configured on the RDMA NIC driver (typically through Mellanox's mlnx-tools or OFED configuration):
- Rate reduction on CNP receipt
- Rate recovery rate after CNP stops
- Initial and minimum rate limits

These parameters interact with the switch ECN thresholds. If the RNIC recovers too aggressively, queue depths oscillate. If it recovers too conservatively, throughput suffers after a congestion event. Tuning requires load testing with realistic traffic patterns.

## Monitoring a Lossless RDMA Fabric

The key counters to monitor — on both switches and RNICs:

**Switch-side counters:**
- `PFC pause frames sent` per priority per port: Should be low. High rates indicate the downstream device is congested and sending pauses upstream.
- `PFC pause frames received` per priority per port: Should be low. High rates indicate this port is being paused by upstream congestion.
- `ECN CE marks` per queue: Should increase under load. Zero marks under load suggests ECN threshold is too high.
- `Discards` in the RDMA queue: Should be zero. Any non-zero value is a critical alert.

**RNIC-side counters (via perfquery, rdma stat, or vendor tools):**
- `out_of_buffer`: Packets dropped because the receive queue was full — indicates receiver is not posting receives fast enough
- `out_of_sequence`: Packets received out of order — indicates reordering in the fabric (ECMP hash causing reordering, which is catastrophic for RDMA)
- `rdma_rnr_nak`: Receiver Not Ready NAKs — receiver had no posted receive when a Send arrived
- `roce_rx_pkts`, `roce_tx_pkts`: Baseline traffic counters

**Application-level throughput:** The ultimate validation is the application's measured throughput and GPU utilization during training. An RDMA fabric that shows clean switch counters but degrades training throughput has a subtle problem — often reordering, DCQCN mistuning, or slow RDMA library paths.

## Common Failure Modes

### PFC Deadlock

**What you see:** Traffic completely stops in the RDMA priority class. All ports show maximum PFC pause counts. Clearing RDMA flows does not restore forwarding — the fabric is frozen.

**Why it happens:** PFC pause propagates upstream to stop senders. If the traffic pattern creates a circular dependency, every switch is waiting for another to drain and none of them can:

```
    SW-A  ←── pauses ───  SW-B
      │                     │
   pauses                pauses
      │                     │
    SW-C  ───── pauses ──→ SW-D
                    ↑
           SW-D also pauses SW-A
           → circular, no one can drain
```

**How to prevent it:** Ensure the physical topology has no circular buffer dependencies. RDMA flows must not create routing loops. Fat-tree avoids this naturally; more complex topologies need explicit analysis.

---

### RDMA Packet Reordering

**What you see:** High `out_of_sequence` counters on RNICs. Low RDMA throughput despite clean PFC counts and no discards — the network looks fine but application performance is poor.

**Why it happens:** ECMP is splitting packets of the same RDMA flow across different paths. Each path has a different latency, so packets arrive out of order. RDMA cannot tolerate this — a single out-of-order packet triggers retransmission of everything after it.

```
GPU-A sends packets P1, P2, P3, P4 to GPU-B (same flow):

         ┌─── Path 1 (latency 10µs) ───┐
P1, P3 ──┤                              ├──→ GPU-B receives: P1, P3, P2, P4
P2, P4 ──┤                              │                    ↑
         └─── Path 2 (latency 15µs) ───┘        out-of-order → retransmit P2, P3, P4
```

**How to fix it:** Verify ECMP hashing uses the full 5-tuple (src IP, dst IP, src port, dst port, protocol). All packets of the same RDMA flow must hash to the same path.

---

### DCQCN Mistuning

**What you see:** Oscillating throughput — the application alternates between high utilization and near-zero utilization in a repeating pattern.

**Why it happens:** DCQCN rate recovery is too aggressive. The sender never settles at a stable rate:

```
Throughput
    │       ┌──┐        ┌──┐        ┌──┐
    │       │  │        │  │        │  │
    │  ┌────┘  └──┐  ┌──┘  └──┐  ┌─┘  └─
    │  │          │  │         │  │
    └──┘          └──┘         └──┘
       flood → ECN → back off → flood → repeat
```

**How to fix it:** Tune DCQCN rate recovery parameters on the RNIC — specifically the rate increase step and timer — to ramp up more gradually after a congestion event. Requires load testing with representative traffic to find stable values.

---

### PFC Not Configured End-to-End

**What you see:** Packet drops in the RDMA queue on specific switch ports, even though PFC appears to be configured. Drops are localized to particular links.

**Why it happens:** PFC must be enabled on every port in the RDMA path. One port missing PFC breaks the lossless guarantee — during a burst, that port's buffer overflows with nothing to stop the upstream sender.

```
GPU-A → [SW1: PFC ✓] → [SW2: PFC ✓] → [SW3: PFC ✗] → GPU-B
                                              ↑
                                    buffer overflows here
                                    drops RDMA packets
                                    (PFC cannot propagate past this point)
```

**How to fix it:** Audit PFC configuration on every port in the RDMA traffic path — not just that PFC is globally enabled, but that it is enabled on the correct priority class on each individual port.

## The Network Engineer's Role in RDMA Infrastructure

When something goes wrong in an RDMA cluster, the investigation requires cooperation between the network team, the server team, and the application team — because the problem could be at any layer:

- Switch misconfiguration (PFC not enabled, ECN threshold wrong)
- RNIC misconfiguration (wrong DCQCN parameters, wrong priority mapping)
- Application misconfiguration (wrong QP parameters, incorrect memory registration)
- Physical layer (cable errors, optic degradation causing CRC errors that cause RNICs to drop flows)

The network engineer's contribution is clarity on the switch layer: "PFC is enabled on priority 4 on all ports in the path. ECN marks are appearing at the expected rate. No discards in the RDMA queue. Switch-side is clean." That definitive answer narrows the investigation to the server or application layers.

That clarity — being able to confirm or eliminate the network as the cause of an RDMA performance problem — is exactly what the DC network team is responsible for providing.
