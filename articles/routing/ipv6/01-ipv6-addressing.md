# IPv6 Addressing

IPv4 is running out. That statement has been true for two decades, and the network industry's response — NAT, CIDR, private address space — delayed the crisis long enough that IPv6 adoption happened gradually rather than catastrophically. But in a hyperscale data center in 2024, IPv6 is not optional. The number of addressable endpoints — servers, containers, pods, virtual machines — has grown beyond what any reasonable IPv4 address plan can accommodate without aggressive NAT. IPv6 is increasingly the native addressing for DC infrastructure.

Understanding IPv6 addressing is a prerequisite for designing or operating any large-scale network.

## The Address Space

An IPv6 address is 128 bits — compared to IPv4's 32 bits. The number of possible addresses is 2^128, which is so large it effectively eliminates the scarcity problem forever. The practical way to understand the scale: the Earth has approximately 10^50 atoms. IPv6 has 3.4 × 10^38 addresses. You can address every atom on Earth multiple times and still have addresses left over.

IPv6 addresses are written as eight groups of four hexadecimal digits, separated by colons:

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

Two abbreviation rules make IPv6 addresses more manageable in practice:

**Leading zeros in any group can be omitted:**
```
2001:db8:85a3:0:0:8a2e:370:7334
```

**One consecutive sequence of all-zero groups can be replaced with `::`:**
```
2001:db8:85a3::8a2e:370:7334
```

The `::` can only appear once in an address. The reader reconstructs the full address by counting the groups present and filling in as many zero groups as needed to reach 8 total.

## Address Types

**Global Unicast (2000::/3):** Globally routable IPv6 addresses — the equivalent of public IPv4 addresses. Currently allocated from the 2001::/16 range by IANA and regional registries. These are the addresses you use for internet-facing infrastructure and for inter-DC routing.

**Link-Local (fe80::/10):** Automatically configured on every IPv6-enabled interface. Link-local addresses are not routable — they are only valid on the directly connected link. They are used for neighbor discovery (replacing ARP), router advertisements, and routing protocol adjacencies. Every IPv6 interface has a link-local address, even if it also has a global unicast address. Routing protocols like OSPFv3 and BGP for IPv6 often use link-local addresses for their peering sessions — this eliminates the need to allocate global addresses for every inter-router link.

**Unique Local (fc00::/7, specifically fd00::/8):** The IPv6 equivalent of RFC 1918 private addresses. Not globally routable. Used for DC-internal addressing where you want globally unique addresses without requesting a public prefix. The fd00::/8 range requires a randomly generated 40-bit "Global ID" to make the prefix unique — in practice, `fdXX:XXXX:XXXX::/48` where the X values are random. This pseudo-uniqueness prevents conflicts when two organizations using Unique Local addresses connect their networks.

**Multicast (ff00::/8):** IPv6 multicast addresses replace both IPv4 multicast and IPv4 broadcast. IPv6 has no broadcast — every operation that IPv4 implemented as broadcast is implemented in IPv6 as multicast to specific well-known multicast groups. Key examples:
- `ff02::1`: All nodes on the link (equivalent of 255.255.255.255)
- `ff02::2`: All routers on the link
- `ff02::5`: All OSPF routers (link-local OSPF)
- `ff02::6`: All OSPF DR/BDR routers

**Loopback (::1):** The single loopback address. Equivalent of 127.0.0.1.

**Unspecified (::):** The unspecified address. Used as a source address before a proper address is assigned (during DHCPv6 discovery, for example).

## Prefix Notation and Subnetting

IPv6 uses CIDR prefix notation identical to IPv4: address/prefix-length. A /64 prefix leaves 64 bits for the host portion:

```
2001:db8:1:1::/64
```

**Why /64 is standard for all subnets:** IPv6's Stateless Address Autoconfiguration (SLAAC) uses the EUI-64 format to generate a host address from the interface's MAC address. EUI-64 uses 64 bits for the host portion. If a subnet uses a shorter prefix than /64, SLAAC does not work. Industry convention: all subnets, including point-to-point links, use /64. Some engineers argue for /126 or /127 on point-to-point links (the same as IPv4 /30 and /31), but /64 is the dominant convention.

**Address planning hierarchy:**

```
/32  — Assigned to a large organization or regional registry
/48  — Assigned to a single site or DC
/56  — For intermediate aggregation within a site
/64  — Individual subnet (VLAN, link, pod network)
```

A /48 prefix gives 65,536 /64 subnets — more than enough for any DC to have unique /64s for every VLAN, every rack, every point-to-point link, and every loopback.

## IPv6 Address Assignment Methods

**Static:** Manually configured. Used for infrastructure addresses — router loopbacks, switch management addresses, server addresses that need stability. Same as IPv4 static assignment.

**SLAAC (Stateless Address Autoconfiguration):** The host generates its own address from the advertised prefix and its MAC address (or a random Interface ID). No DHCP server required. The router advertises the /64 prefix via Router Advertisement (RA) messages; hosts configure themselves using the prefix and their own Interface ID. Simple but does not give the network visibility into which host has which address (no DHCP lease database).

**DHCPv6 (Stateful):** The host requests an address from a DHCPv6 server, which assigns and tracks leases. Provides visibility into address assignments. Used in environments where address tracking matters.

**Prefix Delegation (DHCPv6-PD):** A router requests a prefix (rather than a single address) from a DHCPv6 server and uses it to address its downstream network. Common in ISP and enterprise WAN environments.

## Neighbor Discovery: ARP's Replacement

IPv6 eliminates ARP. The function of address resolution — finding the MAC address of a known IP address — is handled by **NDP (Neighbor Discovery Protocol)**, which uses ICMPv6 messages.

When a node needs the MAC address of another node on the same link:
1. It sends an ICMPv6 **Neighbor Solicitation** to the **Solicited-Node Multicast Address** of the target (`ff02::1:ffXX:XXXX`, where the last 24 bits are the last 24 bits of the target's IPv6 address)
2. Only the target (or targets with the same last 24 bits) receive the solicitation
3. The target responds with an ICMPv6 **Neighbor Advertisement** containing its MAC address

The solicited-node multicast addresses are a significant efficiency improvement over ARP broadcast: only the intended target receives the solicitation. This eliminates the ARP storm scaling problem that affects large IPv4 subnets.

NDP also handles router discovery (hosts find their default gateway via **Router Advertisement** messages), duplicate address detection (confirming a chosen address is not in use before configuring it), and redirect (telling hosts about better first-hop routers).
