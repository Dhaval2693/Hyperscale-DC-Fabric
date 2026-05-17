# AWS Networking for Network Engineers

For any hyperscaler or AI infrastructure role, knowing **one** cloud provider's networking model deeply is required. AWS is the most common ask. This article covers the AWS networking primitives you need to discuss intelligently and the cost model that drives most architecture decisions.

## VPC: The Foundation

A **VPC (Virtual Private Cloud)** is your private network in AWS — a logically isolated section of the cloud with your own IP address space, subnets, and routing.

**Core components:**

| Component | Purpose |
|---|---|
| **CIDR block** | IP range for the VPC (e.g., `10.0.0.0/16`) |
| **Subnets** | Sub-ranges of the CIDR, each in a single Availability Zone |
| **Route tables** | Control where traffic from each subnet goes |
| **Internet Gateway (IGW)** | Connects subnets to the public internet |
| **NAT Gateway** | Outbound internet from private subnets (no inbound) |
| **Security Groups (SG)** | Stateful firewall at the instance level |
| **NACLs** | Stateless firewall at the subnet level |

### SG vs NACL (Common Interview Question)

| | Security Group | NACL |
|---|---|---|
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions) |
| Scope | Instance | Subnet |
| Rules | Allow only | Allow + deny |
| Default | Deny all | Allow all |

Most security work happens at the SG level. NACLs are a coarse blast-radius safety net.

## Transit Gateway (TGW): Multi-VPC Hub

When you have many VPCs (and at hyperscaler scale, you will), you don't want full-mesh peering. **TGW** is a central hub:

- Attach VPCs, VPN connections, Direct Connect, and other TGWs
- Route between attached networks via TGW route tables
- Inter-region TGW peering for cross-region traffic
- Charged per attachment + per GB processed

**The standard architecture pattern:** one TGW per region, peered to TGWs in other regions. VPCs attach to local TGW. This scales to thousands of VPCs without VPC peering's N² complexity.

## Direct Connect (DX): Hybrid Cloud

DX gives you a **physical/dedicated** connection from your data center (or colo) to AWS. Bypasses the public internet.

- **Dedicated** — your own physical cross-connect at an AWS DX location (1, 10, 100 Gbps)
- **Hosted** — DX partner provides a slice of their dedicated connection
- **Virtual Interfaces (VIFs)** —
  - *Public VIF*: access AWS public services (S3, DynamoDB)
  - *Private VIF*: access VPCs directly
  - *Transit VIF*: access TGW (then to all attached VPCs)
- **Pricing** — port-hour fee + data transfer out fee (much cheaper than internet egress)

For high-throughput, low-latency, predictable cross-cloud or cloud-to-DC traffic, DX is the standard. AI training clusters with on-prem data often need DX.

## Gateway Load Balancer (GLB): Appliance Insertion

GLB lets you transparently insert third-party security/networking appliances (firewalls, deep packet inspection) into the traffic path without breaking source IP visibility. Uses **GENEVE encapsulation**.

Not a daily-driver concept, but the JD mentions it. Know it exists for transparently routing traffic through middlebox appliances.

## Connectivity Options Summary

| Option | Use case | Pricing model |
|---|---|---|
| **VPC Peering** | Connect 2 VPCs, simple | Per GB transferred |
| **TGW** | Hub connecting many VPCs | Per attachment + per GB |
| **VPN** | DC ↔ AWS over internet | Hourly fee + data |
| **Direct Connect** | DC ↔ AWS dedicated link | Port fee + cheaper data |
| **Cloud WAN** | Multi-region managed WAN | Per attachment + data |
| **PrivateLink** | Private access to a service | Per endpoint + per GB |

## The AWS Cost Model (Critical for This Role)

**Data transfer is where the money goes.** Compute and storage costs are predictable; network costs surprise you.

The hierarchy of network costs (cheapest → most expensive):

1. **Intra-AZ** (within same AZ, same VPC) — often free
2. **Inter-AZ** (different AZs, same region) — ~$0.01/GB each way
3. **Inter-region** (different regions) — ~$0.02-0.09/GB
4. **Internet egress** — $0.05-0.09/GB (tiered, can be much higher for small volumes)
5. **Cross-cloud egress** — same as internet but you pay both sides

**Common cost pitfalls:**
- Cross-AZ traffic from an unaware load balancer quietly burns money
- NAT Gateway per-GB charges add up fast (~$0.045/GB)
- Pulling container images from the internet costs more than the compute
- Cross-region replication for "DR" can dominate the bill

## How to Talk About It

**Architecture question:**
> "I'd use a TGW per region as a hub, VPCs attaching locally, TGW-to-TGW peering for cross-region. For on-prem, Direct Connect with a Transit VIF to TGW. Security via SGs at the instance layer, NACLs as subnet-level safety nets."

**Cost question:**
> "Network cost in AWS is dominated by data transfer. I'd watch for cross-region replication of non-critical data, NAT Gateway throughput, and cross-AZ traffic between services that should be co-located. I'd build attribution at the TGW and VPC flow log level to expose the real cost drivers."

## What to Be Able to Diagram

On a whiteboard from memory:
- Two regions, each with TGW + 3 VPCs
- TGW-to-TGW peering for inter-region
- DX with Transit VIF to one region's TGW
- Where the cost meters are on every edge

If you can draw and explain this, you've covered ~80% of the AWS networking interview surface.

## Anthropic-Specific Framing

This role cares about **measuring** the network, not just running it. The questions tend toward:

- "Where does cross-AZ traffic come from in our VPC?" → VPC flow logs + attribution
- "Is this workload's cost dominated by compute or egress?" → tag-based + flow-based attribution
- "Should we put a TGW per region or peer VPCs directly?" → utilization-driven decision

Your answers should sound like an engineer who would *look at the data first*, not someone who quotes best practices.
