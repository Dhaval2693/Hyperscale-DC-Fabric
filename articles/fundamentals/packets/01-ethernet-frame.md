# Ethernet Frame Structure

The Ethernet frame is the L2 envelope that carries every packet on a LAN. Knowing the fields helps you read packet captures (Wireshark) and answer "what's in the header" questions.

## Standard Ethernet II Frame

```
+---------+---------+----------+----------+-------------+-----+
|Preamble |  SFD    | Dest MAC | Src MAC  | EtherType   | Pld | FCS
| 7 bytes | 1 byte  | 6 bytes  | 6 bytes  | 2 bytes     | ... | 4 bytes
+---------+---------+----------+----------+-------------+-----+
```

| Field | Size | Purpose |
|---|---|---|
| **Preamble** | 7 bytes | Sync pattern (10101010 ×7) for receiver clock |
| **SFD** (Start Frame Delimiter) | 1 byte | Marks frame start (10101011) |
| **Destination MAC** | 6 bytes | Receiver's hardware address |
| **Source MAC** | 6 bytes | Sender's hardware address |
| **EtherType** | 2 bytes | What protocol is in the payload |
| **Payload** | 46-1500 bytes | The actual data (IP packet, ARP, etc.) |
| **FCS** (Frame Check Sequence) | 4 bytes | CRC32 checksum for integrity |

Preamble + SFD are stripped by the NIC and usually not shown in captures.

## EtherType — What's Inside?

The 2-byte EtherType tells the receiver what's in the payload:

| EtherType (hex) | Protocol |
|---|---|
| 0x0800 | IPv4 |
| 0x0806 | ARP |
| 0x86DD | IPv6 |
| 0x8100 | 802.1Q VLAN tag |
| 0x8847 | MPLS unicast |
| 0x8848 | MPLS multicast |
| 0x88CC | LLDP (Link Layer Discovery) |

When you see EtherType 0x8100, the next 4 bytes are a VLAN tag, then the real EtherType.

## 802.1Q Tagged Frame (VLAN)

When VLAN tagging is in use, 4 bytes are inserted between Source MAC and EtherType:

```
| Dest MAC | Src MAC | TPID  | TCI   | EtherType | Payload | FCS
                     | 0x8100|       |
                       (2)    (2)
```

The TCI (Tag Control Information) breaks down as:
- 3 bits **PCP** (Priority Code Point) — QoS priority 0-7
- 1 bit **DEI** (Drop Eligible Indicator)
- 12 bits **VID** (VLAN ID) — 1-4094 usable

So 4094 usable VLANs per L2 domain (12-bit field, 0 and 4095 reserved).

## Frame Size Constraints

- **Minimum:** 64 bytes (including header + FCS, excluding preamble) — required for collision detection on legacy CSMA/CD; smaller frames are padded
- **Maximum (standard):** 1518 bytes (1500-byte payload + 18-byte overhead)
- **Jumbo frames:** up to 9000+ bytes payload — must be supported end-to-end; common in data centers for throughput

The 1500-byte MTU is the historical default. Storage / DC fabrics often use 9000-byte jumbos to reduce per-packet overhead.

## How to Read a Capture

In Wireshark, an Ethernet frame might show:

```
Ethernet II, Src: 00:11:22:33:44:55, Dst: aa:bb:cc:dd:ee:ff
    Type: IPv4 (0x0800)
```

Then the next section shows the IPv4 header inside the payload.

## What to Memorize

- Dest MAC + Src MAC are first (6 bytes each)
- EtherType identifies the L3 protocol (0x0800 IPv4, 0x86DD IPv6, 0x0806 ARP)
- VLAN tag is 4 bytes inserted between source MAC and EtherType (TPID 0x8100)
- Standard payload: 46-1500 bytes; jumbo: up to ~9000
- FCS at the end is a CRC32 for integrity
