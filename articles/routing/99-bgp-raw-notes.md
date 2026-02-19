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



