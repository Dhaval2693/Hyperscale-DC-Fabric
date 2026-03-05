<BGP Basics>
Imagine what happen if you share all the routes in OSPF? World need better & scalable protocol. The visibility of every subnet address would make stability almost impossible. Security would be a nightmare because an attack against the routing protocol—or even an innocent configuration error—could bring down the entire Internet.
Neighbors are two routers running a routing protocol session directly between them, whereas peers are two neighbors sharing reachability information over that session.
The attempts to enhance EGP failed because it was only a reachability protocol, not a true routing protocol.
BGP establishes a unique, unicast-based connection to each of its neighbors. To increase the reliability of the connection, BGP uses TCP (port 179) as its underlying delivery mechanism
AS_PATH attribute to find shortest path & to prevent loop
When two neighbors first establish a BGP peer connection, they exchange their entire BGP routing tables. After that, they exchange incremental, partial updates; that is, they exchange routing information only when something changes, and only information about what changed. 
BGP uses the same concept: If a BGP session is established between two neighbors in different autonomous systems, the session is external BGP (EBGP), and if the session is established between two neighbors in the same AS, the session is internal BGP (IBGP)
IBGP Problems:
BGP routers use the AS_PATH not only as an AS hop count metric but also as a loop avoidance device: If a router sees its own AS number on the AS_PATH list, it drops the route. This presents some interesting problems for IBGP
Require peering with each other to share all info - every router along the path over which a packet will be forwarded must have enough information in its routing table to know what to do with the packet

How about redistribute EBGP routes in IBGP?
tossing external routes into your IGP database exposes you to security and stability threats
A large set of routes (the specific thresholds depend on the individual router’s memory capacity, CPU speed, and efficiency of IGP coding) can cause the IGP to consume most or all the router’s processing capacity, bringing the router’s availability quickly down to 0 and in many cases causing a complete platform failure.

The practice for efficient routing across an IBGP infrastructure is that a full mesh of IBGP sessions should exist between all BGP routers within a single AS. 

<Multihoming>
A transit AS must, by definition, be multihomed for a packet to transit the AS. But a stub AS can also be multihomed.
B
A transit AS is usually a service provider network, delivering services such as basic Internet connectivity or voice and video services to connected customers, or a carrier network, specializing in providing a geographically large backbone to smaller service provider networks. However, a transit AS might also be the backbone of a large commercial, government, or academic organization.

In general, three types of external connections from a transit network exist:

User (customer) peering: Networks that originate or terminate traffic and use the transit AS to get to either other user networks connected to the AS or to get to user networks connected to some other AS.

Private peering: When two or more service providers agree to share routes, they enter into a peering agreement.
Traffic patterns play a major role in determining the financial nature of the agreement.
Tiers are defined by peering relationships. Tier 1 service providers peer with each other exclusively through settlement-free peering. Tier 2 service providers peer with some or, occasionally, all the Tier 1 providers (upstream peering),
Public peering: These connections take place at well-known Internet exchange points (IXP)8 built specifically for allowing such peering.

multihoming is also common in stub autonomous systems. If a stub AS is small enough to not need multihoming—that is, it has only a single link to some higher-level AS—BGP probably is not needed. Static routes on each side of the connection are easy to configure and safer to manage.

good reasons for a stub AS to multihome:

Image Redundancy against access loss because of link and interface failures

Image Redundancy against access loss because of router failures

Image Redundancy against access loss because of ISP failures

Image Local connectivity for autonomous systems with wide geographical footprints

Image Provider independence

Image Corporate or external policies such as acceptable use policies or economic partnerships

Image Load sharing

The principal benefits of multihoming are redundancy, path diversity, and increased bandwidth to external peers.

The point is that load sharing is not the same as load balancing, in which an effort (usually misguided) is made to maintain equal load percentages on all external links in the name of efficient bandwidth usage.  Multihoming is for redundancy and increased routing efficiency, not load balancing.

