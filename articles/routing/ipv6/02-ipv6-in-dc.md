# IPv6 in Data Center Networks

Understanding IPv6 addressing is the foundation. Understanding how IPv6 is actually deployed in a production data center — the design decisions, the dual-stack realities, the protocol-specific changes — is what makes the knowledge operational.

## Dual-Stack: The Reality of IPv6 Deployment

In most production data centers today, IPv6 is deployed alongside IPv4 in a **dual-stack** model — every device and interface runs both protocols simultaneously. Pure IPv6-only deployment is the goal for new greenfield environments, but the majority of existing infrastructure, applications, and tooling still require or assume IPv4.

In a dual-stack DC:
- Every router interface has both an IPv4 and an IPv6 address
- Routing protocols run for both address families — either separate protocol instances (e.g., OSPFv2 for IPv4 and OSPFv3 for IPv6) or a single protocol with multiple address families (BGP with both IPv4 and IPv6 AFIs)
- Servers have both IPv4 and IPv6 addresses configured
- DNS returns both A records (IPv4) and AAAA records (IPv6)
- Applications prefer IPv6 when both are available (Happy Eyeballs algorithm in modern OS TCP stacks)

The operational overhead of dual-stack is real: two address planes to manage, two routing tables to maintain, two sets of ACLs to write, two IPAM entries per address. But the transition is unavoidable, and a senior network engineer must be equally comfortable operating both.

## BGP for IPv6 in Spine-Leaf Fabrics

BGP is the routing protocol of choice for spine-leaf fabrics, and it handles IPv6 via **MP-BGP** (Multiprotocol BGP) using the IPv6 Unicast address family (AFI 2, SAFI 1).

**Using link-local addresses for peering:** In an IPv6 spine-leaf fabric, it is common to peer BGP sessions using link-local addresses (`fe80::/10`) rather than global unicast addresses. This eliminates the need to allocate global IPv6 addresses for every point-to-point link — the link-local address is automatically generated and always present.

```
# Arista EOS example — BGP over link-local
router bgp 65001
   neighbor interface Ethernet1 peer-group SPINES
   neighbor interface Ethernet2 peer-group SPINES
   address-family ipv6
      neighbor SPINES activate
      neighbor SPINES next-hop link-local
```

The benefit: you do not need to track or allocate global IPv6 addresses for every inter-switch link. The link-local address serves as the peer address. The tradeoff: link-local addresses are not globally routable — you must use the interface name (not an IP address) to identify the session, and some older tools do not handle link-local peering well.

**Advertising global prefixes:** While peering uses link-local addresses, the routes advertised via BGP use global unicast addresses (the loopback addresses and connected subnets). This is the same model as IPv4.

## OSPFv3 vs OSPFv2

IPv4 uses OSPFv2 (RFC 2328). IPv6 requires **OSPFv3** (RFC 5340) — not because the algorithms changed but because the protocol headers were updated to handle 128-bit addresses and the address family was generalized. OSPFv3 supports both IPv4 and IPv6 as address families, making it potentially the single IGP for dual-stack environments.

Key differences from OSPFv2:
- OSPFv3 runs per-link rather than per-address — the OSPFv3 instance runs on an interface regardless of what IPv6 addresses are configured
- OSPFv3 uses link-local addresses for all adjacency communication and as the next-hop for intra-area routes
- OSPFv3 uses IPSec or OSPFv3 authentication extension for authentication (OSPFv2 used MD5 in the protocol header)
- LSA types were restructured — LSA Type 8 (link-local scope) and LSA Type 9 (link-scope) are new in OSPFv3

In practice, many DC deployments use BGP as the sole routing protocol for the spine-leaf fabric and do not run a separate IGP. In this case, OSPFv3 is less relevant for DC-specific design. But for campus networks and some WAN designs, OSPFv3 remains important.

## ACL and Security Considerations

IPv6 ACLs require the same thought as IPv4 ACLs, plus additional IPv6-specific considerations:

**ICMPv6 must be permitted selectively.** IPv6 fundamentally relies on ICMPv6 for Neighbor Discovery, Router Advertisements, and path MTU discovery. Blocking ICMPv6 completely breaks IPv6 connectivity. At minimum, always permit:
- ICMPv6 type 135/136 (Neighbor Solicitation/Advertisement — ND)
- ICMPv6 type 133/134 (Router Solicitation/Advertisement — SLAAC)
- ICMPv6 type 2 (Packet Too Big — path MTU discovery)

**Extension headers complicate filtering.** IPv6 uses a chain of extension headers (Routing, Fragment, Hop-by-Hop Options, etc.) rather than the single Options field of IPv4. Filtering on upper-layer protocol (TCP, UDP) requires parsing through the extension header chain. Some older network hardware cannot do this at line rate, which can cause IPv6 traffic with extension headers to be processed at lower speeds or dropped.

**SLAAC and RA guard.** In an environment using SLAAC, any rogue device that sends Router Advertisement messages can redirect traffic. **RA Guard** is a switch feature that drops RA messages on host-facing ports, ensuring only the legitimate router's RA is heard by hosts.

## MTU Considerations

IPv6 requires a minimum path MTU of 1280 bytes (IPv4's minimum is 68 bytes, though in practice 576 bytes). IPv6 routers do not fragment packets — only the source can fragment, and only if it chooses to send smaller packets. Path MTU Discovery (PMTUD) is therefore essential for IPv6: if a packet is too large for a link along the path, the router sends an ICMPv6 Packet Too Big message to the source, and the source retransmits at a smaller size.

In a DC fabric where jumbo frames are common (9000-byte MTU on server-to-switch links), the MTU must be consistent end-to-end. An MTU mismatch that causes silent drops — because ICMP Packet Too Big messages are being blocked by a firewall — is a classic IPv6 black hole problem. The symptom: connections work for small transfers but hang for large ones. The diagnosis: check whether ICMPv6 type 2 is being permitted through all ACLs and firewalls.

## IPv6 in VXLAN Fabrics

VXLAN encapsulation works with both IPv4 and IPv6 as the underlay. An IPv6-underlay VXLAN fabric uses IPv6 addresses for VTEP IPs and routes VXLAN traffic over the IPv6 routing domain.

With EVPN, the control plane handles IPv6 seamlessly — EVPN Type 2 routes can carry IPv6 host addresses (the host's IPv6 address alongside its MAC in the NLRI). EVPN Type 5 routes carry IPv6 prefixes for inter-subnet routing.

The combination — IPv6 underlay, EVPN control plane, IPv6 and IPv4 overlay addressing — is where modern DC fabric design is heading. The complexity is manageable, but it requires understanding both IPv6 addressing and EVPN thoroughly before attempting to design or operate such an environment.
