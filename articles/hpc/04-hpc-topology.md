# HPC Network Topology: Fat-Tree and Dragonfly

The DC spine-leaf topology optimized for cloud computing is not always the right topology for HPC and AI training. When the workload is a large-scale distributed training job where thousands of GPUs must perform collective operations — allreduce, allgather, broadcast — the bisection bandwidth of the network fabric and the number of hops between communicating GPUs directly determine training performance.

HPC network topology design is a distinct discipline from general DC topology design. This article covers the two dominant HPC topologies — fat-tree and dragonfly — and why each exists.

## The Core Requirement: Full Bisection Bandwidth

In a distributed training job, at the allreduce step, every GPU sends gradients to every other GPU simultaneously. If you divide the cluster in half, the bandwidth crossing the imaginary midplane must equal the aggregate bandwidth of all the links on one side — this is **full bisection bandwidth**.

A standard cloud DC spine-leaf is oversubscribed: 4:1 or 8:1 oversubscription means the downlink bandwidth exceeds the uplink bandwidth by that factor. This is acceptable for cloud workloads because most traffic is north-south (client to server) or short-lived east-west bursts — the statistical multiplexing works out.

For HPC allreduce, every server sends simultaneously to every other server. There is no statistical multiplexing — the worst case is the operating case. An oversubscribed fabric becomes a bandwidth bottleneck at exactly the worst moment.

HPC fabrics must provide non-blocking or near-non-blocking bandwidth — every server can communicate with every other server at full line rate simultaneously.

## Fat-Tree Topology

The fat-tree topology achieves full bisection bandwidth by using a hierarchical tree structure where the number of links increases (gets "fatter") at each level going up.

**Structure:**

In a k-port fat-tree (using k-port switches throughout):
- Edge switches: k/2 ports face servers (downlinks), k/2 ports face aggregation (uplinks)
- Aggregation switches: k/2 ports face edge (downlinks), k/2 ports face core (uplinks)
- Core switches: k ports face aggregation switches only
- Total servers: k³/4

For a 64-port fat-tree:
- 64 pods, each with 32 edge + 32 aggregation switches
- 1024 core switches
- 32,768 servers total

Each level doubles the bandwidth available. At the core level, every aggregation pod has equal connectivity to every core switch — providing full bisection bandwidth. Any server can communicate with any other server at full rate without contention at the core.

**ECMP in fat-tree:** Fat-tree relies on ECMP across multiple equal-cost paths between every pair of servers. At the core, there are k/2 equal-cost paths between any two pods. Traffic is hashed across all available paths. The correctness of ECMP hashing is critical — poor hashing that sends multiple heavy flows to the same path causes congestion while other paths are idle.

**Cabling complexity:** A large fat-tree requires enormous cabling density. In a 64-port fat-tree with 32,768 servers: 3 levels of switches, thousands of switches, and hundreds of thousands of cables. Data center physical layout must be carefully designed to accommodate cabling without excessive cable lengths (which introduce latency) or airflow obstructions.

**Used by:** Most large-scale InfiniBand clusters use fat-tree topology. NVIDIA's DGX SuperPOD uses fat-tree with HDR/NDR InfiniBand. Many RoCEv2 clusters also use fat-tree because the topology maps naturally to spine-leaf (the cloud fat-tree is a two-level version of the same architecture).

## Dragonfly Topology

Fat-tree requires many switches and many cables per server. As cluster sizes grow to tens of thousands of GPUs, fat-tree becomes expensive — both in switch cost and in cabling infrastructure.

**Dragonfly** trades cable count for routing sophistication. It uses a two-level interconnect:
- **Local network:** A group of switches that are fully or densely connected within the group (all-to-all within a group)
- **Global network:** Single links connecting groups to each other

Instead of the multi-level redundancy of fat-tree, dragonfly uses exactly one inter-group link per group pair — accepting that inter-group bandwidth is limited, but dramatically reducing total cable count.

**How dragonfly achieves high performance:**

Traffic that stays within a group (local traffic) benefits from the all-to-all local connectivity — any switch in the group can reach any other in one hop.

Traffic that crosses groups takes exactly three hops:
1. Local hop: source switch to a switch in the source group that has the inter-group link
2. Global hop: across the single inter-group link to the destination group
3. Local hop: from the border switch to the destination switch

Three hops maximum, regardless of cluster size. Diameter is constant.

**Adaptive routing:** Because each inter-group link is a potential bottleneck (only one link between each group pair), dragonfly fabrics use **adaptive routing** — choosing the inter-group link dynamically based on current congestion, not just based on destination. If the direct link between group A and group B is congested, traffic can route through an intermediate group (A → C → B) using less-loaded links. This three-hop path becomes a four-hop path, but with better throughput than waiting on a congested direct link.

Adaptive routing requires the network to have real-time congestion visibility and make per-packet (or per-flow) routing decisions. This is significantly more complex than the static ECMP of fat-tree but provides better performance under non-uniform traffic patterns.

**Dragonfly is used by:** The world's largest supercomputers — Cray Slingshot (used in Frontier, the first exascale computer) uses a dragonfly topology. For AI training clusters at the scale of 100,000+ GPUs, dragonfly becomes cost-competitive with fat-tree while providing similar or better performance.

## Comparing Fat-Tree and Dragonfly for AI Clusters

| | Fat-Tree | Dragonfly |
|---|---|---|
| Bisection bandwidth | Full (non-blocking) | Near-full (with adaptive routing) |
| Diameter | O(log N) hops | 3 hops (constant) |
| Cables per server | High | Lower |
| Switch count | Higher | Lower |
| Routing algorithm | ECMP (simple) | Adaptive routing (complex) |
| Congestion handling | ECMP spreads load | Adaptive routing, congestion-aware |
| Scale | Excellent to ~32K servers | Better at >32K servers |

## What This Means at LinkedIn Scale

LinkedIn's AI/ML infrastructure is growing — the JD specifically mentions AI/ML network infrastructure as a preferred qualification. Understanding these topologies is important even if LinkedIn is not operating a 100,000-GPU cluster today:

- **Fat-tree is the near-term topology:** Any GPU cluster LinkedIn operates is most likely using InfiniBand fat-tree or a RoCEv2 fat-tree (which maps directly onto spine-leaf). Understanding fat-tree is directly applicable.
- **The scale-out question will come up:** As LinkedIn's ML workloads grow, topology choices become network engineering decisions. Knowing the tradeoffs between fat-tree and dragonfly, between InfiniBand and RoCEv2, positions you to contribute to those decisions.
- **The operating model:** Whether the topology is fat-tree or dragonfly, the operational requirements are the same — lossless Ethernet (or InfiniBand), ECMP or adaptive routing, congestion monitoring, and fast failure detection. These skills transfer.
