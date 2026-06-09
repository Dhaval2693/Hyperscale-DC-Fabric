## Building a Network for YouTube Scale — From First Principles

When someone asks how you would build YouTube's network, the temptation is to jump straight to load balancers and CDNs. That instinct is wrong. The right starting point is not the tools — it is the scale. At YouTube's scale, the numbers themselves make most of the decisions for you.

Start with one figure: YouTube serves more than one billion hours of video every day. Not views. Hours.

That single number rewrites every assumption you might have about what a network needs to do.

---

### Step One: Translate Usage Into Infrastructure

Before designing anything, you need to understand what a billion hours of daily viewing means in terms of bandwidth, storage, and compute. This is the step most people skip, and it is the most important one.

**Bandwidth:**

If you assume an average bitrate of 2 Mbps per stream — a reasonable blend of mobile 360p and desktop 1080p — and a peak concurrency of around 50 million simultaneous viewers, the math is immediate:

50,000,000 × 2 Mbps = **100 Tbps of outbound bandwidth**

No single data center can push 100 Tbps to users around the world. This is not a technical problem you solve by buying bigger switches. It is the reason you need a CDN, and it is the first constraint that shapes every decision downstream.

**Storage:**

YouTube receives approximately 500 hours of new video every minute. Each upload is transcoded into multiple resolutions — 360p, 480p, 720p, 1080p, 4K, and HDR variants — before it can be served. A single hour of video, stored in all variants, occupies roughly 20–30 GB. Across years of uploads, YouTube's stored video library is estimated in the hundreds of exabytes.

**Compute:**

Every video upload triggers a transcoding pipeline before it can appear to viewers. Transcoding is CPU and GPU intensive. A one-hour video may require dozens of parallel transcoding workers to produce all resolution variants within minutes of upload. At 500 hours per minute arriving continuously, you are running a transcoding pipeline that never stops.

These three numbers — 100 Tbps, hundreds of exabytes, continuous parallel transcoding — define the architecture you need to build.

---

### The Origin Data Center

The origin data center is where the master copies live. It handles uploads, runs the transcoding pipeline, stores everything, and answers requests that the CDN cannot serve from cache.

The internal network of the origin DC is a Clos fabric, for the same reasons we have already discussed: non-blocking bandwidth between any two points, horizontal scalability, and no single failure that takes down the fabric. But the server population inside that fabric is different from a general-purpose cloud.

**Ingestion layer:** Servers that accept video uploads from creators around the world. Bandwidth-heavy on inbound. They validate uploads, strip metadata, and immediately hand off to the transcoding queue.

**Transcoding workers:** CPU and GPU intensive servers that pull raw video from storage, process it, and write multiple output files back to storage. A single video generates dozens of simultaneous storage reads and writes — all east-west traffic across the fabric.

**Distributed storage:** Most of the rack count in the origin DC is storage. These servers hold petabytes of video data. They are read and written by transcoding workers, by the ingest layer, and by the cache servers.

**Origin cache:** A warm tier of recently uploaded and highly requested videos, sitting at the edge of the DC network. When the CDN has a cache miss, it first checks origin cache before pulling from distributed storage.

Because the transcoding pipeline creates massive east-west traffic — workers reading from distributed storage, writing back, coordinating with orchestration services — the aggregation layer of the DC fabric needs to be low-oversubscription or non-blocking. Congestion in the transcoding pipeline slows down video availability for viewers.

![Origin DC Architecture — Clos fabric with ingestion, transcoding, and storage tiers](./diagrams/dc-architecture.svg)

---

### Getting Traffic Out of the Data Center

Serving traffic directly from the origin to users around the world is not viable. A viewer in Mumbai requesting a video stored in Iowa would see buffering as the packets traverse thousands of kilometres of internet. Even with the fastest hardware, the speed of light is a hard limit.

You need to push content closer to users. But before CDNs can help, you need a way to get that content out of the origin DC and onto the internet efficiently.

