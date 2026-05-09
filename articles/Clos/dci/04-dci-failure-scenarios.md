# DCI Failure Scenarios and Traffic Engineering

The measure of a DCI design is not how it performs when everything works — it is how it behaves when things break. DCI links fail. Routers fail. Carrier networks have outages. In hyperscale environments, the DCI design must anticipate each of these failure modes and define — in advance — exactly what happens to traffic and how quickly the network recovers.

This article covers the failure scenarios that matter most in DCI and the design decisions that minimize their impact.

## Failure Mode 1: DCI Link Failure

The most common and most impactful failure: one or both DCI circuits between DC-A and DC-B go down.

**What happens in a well-designed system:**
1. BFD (Bidirectional Forwarding Detection) running between the Border Leaf switches detects the failure within 100-300ms (much faster than BGP hold-timer expiry).
2. BFD signals to BGP that the peer is unreachable. BGP immediately withdraws routes learned from that peer.
3. If a secondary DCI path exists (via a different carrier or physical path), traffic fails over to the secondary path. BGP reconverges using the secondary path's route attributes.
4. Monitoring systems alert the on-call team with the specific link and timestamp.
5. Traffic flows via the secondary path until the primary is restored.

**What happens if there is no secondary path:**
- Traffic destined for the other DC is dropped or blackholed until the link recovers.
- Applications must handle this: any application that requires cross-DC communication without an alternative local path is unavailable during a single-DC DCI failure.

**Design implication:** Every production DCI must have at least two diverse physical paths — different fiber routes, different carriers, or a combination. "Diverse" means the physical fiber takes a different geographic path, not just a different carrier on the same conduit. Many apparent dual-path designs fail because both circuits share the same fiber conduit between buildings.

**Operational monitoring:** DCI links should be monitored at the physical layer (optical power levels, BER — Bit Error Rate) and the IP layer (BGP session state, traffic volume, latency). An optical power level that is degrading is an early warning of an impending failure — the link has not failed yet, but it will. Proactive intervention (calling the carrier before the link drops) is far better than reactive recovery.

## Failure Mode 2: Border Leaf Failure

The Border Leaf switch is a single point of failure in the DCI path. If it fails, all DCI traffic through that switch is lost, even if the physical DCI circuits are healthy.

**Mitigation: Dual Border Leaves in ECMP**

Deploy two (or more) Border Leaf switches, connected to the same DCI circuits, with ECMP load balancing between them. EVPN/BGP within the DC fabric treats both Border Leaves as equal-cost paths to the remote DC. Traffic is spread across both during normal operation. If one Border Leaf fails, traffic fails over to the surviving one with minimal disruption.

BGP detects the Border Leaf failure immediately (via BFD or BGP hold-timer expiry with fast-convergence tuning). The surviving Border Leaf continues to advertise the DCI routes; only the routes through the failed Border Leaf are withdrawn. Traffic reconverges to the surviving Border Leaf.

**Single-homed DCI circuits:** If the physical DCI circuits connect only to one Border Leaf each (common when there are exactly two Border Leaves, each with its own circuit), a Border Leaf failure also takes down its physical DCI circuit. This is equivalent to a single DCI link failure — the design must handle it the same way.

## Failure Mode 3: Split-Brain

Split-brain occurs when the DCI link fails but both DCs continue operating independently, serving clients and accepting state changes, with no visibility into what the other DC is doing.

**The Layer 2 split-brain scenario:**
- VNI 10010 is stretched across both DCs
- DCI link fails
- In DC-A, a VM with IP 10.1.1.50 is migrated to a different host
- In DC-B, a new VM is assigned IP 10.1.1.50 (because DC-B no longer sees the MAC/IP advertisement from DC-A)
- DCI link recovers
- Both DCs advertise MAC/IP bindings for 10.1.1.50 — they conflict
- Traffic to 10.1.1.50 may go to either VM, depending on which EVPN advertisement is preferred by BGP path selection

**Mitigation:**
- Use Layer 2 extension sparingly and prefer Layer 3 routing
- For stretched VNIs, use a DHCP server that is aware of both DCs and prevents duplicate IP assignment
- Design applications for split-brain tolerance: they should function during a split-brain and reconcile state when connectivity restores, not require the network to prevent the split-brain

**The Layer 3 split-brain scenario is less severe:** If only Layer 3 routing crosses the DCI, a split-brain means each DC serves its own traffic independently. Traffic that requires cross-DC routing is dropped. When connectivity restores, BGP reconverges automatically. There is no conflicting state to reconcile at the IP layer.

## Failure Mode 4: Asymmetric Routing

Asymmetric routing occurs when traffic from DC-A to DC-B follows one path, and the return traffic from DC-B to DC-A follows a different path. In stateful network devices (firewalls, load balancers, NAT devices) on the DCI path, asymmetric routing causes session failures because the stateful device only sees one direction of the traffic.

**Common cause:** Two Border Leaves in DC-A, two Border Leaves in DC-B, ECMP across both, but stateful devices between them that are not synchronized.

**Mitigation:**
- Avoid stateful devices on the DCI path where possible — prefer stateless inspection
- If firewalls are required, deploy them in active-passive pairs with state synchronization, ensuring both directions of a session always traverse the same firewall
- Use BGP communities and route policy to pin specific traffic to specific Border Leaf pairs when stateful device placement requires it

## Traffic Engineering on DCI Links

Not all inter-DC traffic is equal. Database replication traffic that runs in the critical path of user transactions needs low latency and high priority. Backup jobs that run overnight can use whatever bandwidth is available without priority.

**QoS on DCI links:** Apply DSCP marking at the ingress to the DCI link based on traffic class. Database replication and real-time services get EF or AF41. Bulk backup traffic gets BE. The DCI link's scheduler enforces these markings, ensuring that bulk traffic never starves latency-sensitive replication traffic.

**Traffic engineering with multiple DCI paths:** When two physically diverse DCI paths are available, you have the option to traffic-engineer: route latency-sensitive traffic via the lower-latency path and bulk traffic via the other. BGP communities and local-preference attributes control which path BGP prefers for different traffic classes. At hyperscale inter-DC traffic volumes, this kind of deliberate traffic engineering prevents the lower-latency path from being saturated by backup traffic.

**Capacity planning:** DCI bandwidth must be planned based on worst-case requirements, not average requirements. If a DC failure causes all traffic to reroute through the DCI, the DCI must have enough capacity to carry it. This is the "N+1" or "N+N" capacity model — the available DCI capacity (excluding the failed path) must be sufficient for the traffic that would normally use the failed path.

## The Operational Playbook

When a DCI incident occurs, the investigation follows a specific sequence:

1. **Confirm the scope:** Is this one DCI path or all DCI paths? Is traffic completely lost or partially degraded? Which DCs are affected?
2. **Check physical layer:** Optical power levels, BER on the affected circuit. Is this a physical fiber issue or an IP-layer issue?
3. **Check BGP state:** Are BGP sessions between Border Leaves up? What routes are being exchanged? Are the expected routes present on each side?
4. **Check traffic distribution:** Is traffic flowing via the secondary path? Is the secondary path saturated?
5. **Engage the carrier:** If physical layer issues are confirmed, open a carrier ticket immediately with the optical measurements.
6. **Post-mortem:** After restoration, document the timeline, root cause, and any design improvements that would have reduced impact or detection time.

This is the operational context that any DCI role requires: not just knowing that DCI exists, but knowing how to design it for failure and operate it through incidents.
