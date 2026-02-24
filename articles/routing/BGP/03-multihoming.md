# Multihoming: Redundancy, Control, and Independence

Imagine your entire network connected to the world through a single link. One fiber. One router. One ISP. Everything works until it doesn’t. A backhoe cuts the fiber. The ISP has an outage. A router crashes. Your connectivity disappears.

That is why multihoming exists.

Multihoming simply means connecting your Autonomous System to more than one external AS. But the motivation is deeper than just “two links are better than one.”

There are two types of Autonomous Systems in the Internet. A **stub AS** originates or terminates traffic but does not carry traffic between other ASes. Most enterprises fall into this category. A **transit AS** carries traffic across itself. Service providers and large backbone networks operate as transit ASes. By definition, a transit AS must be multihomed - otherwise traffic cannot pass through it.

But even stub ASes choose to multihome.

Because multihoming provides:
- Redundancy against link failures  
- Redundancy against router failures  
- Protection against ISP outages  
- Geographic resilience  
- Provider independence  
- Policy flexibility  
- Increased aggregate bandwidth  

Multihoming is not primarily about load balancing. That is a common misunderstanding. Load balancing tries to keep equal utilization on multiple links. Multihoming is about resilience and routing efficiency. It gives you **path diversity**. It allows you to survive failure. It gives you options.
The moment you connect to multiple providers, routing stops being automatic and starts becoming strategic. You can choose which provider handles outbound traffic. You can influence how inbound traffic reaches you. You can enforce policies based on economics, performance, or partnerships.
BGP policies allow you to define what “better” means. Shorter AS path. Preferred provider. Lower cost transit. Community-based routing decisions. 

Transit networks take this even further. They engage in different types of peering relationships. Customer peering happens when users connect to a transit AS to reach the Internet. Private peering happens when two service providers directly interconnect and exchange routes based on negotiated agreements. Public peering happens at Internet Exchange Points (IXPs), where many providers connect to a shared switching fabric to exchange traffic efficiently.
Multihoming turns routing into an economic and architectural decision, not just a technical one. At small scale, static routing may be enough. But once redundancy, policy, and provider independence matter, BGP becomes unavoidable.

The principal benefits of multihoming are simple: redundancy, path diversity, and greater control. Not perfect symmetry. Not equal traffic percentages.
And at Internet scale, those are the properties that matter most.
