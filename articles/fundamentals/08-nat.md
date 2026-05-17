# NAT — Network Address Translation

NAT translates IP addresses (and often ports) as packets cross a boundary — typically the edge of a private network. NAT is what made IPv4's 4.3 billion addresses scale to billions of devices: hide many private addresses behind one public address.

It's everywhere: your home router does NAT; AWS NAT Gateway does NAT; carrier-grade NAT does NAT at ISP scale.

## The Problem NAT Solves

IPv4 has ~4.3 billion addresses. Today's internet has tens of billions of devices. The math doesn't work.

NAT solves this by letting many devices share a smaller pool of public addresses. Inside a private network, devices use RFC 1918 addresses (10/8, 172.16/12, 192.168/16). When they communicate with the public internet, NAT translates their private IP to a public IP (and back).

## How NAT Works (PAT, the Common Case)

Most NAT is actually **PAT (Port Address Translation)**, also called NAPT or "NAT overload" — many private IPs share **one** public IP, distinguished by port numbers.

Example: home network with three devices behind one public IP `203.0.113.5`.

```
Private side                      Public side
10.0.0.10:54321  -->  Router  -->  203.0.113.5:60001  --> server.com:443
10.0.0.20:54321  -->  Router  -->  203.0.113.5:60002  --> server.com:443
10.0.0.30:54321  -->  Router  -->  203.0.113.5:60003  --> server.com:443
```

The router maintains a **NAT translation table**:

| Internal IP:Port | External IP:Port | Destination |
|---|---|---|
| 10.0.0.10:54321 | 203.0.113.5:60001 | server.com:443 |
| 10.0.0.20:54321 | 203.0.113.5:60002 | server.com:443 |
| 10.0.0.30:54321 | 203.0.113.5:60003 | server.com:443 |

When the server replies to `203.0.113.5:60001`, the router looks it up and rewrites the destination to `10.0.0.10:54321`. The internal host doesn't even know NAT happened.

## NAT Types

| Type | Mapping | Use case |
|---|---|---|
| **Static NAT** | 1:1 fixed | Public-facing servers (one private IP always maps to one public IP) |
| **Dynamic NAT** | 1:1, pool-based | Less common; private IPs map to first available public IP |
| **PAT (NAPT)** | Many-to-one with ports | Default for home routers, most edge NAT |
| **Carrier-Grade NAT (CGN)** | NAT at ISP scale | ISPs running out of public IPs share them across customers |
| **NAT64** | IPv6 ↔ IPv4 | IPv6-only client reaching IPv4 server |

## NAT and Connection State

NAT is **stateful** — the router tracks every active translation. This means:

- **Outbound connections work fine** — host initiates, NAT entry created automatically
- **Inbound unsolicited traffic fails** — there's no NAT entry for it; router doesn't know which internal host to forward to. The internet effectively can't reach internal hosts. (This is sometimes called "NAT firewall" effect — security side benefit.)

To allow inbound connections to internal services, you need **port forwarding** (configured static NAT entry):
```
Public 203.0.113.5:80  →  Internal 10.0.0.50:80
```
Now traffic to your public IP on port 80 reaches your internal web server.

## NAT Traversal Problems

NAT breaks several things that "just work" without it:

1. **End-to-end addressability** — internal hosts have no globally reachable IP
2. **VoIP / SIP / WebRTC** — protocols that embed IPs/ports inside the application payload (NAT doesn't rewrite those)
3. **IPsec** — NAT changes the IP header, breaking IPsec's integrity checks. Solution: NAT-T (NAT Traversal, uses UDP encapsulation)
4. **Peer-to-peer** — both peers behind NAT can't directly connect

### NAT Traversal Techniques

Apps that need P2P or inbound connections use:
- **STUN** (Session Traversal Utilities for NAT) — discover your public IP/port
- **TURN** (Traversal Using Relays around NAT) — relay traffic through a public server (used when NAT punching fails)
- **ICE** (Interactive Connectivity Establishment) — combines STUN/TURN, picks best path
- **UPnP / NAT-PMP / PCP** — apps ask router to open ports automatically
- **Hole punching** — clever trick where both peers initiate outbound to each other simultaneously

WebRTC (video calls in your browser) uses ICE/STUN/TURN under the hood.

## "Hairpin NAT" (NAT Loopback)

You're behind NAT. You have a port forward (`public 203.0.113.5:80` → `internal 10.0.0.50:80`). What happens when you try to access your own server using the public address?

- Without hairpin NAT: packet hits the router, can't loop back, fails.
- With hairpin NAT: router translates the source AND destination, sends the packet back into the internal network correctly.

Many home routers don't support this — internal users have to use the internal IP directly.

## NAT64 and IPv6 Transition

For IPv6-only networks needing to reach IPv4 servers:
- **NAT64** translates IPv6 → IPv4 at a gateway
- **DNS64** synthesizes AAAA records pointing into a special IPv6 prefix for IPv4-only services

Mobile carriers heavily use this — many cellular networks are IPv6-only internally.

## Cloud NAT Examples

| Cloud product | What it does |
|---|---|
| **AWS NAT Gateway** | PAT for private subnet → internet egress |
| **AWS Elastic IP** | Static NAT — 1:1 IP allocation |
| **GCP Cloud NAT** | Like AWS NAT Gateway |
| **Azure NAT Gateway** | Same idea |

These are billed per-GB processed — at scale, NAT egress is a real cost line item.

## How to Talk About It

For "explain NAT":
> "NAT translates private IPs to public ones at a network boundary. Most NAT is actually PAT — many private IPs share one public IP, distinguished by port numbers. The router keeps a translation table mapping internal IP:port to external IP:port. Outbound connections create entries automatically; inbound traffic without a matching entry is dropped, which is why port forwarding is needed for inbound services."

For "why does NAT make P2P hard":
> "NAT only forwards inbound traffic that matches an existing outbound entry. Two peers behind NAT can't directly initiate to each other — there's no entry yet. Solutions are STUN (discover your public address), TURN (relay through a public server), and NAT hole punching (both peers simultaneously initiate)."

## Common Interview Questions

**Q: "What's the difference between NAT and PAT?"**
- NAT (static/dynamic) maps IPs 1:1
- PAT (NAPT, NAT overload) maps many private IPs to one public IP using port translation
- Most "NAT" in practice is actually PAT

**Q: "Why does port forwarding exist?"**
- NAT only allows inbound traffic matching an existing outbound entry. To accept unsolicited inbound (like hosting a web server), you configure a static NAT entry mapping public IP:port to internal IP:port.

**Q: "Does NAT provide security?"**
- Side-effect security (inbound blocked by default), but not a real firewall. Treat NAT's security as a side benefit, not a strategy.

**Q: "What's hairpin NAT?"**
- Lets internal hosts access internal services via the public IP (looping back through NAT). Useful for testing public-facing services from inside the network.

## What to Memorize

- NAT vs PAT (1:1 vs many-to-one with ports)
- The translation table (internal IP:port ↔ external IP:port)
- Outbound creates entries; inbound needs port forwarding
- RFC 1918 ranges (10/8, 172.16/12, 192.168/16)
- NAT breaks P2P; solutions are STUN/TURN/ICE
- NAT64 for IPv6 transition
- Cloud NAT products are billed per-GB
