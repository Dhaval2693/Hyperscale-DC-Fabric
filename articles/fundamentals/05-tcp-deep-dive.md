# TCP Deep Dive

TCP is the workhorse of internet transport. This article covers the mechanics — connection lifecycle, sliding window, flow control, and congestion control variants — that come up in interviews and matter in practice.

## The Three-Way Handshake (Connection Setup)

```
Client                              Server
  |                                    |
  |---- SYN (seq=X) --------------->  |
  |                                    |
  |<--- SYN-ACK (seq=Y, ack=X+1) ----|
  |                                    |
  |---- ACK (ack=Y+1) ------------>   |
  |                                    |
  |       [data transfer begins]      |
```

1. **SYN** — Client picks a random initial sequence number X, sends SYN
2. **SYN-ACK** — Server picks its own random sequence Y, acknowledges X+1
3. **ACK** — Client acknowledges Y+1; connection established

Why random initial sequence numbers? Security — predictable sequence numbers enable spoofing attacks.

## TCP Connection States

A TCP connection passes through a defined set of states:

| State | Meaning |
|---|---|
| **CLOSED** | No connection |
| **LISTEN** | Server waiting for incoming connections |
| **SYN-SENT** | Client sent SYN, waiting for SYN-ACK |
| **SYN-RECEIVED** | Server received SYN, sent SYN-ACK, waiting for ACK |
| **ESTABLISHED** | Connection open, data flowing |
| **FIN-WAIT-1** | Sent FIN to close, waiting for ACK |
| **FIN-WAIT-2** | Got ACK for FIN, waiting for peer's FIN |
| **CLOSE-WAIT** | Got peer's FIN, app hasn't closed yet |
| **LAST-ACK** | Sent FIN after peer's FIN, waiting for final ACK |
| **TIME-WAIT** | Waiting (2x MSL) before fully closing |

You'll see these in `netstat` and `ss` output. **TIME_WAIT** is the one most engineers encounter — sockets that haven't been fully released yet.

## Connection Close (4-Way Handshake)

```
Client                              Server
  |---- FIN ------------------->    |
  |<--- ACK --------------------    |
  |                                  |
  |    [server can still send]      |
  |                                  |
  |<--- FIN --------------------    |
  |---- ACK ------------------->    |
  |                                  |
  |     [TIME-WAIT]                 |
```

Asymmetric close — each direction is closed independently. TIME-WAIT prevents stray packets from corrupting later connections reusing the same port pair.

## Sequence and Acknowledgment Numbers

TCP treats data as a **byte stream**. Every byte has a sequence number.

- **Sequence number** = position of the first byte in this segment
- **Acknowledgment number** = next byte expected from the peer (cumulative ACK)

Example: Client sends bytes 1000-1999. Server replies with `ack=2000` meaning "I got everything up to 1999; send me 2000 next."

This is **cumulative** — ACK 2000 acknowledges everything before 2000, not just one packet. **SACK (Selective ACK)** is an option that lets the receiver tell the sender about specific holes ("I got 2000-2999 but missed 1500-1999"), enabling smarter retransmits.

## Sliding Window (Flow Control)

The receiver advertises a **window size** — how many bytes it can buffer before the sender must wait.

```
Sender's view:
|-- sent and ACKed --|-- sent, not ACKed --|-- can send --|-- can't send yet --|
                     <-------- WINDOW -------->
```

As ACKs come in, the window slides forward. If the receiver is slow, the window shrinks; the sender slows down. **Window size = 0 means "stop sending, my buffers are full."**

This is **flow control** — protecting a slow receiver from a fast sender. It's NOT congestion control (which protects the network from being overwhelmed).

## Congestion Control

Congestion control is separate from flow control: it protects the **network** (intermediate routers) from being overwhelmed.

TCP maintains a **congestion window (cwnd)** — its own internal estimate of how much it can safely send. The actual amount in flight is `min(receiver_window, cwnd)`.

### The Phases

