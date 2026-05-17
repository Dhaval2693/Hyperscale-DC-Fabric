# What Is DCI — Data Center Interconnect

A single data center is not enough. Every hyperscaler and most large enterprises run multiple data centers — for geographic redundancy, disaster recovery, latency optimization for regional users, and regulatory requirements that mandate data residency in specific locations. When these data centers need to communicate — sharing traffic, replicating data, failing over workloads — you need connectivity between them.

This connectivity is **DCI: Data Center Interconnect**.

DCI sounds simple: connect two buildings. In practice, it is one of the more architecturally complex challenges in large-scale network engineering. The difficulty comes from a set of competing requirements that exist nowhere else in network design.

## The Requirements That Make DCI Hard

**High bandwidth, deterministic latency.** The workloads that run between data centers are often the most demanding: live database replication, storage synchronization, real-time application state sharing, and increasingly, distributed AI training where gradient synchronization between GPU clusters in two data centers must happen within tight latency budgets. A DCI link is not a backup path — in many architectures, it is in the critical path of every transaction.

**Layer 2 extension.** Some applications — particularly legacy enterprise applications, virtual machine live migration (vMotion), and certain distributed storage systems — require that endpoints in two data centers appear on the same Layer 2 network. They use ARP, they broadcast, they assume adjacency. Moving these applications to separate Layer 3 networks would require re-engineering them. DCI must transport Layer 2 semantics across a physically separate network.

**Layer 3 routing across sites.** Modern distributed applications need to route between data centers using IP. BGP between sites, route redistribution, traffic engineering across the inter-DC links — DCI must also function as a routed backbone.

**Fault isolation.** Two data centers are supposed to be independent failure domains. A power outage, network failure, or software bug in DC-A should not cascade into DC-B. DCI designs must carry traffic between sites while maintaining strong fault isolation — spanning Layer 2 without spanning broadcast storms or spanning tree failures.

**Encryption and security.** Traffic traversing DCI crosses infrastructure that may not be entirely within the organization's control (leased dark fiber, DWDM circuits on shared carrier infrastructure, internet-based VPNs). This traffic often carries sensitive data and must be encrypted in transit.

No single technology solves all of these simultaneously. DCI is always a combination of transport, overlay, routing, and security technologies layered together.

## The DCI Problem Space

DCI problems fall into three categories:

**Physical connectivity:** How do the two DCs physically connect? Options range from owned dark fiber (high cost, highest performance, full control) to leased wavelengths on a carrier's DWDM network (medium cost, managed bandwidth) to internet VPNs (low cost, variable performance, last resort for critical workloads). The choice determines what bandwidth and latency characteristics are available for everything built on top.

**Layer 2 extension:** How are Layer 2 segments stretched across the DCI? Options include EVPN/VXLAN over the DCI link (preferred for modern fabrics), OTV (Overlay Transport Virtualization, a Cisco technology), or VPLS (for MPLS-based DCI). The key engineering challenge: Layer 2 extension inherently risks extending broadcast domains and failure domains. Good DCI design minimizes this risk while providing the extension that applications require.

**Layer 3 routing:** How are IP routes exchanged between DCs? BGP is the universal answer — the same BGP that runs within each DC's spine-leaf fabric is extended across the DCI link between the two fabrics. Route filtering, community-based policy, and BGP path attributes control how traffic is distributed across the DCI.

## DCI in Practice

At hyperscale — platforms that must maintain high availability across global regions, with data replication requirements between DCs — DCI is not an occasional concern but a core part of the infrastructure. DCs are interconnected by high-bandwidth optical circuits, and the DCI network must carry:

- Database replication traffic (real-time, latency-sensitive)
- User data that must be regionally consistent
- Internal service traffic between microservices deployed across multiple regions
- Infrastructure management traffic (network telemetry, configuration management, monitoring)

Understanding DCI — from the physical transport through the overlay design to the routing policy — is central to what any hyperscale DC network team does every day.

The next articles cover the transport technologies, how EVPN extends across the DCI link, and how failures in DCI are designed for and managed.
