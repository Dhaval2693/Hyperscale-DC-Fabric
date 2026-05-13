# Hyperscale DC Fabric

Network engineering is hard to learn from documentation alone. Specs tell you what a protocol does. They rarely tell you *why* it exists, what problem it was designed to solve, or what breaks when you get it wrong.

This repo is my attempt to learn hyperscale data center networking the way I think it should be learned — through stories. Each article starts with a problem. A real constraint. A situation that makes the technology feel necessary rather than arbitrary. Then it explains how the technology solves that problem, and what happens at the edges where it falls apart.

The goal is to build intuition, not just vocabulary.

---

## What's Inside

### DC Fabric
The physical and logical structure of modern data centers — why Clos topologies replaced legacy three-tier designs, how VXLAN stretches Layer 2 across a routed fabric, and how EVPN brings control-plane intelligence to overlays.

- Clos architecture and why it scales
- VXLAN: underlay vs overlay, VNIs, VTEPs, packet walkthrough
- EVPN: route types, EVPN+VXLAN together, symmetric vs asymmetric IRB
- MLAG: dual-homing servers without spanning tree

### Data Center Interconnect (DCI)
Connecting two data centers sounds simple. It is one of the harder problems in network engineering. These articles cover transport options, how EVPN extends across the DCI link, and how to design for failure when the DCI itself goes down.

### Routing Protocols
BGP runs the internet and the data center. OSPF handles the underlay. MPLS and its VPN derivatives move traffic across service provider networks. IPv6 is no longer optional.

- BGP: state machine, path selection, multihoming, eBGP vs iBGP
- OSPF: areas, LSA types, DR/BDR, network types
- MPLS: why it exists, LSPs, L3VPN and L2VPN
- IPv6: addressing and DC deployment

### Congestion and QoS
At hyperscale, congestion is not an exception — it is a design input. These articles explain why standard TCP is not enough for data center workloads, how ECN and DCTCP fix it, and how PFC creates a lossless fabric for RDMA.

### HPC and RDMA Networking
AI training and HPC workloads demand something TCP cannot give: zero-copy, kernel-bypass, microsecond latency. This section covers RDMA, the InfiniBand vs RoCEv2 tradeoff, and what it takes to build a lossless Ethernet fabric that RDMA can actually use.

### Kubernetes Networking
Kubernetes runs on the DC fabric, which means DC network engineers own it whether they signed up for it or not. CNI plugins, pod routing, Services, kube-proxy, host TCP tuning — explained from a network engineer's perspective.

### Automation
Manual configuration does not scale to thousands of switches. These articles cover the tools (Python, Ansible, NETCONF/YANG, gNMI) and — more importantly — the engineering discipline that makes automation safe at scale.

### Operations and Observability
Networks fail. The question is how fast you find out and how much you understand when you do. Streaming telemetry, gNMI, and what good observability actually looks like in a large DC environment.

### Protocols
Deep dives into specific technologies that cut across the fabric: multicast (PIM-SM, how it works on Arista), eBPF (how it is reshaping DC networking from the host side up).

### Coding
Technical interviews for network engineering roles test general problem-solving, not just protocol knowledge. Graph algorithms, common DSA patterns, and Python networking patterns — practical preparation, not theory.

---

## How to Read This

Each article is self-contained, but they build on each other. If you are new to DC networking, start with the Clos architecture articles and work through VXLAN and EVPN before jumping to DCI or HPC. If you already know the fundamentals, each section stands on its own.

These articles are written to be read, not scanned. The narrative style is intentional — understanding comes from following the logic, not memorizing the output.