1. **Slow Start** — cwnd starts at 1 MSS, doubles every RTT (exponential growth) until it hits a threshold
2. **Congestion Avoidance** — once past the threshold, cwnd grows linearly (one MSS per RTT)
3. **Loss event** — cwnd is cut, threshold reduced
4. Back to Congestion Avoidance

### Congestion Control Variants

TCP doesn't have ONE congestion control algorithm — there are many, each tuned for different conditions:

| Algorithm | When to use | Notes |
|---|---|---|
| **Reno** (classic) | Older default | Loss-based; cuts cwnd in half on loss |
| **NewReno** | Better than Reno on multiple losses | Improved fast recovery |
| **CUBIC** | Linux default since ~2006 | Aggressive growth on high-bandwidth, high-latency links |
| **BBR** (Google) | Modern default in many systems | Models bottleneck bandwidth + RTT; ignores loss as primary signal |
| **DCTCP** | Data center fabrics | Uses ECN marks instead of loss; finer-grained reaction |
| **Vegas** | Research / academic | Latency-based; rarely deployed in practice |

**Trends:**
- **Classic (Reno, CUBIC):** loss = congestion. Works on the internet but is slow to recover from losses unrelated to congestion (lossy Wi-Fi).
- **Modern (BBR, DCTCP):** uses ECN or RTT signals. Better behavior in data centers and on high-bandwidth links.

(For depth on DCTCP and data center congestion control, see `protocols/congestion/03-dctcp-and-ecn.md`.)

## Retransmits

When the sender doesn't get an ACK in the expected time, it retransmits:

- **RTO (Retransmission Timeout)** — sender waits this long before retransmitting. Initially based on RTT estimates; backs off exponentially on repeated failures.
- **Fast Retransmit** — three duplicate ACKs in a row signal a missing packet; retransmit immediately without waiting for RTO.

## Key TCP Options

| Option | Purpose |
|---|---|
| **MSS (Max Segment Size)** | Largest segment the receiver can handle |
| **Window Scaling** | Multiplier on the 16-bit window field (for high-BW links) |
| **SACK** | Selective acknowledgment for non-contiguous gaps |
| **Timestamps** | RTT measurement, PAWS (protect against wrapped sequence numbers) |

## Common Performance Problems

1. **Bufferbloat** — excessive buffering in routers/switches causes massive latency under load. Solution: AQM (Active Queue Management) like CoDel.

2. **TCP global synchronization** — all flows back off together on loss, then ramp up together. Solution: RED (Random Early Detection), DCTCP.

3. **Long-tail latency** — single packet loss + RTO can cause hundreds of ms delay. Solution: tail-loss probes, lower RTO_MIN, parallel connections.

4. **Slow start cost on short connections** — for tiny HTTP responses, slow start dominates. Solution: TCP Fast Open, HTTP/2 multiplexing, QUIC.

## How to Talk About It

For "explain the three-way handshake":
> "SYN, SYN-ACK, ACK. Client picks a random initial sequence number and sends SYN. Server picks its own initial sequence, acknowledges client's, sends SYN-ACK. Client acknowledges server's. After that, data flows. Random initial sequences prevent spoofing."

For "what's the difference between flow control and congestion control":
> "Flow control protects the receiver — sender slows down when the receiver's buffer fills. Congestion control protects the network — sender slows down when packets are being dropped or marked. Receiver-advertised window is flow control; cwnd is congestion control. The sender uses min of both."

For "what TCP congestion control algorithms have you used":
> "CUBIC is the Linux default — aggressive on high-BW links. BBR is Google's newer approach that models bandwidth and RTT instead of just reacting to loss; works better on lossy paths. DCTCP is the data center variant — uses ECN marks for fine-grained control instead of waiting for actual drops."

## What to Memorize

- 3-way handshake (SYN, SYN-ACK, ACK)
- TCP states (especially ESTABLISHED, TIME_WAIT)
- Sequence/ack numbers, cumulative ACK, SACK
- Flow control = receiver window; congestion control = cwnd
- Slow start (exponential) → Congestion Avoidance (linear)
- Variants: CUBIC (default Linux), BBR (Google), DCTCP (data center)
- Fast retransmit triggered by 3 duplicate ACKs
