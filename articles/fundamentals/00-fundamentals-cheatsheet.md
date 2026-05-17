# Networking Fundamentals Cheat Sheet

Single-page reference for the core networking concepts every engineer should know cold. Read this before any technical interview.

## The Layered Model

| OSI | TCP/IP | Protocols | Purpose |
|---|---|---|---|
| 7. Application | Application | HTTP, DNS, DHCP, SSH | User-facing apps |
| 6. Presentation | Application | TLS, encoding | Format/encrypt |
| 5. Session | Application | NetBIOS | Session mgmt |
| 4. Transport | Transport | TCP, UDP | End-to-end delivery |
| 3. Network | Internet | IP, ICMP | Routable addressing |
| 2. Data Link | Link | Ethernet, ARP | Hop-by-hop on a link |
| 1. Physical | Link | Cables, optics | Bits on the wire |

**Memory tip:** "Please Do Not Throw Sausage Pizza Away" (Physical → Application).

## The Daily Protocols

| Protocol | Port | Layer | Purpose |
|---|---|---|---|
| DNS | 53 (UDP/TCP) | App | Name → IP |
| DHCP | 67/68 (UDP) | App | Auto IP assignment |
| HTTP | 80 (TCP) | App | Web (unencrypted) |
| HTTPS | 443 (TCP) | App | Web (TLS) |
| SSH | 22 (TCP) | App | Remote shell |
| TCP | — | Transport | Reliable, ordered |
| UDP | — | Transport | Fast, connectionless |
| IP | — | Network | Routable addressing |
| ARP | — | Link | IP → MAC |
| Ethernet | — | Link | Frame format |

## TCP vs UDP Quick Compare

| Feature | TCP | UDP |
|---|---|---|
| Connection | Yes (3-way handshake) | No |
| Reliability | Guaranteed | Best-effort |
| Ordering | In-order | No guarantee |
| Speed | Slower (overhead) | Faster |
| Header size | 20+ bytes | 8 bytes |
| Use cases | HTTP, SSH, email | DNS, VoIP, streaming, gaming |

## DHCP: DORA

1. **Discover** — client broadcasts "anybody home?"
2. **Offer** — server replies "use this IP"
3. **Request** — client says "I'll take it"
4. **Acknowledge** — server confirms

## DNS Resolution (Recursive)

1. Browser checks its cache → OS cache → hosts file
2. Query local resolver (DHCP-assigned or 8.8.8.8)
3. Resolver queries root (`.`) → TLD (`.com`) → authoritative (`example.com`)
4. Returns IP, cached with TTL at every step

## ARP

Resolves **IP → MAC** for next-hop delivery on the local L2 segment.
- Client broadcasts: "Who has 10.0.0.1? Tell 10.0.0.5"
- Owner replies: "10.0.0.1 is at MAC AA:BB:CC:DD:EE:FF"
- Cached for ~minutes

## NAT Types

| Type | Purpose |
|---|---|
| Static NAT | 1:1 fixed mapping |
| Dynamic NAT | Pool of public IPs |
| PAT (NAPT) | Many private IPs share one public via port translation (home router default) |
| NAT64 | IPv6 ↔ IPv4 translation |

## TCP Three-Way Handshake

```
Client                  Server
  |---- SYN ---------->|
  |<--- SYN-ACK -------|
  |---- ACK ---------->|
  |   [data flows]     |
```

## TCP Connection Close (Four-Way)

```
Client                  Server
  |---- FIN ---------->|
  |<--- ACK -----------|
  |<--- FIN -----------|
  |---- ACK ---------->|
```

## What Happens When You Type a URL

1. Browser cache check
2. **DNS lookup** (cache → resolver → root → TLD → authoritative)
3. **ARP** for default gateway's MAC (if not cached)
4. **TCP handshake** to destination IP:443
5. **TLS handshake** (for HTTPS)
6. **HTTP request** (GET /)
7. Server response + render

See `09-when-you-type-a-url.md` for the deep version.

## What to Memorize

- Port numbers: 22 SSH, 53 DNS, 67/68 DHCP, 80 HTTP, 443 HTTPS
- TCP vs UDP tradeoff
- DHCP DORA process
- TCP three-way handshake (SYN, SYN-ACK, ACK)
- ARP scope: same L2 segment only
- The "type a URL" sequence end-to-end

If you know everything on this page, you've covered ~80% of fundamental networking interview questions.
