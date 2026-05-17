# DHCP — Dynamic Host Configuration Protocol

DHCP is how devices get IP addresses (and other network config) automatically when they connect to a network. Without DHCP, every device would need manual IP configuration — unworkable at scale.

## The Problem DHCP Solves

When a brand-new device connects to a network:
- It has a MAC address (factory-assigned)
- It has no IP, no gateway, no DNS server
- It needs all that config to participate

DHCP automates the assignment. Plug in → get configured → start communicating.

## The DORA Process

DHCP uses a 4-step exchange. **DORA** = Discover, Offer, Request, Acknowledge.

```
Client                              DHCP Server
  |                                       |
  |---- DHCPDISCOVER (broadcast) ------> |
  |                                       |
  |<--- DHCPOFFER (broadcast/unicast)----|
  |                                       |
  |---- DHCPREQUEST (broadcast) -------> |
  |                                       |
  |<--- DHCPACK (broadcast/unicast)------|
  |                                       |
  [client configures itself]
```

1. **Discover** — Client broadcasts "anybody home?" (`255.255.255.255`, source `0.0.0.0` because it doesn't have an IP yet)
2. **Offer** — DHCP server responds with an IP offer
3. **Request** — Client formally requests the offered IP (broadcasts so other DHCP servers see it and withdraw their offers)
4. **Acknowledge** — Server confirms the assignment

After DORA, the client has an IP, subnet mask, gateway, DNS, and a lease time.

## Why Broadcast?

Before DHCP, the client has no IP. It can't talk unicast yet — broadcast is the only option. After step 1, the server CAN send back to the client's MAC, but historically broadcast is used throughout to keep the exchange visible to other DHCP servers (which need to know the client took someone else's offer).

## DHCP Lease

The IP isn't permanent — it's a **lease** for a defined time (often 24 hours, can be days/weeks).

- At **50%** of the lease, client renews directly with the original DHCP server (no DORA, just REQUEST/ACK)
- At **87.5%** (T2), if renewal failed, client rebroadcasts to find any DHCP server
- At **100%**, lease expires; client must restart DORA

This keeps the IP space efficient — devices that leave don't hold IPs forever.

## DHCP Options

The DHCP message carries optional fields beyond the IP. Common ones:

| Option | Purpose |
|---|---|
| Option 1 | Subnet mask |
| Option 3 | Default gateway |
| Option 6 | DNS servers |
| Option 15 | Domain name |
| Option 51 | Lease time |
| Option 53 | DHCP message type (DISCOVER/OFFER/etc.) |
| Option 54 | DHCP server identifier |
| Option 66 | TFTP server (for PXE boot) |
| Option 82 | Relay agent info (used by ISPs) |

Custom options exist too — VoIP phones, time servers, anything.

## DHCP Relay

DHCP relies on broadcast, but broadcasts don't cross routers. If DHCP server is on a different subnet, you need a **DHCP relay** (also called "ip helper-address" on Cisco gear).

The relay:
1. Receives the DHCPDISCOVER broadcast on its local interface
2. Re-sends it as **unicast** to the configured DHCP server (in another subnet)
3. Receives the DHCPOFFER and forwards it back to the client

This lets a single centralized DHCP server serve hundreds of subnets.

## DHCP Failover and Redundancy

For reliability, run multiple DHCP servers:
- **Split-scope** — divide the IP pool between two servers (each owns half)
- **DHCP Failover protocol** — two servers coordinate, share state
- **Anycast DHCP** — multiple servers share an IP; routing picks the nearest

## DHCPv6

The IPv6 equivalent. Two main modes:
- **Stateful DHCPv6** — like IPv4 DHCP, server assigns IPv6 addresses
- **Stateless DHCPv6** — host uses SLAAC for the address; DHCPv6 just provides DNS, etc.

IPv6 also has **SLAAC (Stateless Address Auto-Configuration)** where hosts derive their own addresses from router advertisements, no DHCP at all.

## DHCP Snooping (Security)

Switches can validate DHCP traffic:
- Only allow DHCPOFFER/ACK from **trusted ports** (where the legit server is)
- Block rogue DHCP servers (a misconfigured laptop or attacker)
- Build a table of legit IP↔MAC↔port bindings (used by Dynamic ARP Inspection)

Important in any production network. Without it, a rogue DHCP server hands out wrong addresses and breaks things.

## Common Failure Modes

1. **No DHCP server reachable** — client gets a 169.254.x.x APIPA address. Can talk to local segment but not the internet.
2. **DHCP exhaustion** — pool full, new clients can't get IPs. Usually means lease times are too long or pool too small.
3. **Rogue DHCP server** — wrong gateway/DNS handed out, traffic redirected. Fix: DHCP snooping.
4. **Stale leases after a server restart** — clients keep working, but server has lost state. Some implementations use a lease database to survive restarts.

## How to Talk About It

For "explain DHCP":
> "DHCP auto-configures hosts when they join a network. Four-message exchange — DORA: Discover, Offer, Request, Acknowledge. Client broadcasts, server replies. The client gets an IP, mask, gateway, DNS, and a lease time. At half the lease, the client renews directly with the server. Without DHCP, every device would need manual config — not feasible at scale."

For "why does DHCP need a relay":
> "DHCPDISCOVER is broadcast and broadcasts don't cross routers. If the DHCP server is on a different subnet, the local router needs to be a DHCP relay — receive the broadcast, forward it as unicast to the server, then forward responses back."

## Common Interview Questions

**Q: "What's APIPA / link-local?"**
- When DHCP fails, hosts auto-assign themselves a 169.254.x.y address. Lets them communicate on the local segment even without a DHCP server. Won't get internet — no gateway.

**Q: "How does DHCP work across subnets?"**
- DHCP relay on the router forwards DHCPDISCOVER as unicast to the central DHCP server.

**Q: "What's option 82?"**
- Relay-agent info inserted by the DHCP relay. Tells the central server "this DHCPDISCOVER came from this circuit/port." ISPs use it for billing and subscriber identification.

**Q: "What's DHCP snooping?"**
- Switch feature that blocks DHCP responses from untrusted ports, preventing rogue DHCP servers from hijacking the network.

## What to Memorize

- DORA: Discover, Offer, Request, Acknowledge
- DHCP uses **UDP ports 67 (server) and 68 (client)**
- DHCPDISCOVER is broadcast (`255.255.255.255`), source `0.0.0.0`
- Lease renewal at 50% (T1), rebroadcast at 87.5% (T2)
- Common options: gateway, DNS, mask, lease time
- DHCP relay for cross-subnet (no broadcasts across routers)
- DHCP snooping for security
