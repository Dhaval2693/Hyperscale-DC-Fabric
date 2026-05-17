# Ethernet and ARP

Ethernet is the dominant Layer 2 protocol — what frames look like on local networks, both copper and fiber. ARP is the bridge between Layer 3 (IP) and Layer 2 (MAC), translating IP addresses into MAC addresses so frames know where to go.

You can't talk about networking fundamentals without these two.

## Ethernet Basics

Ethernet defines:
- **Frame format** — how bits are arranged on the wire
- **MAC addressing** — 48-bit hardware identifier (e.g., `AA:BB:CC:DD:EE:FF`)
- **Access method** — historically CSMA/CD; modern switched Ethernet doesn't need it

### MAC Addresses

- **48 bits** (6 bytes), usually shown as `AA:BB:CC:DD:EE:FF` or `aa-bb-cc-dd-ee-ff`
- First 24 bits = **OUI (Organizationally Unique Identifier)** — assigned to a vendor (Cisco, Intel, Apple)
- Last 24 bits = unique within that vendor
- **Broadcast MAC:** `FF:FF:FF:FF:FF:FF`
- **Multicast MAC:** starts with `01:` (low bit of first byte set)

### How Ethernet Forwarding Works

On a switch:
1. Frame arrives on a port
2. Switch reads destination MAC
3. Looks up MAC in its **MAC table** (learned by watching source MACs of incoming traffic)
4. Forwards to the appropriate port
5. If destination MAC is unknown, **floods** to all ports except the incoming one

This is "transparent bridging" — the switch learns MACs by observation, no configuration.

### VLANs (802.1Q)

A VLAN tags Ethernet frames so multiple logical networks share the same physical infrastructure. The 802.1Q tag adds 4 bytes between source MAC and EtherType.

- Up to 4094 usable VLANs (12-bit ID)
- Trunks carry tagged frames between switches; access ports carry untagged frames to end hosts
- Inter-VLAN traffic requires routing (Layer 3)

## ARP: Address Resolution Protocol

**Problem ARP solves:** Layer 3 has IP addresses; Layer 2 has MAC addresses. To put an IP packet on the wire, you need to know the destination MAC. ARP fills in that gap.

### The ARP Exchange

Imagine host `10.0.0.5` (MAC: `AA:...`) wants to send a packet to `10.0.0.1` (MAC: unknown). Both are on the same subnet.

```
1. 10.0.0.5 broadcasts an ARP Request:
   "Who has 10.0.0.1? Tell 10.0.0.5"
   → Destination MAC: FF:FF:FF:FF:FF:FF (broadcast)

2. 10.0.0.1 sees the request (everyone does — it's broadcast)
   and responds with an ARP Reply (unicast):
   "10.0.0.1 is at BB:..."

3. 10.0.0.5 caches the mapping (10.0.0.1 → BB:...) and
   sends the IP packet in an Ethernet frame to BB:...
```

The mapping is cached for a few minutes (varies by OS — typically 60s to 20min). Refreshed lazily.

### ARP Is L2 — It Doesn't Cross Routers

ARP is broadcast — it works only within a single L2 segment (a single VLAN or broadcast domain). If the destination IP is on a different subnet, your host ARPs for the **default gateway's MAC** instead, then sends the packet to the gateway, which routes it onward.

This is the source of the classic interview answer for "what does a host do when sending to a different subnet":
1. Compare destination IP to local subnet mask
2. If outside local subnet → ARP for default gateway MAC
3. Encapsulate IP packet in frame with destination MAC = gateway MAC
4. Send

### Gratuitous ARP

A host announces its own IP→MAC mapping unsolicited. Used for:
- Detecting duplicate IPs ("does anyone else claim this IP?")
- Updating caches when an IP moves to a new MAC (failover, VRRP)

### ARP Spoofing (Security)

An attacker sends fake ARP replies to associate **their** MAC with the gateway's IP. Other hosts then send their traffic to the attacker (MitM). Defenses: Dynamic ARP Inspection on switches, static ARP entries on critical hosts.

## How to Talk About It

For "explain what ARP does":
> "ARP translates IP addresses to MAC addresses on the local L2 segment. When a host needs to send a packet, it broadcasts an ARP Request asking 'who has this IP?' The owner replies with its MAC. The mapping is cached. ARP doesn't cross routers — for off-subnet destinations, a host ARPs for the default gateway instead."

For "what happens at L2 when I send to a different subnet":
> "Compare destination IP against my subnet. If outside, ARP for the default gateway's MAC. Encapsulate the IP packet in an Ethernet frame addressed to the gateway. The gateway strips the frame, looks up the destination IP in its routing table, builds a new frame for the next hop, and forwards."

## Common Interview Questions

**Q: "What's the difference between MAC address and IP address?"**
- MAC = hardware identifier, L2, doesn't cross routers, factory-assigned
- IP = logical address, L3, routable across networks, configurable

**Q: "What does a switch do when it receives a frame for an unknown MAC?"**
- Floods to all ports except the incoming one (unknown unicast flooding)
- Once the destination replies, switch learns the MAC and stops flooding

**Q: "What's the broadcast MAC?"**
- `FF:FF:FF:FF:FF:FF` — every host on the segment processes it

**Q: "Why is ARP a security concern?"**
- It's unauthenticated. ARP spoofing lets an attacker redirect traffic. Defenses include DAI (Dynamic ARP Inspection) and static ARP entries.

## What to Memorize

- MAC address format and the broadcast MAC
- ARP exchange (request broadcast → reply unicast)
- ARP is L2-only, doesn't cross routers
- VLANs use 802.1Q tags
- Switches learn by observing source MACs; flood on unknown destinations
