# TCP Segment Structure

The TCP header carries all the state needed for reliable, ordered, connection-oriented delivery — that's why it's substantially bigger than UDP's.

## TCP Header (20+ Bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Off  |Reserved | C E U A P R S F |          Window Size         |
| set  |         | W C R C S S Y I |                              |
|      |         | R E G K H T N N |                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |        Urgent Pointer         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options (variable)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Data (variable)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Field Breakdown

| Field | Bits | Purpose |
|---|---|---|
| **Source Port** | 16 | Sender's port |
| **Destination Port** | 16 | Receiver's port |
| **Sequence Number** | 32 | Byte position in the stream |
| **Acknowledgment Number** | 32 | Next expected byte from peer |
| **Data Offset** | 4 | Header size in 32-bit words (5 = 20 bytes) |
| **Reserved** | 3 | Always 0 (formerly 6 bits) |
| **Flags** | 9 | Control bits (see below) |
| **Window Size** | 16 | Receiver buffer space (flow control) |
| **Checksum** | 16 | Integrity over header + pseudo-header + data |
| **Urgent Pointer** | 16 | Only meaningful if URG flag set (rarely used) |
| **Options** | variable | MSS, window scaling, SACK, timestamps |
| **Data** | variable | The actual application payload |

## The Flags (9 Bits)

| Flag | Meaning |
|---|---|
| **NS** | ECN nonce concealment (rare) |
| **CWR** | Congestion Window Reduced (response to ECN echo) |
| **ECE** | ECN Echo (signal congestion seen) |
| **URG** | Urgent Pointer field is valid (rarely used) |
| **ACK** | Acknowledgment Number field is valid |
| **PSH** | Push — deliver buffered data to app immediately |
| **RST** | Reset the connection (abnormal abort) |
| **SYN** | Synchronize sequence numbers (start of handshake) |
| **FIN** | Finish — no more data from sender |

You'll see common combinations:
- **SYN** alone — first packet of handshake
- **SYN, ACK** — server's reply in handshake
- **ACK** — acknowledges previous data
- **FIN, ACK** — graceful close
- **RST, ACK** — connection abort
- **PSH, ACK** — data pushed to app + acknowledge

## Sequence and Acknowledgment Numbers

TCP treats data as a continuous **byte stream**, not packets:

- **Sequence Number** = the byte position of the FIRST byte in this segment
- **Acknowledgment Number** = the next byte the sender expects to receive

Example: If A sends bytes 1000-1499 with `seq=1000`, B replies with `ack=1500` meaning "got everything up to and including 1499; send me 1500 next."

This is **cumulative** — one ACK covers everything before it.

## Window Size and Window Scaling

The 16-bit Window Size field = how many bytes the receiver can buffer (max 65,535).

That's tiny for modern high-bandwidth networks. **Window Scaling option** (negotiated in SYN/SYN-ACK) multiplies it by 2^N, where N can be up to 14 — yielding effective windows up to 1 GB.

## Important TCP Options

| Option Kind | Length | Purpose |
|---|---|---|
| **0** | — | End of Options |
| **1** | — | NOP (padding) |
| **2** | 4 | MSS (Maximum Segment Size) |
| **3** | 3 | Window Scale |
| **4** | 2 | SACK Permitted (signals SACK support) |
| **5** | variable | SACK blocks (which non-contiguous bytes received) |
| **8** | 10 | Timestamps (RTT measurement, PAWS) |

Most modern TCP connections negotiate MSS, window scaling, SACK, and timestamps in the SYN/SYN-ACK.

## Reading Captures

In Wireshark, a TCP segment might show:

```
Transmission Control Protocol
    Source Port: 54321
    Destination Port: 443
    Sequence number: 1 (relative)
    Acknowledgment number: 1 (relative)
    Header Length: 32 bytes (8 = 32 bytes for 20-byte header + 12 bytes of options)
    Flags: 0x018 (PSH, ACK)
    Window size value: 65535
    [Window size scaling factor: 128]
    Checksum: 0x...
```

## How to Read TCP Flags Practically

When debugging:

| You see... | Likely meaning |
|---|---|
| Only SYNs from one side | TCP handshake failing — firewall, missing port, host down |
| RST in mid-stream | Connection was aborted (server crashed, RST attack, etc.) |
| Many duplicate ACKs | Packet loss in the path |
| Window size = 0 | Receiver is overloaded; sender must stop |

## What to Memorize

- Header minimum **20 bytes**, up to 60 with options
- **Source/Destination Port** (16 bits each)
- **Sequence number** = byte position; **Ack number** = next expected byte (cumulative)
- 9 flags — know SYN, ACK, FIN, RST, PSH
- **Window Size** = flow control (max 65K without window scaling)
- Important options: MSS, Window Scale, SACK, Timestamps
- Header is bigger than UDP (20 vs 8) because of all the state for reliability
