# DNS and DHCP Message Formats

DNS and DHCP run over UDP but have their own structured message formats. Knowing the key fields helps when reading captures or debugging.

## DNS Message Format

A DNS message has 5 sections, all carried in a UDP/53 (or TCP/53) payload:

```
+---------------------+
|       Header        | 12 bytes — always
+---------------------+
|      Question       | what's being asked
+---------------------+
|       Answer        | RRs answering the question
+---------------------+
|     Authority       | RRs for authoritative servers
+---------------------+
|     Additional      | extra useful RRs
+---------------------+
```

### DNS Header (12 Bytes)

| Field | Bits | Purpose |
|---|---|---|
| **ID** | 16 | Transaction ID (matches query to response) |
| **Flags** | 16 | QR, Opcode, AA, TC, RD, RA, Z, RCODE |
| **QDCOUNT** | 16 | Number of questions |
| **ANCOUNT** | 16 | Number of answers |
| **NSCOUNT** | 16 | Number of authority records |
| **ARCOUNT** | 16 | Number of additional records |

### DNS Flag Bits

| Flag | Meaning |
|---|---|
| **QR** | 0 = query, 1 = response |
| **Opcode** | Standard query (0), inverse (1), status (2) — 0 is normal |
| **AA** | Authoritative Answer (set if responder is the authority) |
| **TC** | Truncated (response > 512 bytes; retry over TCP) |
| **RD** | Recursion Desired (client wants recursive resolution) |
| **RA** | Recursion Available (server supports recursion) |
| **RCODE** | Response code: 0 = OK, 1 = format error, 2 = server failure, 3 = NXDOMAIN, etc. |

### DNS Question Section

For each question:

```
NAME    — variable-length, encoded as labels (length-prefixed strings)
QTYPE   — 16 bits — A (1), AAAA (28), CNAME (5), MX (15), NS (2), TXT (16), PTR (12), SOA (6), SRV (33)
QCLASS  — 16 bits — almost always IN (Internet) = 1
```

The NAME encoding compresses repeated suffixes with pointers — a wire-format optimization for things like `www.example.com` and `mail.example.com` appearing in the same packet.

### DNS Answer Records (RRs — Resource Records)

```
NAME      — same encoding as question
TYPE      — A, AAAA, CNAME, MX, etc.
CLASS     — usually IN
TTL       — 32 bits — seconds to cache this record
RDLENGTH  — 16 bits — length of RDATA
RDATA     — the actual answer (IP for A, name for CNAME, etc.)
```

### Common DNS RR Types

| Type | Number | Purpose |
|---|---|---|
| A | 1 | IPv4 address |
| NS | 2 | Authoritative name server |
| CNAME | 5 | Alias |
| SOA | 6 | Start of Authority (zone metadata) |
| PTR | 12 | Reverse DNS pointer |
| MX | 15 | Mail server |
| TXT | 16 | Text (SPF, DKIM, verification) |
| AAAA | 28 | IPv6 address |
| SRV | 33 | Service location |
| OPT | 41 | EDNS0 metadata |
| CAA | 257 | Certificate Authority Authorization |

## DHCP Message Format

DHCP (IPv4) builds on the older BOOTP protocol. The packet is significantly larger than DNS — 240 bytes of fixed fields plus variable options.

```
+-------------------------+
|   op (1)                | BOOTREQUEST (1) or BOOTREPLY (2)
+-------------------------+
|   htype (1)             | hardware type — Ethernet = 1
+-------------------------+
|   hlen (1)              | hardware address length — 6 for MAC
+-------------------------+
|   hops (1)              | incremented by relays
+-------------------------+
|   xid (4)               | transaction ID
+-------------------------+
|   secs (2)              | seconds since client started
+-------------------------+
|   flags (2)             | broadcast bit
+-------------------------+
|   ciaddr (4)            | client IP (if known)
+-------------------------+
|   yiaddr (4)            | "your" IP — what server offers
+-------------------------+
|   siaddr (4)            | next server IP (for boot)
+-------------------------+
|   giaddr (4)            | gateway / relay IP
+-------------------------+
|   chaddr (16)           | client hardware address (MAC)
+-------------------------+
|   sname (64)            | server hostname (legacy)
+-------------------------+
|   file (128)            | boot filename (PXE)
+-------------------------+
|   magic cookie (4)      | 0x63825363 — start of DHCP options
+-------------------------+
|   options (variable)    | type, requested IP, lease time, etc.
+-------------------------+
```

