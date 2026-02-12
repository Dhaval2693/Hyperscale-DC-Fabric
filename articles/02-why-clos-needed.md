## Why 3-Tier Architecture Was No Longer Enough

If you are in the cloud computing business — or building infrastructure at the scale of companies like Meta — you quickly realize that the traditional 3-tier architecture of core, aggregation, and access layers is no longer sufficient. It was designed for a different era, a different type of application, and a different traffic pattern.

The real reason Clos architecture became dominant was not fashion or vendor marketing. It was driven by a fundamental shift in how applications operate.

In the past, most applications followed a **north–south** traffic model. A client would send a request to a server, the server would process it, and a response would travel back. The network’s primary responsibility was to move traffic in and out of the data center efficiently. That model worked well when applications were mostly monolithic and lived on a single machine or a tightly coupled set of servers.

But modern applications no longer sit inside one server or VM. The growth of the internet and the explosion of data forced applications to become distributed by design. Today, workloads are broken into smaller services that communicate continuously with each other. This is often described as a fan-out/fan-in model, where one request triggers multiple internal requests before a final response is assembled.

Consider what happens when you type `amazon.com` into your browser. That single action does not result in one server responding. Instead, multiple backend systems inside the data center communicate — inventory services, recommendation engines, pricing systems, authentication layers — all exchanging information before the final page is rendered for the user. The visible response depends on invisible coordination.

This is where the traffic pattern shifts from **north–south** to **east–west**. Most communication now happens between servers within the data center rather than between clients and servers. The old 3-tier hierarchy was not optimized for this kind of dense, server-to-server interaction.

As applications became distributed, another challenge emerged: **unpredictable latency**. In distributed systems, the overall response time is determined not by the fastest components, but by the slowest one. If a service fans out requests to ten backend systems and nine respond quickly while one is delayed, the entire user experience waits for that slowest response. Average performance becomes meaningless. Tail behavior dominates. Any variability inside the data center directly impacts customer experience.

At the same time, cloud businesses never stop growing. More customers, more data, more racks, more compute. Traditional scaling methods relied on replacing switches with larger and more complex devices — a model known as **scale-in**. While this approach increases capacity, it also increases cost, complexity, and most dangerously, the size of the failure domain. When a large centralized device fails, the blast radius is significant.

You can only scale vertically for so long before cost and operational risk become unsustainable.

Clos architecture approaches the problem differently. Instead of building bigger boxes, it builds wider fabrics. It embraces **scale-out** rather than scale-in. Rather than relying on massive centralized switches, Clos uses many smaller, cost-effective devices connected in a structured, highly redundant pattern. Every server becomes just a few predictable hops away from any other server. Failures reduce available bandwidth instead of causing outages. Growth is achieved by adding identical building blocks rather than replacing core infrastructure.

Clos architecture is not just a topology. It is a mindset shift. It accepts that failure is normal. It optimizes for **east–west traffic**. It minimizes **blast radius**. And it aligns the network with the realities of distributed computing.

That is why hyperscalers adopted it. Not because it looked elegant on a diagram, but because it solved the problems that modern applications created.


