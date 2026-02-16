## General Rules of Routing

Before diving deep into any specific protocol, it helps to step back and understand something fundamental: routing follows a few universal rules. These rules apply whether you are configuring a tiny lab network with static routes or operating a hyperscale data center fabric.

The first rule of routing is simple: a router must know how to reach a destination.

No matter which protocol you use — static or dynamic — the device needs basic **reachability information**. In its simplest form, routing is just a statement that says, “To reach this network, send traffic there.”

If you configure a static route, for example, you are manually telling the router: to reach the `10.2.2.0/24` network, forward traffic to the next-hop IP `10.0.0.2`, which happens to be the neighboring switch. The exact syntax may vary across vendors, but the idea is always the same: destination prefix plus next-hop.

Dynamic routing protocols follow the same principle, but instead of manually specifying next-hops, routers discover them. They form neighbors, exchange updates, build routing tables, and compute the best path automatically. The process involves more steps — neighbor relationships, route advertisements, convergence logic — but the end result is identical: populate the routing table with valid reachability information.

The second rule of routing comes into play when things become interesting.

A router often learns multiple routes to the same destination. Now it must decide which one to use. This is where decision logic begins. The router uses CPU resources and predefined selection rules to determine the **best path**.

The first factor considered is something called **Administrative Distance (AD)**. Administrative distance is essentially a trust value assigned to different route sources. Lower values are preferred. It answers the question: which routing source do I trust more?

Here are the common administrative distances:

| Protocol   | Administrative Distance |
|------------|-------------------------|
| Connected  | 0                       |
| Static     | 1                       |
| eBGP       | 20                      |
| EIGRP      | 90                      |
| OSPF       | 110                     |
| IS-IS      | 115                     |
| iBGP       | 200                     |

If a router learns the same prefix via both OSPF and eBGP, it will prefer the eBGP route because 20 is lower than 110. Administrative distance comparison happens before any protocol-specific logic is evaluated.

If the administrative distance is equal, the router then moves to the next rule: compare the **metric**.

Metrics are protocol-specific. OSPF prefers the path with the lowest cost. RIP prefers the path with the fewest hops. BGP uses a more complex multi-step path selection algorithm.

Here is the list for reference:

| Protocol | Metric Basis | Formula (Simplified) |
|----------|--------------|----------------------|
| OSPF     | Bandwidth    | Cost = Reference Bandwidth / Interface Bandwidth |
| EIGRP    | Composite    | Based on bandwidth and delay (default) |
| RIP      | Hop Count    | Number of routers traversed |
| BGP      | Path Attributes | AS_PATH, Local Preference, MED, etc. |

Now there is another important concept: sometimes the router does not have to choose just one path.

If multiple routes have equal administrative distance and equal metric, many protocols allow **Equal-Cost Multi-Path (ECMP)**. This means the router installs multiple next-hops into the forwarding table and load-balances traffic across them. OSPF, EIGRP, IS-IS, and BGP (with proper configuration) all support ECMP in various forms.

ECMP is especially important in Clos fabrics, where multiple equal-cost paths naturally exist between endpoints.

Beyond administrative distance and metric, there are a few more universal routing principles that apply across all protocols.

One is the **longest prefix match rule**. When forwarding packets, the router always prefers the most specific route. For example, if it has both `10.0.0.0/8` and `10.1.1.0/24` in its table, traffic destined for `10.1.1.5` will match the /24 route because it is more specific. This rule operates at the forwarding plane level and applies regardless of which protocol installed the route.

Another important rule is that only the **best route per protocol** enters the routing table (unless multipath is enabled). Protocols may learn many candidate routes internally, but only the selected best path is installed in the main routing table.

Finally, routing is always hierarchical in decision order:

1. Longest prefix match (forwarding decision)
2. Administrative distance (which routing source to trust)
3. Protocol-specific metric (which path within that source)
4. Optional multipath (if equal)

Understanding these rules simplifies everything. Whether you are debugging static routes in a lab or analyzing BGP behavior in a hyperscale fabric, the same decision hierarchy applies.

Routing may look complex because of the number of protocols involved, but at its core, it follows consistent and predictable logic.
