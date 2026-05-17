# IP Packet Structure (IPv4 and IPv6)

The IP packet sits inside the Ethernet payload (or any L2 frame) and carries the source/destination IP addresses plus enough metadata for routers to forward correctly.

## IPv4 Header (Fixed 20 Bytes, Up to 60 with Options)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |    DSCP   |ECN|         Total Length          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|     Fragment Offset     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   TTL         |   Protocol    |       Header Checksum         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source IP Address                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination IP Address                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Options (if any)                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Field Breakdown

| Field | Bits | Purpose |
|---|---|---|
| **Version** | 4 | Always 4 for IPv4 |
| **IHL** (Header Length) | 4 | Header size in 32-bit words (min 5 = 20 bytes) |
| **DSCP** (Differentiated Services) | 6 | QoS class marking (EF, AF31, etc.) |
| **ECN** | 2 | Explicit Congestion Notification |
| **Total Length** | 16 | Whole packet length (header + data) |
| **Identification** | 16 | Used for fragmentation reassembly |
| **Flags** | 3 | DF (Don't Fragment), MF (More Fragments) |
| **Fragment Offset** | 13 | Where this fragment fits in the whole packet |
| **TTL** (Time To Live) | 8 | Decremented at each hop; 0 = drop |
| **Protocol** | 8 | What's in the payload (TCP=6, UDP=17, ICMP=1) |
| **Header Checksum** | 16 | Header integrity check |
| **Source IP** | 32 | Sender's IP |
| **Destination IP** | 32 | Receiver's IP |
| **Options** | variable | Rarely used (timestamps, record route, etc.) |

### Key Field Details

**Protocol field** — identifies the next-header:
- 1 = ICMP
- 6 = TCP
- 17 = UDP
- 47 = GRE
- 50 = ESP (IPsec)
- 89 = OSPF

**TTL** — every router decrements it by 1. When it hits 0, the packet is dropped and an ICMP Time Exceeded is sent. This is how `traceroute` works — it sends packets with increasing TTL to discover each hop.

**DSCP** — 6 bits for QoS classification. Common values:
- 0 (default / best effort)
- 46 (EF — Expedited Forwarding, voice)
- 34 (AF41 — Assured Forwarding, video)
- 10 (AF11 — Assured Forwarding, bulk data)

## IPv6 Header (Fixed 40 Bytes)

IPv6 simplifies dramatically — no fragmentation in header, no checksum, no options (uses extension headers instead).

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version| Traffic Class |           Flow Label                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Payload Length        |  Next Header  |   Hop Limit   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                                                               +
|                         Source Address (128 bits)             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Destination Address (128 bits)           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Field | Bits | Purpose |
|---|---|---|
| **Version** | 4 | Always 6 |
| **Traffic Class** | 8 | DSCP + ECN (like IPv4) |
| **Flow Label** | 20 | Identifies a flow (for QoS / ECMP hashing) |
| **Payload Length** | 16 | Length of data after the header |
| **Next Header** | 8 | Like IPv4's Protocol field — 6 (TCP), 17 (UDP), 58 (ICMPv6) |
| **Hop Limit** | 8 | Same as IPv4 TTL |
| **Source IPv6** | 128 | 16 bytes |
| **Destination IPv6** | 128 | 16 bytes |

## What IPv6 Removed (and Why)

| IPv4 had | IPv6 removed | Reason |
|---|---|---|
| Header checksum | Removed | L2 (Ethernet) and L4 (TCP/UDP) already checksum |
| Fragmentation in header | Moved to extension header | Routers don't fragment; only source can fragment |
| Options in header | Replaced with extension headers | Variable-length options slowed router processing |
| IHL field | Removed | Header is always 40 bytes |

The result: a fixed-length IPv6 header, faster to process at high speeds. Same idea, simpler.

## Fragmentation

When a packet is larger than the MTU on a link, IPv4 fragments it (router or sender). Fragments share the same Identification, have Fragment Offset showing position, and MF flag set on all but the last.

**IPv6 doesn't fragment at routers** — too slow at scale. If the packet is too big, the router sends ICMPv6 "Packet Too Big" back to the source. Source then uses **Path MTU Discovery** to size future packets correctly.

## TTL / Hop Limit and Traceroute

`traceroute` sends UDP/ICMP packets with TTL=1, 2, 3, ... Each TTL expires at the next hop, generating an ICMP Time Exceeded reply. By reading the source of those replies, traceroute discovers the path hop-by-hop.

## How to Talk About It

For "what's in an IP packet":
> "IPv4: 20-byte header with version, header length, DSCP/ECN for QoS, total length, fragmentation fields, TTL, protocol (TCP/UDP/ICMP), header checksum, source and destination IPs. IPv6 simplifies — fixed 40-byte header, no fragmentation, no header checksum, options moved to extension headers."

## What to Memorize

- IPv4 header is **20 bytes** minimum (40 with options)
- IPv6 header is **always 40 bytes**
- Source and destination IPs are the key fields
- **Protocol** field (IPv4) / **Next Header** (IPv6) identifies the L4 payload: 6=TCP, 17=UDP, 1=ICMP
- **TTL / Hop Limit** decremented per hop; 0 = drop + ICMP Time Exceeded
- **DSCP** for QoS marking
- IPv6 doesn't fragment in transit — uses Path MTU Discovery instead