YouTube (as part of Google) connects to the internet through three mechanisms:

**Internet Exchange Points (IXPs):** Physical facilities where networks meet to exchange traffic directly. Google connects at every major IXP — DE-CIX in Frankfurt, AMS-IX in Amsterdam, LINX in London, Equinix in the US. At an IXP, Google's routers peer directly with hundreds of ISPs simultaneously, exchanging routes and traffic without any middleman. This eliminates transit fees and removes one or more hops from the path to users.

**Direct peering:** Google has bilateral peering agreements with major ISPs and telecom operators. Traffic from a Comcast subscriber watching YouTube travels directly from Google's network to Comcast's network — no transit provider involved. Google operates Google Global Cache (GGC), which places Google-owned servers directly inside ISP networks, sometimes as close as the ISP's own content delivery layer.

**Transit:** For locations where direct peering isn't possible, Google purchases transit from tier-1 carriers. Transit is the fallback — it always works, but it costs more per bit and adds AS hops.

The goal of this peering strategy is to minimize the number of autonomous systems between Google and the user. Every extra AS hop is a potential point of congestion, a potential source of latency, and a bill to pay.

---

### The CDN: Three Tiers, One Goal

The CDN's job is to make the origin irrelevant for most requests. A well-designed CDN achieves 95% or higher cache hit rates at the edge, meaning 95 out of 100 video requests never touch the origin servers at all.

This works because video is an extraordinarily cacheable workload. Unlike a search result or a social media feed — which are personalized per user and cannot be cached — a YouTube video is identical bytes for every viewer. One copy at an edge node can serve thousands of simultaneous viewers.

The CDN is organized into three tiers:

**Edge PoPs:** Small to medium nodes deployed close to users, often inside or directly adjacent to ISP networks. An edge PoP might serve a single metro area or a small country. It caches the most popular content — the top few percent of videos that account for the vast majority of views. Most user requests are served here, a few milliseconds from the viewer.

**Regional caches (mid-tier):** Larger nodes positioned between edge PoPs and the origin. When an edge PoP misses its cache, it asks a regional cache before going all the way to origin. Regional caches store a larger and less popular slice of the catalog. They dramatically reduce origin load and improve overall hit rates.

**Origin:** The master. Only contacted when both edge and regional caches have missed. At a 95% edge hit rate and 80% regional hit rate on misses, the origin handles roughly 1% of total requests.

When a video starts trending, the CDN propagates copies outward through the hierarchy. By the time a video has gone viral, every major edge PoP has already cached it from regional traffic, and regional caches filled from origin hours earlier.

![CDN Three-Tier Hierarchy — request flow from edge to regional to origin](./diagrams/cdn-hierarchy.svg)

---

### Anycast: Routing Users to the Nearest PoP

YouTube announces the same IP prefix from multiple PoP locations simultaneously using BGP anycast. From the internet's perspective, that IP address is reachable via many different paths. BGP's shortest-path selection does the work: a user in Tokyo gets routed to the Tokyo PoP because that advertisement is AS-path shortest. A user in Amsterdam gets the Amsterdam PoP.

No application logic is required for this. The routing protocol handles it at the network layer, automatically and in real time. If a PoP fails, its BGP advertisement withdraws, and traffic seamlessly re-routes to the next-closest location.

DNS plays a complementary role. YouTube's authoritative DNS servers use GeoDNS to return different IP addresses based on the location of the recursive resolver making the query. A resolver in Brazil gets a different answer than a resolver in South Korea. This steers users toward the correct regional pool of PoPs before BGP anycast handles the final-hop selection.

Together, these two mechanisms ensure that a viewer in São Paulo hits a Brazil PoP, a viewer in Tokyo hits a Japan PoP, and a viewer in Nairobi hits an East Africa PoP — all without any application-level redirects, and all transparent to the end user.

![Anycast Routing — same IP prefix, multiple PoP locations, BGP selects nearest](./diagrams/anycast-routing.svg)

