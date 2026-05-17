# TCP vs UDP

TCP and UDP are the two transport-layer protocols on the internet. They sit on top of IP and provide application-level data delivery — but with very different guarantees.

If you can answer "when do you use UDP vs TCP and why?" cleanly, you've handled the most common transport-layer interview question.

## The Core Comparison

| Feature | TCP | UDP |
|---|---|---|
| **Connection** | Connection-oriented (3-way handshake) | Connectionless |
| **Reliability** | Guaranteed delivery (retransmits) | Best-effort, no retransmit |
| **Ordering** | In-order delivery | No ordering guarantee |
| **Flow control** | Yes (sliding window) | No |
| **Congestion control** | Yes (multiple algorithms) | No |
| **Header size** | 20+ bytes | 8 bytes |
| **Speed** | Slower (overhead) | Faster (no overhead) |
| **Stream-oriented?** | Yes (byte stream) | No (discrete datagrams) |
| **Multicast/broadcast?** | Unicast only | Yes |

## When to Use TCP

TCP is for things where **correctness > speed**:
- **HTTP / HTTPS** — web traffic; can't have missing bytes
- **SSH** — remote shell; missing characters would corrupt sessions
- **Email (SMTP, IMAP, POP)** — full messages required
- **File transfer (FTP, SCP, rsync)** — every byte matters
- **Database queries (most)** — accuracy matters
- **BGP** — control plane needs reliability

**The pattern:** if losing data is worse than waiting for retransmits, use TCP.

## When to Use UDP

UDP is for things where **speed > correctness** or where the app handles its own reliability:
- **DNS** — small query/response; faster to retry than maintain a connection
- **VoIP / video calls** — late audio is worse than slightly choppy audio
- **Live streaming** — same; missed frame is better than buffering
- **Online gaming** — old positions are useless; need latest data
- **DHCP** — pre-IP bootstrap, no connection state possible
- **SNMP** — small management queries
- **NTP** — small time queries
- **Multicast / broadcast** — only UDP supports these

**The pattern:** if late data is worse than missing data, use UDP.

## TCP Header (Key Fields)

| Field | Bits | Purpose |
|---|---|---|
| Source port | 16 | Sender's port |
| Destination port | 16 | Receiver's port |
| Sequence number | 32 | Byte position in the stream |
| Acknowledgment number | 32 | Next expected byte from peer |
| Data offset | 4 | Header length in 32-bit words |
| Flags (URG, ACK, PSH, RST, SYN, FIN) | 6 | Control bits |
| Window size | 16 | How much receiver can accept |
| Checksum | 16 | Integrity check |
| Options | variable | MSS, window scaling, SACK, etc. |

Minimum 20 bytes, can be more with options.

## UDP Header (4 Fields)

| Field | Bits | Purpose |
|---|---|---|
| Source port | 16 | |
| Destination port | 16 | |
| Length | 16 | Header + payload |
| Checksum | 16 | Integrity check (optional in IPv4) |

8 bytes total. That's it.

## Why the Size Difference Matters

TCP's 20+ byte header carries all the state for reliability (sequence, ack, flags, window). UDP's 8-byte header has just enough to deliver a datagram to the right port.

For high-volume small messages (DNS queries, gaming state updates), UDP's smaller header makes a real difference in bandwidth and CPU.

## Common Gotchas

1. **"UDP has no flow control" is true, but apps often add it.** QUIC (used by HTTP/3) runs over UDP and adds reliability + flow control at the application layer.

2. **TCP isn't always slower than UDP.** For bulk transfers on clean links, TCP can saturate the link. UDP is faster only because it skips guarantees, which matters for small messages or constrained CPUs.

3. **Connection != session.** TCP is "connection-oriented" but that doesn't mean a persistent connection in the app sense. A TCP connection lives only as long as the sender keeps it open.

4. **UDP is not "unreliable" — it's "best-effort."** Packets usually arrive. UDP just doesn't promise they will, and won't retransmit if they don't.

## How to Talk About It

For "TCP vs UDP — when do you use each?":
> "TCP for correctness — HTTP, SSH, file transfer, anything where missing or out-of-order data breaks the app. UDP for speed or for things that can't use connection state — DNS, VoIP, gaming, DHCP. The trade is reliability vs latency overhead: TCP gives you guarantees at the cost of handshake + retransmits + flow control. UDP gives you a fire-and-forget packet at the cost of those guarantees being your app's problem."

For "what's the TCP 3-way handshake":
> "SYN from client, SYN-ACK from server, ACK from client. Three messages establish the connection — agree on initial sequence numbers, window sizes, and options like MSS. After that, data can flow."

## Common Interview Questions

**Q: "Why does DNS use UDP?"**
- Small query/response (usually < 512 bytes)
- High volume — connection setup overhead would be costly
- DNS handles its own retries at the app level
- Note: DNS over TCP is used for large responses (e.g., DNSSEC) and zone transfers

**Q: "Why does HTTP use TCP?"**
- Need full content delivered correctly and in order
- Stream-oriented matches HTTP's request/response model
- (HTTP/3 / QUIC actually uses UDP now, but with reliability added at the app layer)

**Q: "What happens if a UDP packet is lost?"**
- Nothing at the transport layer. The application either notices and handles it (DNS retries), or doesn't (gaming just shows the next state).

**Q: "Can TCP do multicast?"**
- No. TCP is point-to-point only. For multicast, you need UDP.

## What to Memorize

- The comparison table (connection, reliability, ordering, flow control, speed)
- Top 3 TCP use cases (HTTP, SSH, file transfer)
- Top 3 UDP use cases (DNS, VoIP/streaming, gaming/DHCP)
- TCP header has sequence/ack/window/flags; UDP header has just src/dst/len/checksum
- "Correctness > speed = TCP; speed > correctness = UDP"

The next article goes deeper into TCP specifically — handshake, states, sliding window, and congestion control.
