# What Happens When You Type a URL in Your Browser

This is *the* classic networking interview question. A good answer touches every layer of the stack and demonstrates that you understand how the pieces fit together.

Here's the full walkthrough.

## The Scenario

You type `https://www.example.com` and hit Enter. Walk through everything that happens.

## Step 1: URL Parsing

The browser parses the URL into parts:
- **Scheme** — `https` (use TLS over TCP, default port 443)
- **Host** — `www.example.com`
- **Path** — `/` (the default)
- **Port** — 443 (default for HTTPS; explicit if specified like `:8080`)

## Step 2: Cache Check (Avoid Network If Possible)

The browser checks several caches before making any network request:

1. **Browser cache** — fully cached responses for repeat visits
2. **Service Worker cache** — if the site registered one
3. **HSTS list** — sites that have promised "always use HTTPS"

If everything is cached, the browser may render without any network traffic at all.

## Step 3: DNS Resolution

We need the IP address of `www.example.com`.

1. **Browser DNS cache** — quick check
2. **OS DNS cache** — `dnsutil` on macOS, `nscd` on Linux, the resolver cache on Windows
3. **Hosts file** — `/etc/hosts` (Linux/macOS), `C:\Windows\System32\drivers\etc\hosts`
4. **Local DNS resolver** (configured via DHCP — your ISP's, or `8.8.8.8`, `1.1.1.1`)
5. Resolver walks the hierarchy if needed:
   - Root server (`.`) — points to `.com` TLD
   - `.com` TLD server — points to `example.com` authoritative
   - Authoritative server — returns the IP for `www.example.com`
6. Resolver returns the IP, caches it for the TTL

Result: `www.example.com → 93.184.216.34`

## Step 4: ARP (If Destination Is on a Different Subnet)

The IP `93.184.216.34` is clearly not on your local subnet. Your computer needs to send the packet to its **default gateway** (your home router or office gateway).

To send a frame to the gateway, you need the gateway's MAC. If not cached:

1. Computer broadcasts an ARP Request: "Who has 192.168.1.1? Tell 192.168.1.100"
2. Gateway replies: "192.168.1.1 is at AA:BB:CC:DD:EE:FF"
3. Computer caches the mapping

(If the destination IP WAS on your local subnet, ARP would resolve the destination directly instead of the gateway.)

## Step 5: TCP Three-Way Handshake

Your computer initiates a TCP connection to `93.184.216.34:443`.

```
You                              Server
  |---- SYN (seq=X) ---------->  |
  |<--- SYN-ACK (seq=Y, ack=X+1)-|
  |---- ACK (ack=Y+1) -------->  |
```

After three messages, the TCP connection is established.

Note: along the way, each router on the path strips the Ethernet frame, looks up the destination IP in its routing table, builds a new Ethernet frame for the next hop, and forwards. Many hops between you and the server.

## Step 6: TLS Handshake

Because we're using HTTPS, before sending HTTP data, TLS negotiates encryption.

Simplified TLS 1.3 handshake:

```
Client                          Server
  |---- ClientHello ---------->  |
  |     (supported ciphers,      |
  |      key share)              |
  |                              |
  |<--- ServerHello -------------|
  |     Certificate              |
  |     (signed key)             |
  |     EncryptedExtensions      |
  |     Finished                 |
  |                              |
  |---- Finished -------------> |
  |                              |
  [encrypted application data]
```

- Client and server agree on a cipher suite
- Server presents a certificate (proves identity)
- Client validates the cert chain back to a trusted root CA
- Both derive symmetric session keys
- All further traffic encrypted with those keys

TLS 1.3 does this in 1 round-trip (1-RTT). TLS 1.2 takes 2-RTT.

## Step 7: HTTP Request

Inside the encrypted TLS channel, the browser sends an HTTP request:

```
GET / HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 ...
Accept: text/html,...
Cookie: session=...
```

## Step 8: Server Processing

The server:
1. Receives the HTTP request
2. Routes it to the right application (often through a load balancer first)
3. Application generates the response (might query a database, render templates, call other services)
4. Returns the HTTP response

## Step 9: HTTP Response

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Cache-Control: max-age=3600

<!DOCTYPE html>
<html>...
```

## Step 10: Browser Render

The browser:
1. Parses HTML
2. Discovers additional resources (CSS, JS, images) — repeats steps 3-9 for each, often in parallel
3. Builds DOM and CSSOM
4. Computes layout
5. Paints pixels to the screen
6. Executes JavaScript

For a complex page, dozens of additional requests happen. HTTP/2 multiplexes them on one connection; HTTP/3 (over QUIC/UDP) reduces head-of-line blocking.

## Step 11: Connection Close

When done, the TCP connection is closed with a 4-way handshake:

```
You                             Server
  |---- FIN ----------------->  |
  |<--- ACK -------------------|
  |<--- FIN -------------------|
  |---- ACK ----------------->  |
```

Modern browsers often keep connections open (HTTP keep-alive) to reuse them for follow-up requests.

## The Layered View

| Layer | What Happens |
|---|---|
| **Application** | URL parsing, HTTP request, HTML render |
| **Presentation** | TLS encryption/decryption |
| **Transport** | TCP handshake, sliding window, retransmits |
| **Network** | IP routing across many hops |
| **Data Link** | ARP, Ethernet framing |
| **Physical** | Signals on cable/fiber/Wi-Fi |

A good interview answer touches all of these. Don't just say "DNS happens"; explain each layer's involvement.

## How to Talk About It (Compact Version)

If the interviewer wants a 60-second summary:

> "Browser parses the URL, checks cache. If not cached, DNS resolution — browser/OS/resolver cache, then walk root → TLD → authoritative. Now I have the IP. ARP for the default gateway's MAC. TCP three-way handshake to the destination. TLS handshake for HTTPS. HTTP request. Server responds. Browser renders. Connection closed or kept alive."

If they want the deep version, expand each step.

## Common Follow-Up Questions

**"What if DNS is down?"**
- Use cached entries until TTL expires; after that, resolution fails.

**"What if the destination is on the same subnet?"**
- Skip the default gateway; ARP for the destination directly.

**"What's TLS doing exactly?"**
- Establishing identity (cert chain) and deriving symmetric session keys.

**"How does the response find its way back?"**
- TCP source port + destination IP are the return address. The packet flows back through the same NAT/routing path (which is stateful — return path is computed independently per router).

**"What if the server's behind a load balancer?"**
- DNS resolves to the load balancer's IP. The LB terminates the connection (or proxies it), picks a backend, forwards.

**"What if the server uses a CDN?"**
- DNS returns the CDN's IP (often anycast — same IP advertised from many locations). You connect to the nearest CDN POP. CDN may serve from cache or proxy to the origin.

## What to Memorize

- The full sequence: parse → cache → DNS → ARP → TCP → TLS → HTTP → render → close
- DNS hierarchy walk (root → TLD → authoritative)
- ARP is for the default gateway when destination is off-subnet
- TCP handshake: SYN, SYN-ACK, ACK
- TLS gives you encryption + identity
- HTTP/2 multiplexes; HTTP/3 uses QUIC over UDP

This is a single question that lets you demonstrate the entire stack. **Practice saying it out loud.** Fluency matters more than perfect detail.