---

### Caching: The Full Stack

Caching is not only what the CDN does. It is a principle that operates at every layer of the stack, and understanding each layer is important for reasoning about latency and bandwidth.

**Browser cache:** Static assets — thumbnails, JavaScript, CSS, icons — are returned with aggressive `Cache-Control` headers. They are cached by the browser and not re-fetched on subsequent visits. Video segments themselves are not typically cached in the browser; they are streamed progressively. But the manifest file (the playlist that tells the video player which segments to fetch, in what order, at what bitrate) is often cached briefly.

**ISP transparent proxy:** Some ISPs deploy transparent caches inside their own network. These are outside Google's control, but they reduce the ISP's transit costs and improve latency for popular content. Google's GGC deployments — physical Google caches inside ISP racks — serve a similar purpose but are under Google's control.

**CDN edge cache:** The primary cache. Popular videos are cached here for hours or days, refreshed according to TTL and eviction policies. The eviction algorithm is typically LRU-weighted, sometimes augmented by predicted future popularity from view-count signals.

**CDN regional cache:** Less popular but still worth caching regionally. Larger storage footprint. Longer TTLs. Serves edge misses before origin is contacted.

**Origin hot cache:** A warm layer at the origin for content that is freshly uploaded (before it propagates to CDN) or experiencing sudden unexpected demand. This prevents a single viral video from hammering distributed storage directly.

Each cache layer reduces load on the layer behind it. The goal is that most requests terminate at the edge, and the origin only ever sees a trickle.

![Caching Layers — cache hit vs miss flow from browser to origin](./diagrams/caching-layers.svg)

---

### Bandwidth Engineering: Planning the Capacity

With a system of this kind, every tier's required capacity follows from the cache hit rates and the total egress number.

At 100 Tbps total:

| Tier | Cache hit rate | Bandwidth served |
|------|---------------|-----------------|
| CDN edge PoPs | ~95% | ~95 Tbps |
| CDN regional | ~80% of misses | ~4 Tbps |
| Origin | remainder | ~1 Tbps |

These numbers drive every capacity decision:

**Edge PoP storage:** More storage per edge means a higher local hit ratio. A 200 TB cache at an edge PoP holds far more popular content than a 20 TB cache and dramatically reduces regional and origin traffic.

**Edge PoP count:** More PoPs means lower bandwidth per PoP and lower latency for users in more locations. But each PoP has operational overhead. The tradeoff is between latency, bandwidth cost, and complexity.

**Peering capacity:** At each IXP, the ports connecting to peers must be sized for peak traffic to that region, with headroom. Running links at 90%+ utilization means any traffic spike causes congestion.

**DC egress:** Even though the origin serves only ~1% of requests, at 100 Tbps total, that is still 1 Tbps of origin egress. The border routers, IXP ports, and DC uplinks must all be sized for this.

**Transcoding pipeline throughput:** Internally, the east-west bandwidth required by transcoding is largely decoupled from viewer egress. It is driven by upload volume and transcoding speed requirements. With 500 hours per minute arriving, and each hour requiring perhaps 10–15 parallel transcoding jobs, the fabric must support tens of thousands of concurrent read/write streams between workers and storage.

The architecture that results from following this logic is the same pattern used by every large-scale video platform: a Clos-fabric origin DC, a three-tier CDN, BGP anycast steering, and caching at every layer. The details differ; the structure does not. The scale makes it the only sensible answer.

---

## Part Two: The Protocols and Internals

*Everything above describes what the system does. This section explains how it does it — the protocols running at each layer, how components talk to each other, and the failure modes that matter. This is where an interviewer goes when they want to understand whether you have actually operated a system like this or just read about it.*

---

### Routing Inside the DC: Why BGP Replaced OSPF

If you have studied traditional enterprise networking, your instinct is to run OSPF or IS-IS inside the data center. Both are link-state protocols, both converge quickly, and both are well understood. At a few hundred nodes, either works fine.

