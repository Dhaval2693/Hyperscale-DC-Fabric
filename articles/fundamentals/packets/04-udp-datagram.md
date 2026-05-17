# UDP Datagram Structure

UDP's claim to fame is simplicity. The header is 8 bytes — that's it. Source port, destination port, length, checksum. No connection state, no sequence numbers, no flow control. Just delivery.

## UDP Header (8 Bytes — That's All)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|             Length            |           Checksum            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Data                                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| Field | Bits | Purpose |
|---|---|---|
| **Source Port** | 16 | Sender's port |
| **Destination Port** | 16 | Receiver's port |
| **Length** | 16 | Header (8) + data length |
| **Checksum** | 16 | Integrity check (optional in IPv4, mandatory in IPv6) |

## What's NOT in the Header (And Why It Matters)

Compare to TCP. UDP has no:
- Sequence number — no ordering guarantee
- Acknowledgment number — no acknowledgment, period
- Window size — no flow control
- Flags — no connection state to track
- Options — no MSS, no SACK, no timestamps

Every "missing" field is intentional. The app handles those concerns or doesn't need them.

## Why This Matters

**The 8-byte header is 1/3 the size of TCP's 20-byte minimum.** For small payloads (a 50-byte DNS query), the overhead difference is significant — TCP adds 40%, UDP adds 16%.

For high-volume small messages, that overhead compounds. DNS at scale, gaming server tick rates, VoIP packets — UDP's compactness matters.

## Checksum

The 16-bit checksum covers:
- A "pseudo-header" with source IP, dest IP, protocol (17), and UDP length
- The UDP header
- The UDP data

In IPv4, the checksum is **optional** — a value of 0 means "didn't compute it." Most modern stacks always compute it. In IPv6 it's **mandatory**.

## What UDP Doesn't Tell You

If you receive a UDP datagram, you know:
- The source IP (from the IP header)
- The source port
- The data

You don't know:
- Whether the sender knows you received it
- Whether the sender will send more
- The order in which packets were sent
- Whether anything was lost

If you need any of those, your app provides them (or you're using TCP).

## Common Apps Built on UDP

| App | Pattern |
|---|---|
| DNS | Small query, small response, retry at app level |
| DHCP | Pre-IP bootstrap; broadcast required (TCP can't broadcast) |
| VoIP (RTP) | Real-time audio; late = useless |
| Video streaming | Frame-based; late = drop |
| Online gaming | State updates; latest only matters |
| NTP | Tiny time query, low overhead |
| SNMP | Management queries; mostly fire-and-forget |
| QUIC (HTTP/3) | Uses UDP for transport, adds reliability at app layer |

## QUIC — The Modern Twist

QUIC (used by HTTP/3) runs over UDP but adds:
- Connection state
- Reliability
- Stream multiplexing
- Encryption (TLS 1.3 built in)

Why UDP? Because the app layer can iterate faster than kernel TCP can. New congestion control, new features — all deployable as user-space updates instead of waiting for OS upgrades.

QUIC has fundamentally changed how new protocols are designed: build on UDP for evolvability, add features in user space.

## Reading a Capture

In Wireshark, a UDP datagram looks trivially short:

```
User Datagram Protocol
    Source Port: 53
    Destination Port: 51234
    Length: 78
    Checksum: 0x... [validation disabled]
```

Then immediately you see the DNS payload, with no flags, sequence numbers, or windowing to interpret.

## How to Talk About It

For "what's in a UDP header":
> "Four fields, 8 bytes total: source port, destination port, length, checksum. That's it. No sequence numbers, no flags, no flow control. The tradeoff is no guarantees — packets can be lost, duplicated, or arrive out of order, and UDP doesn't care. The application handles whatever it needs."

For "why does DNS use UDP if it's unreliable":
> "DNS queries are small, mostly under 512 bytes. TCP setup would be 3-way handshake plus FIN exchange — way more overhead than the query itself. UDP just sends the query directly. If a response doesn't come back in time, the DNS client retries. Faster overall, even with retries."

## What to Memorize

- UDP header is **8 bytes**: src port (2), dest port (2), length (2), checksum (2)
- No sequence numbers, no flags, no flow control — by design
- Smaller header than TCP (8 vs 20) → less overhead per packet
- Checksum optional in IPv4, mandatory in IPv6
- QUIC runs over UDP to escape TCP's kernel-update cycle
