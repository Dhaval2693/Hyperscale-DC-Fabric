# DNS — Domain Name System

DNS is the internet's phone book — it translates human-readable names (`example.com`) to IP addresses (`93.184.216.34`). Every "what happens when I type a URL" interview question starts with DNS.

## The Big Picture

When you type `example.com`:
1. Your computer needs the IP address to connect
2. Your computer asks DNS
3. DNS returns the IP
4. Your computer connects

The whole DNS system is designed to be **distributed**, **cached**, and **fast**.

## The DNS Hierarchy

DNS is a tree, read right-to-left:

```
.                       ← root
└── com.                ← TLD (Top Level Domain)
    └── example.com.    ← second-level domain (yours)
        └── www.example.com.   ← subdomain (host)
```

- **Root servers** — 13 logical clusters worldwide (`a.root-servers.net` through `m.root-servers.net`)
- **TLD servers** — for `.com`, `.org`, `.net`, country codes, etc.
- **Authoritative servers** — the actual owner of `example.com` runs these (or pays a hosting provider)

## DNS Resolution Walkthrough

When your computer needs to resolve `www.example.com`:

1. **Browser cache** — already know it? Use it.
2. **OS cache** — already cached in the OS? Use it.
3. **Hosts file** — `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows). Local override.
4. **Local resolver** (recursive DNS server) — usually your ISP's, or `8.8.8.8` (Google), `1.1.1.1` (Cloudflare). Configured via DHCP.
5. The local resolver does the hard work:
   - Asks a **root server**: "where can I find `.com`?"
   - Root replies: "ask the `.com` TLD servers at \[these IPs\]"
   - Asks a `.com` TLD server: "where's `example.com`?"
   - TLD replies: "ask the authoritative servers at \[these IPs\]"
   - Asks the authoritative server: "what's `www.example.com`?"
   - Authoritative replies: "`www.example.com` is at `93.184.216.34`"
6. Local resolver caches the answer (TTL-bounded) and returns it to you
7. Your computer caches the answer

This is **recursive** resolution from your perspective (you make one query and get an answer); **iterative** from the resolver's perspective (it queries multiple servers in steps).

## Common DNS Record Types

| Type | Purpose | Example |
|---|---|---|
| **A** | Hostname → IPv4 address | `www → 93.184.216.34` |
| **AAAA** | Hostname → IPv6 address | `www → 2606:2800:220:1::1` |
| **CNAME** | Alias to another name | `www → example.com` |
| **MX** | Mail server for domain | `example.com → mail.example.com priority 10` |
| **NS** | Authoritative name servers | `example.com → ns1.example.com` |
| **TXT** | Arbitrary text (often verification) | `example.com → "v=spf1 ..."` |
| **PTR** | IP → hostname (reverse lookup) | Used in reverse DNS zones |
| **SOA** | Start of Authority (zone metadata) | TTLs, serial, refresh times |
| **SRV** | Service location | `_sip._tcp → sipserver:5060` |
| **CAA** | Which CAs can issue certs | `example.com → "letsencrypt.org"` |

## Caching and TTL

Every DNS record has a **TTL (Time To Live)** in seconds. Caches respect this — after TTL expires, the cache discards the entry and must re-resolve.

- Low TTL (60s) → fast propagation when records change, more DNS traffic
- High TTL (86400s / 1 day) → slow propagation, less DNS traffic

Common pattern: lower TTL before a planned change, change the record, monitor, raise TTL after.

## Caching Layers

Caching happens at every level:

1. **Browser** — short cache, app-specific
2. **OS resolver** — per-machine, varies by OS
3. **Local resolver** (ISP / `8.8.8.8`) — shared across many users
4. **Authoritative server** — never caches (it IS the source of truth)

This caching is what makes DNS scale to billions of queries per second.

## DNS Transport

- **UDP port 53** — default for queries and responses (small, fast)
- **TCP port 53** — used when response > 512 bytes (DNSSEC, zone transfers, EDNS)
- **DoT (DNS over TLS, port 853)** — encrypted DNS over TCP
- **DoH (DNS over HTTPS, port 443)** — encrypted DNS inside HTTPS
- **DoQ (DNS over QUIC)** — newer, encrypted over UDP/QUIC

Privacy-driven shift: traditional DNS is unencrypted; ISPs and middleboxes can see your queries. DoT/DoH encrypt them.

## DNS Security

- **DNS spoofing / cache poisoning** — attacker injects fake responses. Mitigation: source port randomization, **DNSSEC**.
- **DNSSEC** — DNS records signed cryptographically. Resolvers verify signatures. Limited deployment.
- **Recursive resolver abuse** — open resolvers used in amplification DDoS. Don't run open resolvers.

## How to Talk About It

For "explain DNS resolution":
> "When you query a hostname, your local resolver walks the DNS hierarchy. Root → TLD → authoritative server. Each step returns the next server to ask, not the final answer. The authoritative server returns the actual IP. Every step is cached with TTL — that's how DNS scales."

For "what's the difference between A and CNAME":
> "A is a direct mapping from hostname to IPv4. CNAME is an alias — it says 'this name is really another name; resolve THAT.' CNAME adds a lookup step but is useful for centralizing changes; updating one A record propagates to all CNAMEs pointing at it."

For "what's DNS caching for":
> "Scaling. Without caching, every browser would hit the root servers for every query. Caching at the browser, OS, and local resolver layers means most queries are answered in microseconds without touching the wider DNS system."

## Common Interview Questions

**Q: "What's recursive vs iterative DNS resolution?"**
- Recursive: client asks one server, gets the final answer (the server does the work)
- Iterative: client follows referrals step by step, querying each server in the chain

In practice: clients use **recursive** resolution (toward their local resolver), and the local resolver uses **iterative** resolution upstream.

**Q: "What's a CNAME loop?"**
- A → CNAME → B → CNAME → A. Resolvers detect this and return an error to avoid infinite loops.

**Q: "Can a CNAME coexist with other records at the same name?"**
- No. CNAME at a name precludes any other record at that name. That's why you can't put a CNAME at the apex (`example.com` itself) if you also need MX records — use ALIAS / ANAME records instead (provider-specific extension).

**Q: "What does `dig` show?"**
- Detailed DNS query output: question, answer, authority, additional sections. Powerful debugging tool.

## What to Memorize

- The DNS hierarchy (root → TLD → authoritative)
- Common record types (A, AAAA, CNAME, MX, NS, TXT, PTR)
- Caching at every layer with TTL
- UDP/53 default, TCP/53 for large responses
- Recursive (client view) vs iterative (resolver view) resolution
- `8.8.8.8` (Google), `1.1.1.1` (Cloudflare) are well-known public resolvers
