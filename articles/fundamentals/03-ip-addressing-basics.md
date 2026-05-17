# IP Addressing Basics (IPv4)

IPv4 addressing is foundational. You'll be asked about subnetting, CIDR notation, private vs public addressing, and reserved ranges in any networking interview. This article covers what you need to know.

(IPv6 is covered separately in `routing/ipv6/`.)

## IPv4 Address Format

- **32 bits** total, written as four 8-bit "octets" separated by dots
- Each octet: 0-255 (because 2^8 = 256)
- Example: `192.168.1.100`

The full address space: ~4.3 billion unique addresses (2^32). Largely depleted, which is why IPv6 exists and why NAT is everywhere.

## CIDR Notation

CIDR (Classless Inter-Domain Routing) replaces the old class-based system (A/B/C). Format: `IP/prefix-length`.

The prefix length tells you how many bits are the **network** portion. The remaining bits are the **host** portion.

| CIDR | Subnet Mask | Network bits | Host bits | # Hosts |
|---|---|---|---|---|
| /8 | 255.0.0.0 | 8 | 24 | 16,777,214 |
| /16 | 255.255.0.0 | 16 | 16 | 65,534 |
| /24 | 255.255.255.0 | 24 | 8 | 254 |
| /25 | 255.255.255.128 | 25 | 7 | 126 |
| /26 | 255.255.255.192 | 26 | 6 | 62 |
| /27 | 255.255.255.224 | 27 | 5 | 30 |
| /28 | 255.255.255.240 | 28 | 4 | 14 |
| /29 | 255.255.255.248 | 29 | 3 | 6 |
| /30 | 255.255.255.252 | 30 | 2 | 2 |
| /31 | 255.255.255.254 | 31 | 1 | 0 (point-to-point) |
| /32 | 255.255.255.255 | 32 | 0 | 1 (host route) |

**Host count formula:** `2^(host_bits) - 2` (subtract network address + broadcast address). Exception: `/31` is used for point-to-point links (RFC 3021), no network/broadcast subtraction.

## Subnetting Mental Model

For `192.168.1.0/24`:
- Network address: `192.168.1.0` (host bits all 0)
- Broadcast address: `192.168.1.255` (host bits all 1)
- Usable host range: `192.168.1.1` to `192.168.1.254`
- 254 usable hosts

If you split `/24` into two `/25`s:
- `192.168.1.0/25` → range `192.168.1.0` to `192.168.1.127` (126 usable)
- `192.168.1.128/25` → range `192.168.1.128` to `192.168.1.255` (126 usable)

## Private vs Public Addresses (RFC 1918)

Private addresses are non-routable on the public internet. Used for internal networks, translated via NAT when going to the internet.

| Range | CIDR | Common use |
|---|---|---|
| 10.0.0.0/8 | `10.0.0.0` – `10.255.255.255` | Enterprise networks |
| 172.16.0.0/12 | `172.16.0.0` – `172.31.255.255` | Less common |
| 192.168.0.0/16 | `192.168.0.0` – `192.168.255.255` | Home routers |

Everything else is **public** — routable on the internet, assigned by IANA/regional registries.

## Special / Reserved Addresses

| Address | Purpose |
|---|---|
| `0.0.0.0` | "This network" / unspecified |
| `127.0.0.0/8` | Loopback (your own machine) |
| `127.0.0.1` | The classic loopback IP ("localhost") |
| `169.254.0.0/16` | Link-local (APIPA — when DHCP fails) |
| `224.0.0.0/4` | Multicast |
| `255.255.255.255` | Limited broadcast |

## How to Subnet in Your Head (Interview-Friendly)

Memorize these powers of 2:

| Bits | Hosts (2^N) |
|---|---|
| 1 | 2 |
| 2 | 4 |
| 3 | 8 |
| 4 | 16 |
| 5 | 32 |
| 6 | 64 |
| 7 | 128 |
| 8 | 256 |

**Quick CIDR math:**
- `/24` = 256 addresses in last octet
- `/25` = 128 (split last octet in half)
- `/26` = 64
- `/27` = 32
- `/28` = 16
- `/29` = 8
- `/30` = 4

So `/27` has 32 addresses = 30 usable hosts. Easy to derive.

## Routing vs Subnetting

- **Subnetting** = dividing a network into smaller networks (a /24 → two /25s)
- **Routing** = deciding where to send a packet based on destination IP

A router has a routing table. For each entry, it has a **longest-prefix match** rule — the most specific subnet wins.

Example:
```
10.0.0.0/8     via R1
10.0.5.0/24    via R2
```
A packet for `10.0.5.42` matches both entries. `/24` is more specific than `/8`, so R2 wins.

## How to Talk About It

For "explain subnetting":
> "Subnetting splits a network into smaller pieces by extending the prefix length. A /24 has 256 addresses; splitting it into two /25s gives me two networks of 128 each. Useful for isolating broadcast domains, applying different policies, or fitting addresses into a routing table efficiently."

For "what's the difference between a /24 and a /16":
> "/24 has 8 host bits = 256 addresses, /16 has 16 host bits = 65,536. So /16 is 256 times larger. CIDR notation shows the network/host split: the number after the slash is how many bits identify the network."

## Common Interview Questions

**Q: "How many usable hosts in a /28?"**
- /28 has 4 host bits → 16 addresses, minus network and broadcast → **14 usable**

**Q: "What's the network address of 192.168.5.100/24?"**
- /24 means last octet is host → network is `192.168.5.0`

**Q: "What's APIPA / 169.254 used for?"**
- Link-local addressing when DHCP fails. Hosts auto-assign themselves a 169.254.x.y address so they can still talk on the local segment.

**Q: "What's 127.0.0.1?"**
- Loopback — your own machine. Useful for local testing without sending packets on a real network.

## What to Memorize

- IPv4 = 32 bits, 4 octets, each 0-255
- CIDR notation (/N = N network bits)
- Powers of 2 up to 8 (for fast subnetting)
- Private ranges (10/8, 172.16/12, 192.168/16)
- Loopback (127.0.0.1), link-local (169.254/16)
- Longest-prefix match for routing