### Key DHCP Options

| Option | Number | Purpose |
|---|---|---|
| Subnet Mask | 1 | Mask for the assigned address |
| Router (gateway) | 3 | Default gateway |
| DNS servers | 6 | List of DNS resolvers |
| Domain Name | 15 | Local domain (e.g., `corp.example.com`) |
| Lease Time | 51 | Lease duration in seconds |
| **Message Type** | 53 | DISCOVER (1), OFFER (2), REQUEST (3), DECLINE (4), ACK (5), NAK (6), RELEASE (7), INFORM (8) |
| Server Identifier | 54 | DHCP server's IP |
| Parameter Request List | 55 | What options the client wants in the reply |
| Renewal Time (T1) | 58 | When to start renewing |
| Rebinding Time (T2) | 59 | When to broadcast for any server |
| Vendor Class ID | 60 | Client vendor identifier |
| Client ID | 61 | Unique client identifier (often MAC) |
| TFTP Server | 66 | For PXE boot |
| Boot File Name | 67 | PXE boot image |

Option 53 (Message Type) is what distinguishes a DISCOVER from an OFFER, REQUEST, ACK, etc.

### DHCP Message Sequence — Field by Field

**DHCPDISCOVER** (client → broadcast):
- op = 1 (BOOTREQUEST)
- chaddr = client MAC
- ciaddr = 0.0.0.0 (no IP yet)
- options: msg type = DISCOVER, requested IP (optional), parameter list

**DHCPOFFER** (server → client):
- op = 2 (BOOTREPLY)
- yiaddr = offered IP
- chaddr = client MAC
- siaddr = server IP (for next steps)
- options: msg type = OFFER, lease time, subnet mask, router, DNS, server ID

**DHCPREQUEST** (client → broadcast):
- options: msg type = REQUEST, requested IP (the offered one), server ID

**DHCPACK** (server → client):
- yiaddr = confirmed IP
- options: msg type = ACK, all final settings

## How to Read These in Wireshark

DNS in Wireshark:
```
Domain Name System (response)
    Transaction ID: 0xa1b2
    Flags: 0x8180 Standard query response, No error
    Questions: 1
    Answer RRs: 1
    Queries
        example.com: type A, class IN
    Answers
        example.com: type A, class IN, ttl 300, addr 93.184.216.34
```

DHCP in Wireshark:
```
Dynamic Host Configuration Protocol (DHCPACK)
    Message type: Boot Reply (2)
    Hardware type: Ethernet (0x01)
    Transaction ID: 0xabcdef01
    Your (client) IP address: 192.168.1.50
    Bootp flags: 0x0000 (Unicast)
    Magic cookie: DHCP
    Option: (53) DHCP Message Type (ACK)
    Option: (54) DHCP Server Identifier (192.168.1.1)
    Option: (51) IP Address Lease Time (86400 seconds)
    Option: (1)  Subnet Mask (255.255.255.0)
    Option: (3)  Router (192.168.1.1)
    Option: (6)  Domain Name Server (8.8.8.8)
```

## What to Memorize

**DNS:**
- 12-byte fixed header + 5 sections (Header, Question, Answer, Authority, Additional)
- Transaction ID matches query to response
- TC flag (truncated) → retry over TCP
- Common QTYPEs: A (1), AAAA (28), CNAME (5), MX (15), NS (2)

**DHCP:**
- BOOTP-derived format, 240+ bytes
- Key fields: chaddr (client MAC), yiaddr (your IP), giaddr (relay)
- DORA = options 53 values: DISCOVER (1), OFFER (2), REQUEST (3), ACK (5)
- Common options: 1 (mask), 3 (gateway), 6 (DNS), 51 (lease), 53 (msg type)
