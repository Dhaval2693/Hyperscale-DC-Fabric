# Kubernetes Networking in a DC Context

The previous articles covered Kubernetes networking from the inside — pods, CNI, services, host networking. This article steps back and looks at how Kubernetes integrates with the physical DC fabric — the spine-leaf network, the WAN uplinks, the security boundaries, and the operational responsibilities that belong to the DC network team rather than the Kubernetes platform team.

In large organizations, there is typically a boundary: the Kubernetes team manages the cluster, and the DC network team manages the fabric. Understanding where that boundary sits, what crosses it, and what breaks when the two teams do not coordinate is essential for a senior network engineer.

## Pod CIDR Planning: The First Intersection

Every Kubernetes cluster needs a **Pod CIDR** — a block of IP addresses to allocate to Pods. This address space must:

- Not overlap with any physical DC addressing (server IPs, switch management IPs, loopback addresses)
- Not overlap with other Kubernetes clusters running in the same DC
- Not overlap with VPN or DCI addresses that are reachable from the DC
- Be large enough for the maximum number of Pods the cluster will ever run

The Pod CIDR decision is made before the cluster is deployed. Changing it later requires rebuilding the cluster. This is a joint decision between the Kubernetes platform team (who knows how many Pods the cluster needs) and the DC network team (who knows what address space is available and what conflicts exist).

A typical planning model:
- Reserve a /16 for Kubernetes Pod networking (e.g., 10.244.0.0/16)
- Divide into /24 per node (256 addresses per node, minus reserved addresses ≈ 250 usable Pod IPs per node)
- For clusters larger than 256 nodes, use a /8 or plan more carefully

The Service CIDR (for ClusterIPs) must also be planned separately — 10.96.0.0/12 is the default, giving ~1M Service IPs.

## BGP Integration: Direct Routing

In DC environments where Calico or Cilium runs in BGP mode (direct routing, no overlay), the DC fabric must peer BGP with each Kubernetes node. This is a concrete, operational integration between the DC fabric and the Kubernetes cluster.

Each node runs a BGP daemon (Calico uses Bird or its own daemon; Cilium uses its own). The daemon advertises the node's Pod CIDR into the BGP session with the leaf switch. The leaf switch accepts these routes and redistributes them through the spine-leaf fabric.

**Configuration on the leaf switch side (Arista EOS example):**
```
router bgp 65000
   neighbor 192.168.1.10 remote-as 65001   ! k8s node
   neighbor 192.168.1.10 description kubernetes-node-1
   address-family ipv4
      neighbor 192.168.1.10 activate
      neighbor 192.168.1.10 prefix-list ALLOW-POD-CIDR in
      neighbor 192.168.1.10 maximum-routes 300
```

The prefix-list `ALLOW-POD-CIDR` filters to only accept Pod CIDR routes from the node — you do not want a misconfigured Kubernetes node to advertise arbitrary routes into your DC fabric.

**What the DC network team must provide:**
- BGP AS numbers for the cluster and for the fabric
- Peer IP addresses on the leaf switches for each node
- Prefix list policies to filter accepted routes
- Monitoring for BGP session state between nodes and leaf switches

**What breaks when it goes wrong:**
- A node loses its BGP session with the leaf → Pods on that node become unreachable from the rest of the cluster → Service health checks fail → Kubernetes eventually drains the node
- A node advertises an incorrect Pod CIDR (configuration error) → routing black holes appear in the fabric → traffic to a range of legitimate IPs is hijacked

## External Load Balancer Integration

For Services of type LoadBalancer on bare-metal Kubernetes (without cloud provider integration), **MetalLB** is the common solution. MetalLB watches for LoadBalancer Services, allocates external IPs from a configured pool, and advertises those IPs into the DC fabric via BGP.

This means MetalLB is another BGP peer on your fabric — typically peering with the leaf switches that connect the Kubernetes cluster nodes. The DC network team must:
- Allocate a pool of external IP addresses for MetalLB (distinct from Pod CIDR and Service CIDR — these are real, routable DC addresses)
- Configure BGP peering with MetalLB's speaker pods
- Apply appropriate route filtering and QoS to external Service traffic

**Ingress controllers** (NGINX, Traefik, HAProxy Ingress) typically sit behind a MetalLB LoadBalancer Service and handle HTTP-layer routing — routing traffic to different backend Services based on URL path or hostname. From the DC network team's perspective, Ingress controllers appear as pods behind an external IP — the same as any other Service.

## Kubernetes Network Policy and DC ACLs

Kubernetes **NetworkPolicy** is a cluster-level firewall — a set of rules that control which pods can communicate with which other pods. NetworkPolicy is implemented by the CNI plugin (Calico, Cilium, etc.) using iptables, eBPF, or similar host-level mechanisms.

NetworkPolicy operates on Pod IP addresses and namespace selectors — constructs that are invisible to the DC fabric. A NetworkPolicy that says "pods in namespace A can only talk to pods in namespace B" is implemented entirely inside the Kubernetes nodes — the DC fabric never sees it.

This creates an important operational boundary:
- **Pod-to-pod security** within the cluster: NetworkPolicy (Kubernetes team responsibility)
- **Pod-to-external security** at the fabric level: traditional ACLs on the leaf switches (DC network team responsibility)
- **North-south traffic filtering**: applied at the border leaf switches or upstream firewalls

The two systems must be coordinated. A NetworkPolicy that permits traffic to a Pod is ineffective if the DC ACL blocks the traffic before it reaches the node. Conversely, DC ACLs that are too permissive are not compensated by NetworkPolicy alone if a node is compromised.

## Observability: What the DC Network Team Sees

When you look at a leaf switch's traffic counters in a cluster that runs Kubernetes, you see:

- High volumes of UDP traffic (VXLAN-encapsulated pod traffic, if overlay CNI is in use)
- BGP sessions from node IPs (if direct routing CNI is in use)
- Occasional spikes in ARP traffic (from pods starting up)
- TCP flows between node IPs for inter-pod traffic (in direct routing mode)

Understanding what you are seeing — and knowing when a traffic pattern is normal Kubernetes behavior versus a misconfiguration or attack — requires understanding the networking model.

A leaf switch that shows a BGP session suddenly dropping is probably a Kubernetes node that is being drained, rebooted, or has lost its BGP daemon. A sudden spike in VXLAN traffic from a node is probably a workload scaling event. Unusual traffic from pod IPs to external destinations may indicate a pod networking misconfiguration or a security incident.

The DC network team cannot operate Kubernetes infrastructure effectively without understanding what Kubernetes generates on the wire. And Kubernetes administrators cannot diagnose network issues without understanding what the DC fabric does with Kubernetes traffic. The operational boundary exists, but the knowledge must overlap.
