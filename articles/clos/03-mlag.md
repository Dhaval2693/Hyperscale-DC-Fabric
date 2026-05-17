# MLAG: Multi-Chassis Link Aggregation

In a standard spine-leaf fabric, every leaf switch connects to every spine switch — providing multiple paths and automatic failover via ECMP. The server connects to a single leaf switch (or in high-availability designs, to two leaf switches via active-passive bonding). But active-passive bonding wastes half the available uplink bandwidth: the standby link carries no traffic until the active link fails.

**MLAG (Multi-Chassis Link Aggregation)** solves this by allowing a server to form a single Link Aggregation Group (LAG) across two physically separate leaf switches, both links active simultaneously. From the server's perspective, it has one logical bond interface with double the bandwidth. From the network's perspective, the two leaf switches behave as a single logical switch for the purpose of this server's connection.

## The Problem MLAG Solves

Standard 802.3ad LACP (Link Aggregation Control Protocol) requires all links in a LAG to terminate on the same switch. If you connect two server NICs to the same switch in a LAG, you gain bandwidth and the switch handles link failures, but you have no protection against switch failure — a failed switch takes down both links regardless of the LAG.

Connecting the two server NICs to different switches (active-passive bonding) provides switch failure protection but halves effective bandwidth: only one link forwards at a time.

MLAG breaks the LACP constraint by making two physical switches appear as a single logical switch to the server's bonding driver. Both links are active, both carry traffic, and the failure of either switch or link is handled transparently.

## How MLAG Works

The two leaf switches (the MLAG pair) are connected by a dedicated link called the **MLAG Peer Link** (sometimes called the Inter-Chassis Link — ICL). The peer link carries:
- Control plane traffic for MLAG state synchronization
- Data plane traffic for flows that arrive on one peer but need to egress through the other

**State synchronization:** The two MLAG peers continuously synchronize state over the peer link:
- LACP PDUs: The LACP session with the server appears to come from a single entity (both peers use the same System ID — a shared MAC address)
- MAC table entries: A MAC learned on Peer-A is distributed to Peer-B so that both switches can forward traffic to that host
- ARP/ND table: So both peers can answer ARP requests for hosts attached via MLAG

**The shared System ID:** For the server's LACP to see the two physical switches as one logical switch, both peers must present the same LACP System ID. This is a shared MAC address configured on both peers specifically for MLAG. The server's bonding driver treats all LACP PDUs with the same System ID as coming from the same logical partner.

## Traffic Forwarding in MLAG

When a server sends traffic out its bond interface, the bonding driver distributes flows across both physical links using a hash of packet headers (source/destination IP, source/destination MAC, or L4 ports — depending on bonding mode). This means different flows from the same server can exit via different leaf switches simultaneously.

When traffic arrives destined for an MLAG-attached server, the receiving switch checks whether the destination MAC is reached via a local MLAG port-channel or via the peer link:
- If the egress port-channel is on this switch: forward directly
- If the egress port-channel is on the peer switch: send across the peer link to the peer, which forwards to the server

The peer link is sized to handle the worst-case traffic that must transit between switches: typically 2×40GbE or higher for 10GbE server links.

## The Orphan Port Problem

Not every server connects to an MLAG pair. Some servers may be singly-homed — connected to only one of the two MLAG peers. These are called **orphan ports**.

For traffic from an orphan port to reach the wider fabric, it flows normally via the connected switch's uplinks to the spines. But for traffic arriving from the fabric destined for the orphan host — if it arrives at the wrong peer — it must cross the peer link to reach the correct switch.

This is the reason the peer link must be sized generously: in the worst case, a significant portion of traffic destined for one switch's orphan ports arrives at the other switch and must transit the peer link.

## MLAG Failure Scenarios

**Single link failure (server side):** The server's bonding driver detects the failed link via LACP PDU absence and removes it from the active set. The remaining link continues forwarding. No traffic interruption beyond the brief convergence period.

**Single switch failure (one MLAG peer fails):** The surviving peer detects the failure via:
- Peer link going down (the most direct signal)
- MLAG heartbeat timeout (a keepalive mechanism separate from the peer link, often over the management network)

The surviving peer transitions into a mode where it handles all traffic for MLAG port-channels that were previously shared. LACP on the server side detects that the failed link is down (the failed peer stops sending LACP PDUs) and moves traffic to the surviving link. Recovery time is typically sub-second for the network side; the server bonding driver convergence depends on the OS and bonding configuration.

**Peer link failure (peer link goes down, both switches still up):** This is the most dangerous failure scenario. Both switches are up, both are connected to servers, but they cannot communicate. Each switch's MLAG state is now stale — it does not know the current MAC tables or LACP state of the peer.

Most MLAG implementations handle this with a **dual-active detection** mechanism:
- If the peer link goes down AND the keepalive (via management network) confirms both switches are still reachable: a split-brain has occurred. The secondary peer disables its MLAG port-channels to prevent a situation where the same LACP System ID appears on two independent switches simultaneously.
- If the peer link goes down AND the keepalive shows the peer is unreachable: the peer has probably failed. The surviving switch assumes primary status.

## MLAG vs. Active-Passive Bonding: The Design Choice

| | Active-Passive Bonding | MLAG |
|---|---|---|
| Link utilization | 50% (one link idle) | 100% (both links active) |
| Switch failure protection | Yes | Yes |
| Complexity | Low (no peer link, no sync) | Higher (peer link, state sync) |
| Failure scenarios | Simpler | More edge cases (split-brain) |
| When to use | Cost-sensitive, low-bandwidth | High-bandwidth, fully redundant |

In production DC designs at hyperscale, MLAG (or equivalent vendor implementations — Arista uses "MLAG," Cisco NX-OS uses "vPC," Juniper uses "MC-LAG") is common for any server that requires full-bandwidth dual-homing. For servers where the bandwidth of one link is sufficient and switch-level redundancy is provided by the spine-leaf architecture above, active-passive bonding is simpler and sufficient.
