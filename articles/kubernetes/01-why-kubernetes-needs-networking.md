# Why Kubernetes Needs Its Own Networking Model

Before Kubernetes, deploying an application on a server meant giving that server an IP address and opening ports on it. Simple. The server was a fixed thing, with a fixed location, and its network identity was stable.

Kubernetes exists to make servers interchangeable. A containerized application does not run on "the server at 10.1.1.50." It runs on "whichever node has available capacity right now." The scheduler places workloads dynamically, restarts failed containers on different nodes, scales horizontally by adding more container instances, and evicts containers when nodes need to be reclaimed. The entire model assumes that containers are ephemeral and their placement is unpredictable.

This creates a fundamental networking problem: if you do not know where a container will run, you cannot pre-assign it a fixed IP address in the traditional sense. And if IP addresses are ephemeral — assigned when a container starts, released when it stops — you need a networking model that makes ephemeral, dynamically-placed workloads reachable as if they were stable.

Kubernetes solves this with a specific networking model that every network engineer working with modern DC infrastructure needs to understand.

## The Kubernetes Networking Model

Kubernetes defines a networking model with four core requirements:

**1. Every pod gets its own IP address.** A Pod is Kubernetes' basic unit of deployment — one or more containers that share a network namespace. Each Pod has its own unique IP address, visible across the entire cluster. Two pods can communicate directly using each other's Pod IPs without NAT, regardless of which nodes they run on.

**2. All pods can communicate with all other pods without NAT.** This is the flat network requirement. In a traditional infrastructure, you might use NAT to translate between private addresses in different subnets. Kubernetes prohibits this between pods. Pod A at 10.244.1.5 communicates directly with Pod B at 10.244.2.7 using those addresses — no address translation.

**3. Agents on a node can communicate with all pods on that node.** Node agents (the kubelet, monitoring daemons, CNI plugins) can reach pods running on the same node without going through the cluster network.

**4. Pods that declare a port should be accessible via that port.** Containers that listen on a port are reachable via their Pod IP and that port.

These four requirements define what any Kubernetes networking implementation must provide. How it provides them is left to the CNI plugin.

## Why This Is Hard

The flat, no-NAT, every-pod-gets-an-IP model sounds simple. Implementing it across a multi-node cluster on top of standard Linux networking is not.

Consider: a Pod on Node-A at 10.244.1.5 needs to send traffic to a Pod on Node-B at 10.244.2.7. The packet leaves Node-A's kernel. It hits the physical network. The physical network needs to know how to route 10.244.2.7 — but 10.244.x.x is not a physical network address. It is an overlay address assigned by Kubernetes. The physical network does not have routes to it.

There are several ways to bridge this gap:

**Overlay networking:** Encapsulate pod-to-pod traffic in an outer IP header using the node's physical IP as the outer address. VXLAN or IP-in-IP tunneling is common. The outer packet is routable on the physical network; the inner packet carries the Pod IPs. The CNI plugin on each node handles encapsulation and decapsulation.

**Direct routing:** Advertise Pod CIDR routes for each node into the physical network via BGP. The physical network (the DC fabric) installs routes: "to reach 10.244.1.0/24, send to Node-A at 192.168.1.10." Pod traffic flows directly through the physical network without encapsulation overhead. This requires the physical network to participate in pod routing — which means the network engineering team needs to know about it.

**Host-local routing:** For single-node setups or test environments, use host routes on each node. Does not scale to multi-node clusters.

In production DC environments — including hyperscalers' — the typical choice is either direct routing via BGP (preferred for performance and simplicity in spine-leaf fabrics) or VXLAN overlay (preferred when the physical network cannot participate in pod routing).

## The Components You Need to Know

**Pod:** The basic unit. Each Pod has one or more containers sharing a network namespace — they see the same IP address, the same network interfaces, the same port space. Containers in a Pod communicate via localhost.

**Node:** The physical or virtual machine running a Kubernetes worker. Each node runs a kubelet (manages pods), a container runtime (Docker, containerd), a kube-proxy (handles Service networking), and a CNI plugin (manages pod network attachment).

**CNI (Container Network Interface):** A plugin interface that Kubernetes calls when a Pod is created or deleted. The CNI plugin assigns the Pod an IP address, sets up routing and network interfaces inside the Pod's namespace, and configures the node's network to reach the Pod. Kubernetes is CNI-agnostic — it defines the interface, not the implementation.

**Service:** An abstraction over a set of pods. Since Pod IPs change constantly (pods restart, get rescheduled), you need a stable address to reach a set of pods regardless of which instances are currently running. Services provide this — a stable ClusterIP that load-balances to healthy pods. Services are what application code actually talks to; Pod IPs are an implementation detail.

**kube-proxy:** The component that implements Service load balancing. It watches the Kubernetes API for Service and Endpoint changes and programs the node's network (via iptables or IPVS) to intercept Service IP traffic and redirect it to the correct Pod IPs.

## Why This Matters for a DC Network Engineer

When Kubernetes runs in a data center (as opposed to a managed cloud service like EKS or GKE), the DC network team becomes responsible for:

- Allocating Pod CIDR ranges that do not conflict with the DC's existing address space
- If using direct routing: peering each node's BGP daemon (typically Bird or FRR, running as part of the CNI plugin) with the DC fabric's leaf switches
- Ensuring the physical network carries the pod-to-pod traffic with appropriate QoS markings
- Understanding how pod traffic appears on the physical fabric: a 10GbE server uplink that shows unusual traffic patterns may be VXLAN-encapsulated pod traffic, which looks like normal UDP traffic to the switch

Modern DC network engineering roles list Kubernetes as a basic qualification — not a nice-to-have. The reason is exactly this: Kubernetes network traffic runs on the DC fabric. A network engineer who does not understand the Kubernetes networking model cannot properly design, operate, or troubleshoot the infrastructure that Kubernetes runs on.

The next articles go deeper into CNI plugins, Services, host networking, and how Kubernetes networking integrates with the DC fabric.
