## OSPF Raw Notes

<Overview of OSPF>
OSPF Full form
Neighbor exchange, LSA updates, Sync database, SPF algorith best route
OSPF packet header
  
<Important table and what it containts>
Neighbor table:
Explain important fields like router-id and how it is decided, State (Full DR/BDR), Purpose of Hello packets, What it contains,
End - not all neighbors will become adjacent. Whether an adjacency is formed or not depends on the type of network to which the two neighbors are attached. Network types also influence the way in which OSPF packets are transmitted
ospf summary table:
show ip ospf database



<Network types concept>
P2P, Broadcast, NBMA, P2MultiPoint, Virtual links - Explain about transit & stub area here

<DR/BDR concepts>
Purpose 1) Manage flooding n(n – 1)/2 adjacencies, 2) represent multi-access network and its attached routers to the rest of the OSPF area
DR/BDR is property of router interface and not router
Router with 0 priority are ineligible to become the DR or BDR
Selection process 
DR Others
Multicast address - 224.0.0.5 & 224.0.0.6

<Timers>
Hello
Dead
Wait - Wait before DR/BDR election happen

<Interface state machine>
Down - No hello
Init - Hello packet seen from neighbor, include  router id of all neighbors
2way - router seen its own router id in the neighbor's hello packet. Neighbor must be in this state or higher to start DR/BDR election process
Exstart - master/slave relationship with neighbor, highest router id wins
Exchange - Sends database Description packets
Loading - send LSR (request) to receive more LSA (Advertisement) from neighbor
Full - Adjacency complete and appear in router LSA and network LSA
<adjacency-building process. picture taken directly from RFC 2328.>

<OSPF packet types>
Database Description packets (type 2)
Link State Request packets (type 3)
Link State Update packets (type 4)

<Areas concept>
Why it is needed? - limit the flooding. the SPF algorithm itself is not particularly processor-intensive. Rather, the related processes, such as flooding and database maintenance, burden the CPU.
Area 0 - backbone area - backbone is responsible for summarizing the topologies of each area to every other area. inter-area traffic must pass through the backbone; non-backbone areas cannot exchange packets directly.
Stuby
Not-so-stuby
Totally stuby

<Router types>
Internal router
ABR - Area border router
ASBR - Autonomous System Boundary Router
Partitioned areas - If a backbone becomes partitioned, each side of the partition and any connected areas become isolated from the other side.
Virtual link - 1) To link an area to the backbone through a non-backbone area 2) To connect the two parts of a partitioned backbone through a nonbackbone area 


<LSA Types>
Purpose of each LSA and originated by whom
1 - Router LSA - Describes all router's interfaces, flooded only within the originating area
2 - Network LSA - produced by the DR on every multi-access network, looded only within the originating area
3 - Network summary LSA - Originated by ABR, sent into a single area to advertise destinations outside that area
4 - ASBR summary LSA - originated by ABRs, ASBR Summary LSAs are identical to Network Summary LSAs except that the destination they advertise is an ASBR
5 - AS External LSA - originated by ASBRs, They advertise either a destination external to the OSPF autonomous system, or a default route external to the OSPF autonomous system
7 - NSSA External LSA - originated by ASBRs within not-so-stubby areas




  