At hyperscale, both fail in the same way: the link-state database.

OSPF requires every router to hold a complete map of the entire network. Every link, every router, every prefix is flooded to every other router and stored in the LSDB. In a 3-tier Clos fabric with thousands of leaf and spine switches, each carrying dozens of prefixes, the LSDB becomes enormous. Convergence on a topology change floods the entire database. SPF recalculation runs across thousands of nodes simultaneously. Memory and CPU requirements grow faster than the fabric.

**The solution is BGP — specifically eBGP on the Clos fabric.**

This was codified in RFC 7938: "Use of BGP for Routing in Large-Scale Data Centers." The key insight is that BGP is a path-vector protocol with excellent policy controls and no requirement to maintain a global topology map. Each router only knows what its neighbours have advertised.

In the Clos design:
- Each **server** runs BGP and announces its own loopback or server subnet to its **top-of-rack (ToR)** switch
- Each **ToR** announces those prefixes up to the **leaf** switches
- Each **leaf** announces to the **spine** layer
- Each spine redistributes to all leaves

Every switch in the fabric is assigned its own private AS number (from the private range 64512–65535). The ToR and leaf layer use different ASNs. The result is that every path through the fabric is a distinct AS path, and ECMP across all available paths comes naturally from BGP's multipath extensions.

**Why eBGP between every adjacent pair instead of iBGP?** Because iBGP requires full mesh or route reflectors, and it does not propagate routes to other iBGP peers by default (to prevent loops). eBGP between each pair of adjacent devices is simpler, provides loop prevention via AS-path, and scales without route reflectors.

**The practical outcome:** When a link between a leaf and a spine fails, that specific BGP session drops. The affected routes are withdrawn. Other paths through other spines remain active and traffic shifts instantly. No full-table recalculation. No LSA flooding across the entire fabric.

*An interviewer question at this point: "Why not just use static routes?" The answer: static routes don't react to failure. If a link goes down and you have a static route pointing through it, traffic blackholes until someone manually intervenes. BGP withdraws the route automatically.*

---

### ECMP: How the Fabric Load Balances Traffic

BGP on the Clos fabric gives you multiple equal-cost paths between any two servers. A packet from a transcoding worker to a storage server can traverse any spine in the fabric — they all have equal cost.

**Equal-Cost Multi-Path (ECMP)** is how the switch hardware selects between those paths. The switch hashes fields from the packet header — typically source IP, destination IP, source port, destination port, and protocol — to produce a consistent hash value. That value selects one of the available paths. The same flow (same 5-tuple) always takes the same path. Different flows take different paths.

This matters enormously for the transcoding pipeline. Thousands of concurrent flows between workers and storage are distributed across all available spine switches. No single spine becomes a bottleneck. The fabric behaves as if every pair of servers has a direct fat pipe between them.

*Interviewer trap: "What goes wrong if you ECMP based only on destination IP?" The answer: all flows to the same server land on the same spine. You lose load balancing for any many-to-one communication pattern, which is exactly what distributed storage looks like.*

**ECMP and TCP:** There is a known interaction problem. If two flows hash to the same path and one is long (a large file transfer) and one is short (a small RPC), the long flow can fill the buffer on that link and cause latency spikes for the short flow. Solutions include:
- Flow-aware scheduling at the switch (hard to do in hardware)
- Per-packet load balancing with reordering tolerance at the receiver (RDMA handles this)
- Explicit congestion notification (ECN) + DCTCP to signal congestion before queues fill

---

### Routing Between the DC and the Internet: BGP Communities and Traffic Engineering

When traffic leaves the origin DC toward an IXP, it crosses the border between the internal DC fabric and the internet. The protocol at this boundary is **eBGP** — the same BGP, but now peering with external autonomous systems.

At each IXP, YouTube's border routers establish BGP sessions with the IXP's route server (a shared BGP speaker that redistributes routes between all IXP members) and with individual ISPs that prefer bilateral sessions.