GP Policies Can Influence How Other Autonomous Systems Choose the Paths into the Local AS
BGP provides you with more than just the means for making better route choices. Its policy capabilities enable you to define a “better route,” on your own terms, outside of what a routing protocol would define by default.

<Intro to BGP>
Unlike IGP, BGP is powerful routing protocol for carrying traffic between two AS and want to control the incoming/outgoing traffic with ISP. Now a days, its been used within Datacenter with clos architecture. But that topic is for another chapter.
It is important to note that, you don't always need to use BGP if you are planning to talk to ISP. For example. if you want to advertise the route to a single ISP for the incoming traffic and use ISP for default route, then you can use static routing and not bother about BGP because it requires tremendos CPU to peer with ISP routers.
You start benefitting from BGP when you have multihome scenario where you are peering with mutliple ISP for your network and you want to control which ISP to peer with. how many routes you want to receive or advertise. Even if multihome scenarios,you just want to advertise traffic to one ISP and use other ISP for backup, you can get away with static routing where you use ISP1 with less metric than othert ISP2. 

It is important to understand the BGP message types & its state machine before we deep dive into different case studies.

BGP has 4 types message types - 1) Open when router starts making peering and it uses TCP 179 port for that, 2) Keepalive to know the peer is healthy and alive , 3) update to send routes, 4) notifciation if for some reason the BGP fail to peer
BGP state finite machine go through these stages before making full neighborship between routers. In idle state, BGP just start initiating TCP session with the peer.
When it wait for the keepalive message, it goes into connect state. If for some reason, peering did not happen then it goes into Active state and initiate another TCP session before go into idle state. If the TCP session was successful and the parameters matches, it goes to OpenConnect state. Once the other router  (R2) also send the BGP parameters, then it (R1) goes to open Confirm. Once both exchange al the info, both routers go to Established state.

## Network Lessons
#### Introduction to BGP

When to use BGP? Routing tables - Default, Partial, and Full
Multi-homed designs: Single & Dual Homed (1 ISP), Single & Dual multi-homed (2 ISP)
eBGP: 
- uses TTL of 1 by default (directly connected neighbor)
- ebgp-multihop (increase TTL)
- update-source (another interface like loopback)
- eBGP multi-home for redunancy when two routers connected through multiple interfaces
iBGP:
- IBGP does not advertise prefixes from one IBGP neighbor to another IBGP neighbor. This is called BGP split horizon.
- Split horizon - Between different ASes, BGP uses the AS_PATH attribute to avoid routing loops. A prefix will not be accepted by a BGP router if it sees its own AS number in it…plain and simple. However, within the autonomous system, the AS number does not change, so we can’t use this loop prevention mechanism.
How to advertise networks in BGP
- BGP network command - exact matches from routing table
- Discard routes to null interface allow you to advertise networks you don't have
- Redistibution injects routes from other protocols such as OSPF, EIGRP into BGP
- Origin codes - i (IGP) and ?  incomplete

#### BGP next hop self
When Internal BGP (IBGP) advertises a prefix to another IBGP router, it doesn’t change the next hop address. External BGP (EBGP) does change the next hop. IBGP keeps the original next hop address. If the other IBGP router can’t reach that next hop address, you will see the prefix in the BGP table, but it won’t be able to install the route in the routing table.
Two options to fix this problem:

    Use the network command to advertise the network where the next hop address is.
    Use the next-hop-self command to change the next hop address to the local IBGP router.
Changing the next hop address is usually the best solution because you won’t have to advertise unnecessary networks.

Using auto-summary has advantages and disadvantages. One major advantage is that the receiving router receives fewer prefixes. This helps with routers with CPU and/or memory constraints. The disadvantage is that you have a loss of detailed routing information. It’s possible that you will receive traffic for prefixes that you don’t have, but that match the advertised summary. Nowadays, we have powerful hardware so it’s best to avoid auto-summary. If you use it, you might want to consider using a route-map so that you only advertise to to specific routers.

