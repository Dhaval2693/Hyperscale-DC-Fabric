## General Rules of Routing

Before diving deep into any specific protocol, it helps to step back and understand something fundamental: routing follows a few universal rules. These rules apply whether you are configuring a tiny lab network with static routes or operating a hyperscale data center fabric.

The first rule of routing is simple: a router must know how to reach a destination.

No matter which protocol you use — static or dynamic — the device needs basic **reachability information**. In its simplest form, routing is just a statement that says, “To reach this network, send traffic there.”

If you configure a static route, for example, you are manually telling the router: to reach the `10.2.2.0/24` network, forward traffic to the next-hop IP `10.0.0.2`, which happens to be the neighboring switch. The exact syntax may vary across vendors, but the idea is always the same: destination prefix plus next-hop.

Dynamic routing protocols follow the same principle, but instead of manually specifying next-hops, routers discover them. They form neighbor relationships, exchange route information, calculate paths, and automatically populate the routing table. The mechanisms differ — OSPF floods link-state information, BGP exchanges path attributes — but the outcome is identical: valid reachability entries in the routing table.

Once reachability exists, the second rule becomes relevant.

A router often learns multiple routes to the same destination. Now it must decide which one to use. This is where decision logic begins. The router applies a strict hierarchy of rules to determine the **best path**.

The first decision applied during forwarding is the **longest prefix match** rule.

If the router has both `10.0.0.0/8` and `10.1.1.0/24` in its routing table, and a packet is destined for `10.1.1.5`, it will always choose the /24 route. The most specific prefix wins, regardless of which protocol installed it. This rule operates at the forwarding level and applies universally.

If multiple routes exist for the same prefix length, the router then evaluates the **administrative distance (AD)**.

Administrative distance represents how trustworthy the routing source is. Lower values are preferred. It answers a simple question: which routing source do I trust more?

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

If the same prefix is learned through both OSPF and eBGP, the router prefers the eBGP route because 20 is lower than 110.

If the administrative distance is equal, the router moves to the next rule: compare the **metric**.

Metrics are protocol-specific. OSPF prefers the path with the lowest cost, which is derived from interface bandwidth. RIP prefers the path with the fewest hops. BGP uses a more complex multi-step best-path algorithm involving attributes such as AS_PATH, Local Preference, and MED.

Within a single routing protocol, the path with the better metric becomes the selected route.

There is one more possibility. If multiple routes have equal prefix length, equal administrative distance, and equal metric, many protocols allow **Equal-Cost Multi-Path (ECMP)**. Instead of choosing a single next-hop, the router installs multiple next-hops into the forwarding table and load-balances traffic across them.

This behavior is especially important in Clos fabrics, where multiple equal-cost paths naturally exist between endpoints. Without ECMP, much of the fabric’s capacity would remain unused.

When you break it down, routing always follows the same pattern. First, configure reachability information. Then, if multiple options exist, apply the hierarchy: longest prefix match, administrative distance, metric, and finally optional multipath.

Understanding these rules simplifies everything. Whether you are debugging static routes in a lab or analyzing BGP behavior in a hyperscale fabric, the same decision hierarchy applies.

Routing may look complex because of the number of protocols involved, but at its core, it follows consistent and predictable logic.