**BGP communities** are the traffic engineering tool at this boundary. A community is a 32-bit tag attached to a BGP prefix advertisement. Both sender and receiver agree on what the tag means, and the receiver applies a routing policy based on it.

Examples of how YouTube might use communities:

- `no-export` — advertise this prefix to my peer, but tell them not to re-advertise it further. Used to limit the scope of an anycast prefix to a specific region.
- `local-preference signals` — YouTube might send a community that tells a peer ISP to prefer a specific next-hop or de-prefer a congested link.
- `blackhole community` — if a DDoS attack is incoming on a specific prefix, YouTube can tag that prefix with the well-known blackhole community (65535:666). Upstream peers drop traffic destined for it at their edge, protecting YouTube's infrastructure before the traffic even arrives.

**AS-path prepending** is another tool. If YouTube wants to steer traffic away from a specific peering point — perhaps because a link is congested or being maintained — it can artificially prepend its own AS number multiple times to the route advertisement from that location. The longer AS path makes that route less preferred by BGP's selection algorithm, gradually draining traffic toward other peers.

*Interviewer question: "How would you gracefully drain traffic from one IXP before taking it offline for maintenance?" The answer: start prepending the AS path from that location a few hours before the maintenance window. Traffic gradually shifts to other peers as their routes become preferred. Withdraw the route entirely once traffic has drained to near zero.*

---

### Routing Between CDN Nodes: How PoPs Talk to Each Other

Each CDN edge PoP is, from the internet's perspective, just another place where YouTube's AS announces a prefix. The anycast routing described earlier is just BGP working normally.

What is less obvious is how the CDN nodes coordinate cache fills — when an edge misses and needs to pull content from a regional node, or when a regional misses and needs to pull from origin.

**Cache fill paths** are not routed by BGP in the same way user traffic is. They travel over YouTube's private backbone — Google's B4 network, a software-defined WAN that connects all Google and YouTube infrastructure globally. This backbone uses a combination of:

- **eBGP** for prefix exchange between Google-operated facilities
- **Traffic engineering** to fill links efficiently — the backbone routes fill traffic differently from user-facing traffic, because fill traffic can tolerate more latency but needs high throughput
- **MPLS or Segment Routing** in some deployments, to create explicit paths through the backbone for different traffic classes (video fills, live streaming, real-time API traffic each get different treatment)

*Interviewer question: "What's the difference between anycast routing and how CDN cache fills are routed?" The answer: anycast is for the user-facing data plane — it routes the viewer's request to the nearest PoP. Cache fills use a private backbone with explicit traffic engineering, decoupled from the public BGP routing table. User traffic and fill traffic are two separate routing domains.*

---

### The Complete Request Journey

This is the question every interviewer asks when they want to understand how well you know the system end-to-end. Walk through every step from a user pressing play to the first video frame appearing on screen.

**Step 1: DNS Resolution**

The user's app makes a DNS query for `googlevideo.com` (YouTube's video delivery domain). This query reaches the user's recursive resolver — typically operated by their ISP or a public resolver like `8.8.8.8`.

The recursive resolver queries YouTube's **authoritative DNS servers**. Those servers inspect the resolver's source IP and apply **GeoDNS** logic: a resolver in Germany gets back a set of IP addresses associated with European PoPs. A resolver in Singapore gets APAC addresses.

The returned IPs are anycast addresses — the same prefix is announced from multiple PoPs. DNS is the coarse-grained steering. BGP handles the final-hop selection.

*Interview trap: "What if a user's ISP uses a resolver in a different country?" This is the GeoDNS problem. If a German user's ISP resolves via a US-based resolver, they get US-targeted IPs and may be routed to a US PoP. Techniques like EDNS Client Subnet (ECS) partially solve this — the resolver forwards the client's IP subnet to the authoritative server so GeoDNS can respond based on where the user actually is, not where the resolver is.*

**Step 2: TCP / QUIC Handshake**

