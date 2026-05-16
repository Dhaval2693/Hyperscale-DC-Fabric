# CNI and Pod Networking

When Kubernetes needs to give a new Pod a network identity, it does not have built-in networking code. Instead, it calls out to a **CNI (Container Network Interface)** plugin — a separately installed component that handles all the details of attaching the Pod to the network, assigning it an IP address, and setting up routing so the Pod can be reached.

This design is intentional. Different environments have different networking requirements — a bare-metal DC has different constraints than a cloud VM environment — and Kubernetes cannot be opinionated about which networking approach to use. The CNI interface defines what Kubernetes will tell the plugin (a Pod is being created on this node) and what the plugin must deliver (the Pod has an IP, it is reachable). Everything in between is the plugin's responsibility.

## What Happens When a Pod Is Created

Walk through the sequence:

1. The scheduler places a Pod on Node-A.
2. The kubelet on Node-A receives the Pod spec and starts creating the container.
3. Before starting the application container, kubelet creates a **pause container** — a minimal container whose only job is to hold the network namespace open. The pod's network namespace will outlive any individual container restart.
4. kubelet calls the CNI plugin binary with the Pod's metadata and the network namespace path.
5. The CNI plugin:
   - Allocates an IP address for the Pod from the node's Pod CIDR range (e.g., 10.244.1.0/24 for Node-A)
   - Creates a **veth pair** — a virtual Ethernet pair where one end is placed inside the Pod's network namespace and the other end stays on the host's root namespace
   - Assigns the Pod IP to the interface inside the Pod namespace
   - Sets up routing: inside the Pod, a default route pointing to the veth peer on the host; on the host, a route to the Pod's IP via the veth interface
   - Calls any chained CNI plugins (for bandwidth limiting, firewall policy, etc.)
   - Returns the assigned IP to kubelet
6. kubelet starts the application containers, which join the network namespace already configured by the CNI plugin.

The Pod is now running with its own IP. Traffic to that IP goes through the veth pair into the Pod's network namespace. Traffic from the Pod exits through the veth pair and hits the host's routing stack.

## How Pod-to-Pod Traffic Flows (Same Node)

When Pod-A (10.244.1.5) sends traffic to Pod-B (10.244.1.7), both on the same node:

- Pod-A's packet exits via its veth interface into the host
- The host has a route: 10.244.1.7 via veth-pod-b
- The packet is delivered directly to Pod-B's veth interface
- No physical network involved

This is pure host networking — fast, no encapsulation, handled entirely by the Linux kernel's routing.

## How Pod-to-Pod Traffic Flows (Different Nodes)

Pod-A on Node-A (10.244.1.5) → Pod-C on Node-B (10.244.2.7). This is where CNI plugins differentiate.

**Overlay approach (VXLAN, used by Flannel's VXLAN backend, Calico in VXLAN mode):**
- Pod-A's packet exits into Node-A's host network
- The CNI plugin has set up a VXLAN interface (e.g., `flannel.1` or `vxlan.calico`)
- A route on Node-A says: 10.244.2.0/24 via the VXLAN interface
- The VXLAN interface encapsulates the Pod packet in UDP/VXLAN with outer IP: Node-A (192.168.1.10) → Node-B (192.168.1.11)
- The physical network routes the outer UDP packet normally
- Node-B's VXLAN interface decapsulates, delivers the original pod packet
- Node-B's host routing delivers the packet to Pod-C via its veth

**Direct routing approach (BGP, used by Calico in BGP mode, Cilium in native routing mode):**
- Pod-A's packet exits into Node-A's host network
- Node-A is running a BGP daemon (Bird or FRR) that has advertised its Pod CIDR (10.244.1.0/24) to the DC fabric's leaf switch
- The DC fabric has a route: 10.244.1.0/24 via Node-A, 10.244.2.0/24 via Node-B
- Pod-A's packet to 10.244.2.7 is routed directly by the DC fabric's spine-leaf, no encapsulation
- Node-B receives the packet, routes to Pod-C via its local veth route

The direct routing approach has lower overhead (no encapsulation) and is easier to troubleshoot (traffic is visible on the DC fabric without decapsulation). But it requires the DC fabric to participate: leaf switches must peer BGP with nodes and install Pod CIDR routes. This is why DC network engineers need to know about CNI — in a direct-routing deployment, the CNI's BGP daemon is a peer on your fabric.

## Major CNI Plugins

**Calico:** The most widely deployed CNI in production DC environments. Supports both VXLAN overlay and direct routing (BGP). In BGP mode, Calico uses Bird or its own BGP daemon on each node to peer with the network fabric and advertise Pod CIDRs. Calico also implements Kubernetes NetworkPolicy using eBPF or iptables, providing fine-grained pod-to-pod firewall rules. For DC deployments with existing BGP fabrics, Calico in BGP mode is the common choice.

**Cilium:** Uses eBPF for data-plane packet processing — bypassing iptables entirely for higher performance and lower latency. Supports VXLAN, Geneve, and native routing modes. Increasingly common in high-performance DC environments, particularly for HPC and AI/ML workloads where network latency is critical. Cilium's eBPF data plane provides visibility into pod-level traffic without TCP dump overhead.

**Flannel:** Simple, stable, widely used in development and smaller clusters. VXLAN overlay only — does not support direct routing. Does not implement NetworkPolicy. For production DC environments at hyperscale, Flannel alone is insufficient, but understanding it provides a baseline for understanding how VXLAN-based pod networking works.

**AWS VPC CNI:** AWS-specific CNI that assigns actual VPC IP addresses to Pods. Each Pod gets a secondary private IP from the node's ENI (Elastic Network Interface). Pod traffic flows natively through the VPC fabric without any overlay. Understanding why AWS's CNI works differently from a generic CNI is directly relevant to the DC networking context.

## IP Address Management (IPAM)

Every CNI needs to allocate IP addresses to pods. IPAM (IP Address Management) within a CNI is typically node-scoped: each node owns a Pod CIDR (e.g., /24), and the CNI allocates Pod IPs sequentially within that range.

The cluster administrator must ensure:
- Pod CIDR ranges are large enough for the maximum pods per node (default 110 in most Kubernetes installations)
- Pod CIDR ranges across all nodes do not overlap
- Pod CIDR address space does not conflict with physical DC addressing or VPN ranges

In a DC with existing address management policies (RFC 1918 space managed by an IPAM system), the Kubernetes Pod CIDR must be planned as a separate block — typically a /16 subdivided into /24s per node. This planning is a DC network engineering responsibility, not a Kubernetes administration responsibility.
