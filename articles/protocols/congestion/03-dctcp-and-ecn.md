# DCTCP and ECN: Congestion Control Without Drops

Standard TCP was designed for the wide area Internet. Its congestion control model is straightforward: TCP sends data, watches for packet loss, and interprets loss as a signal that the network is congested. When TCP detects loss, it cuts its sending window in half and backs off. When no loss is detected, it probes for more bandwidth by gradually increasing the window.

This model works reasonably well for the Internet, where congestion is a normal condition that varies continuously. It was not designed for data center networks, and in DC environments it causes a specific and measurable problem.

## Why Standard TCP Fails in the DC

Data center networks have three properties that make standard TCP congestion control poorly suited:

**Very short RTTs.** In a well-designed spine-leaf fabric, round-trip time between two servers in the same DC is typically 100–500 microseconds. Standard TCP's congestion algorithms — developed for RTTs measured in tens to hundreds of milliseconds — react too slowly. By the time TCP detects congestion via packet loss and backs off, a switch buffer has already filled and dropped many packets.

**High bandwidth, shallow buffers.** DC switches are optimized for line-rate forwarding with small on-chip buffers. A 100GbE port with a 1MB buffer fills in 80 microseconds at full rate. Switch buffers are not sized to absorb the long bursts that TCP's window-based probing generates.

**Incast.** When many servers respond simultaneously to a single request — a common pattern in distributed storage and microservices — multiple flows converge on a single bottleneck link within microseconds. The buffer fills suddenly. All flows hit tail drop simultaneously. All TCP flows interpret the simultaneous loss as congestion and halve their windows simultaneously. Throughput collapses. This is incast-induced TCP throughput collapse, and it is a real operational problem in any large distributed system.

The fundamental issue: TCP's binary congestion signal — loss or no loss — is too coarse for the microsecond timescales of DC congestion.

## ECN: Making Congestion Visible Before Loss

**Explicit Congestion Notification (ECN)** replaces the binary loss signal with an explicit, in-band congestion notification that the switch generates before packets are actually dropped.

ECN uses two bits in the IP header — the ECN field (bits 6 and 7 of the DSCP byte):

- **00 (Not-ECT):** This packet does not support ECN. If the switch needs to signal congestion, it must drop this packet.
- **01 or 10 (ECT — ECN Capable Transport):** Both sender and receiver support ECN. The switch may set the CE bit instead of dropping.
- **11 (CE — Congestion Experienced):** The switch has set this bit to signal that the packet traversed a congested switch. The receiver must notify the sender.

**The signaling flow:**

1. TCP sender and receiver negotiate ECN support during the TCP handshake (via ECE and CWR flags in TCP headers).
2. Both endpoints set ECT in their packets' IP headers to indicate ECN capability.
3. When a switch's queue depth exceeds a configured threshold (typically much less than the queue's maximum capacity), instead of dropping ECT-marked packets, the switch sets the CE bits — **Congestion Experienced**.
4. The receiver sees CE-set packets arriving. It sends a TCP ACK with the ECE (ECN Echo) flag set — "I received congestion notification."
5. The sender sees the ECE flag in the ACK. It reduces its congestion window (by half, in standard ECN), sends a CWR (Congestion Window Reduced) flag to acknowledge the notification, and backs off.
6. The switch clears the CE bit once queue depth falls below the threshold.

**The key difference from loss-based TCP:** The switch signals congestion while packets are still being delivered. No drops occur (in the normal path). TCP backs off based on an explicit signal, not based on observing that packets disappeared. The queue never fills to the point of dropping because TCP is backing off earlier.

## DCTCP: Using ECN Proportionally

Standard ECN with TCP is binary: CE is set or not set. TCP interprets any CE signal as full congestion and halves its window — the same response as a packet drop. This is still too aggressive for the DC context, where congestion may be mild and momentary.

**DCTCP (Data Center TCP)** uses ECN signals proportionally rather than as a binary event. Instead of halving the window on any CE signal, DCTCP measures what fraction of packets are CE-marked and reduces the window proportionally to that fraction.

**How DCTCP measures congestion:**

The receiver tracks the fraction of bytes received with CE set over a sliding window. This fraction — α — is an Exponentially Weighted Moving Average (EWMA) of the CE fraction:

```
α = (1 - g) × α + g × F
```

Where F is the fraction of packets marked CE in the last RTT, and g is a small weight factor (typically 1/16). A high α means heavy congestion; a low α means mild congestion.

The sender reduces its window by:

```
cwnd = cwnd × (1 - α/2)
```

If only 10% of packets are CE-marked (α ≈ 0.1), the window is reduced by only 5% — a small, proportional response. If 80% are CE-marked (α ≈ 0.8), the window is reduced by 40% — a larger response. Compare this to standard TCP, which always halves the window regardless of how much congestion there is.

**Why this matters for DC performance:**

DCTCP keeps queue occupancy low and stable. Because TCP backs off proportionally and early (before the queue fills), the queue depth oscillates around the ECN threshold rather than oscillating between full and empty. This results in:

- Low, predictable queuing latency
- High throughput even during incast events
- Much less TCP synchronization — flows respond differently based on how much CE they each see

DCTCP is deployed in many hyperscale DC environments and is the TCP congestion control algorithm used by Microsoft Azure and others for intra-DC traffic.

## Deployment Considerations

**Both endpoints must support DCTCP.** DCTCP requires changes to the TCP stack. If one endpoint is running standard TCP and the other is running DCTCP, the interaction is undefined and performance may degrade. DCTCP should only be used in homogeneous environments where both clients and servers are under your control — which is why it is common inside a cloud provider's DC but not on the public Internet.

**Switch ECN thresholds must be tuned.** ECN marking begins when queue depth exceeds the configured threshold. If the threshold is too high, ECN kicks in too late — queues still fill and drops occur. If the threshold is too low, ECN fires too aggressively — TCP backs off unnecessarily and throughput suffers. The sweet spot depends on link speed, RTT, and traffic pattern. Typical starting points: threshold at 20-30% of buffer capacity, with tuning based on observed queue depth under realistic load.

**ECN does not help UDP traffic.** DCTCP and ECN only work with TCP. UDP flows — including RDMA over Converged Ethernet (RoCEv2) — do not interpret ECN the same way. RoCEv2 has its own congestion notification mechanism using ECN bits in a different protocol layer, described in the PFC and lossless Ethernet article.

**ECN and WRED can coexist.** In mixed environments where some traffic is ECN-capable and some is not, switches can be configured to mark ECN-capable packets when queue depth exceeds the threshold, while applying WRED drop to non-ECN packets at the same threshold. ECN-capable flows get congestion signals without drops; non-ECN flows get WRED drops as the conventional signal.

DCTCP with ECN represents the state of the art for TCP-based congestion control in data center environments. For any interview discussion about DC networking and performance at hyperscale, knowing this mechanism — and why standard TCP is inadequate — is essential.