YouTube predominantly uses **QUIC** (the protocol underlying HTTP/3) for video delivery. QUIC runs over UDP and incorporates TLS 1.3 directly into the connection setup. The full TLS handshake completes in a single round-trip, versus two round-trips for TLS over TCP.

For returning users, **0-RTT resumption** allows QUIC to send application data on the very first packet — zero round-trip overhead. The server validates the session ticket cryptographically and starts responding immediately.

*Interview follow-up: "Why does YouTube prefer QUIC over TCP for video?" The answer is head-of-line blocking. With TCP, all streams share a single byte stream. If one packet is lost, every stream stalls waiting for retransmission. QUIC's streams are independent — a lost packet in stream 3 does not block stream 5. For video, which involves concurrent streams for video segments, audio tracks, and metadata, this matters.*

**Step 3: TLS and HTTP/2 or HTTP/3**

Once the connection is established, the player sends HTTP requests for the manifest file and then for video segments. In QUIC (HTTP/3), each request is an independent stream. The server can interleave responses freely without any stream blocking its neighbours.

**Step 4: Manifest Fetch and ABR Initialization**

The player first fetches the **manifest file** — an MPEG-DASH `.mpd` file or an HLS `.m3u8` file. The manifest lists all available video representations (bitrate levels) and breaks each into short segments, typically 2–10 seconds each. Each segment has a URL the player can request independently.

The player inspects its current bandwidth estimate, buffer state, and screen resolution, then selects an initial bitrate tier. It starts fetching segments at that tier.

**Step 5: Adaptive Bitrate Streaming in Action**

As segments arrive, the player continuously monitors the download rate versus the segment bitrate. If segments arrive faster than they play (buffer filling), it steps up to a higher bitrate. If the buffer drains (segments arrive slower than playback), it steps down to a lower bitrate.

This **Adaptive Bitrate Streaming (ABR)** algorithm runs entirely in the player. From the network and CDN perspective, it just generates a sequence of HTTP GET requests for different segment URLs.

*Interview question: "Why are video segments independently cacheable at the CDN level?" The answer: because each segment is a fixed-size, immutable chunk with a stable URL. A segment that was cached by one viewer can be served to the next viewer of the same video at the same quality level from the same cache. ABR segments are the unit of caching in a video CDN.*

**Step 6: The Edge PoP Responds (or Misses)**

The request for a video segment arrives at the edge PoP. The PoP checks its cache.

- **HIT:** The segment is in cache. The PoP streams it directly. Latency to first byte: ~5–20 ms. No further upstream requests needed.
- **MISS:** The PoP sends a **cache fill request** upstream to its regional node. The regional either hits (and the edge gets the segment and caches it for future requests) or misses and goes to origin. The first viewer of a video in a region may experience a slightly longer startup time while the cache warms. Every subsequent viewer gets the cached copy.

*Interview question: "What is cache stampede, and how do you prevent it?"*

Cache stampede (also called thundering herd) happens when a popular video expires from cache simultaneously at many edge nodes, and thousands of concurrent requests all miss at the same instant, flooding the regional cache or origin with identical fill requests.

The solutions:

- **Request coalescing:** When multiple requests arrive for the same uncached object simultaneously, the cache node sends only one upstream fill request. All waiting requests are held and answered with the single fetched copy. This is the primary defense.
- **Probabilistic early expiration:** Instead of waiting for TTL to hit zero, nodes start randomly refreshing content slightly before it expires. The probability of early refresh increases as expiration approaches. This staggers cache fills across time, preventing simultaneous expiry.
- **Stale-while-revalidate:** The cache serves the stale copy immediately while fetching a fresh version in the background. The viewer experiences no delay; the cache freshens without blocking.

---

### Load Balancing: Four Layers, Different Problems

Traffic is load balanced at four distinct levels, each solving a different problem.

**Layer 1 — ECMP in the Clos fabric:** As described earlier, traffic within the DC is spread across all available spine paths by 5-tuple hashing. This is stateless and runs in switching hardware at line rate.