#### BGP active vs passive router

    The passive router acts as the server and listens on TCP port 179.
    The active router acts as the client with a random source TCP port number and initiates the connection to TCP port 179

How do BGP routers figure out which one is active or passive? They can compare the BGP router identifier (router ID). Each BGP router knows its identifier and the identifier of the other router, which is configured with the neighbor command. There might be differences between different platforms and OS versions, though.
There are a number of scenarios where this could be useful:

    If you need to allow BGP through a firewall, it’s easier to make rules when the connection is deterministic instead of random.
    When two BGP routers attempt to establish a connection simultaneously, we have a connection collision. The chance that this happens is small, though, and BGP has something built-in to deal with this.
    When you use a route reflector with many clients, you might want to configure the route reflector as passive so it won’t attempt to connect to any BGP routers that are not there (yet).

#### BGP messages
Border Gateway Protocol (BGP) uses four messages to establish a neighbor adjacency, exchange routing information, check if the remote BGP neighbor is still there, and to notify the neighbor if there are any errors. To do all of this, BGP uses these four messages:

    Open Message: establish BGP sessions and negotiate parameters like BGP version, AS numbers, hold timers, and optional capabilities.
    Update Message: advertise new routes (NLRI) or withdraw previously advertised routes using BGP path attributes.
    Keepalive Message: sent every 60 seconds (default) to maintain the BGP session and to confirm the neighbor is still reachable.
    Notification Message: signal errors and terminate BGP sessions when problems occur.

#### BGP Neighbor adjacency troubleshooting

#### BGP Route advertisement troubleshooting

#### BGP attributes and path selection
Priority 	Attribute
1 	Weight - Highest - default 0 - Cisoc proprietary - Not exchanged between routers
2 	Local Preference - highest - control outbound path selection within AS -  Default 100 - set globally or per-neighbor with route-maps - Local preference is exchanged between iBGP routers, so you can configure this on one router, and all your iBGP routers will then receive the local preference value
3 	Originate - path originated by local router over (next hop 0.0.0.0) any other router (networ command, redistribution)
4 	AS path length - shortest - manipulate route by AS path prepending
5 	Origin code - IGP (when you use netwokr command), EGP (historical and no longer there), and INCOMPLETE (redistributed something into BGP) 
6 	MED - lowest - control entry for your AS - exchanged between AS - propogated to all routers within neighbor AS but not passed along to any other AS
7 	eBGP path over iBGP path - eBGP over iBGP
8 	Shortest IGP path to BGP next hop - lowest IGP metric
9 	Oldest path - we received first
10 	Router ID - Lowest bgp neighbor router id 
11 	Neighbor IP address - lowest neighbor ip address

#### Accumulated IGP metric attribute (AIGP)
network designs where the network is under a single administrative authority but divided into multiple ASes, each with its own IGP.
Why do we see networks designed like this? There are several reasons:

    The IGP doesn’t scale for a network of this size.
    One company bought another company, and they haven’t merged their ASes (yet).
    Each business division has a separate network.
    You require a specific routing policy that you can’t do with an IGP.
    You use BGP confederations.
    You use seamless MPLS.
A network with multiple IGPs and BGP in between instead of a single IGP introduces a potential problem. BGP selects a path using the best path selection algorithm, which isn’t based on a “lowest metric” as IGPs do. What happens is that your router will sometimes select sub-optimal paths in your network.
The solution to this problem is to use a BGP attribute named Accumulated IGP Metric Attribute (AIGP).
AIGP is a non-transitive attribute that includes the accumulated IGP metric. BGP routers advertise this AIGP metric to neighbors in other ASes. This allows BGP routers to select the best path based on the end-to-end IGP metric.
To make this possible, AIGP makes some changes to the BGP best-path algorithm.
Once you enable AIGP, BGP will check the AIGP metric right after step 3 (originate). This means we use the AIGP metric as a tie-breaker before other important attributes like the AS path length or MED.
If you use AIGP, you have to use the same IGP. Each IGP uses a different metric, so when you use different IGPs, the AIGP metric won’t make any sense.