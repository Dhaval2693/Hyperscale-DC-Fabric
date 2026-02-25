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