**Layer 2 — Anycast at the PoP level:** BGP anycast distributes user connections across PoPs globally. This is routing-level load balancing — the network itself selects the serving node.

**Layer 3 — L4 load balancer at PoP ingress:** Within a PoP, an L4 load balancer (Google uses Maglev, described in a 2016 paper) distributes incoming connections across the cache server fleet. Maglev uses **consistent hashing** to assign connections to servers.

**Layer 4 — L7 load balancer for cache routing:** An application-layer proxy inspects the HTTP request and routes it to the specific cache server that is responsible for that video's content. This is where consistent hashing matters most for cache efficiency.

**Consistent hashing for cache distribution:**

A naive round-robin or random assignment of requests to cache servers means any server might be asked for any video. With 200 servers in a PoP and random assignment, every video would be stored on every server, wasting enormous amounts of storage, or on none of them, resulting in constant misses.

Consistent hashing solves this. Each video is assigned to a specific server (or a small set of servers) based on a hash of the video ID. When a request arrives for a video, the hash function deterministically identifies which server holds (or should hold) that video. That server either serves from cache or goes upstream to fill.

The "consistent" part matters when servers are added or removed. With standard modular hashing, adding one server remaps roughly N/N+1 of all keys, effectively invalidating most of the cache. With consistent hashing, adding or removing a server only remaps the keys that belonged to that server — a fraction of the total. Cache efficiency is preserved during fleet changes.

*Interview question: "If you add 10 new cache servers to a PoP, what happens to cache hit rate?" With standard hashing, it collapses temporarily as most requests miss and refill. With consistent hashing, only ~1/N of the cache remaps, and hit rate degrades gracefully.*

---

### Health Checking and Automatic Failover

Every layer of this system has a failure mode. The architecture is designed so that no single component failure causes user-visible impact.

**Edge PoP failure:**

When an edge PoP loses its upstream connectivity or its servers fail health checks, its BGP sessions drop (or are withdrawn by the control plane). The anycast prefix from that location disappears from the routing table. BGP converges and routes the affected users to the next-nearest PoP. Convergence typically takes 30–90 seconds for BGP, though faster mechanisms (BFD — Bidirectional Forwarding Detection) can detect link failures in milliseconds and trigger faster BGP withdrawal.

*Interview: "What is BFD and why would you use it with BGP?" BFD is a lightweight hello protocol that runs between router neighbors at sub-second intervals. When a link fails, BFD detects it in milliseconds and signals BGP immediately, bypassing the 90-second default hold timer. In a CDN context, faster BGP convergence means faster failover of user traffic.*

**Regional cache failure:**

If a regional cache goes down, edge PoPs configured to use it start failing their fill requests. The edge must either fall back to a secondary regional or go directly to origin. This is configured as a fallback policy in the CDN's routing software. The origin absorbs the increased load temporarily — which is why origin must always be provisioned with headroom above its steady-state 1% traffic figure.

**Origin DC failure:**

An origin DC failure does not immediately affect viewers watching cached content. Since 95%+ of requests are served from edge, viewers may not notice for some time. New uploads and fresh content that would have been served from origin start generating misses at the CDN that cannot be resolved. This is why large platforms run multiple origin DCs in different regions with synchronised storage — at the cost of significant replication bandwidth.

---

### QUIC and the Move Away from TCP

TCP was designed for reliability in a lossy, unpredictable network. For the early internet, that was the right tradeoff. For a modern video CDN where the CDN edge is typically only 10–50 ms from the viewer, TCP's limitations become visible.

**Head-of-line blocking at the TCP layer** is the primary problem. HTTP/2 introduced multiplexed streams over a single TCP connection to avoid the one-request-at-a-time limitation of HTTP/1.1. But the multiplexing is at the HTTP layer — underneath, all streams share a single TCP byte stream. If one packet is dropped, TCP's retransmission mechanism stalls all streams until the gap is filled. For video, which involves concurrent streams for video data, audio, and metadata, a single dropped packet freezes everything.

