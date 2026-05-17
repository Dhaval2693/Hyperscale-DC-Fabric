# ARP Packet Structure

ARP is the simplest protocol in this folder — a small, fixed-format packet whose only job is to ask "who has this IP?" and get an answer.

## ARP Sits at Layer 2

ARP packets aren't IP packets. They're carried directly in Ethernet frames with EtherType `0x0806`. ARP exists in the same layer as Ethernet, not above it.

## ARP Packet Format (28 Bytes for IPv4/Ethernet)

```
+----------------------+
| Hardware Type    (2) | 0x0001 for Ethernet
+----------------------+
| Protocol Type    (2) | 0x0800 for IPv4
+----------------------+
| HW Address Len   (1) | 6 for MAC
+----------------------+
| Proto Address Len (1)| 4 for IPv4
+----------------------+
| Operation        (2) | 1 = Request, 2 = Reply
+----------------------+
| Sender Hardware Addr | 6 bytes — sender's MAC
+----------------------+
| Sender Protocol Addr | 4 bytes — sender's IP
+----------------------+
| Target Hardware Addr | 6 bytes — target's MAC (00... in request)
+----------------------+
| Target Protocol Addr | 4 bytes — target's IP
+----------------------+
```

### Field Breakdown

| Field | Bytes | Purpose |
|---|---|---|
| **Hardware Type** | 2 | Link-layer type (Ethernet = 1) |
| **Protocol Type** | 2 | L3 protocol being resolved (IPv4 = 0x0800) |
| **HW Address Length** | 1 | Size of hardware address (MAC = 6) |
| **Protocol Address Length** | 1 | Size of protocol address (IPv4 = 4) |
| **Operation** | 2 | 1 = ARP Request, 2 = ARP Reply |
| **Sender Hardware Address** | 6 | MAC of sender |
| **Sender Protocol Address** | 4 | IP of sender |
| **Target Hardware Address** | 6 | MAC of target (zeros in a Request) |
| **Target Protocol Address** | 4 | IP of target |

ARP is general-purpose by design — the hardware/protocol type fields let it resolve any L3 address to any L2 address. In practice it's almost always IPv4 ↔ Ethernet MAC.

## What an ARP Request Looks Like

```
EtherType: 0x0806 (ARP)
ARP:
  Operation: 1 (Request)
  Sender MAC:  AA:BB:CC:DD:EE:01
  Sender IP:   10.0.0.5
  Target MAC:  00:00:00:00:00:00     ← unknown, that's why we're asking
  Target IP:   10.0.0.1               ← who has this IP?
```

The Ethernet frame carrying this has destination MAC `FF:FF:FF:FF:FF:FF` (broadcast) because we don't yet know who to send it to.

## What an ARP Reply Looks Like

```
EtherType: 0x0806 (ARP)
ARP:
  Operation: 2 (Reply)
  Sender MAC:  AA:BB:CC:DD:EE:02      ← the answer
  Sender IP:   10.0.0.1               ← I am the one you asked about
  Target MAC:  AA:BB:CC:DD:EE:01      ← copied from the request
  Target IP:   10.0.0.5
```

The Ethernet frame carrying the reply is **unicast** back to the requester's MAC.

## Special ARP Variants

### Gratuitous ARP

A host announces its own IP→MAC unsolicited. Used for:
- **Duplicate IP detection** — "Does anyone else claim this IP? If yes, reply (and now I know there's a conflict)"
- **Cache update broadcasts** — "My IP just moved to this MAC; update your caches" (used by VRRP/HSRP failover, VM migration)

Format: ARP Request where Sender IP = Target IP.

### ARP Probe

Like gratuitous ARP but with Sender IP = 0.0.0.0. Used before claiming an IP — "Is anyone using this?"

### Proxy ARP

A router answers ARP requests on behalf of hosts on another subnet. Lets two subnets behave like one L2 segment. Generally discouraged — confuses topology and breaks things.

### Reverse ARP (RARP)

Old protocol where a host knew its MAC but not its IP, asked the network. Replaced by BOOTP, then DHCP.

## How an Operating System Uses ARP

When a host wants to send an IP packet:

1. Look up destination IP in routing table → determine "is it on a local subnet, or do I need the gateway?"
2. For local: look up destination IP in ARP cache → got MAC → build Ethernet frame
3. For off-subnet: look up GATEWAY IP in ARP cache → got MAC → build Ethernet frame to gateway
4. If ARP cache miss, send ARP Request, wait briefly, retry
5. If still no response, packet is dropped (or queued)

## ARP Cache

OS keeps a table:

```
$ arp -a
gateway (192.168.1.1) at aa:bb:cc:dd:ee:ff on en0
printer (192.168.1.50) at 11:22:33:44:55:66 on en0
```

- Entries time out after a few minutes (varies by OS)
- Stale entries are refreshed lazily (next time they're needed)
- Can be static (manually configured, never expires)

## ARP Security Concerns

ARP is **unauthenticated**. Any host on the segment can claim any IP. This makes ARP a common attack vector:

- **ARP spoofing / cache poisoning** — attacker sends fake replies, intercepts traffic (MitM)
- **MAC flooding** — overflow the switch's MAC table, force broadcast mode

Defenses:
- **Dynamic ARP Inspection (DAI)** on switches — verifies ARP packets against the DHCP snooping table
- **Static ARP entries** for critical hosts (gateway)
- **Port security** — limit MACs per port

## IPv6: ARP Replaced by NDP

In IPv6, ARP doesn't exist. **Neighbor Discovery Protocol (NDP)** does the same job using ICMPv6 messages:
- Neighbor Solicitation = ARP Request equivalent
- Neighbor Advertisement = ARP Reply equivalent

NDP is more secure (can be authenticated with SEND) and built into ICMPv6 instead of being a separate protocol.

## How to Read in Wireshark

```
Address Resolution Protocol (request)
    Hardware type: Ethernet (1)
    Protocol type: IPv4 (0x0800)
    Hardware size: 6
    Protocol size: 4
    Opcode: request (1)
    Sender MAC address: AA:BB:CC:DD:EE:01
    Sender IP address: 10.0.0.5
    Target MAC address: 00:00:00:00:00:00
    Target IP address: 10.0.0.1
```

## What to Memorize

- ARP packet is 28 bytes (for IPv4/Ethernet)
- Carried in Ethernet with EtherType **0x0806**
- Two operations: Request (1) and Reply (2)
- Request is **broadcast**; Reply is **unicast**
- Target MAC is zeros in a Request
- Gratuitous ARP for duplicate detection and failover announcements
- IPv6 replaces ARP with NDP (Neighbor Discovery)
- ARP is unauthenticated — defenses include DAI, static entries, port security
