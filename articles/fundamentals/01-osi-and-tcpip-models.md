# OSI Model and TCP/IP Model

The OSI and TCP/IP models are two different ways of organizing how network communication works in layers. OSI is the conceptual textbook; TCP/IP is what actually runs on the internet.

Knowing both — and how they map to each other — is fundamental interview material.

## The OSI Model (7 Layers)

| Layer | Name | What It Does | Examples |
|---|---|---|---|
| 7 | Application | Interface to user apps | HTTP, DNS, SMTP, SSH |
| 6 | Presentation | Format, encrypt, encode | TLS/SSL, JPEG, MIME |
| 5 | Session | Manage sessions / dialogues | NetBIOS, RPC |
| 4 | Transport | End-to-end delivery | TCP, UDP |
| 3 | Network | Routing across networks | IP, ICMP, OSPF, BGP |
| 2 | Data Link | Hop-by-hop on a single link | Ethernet, ARP, MAC, PPP |
| 1 | Physical | Electrical/optical signals | Cables, fiber, hubs |

**Memory tricks:**
- Top → bottom: "All People Seem To Need Data Processing"
- Bottom → top: "Please Do Not Throw Sausage Pizza Away"

## The TCP/IP Model (4 Layers)

TCP/IP was designed by the people who actually built the internet. It collapses some OSI layers because in practice they're not cleanly separable.

| Layer | OSI Equivalent | What's in it |
|---|---|---|
| Application | 5, 6, 7 | HTTP, DNS, DHCP, SSH, TLS |
| Transport | 4 | TCP, UDP |
| Internet | 3 | IP, ICMP |
| Link | 1, 2 | Ethernet, ARP |

## OSI vs TCP/IP: Which to Use?

| | OSI | TCP/IP |
|---|---|---|
| Origin | Standards committee (1980s) | Actual deployed protocol stack |
| Used for | Teaching, troubleshooting language | What actually runs |
| Layer count | 7 | 4 |

**In practice:** people TALK in OSI ("that's a layer 7 problem") but the actual code runs TCP/IP. Engineers fluent in both.

## How Data Moves Through the Layers

When you send data, each layer **adds a header** (encapsulation). When it's received, each layer **strips its header** (decapsulation).

```
Sending (top → bottom):
  Application data
  → + TCP/UDP header (becomes "segment" or "datagram")
  → + IP header (becomes "packet")
  → + Ethernet header + trailer (becomes "frame")
  → bits on the wire

Receiving (bottom → top):
  Frame → strip Ethernet header
  Packet → strip IP header
  Segment → strip TCP header
  → Application reads the data
```

Each layer is **only responsible for its own job**. TCP doesn't care how IP routes packets; IP doesn't care how Ethernet physically delivers frames.

## Why Layering Matters

1. **Abstraction.** App developers don't think about cable types. Network engineers don't think about HTML.
2. **Substitution.** You can swap an Ethernet network for Wi-Fi without changing HTTP.
3. **Debugging.** Problems localize to a layer ("DNS works but TCP fails" → layer 4 issue).
4. **Vendor interop.** Standards at each layer mean Cisco and Juniper devices can talk.

## Where Common Tools Live

| Tool | Layer | What it shows |
|---|---|---|
| `curl`, browser | 7 (Application) | HTTP request/response |
| `nslookup`, `dig` | 7 (Application) | DNS resolution |
| `telnet host:port` | 4-7 | TCP connection test + app data |
| `nc` (netcat) | 4 | Raw TCP/UDP |
| `tcpdump`, `wireshark` | 1-7 | Packet capture, decoded |
| `traceroute`, `mtr` | 3 (Network) | Hop-by-hop IP path |
| `ping` | 3 (Network) | ICMP echo |
| `arp -a` | 2 (Data Link) | IP→MAC mappings |

## Common Interview Questions

**Q: "Walk me through the OSI model."**
Recite the 7 layers, what each does, give one protocol example for each. Use the mnemonic.

**Q: "What's the difference between OSI and TCP/IP?"**
> "OSI has 7 layers and is the conceptual model used for teaching and troubleshooting. TCP/IP has 4 layers and is what actually runs the internet. The biggest difference: OSI separates session, presentation, and application; TCP/IP merges them. Engineers TALK in OSI ('this is a layer 7 issue') but the stack we use is TCP/IP."

**Q: "What layer is BGP at?"**
This is a trick question. BGP runs **over TCP** (port 179), so it lives at layer 7 (Application) by strict OSI mapping. But it ROUTES traffic, which is a layer 3 function. Engineers casually call it "L3" because of what it does, but technically it's an L7 application.

**Q: "Where does TLS fit?"**
OSI: layer 6 (Presentation). TCP/IP: Application layer. TLS sits between TCP and the application, encrypting the application's data.

## What to Memorize

- The 7 OSI layers and their order
- One protocol per layer
- The mnemonic
- The 4 TCP/IP layers and how they map
- Tools at each layer (for "how would you debug X" questions)