**QUIC solves this at the transport layer.** Each QUIC stream is independent. A packet loss in one stream does not block others. QUIC also handles connection migration — if a mobile user switches from Wi-Fi to cellular mid-stream, the connection continues without interruption because QUIC uses a connection ID rather than the four-tuple of TCP.

For YouTube specifically, Google measured that switching to QUIC reduced rebuffering rates by approximately 18% and improved startup times significantly on mobile networks, where packet loss rates are meaningfully higher than on wired connections.

*Interview question: "QUIC runs over UDP. Doesn't UDP mean unreliable delivery?" QUIC implements its own reliability, congestion control, and flow control on top of UDP. It is not "unreliable" — it is reliable at the application layer but avoids the head-of-line blocking that comes from TCP's in-order delivery guarantee. The choice of UDP is pragmatic: UDP packets can pass through middleboxes (NAT, firewalls) that would otherwise interfere with new transport protocols.*

---

### The Questions Interviewers Actually Ask

The architecture described in this article is a common interview topic for senior network engineering and distributed systems roles. Here are the questions that separate candidates who have thought deeply about the problem from those who have memorized the surface structure.

**"Walk me through what happens when a user presses play on YouTube."**
The full answer covers: DNS → GeoDNS → anycast IP → QUIC handshake with 0-RTT → manifest fetch → ABR tier selection → segment request → edge cache check → regional fill if miss → adaptive quality during playback. Candidates who stop at "the CDN serves the video" are missing most of the interesting parts.

**"How would you handle a sudden 10x traffic spike on a trending video?"**
The good answer covers: request coalescing at the edge (one fill request despite thousands of concurrent misses), stale-while-revalidate to keep serving during fill, origin rate limiting to prevent stampede, pre-warming the CDN by pushing the content outward before the spike (for scheduled events like a major video premiere or live stream).

**"What routing protocol runs inside Google's data center, and why?"**
eBGP on the Clos fabric, per RFC 7938. Because the DC fabric is too large for OSPF's link-state database, because BGP provides per-prefix policy control, and because ECMP across multiple AS paths distributes load naturally.

**"What is the difference between anycast and load balancing?"**
Anycast is routing-level — the network selects the closest destination for a given IP. Load balancing is node-level — within a location, traffic is distributed across a server fleet. Anycast does not care about server health or load; it cares only about routing topology. You need both: anycast to get to the right PoP, and load balancing to distribute within it.

**"How does consistent hashing help maintain cache efficiency when you add servers?"**
Standard modular hashing remaps almost all keys when the server count changes. Consistent hashing maps keys to a virtual ring and assigns ring segments to servers. Adding a server only takes over a portion of one existing server's ring segment — a fraction of the total keys. Cache hit rate degrades only in proportion to the fraction of keys remapped, not catastrophically.

**"A CDN edge PoP is congested. How do you drain traffic from it without dropping connections?"**
Start AS-path prepending from that PoP's BGP advertisements. Existing connections continue (BGP does not reset established flows). New connections route elsewhere as BGP converges. Once traffic has drained to near zero, bring the PoP down for maintenance. Reverse the prepend to restore it when ready.

**"What is 0-RTT in QUIC and what is its security implication?"**
0-RTT allows a returning client to send application data in the first QUIC packet, skipping the handshake round-trip. The implication: 0-RTT data cannot be protected against replay attacks. An attacker who captures a 0-RTT packet can replay it to a server, which will process it again. For idempotent requests (like a video segment GET), this is acceptable. For state-changing requests, servers should not accept 0-RTT data.

Each of these questions is a thread that, if pulled, reveals how deeply a candidate understands the interaction between routing, caching, transport protocols, and operational constraints. The architecture itself is not secret knowledge — it is described in academic papers, engineering blogs, and IETF RFCs. What an interview tests is whether you can reason from first principles about why each piece exists and what breaks if you remove it.
