# Kubernetes Services and kube-proxy

Pod IPs are ephemeral. When a Pod restarts, it gets a new IP. When a deployment scales up, new Pods with new IPs appear. When a node fails and pods reschedule, they land on different nodes with different IPs. Application code cannot be written to depend on specific Pod IPs — they are implementation details that change constantly.

**Services** solve this: a stable virtual IP (the ClusterIP) that represents a set of Pods and load-balances traffic among healthy instances. Application code talks to the Service IP; the Service directs traffic to whichever Pod instances are currently running and healthy.

## How a Service Works

When you create a Kubernetes Service, three things happen:

1. **ClusterIP is assigned:** The API server allocates a virtual IP from the Service CIDR (typically 10.96.0.0/12 by default, separate from the Pod CIDR). This IP is stable — it does not change as long as the Service exists.

2. **Endpoints are maintained:** Kubernetes' Endpoints controller watches the Pods that match the Service's selector. As Pods come and go, the Endpoints object is updated with the current set of healthy Pod IPs and ports. The Endpoints object is the real-time mapping from a Service to its backing Pods.

3. **kube-proxy programs the data plane:** On every node in the cluster, kube-proxy watches for Service and Endpoints changes and programs the node's networking stack to intercept traffic to the ClusterIP and redirect it to a backing Pod.

## kube-proxy: iptables Mode

The default kube-proxy implementation uses **iptables** to intercept traffic destined for ClusterIPs.

When a Service is created (e.g., ClusterIP 10.96.1.100, port 80), kube-proxy adds iptables rules on every node:

```
-A KUBE-SERVICES -d 10.96.1.100/32 -p tcp --dport 80 -j KUBE-SVC-XXXXX
-A KUBE-SVC-XXXXX -j KUBE-SEP-POD1  (33% probability)
-A KUBE-SVC-XXXXX -j KUBE-SEP-POD2  (50% of remaining = 33%)
-A KUBE-SVC-XXXXX -j KUBE-SEP-POD3
-A KUBE-SEP-POD1 -j DNAT --to-destination 10.244.1.5:80
-A KUBE-SEP-POD2 -j DNAT --to-destination 10.244.2.7:80
-A KUBE-SEP-POD3 -j DNAT --to-destination 10.244.3.2:80
```

Any packet destined for 10.96.1.100:80 hits the KUBE-SERVICES chain, gets randomly redirected to one of the backing Pods via DNAT (destination NAT), and flows directly to that Pod. The source IP of the original client is preserved. The destination IP is rewritten to a real Pod IP before routing.

This works but has a well-known scalability problem: every Service adds iptables rules that are evaluated linearly. With 10,000 Services (not unusual in a large Kubernetes cluster), each packet must traverse potentially 40,000+ iptables rules to find its match. This adds measurable latency and significant CPU overhead on nodes with high traffic rates.

## kube-proxy: IPVS Mode

**IPVS (IP Virtual Server)** is a kernel-level load balancer built into Linux, originally designed for high-performance load balancing. kube-proxy can use IPVS instead of iptables, with significant performance advantages.

IPVS uses hash tables for lookup — O(1) regardless of the number of Services, compared to O(n) for iptables chains. For clusters with thousands of Services, this is the difference between microsecond and millisecond rule evaluation.

IPVS also supports multiple load balancing algorithms: round-robin, least connections, destination hashing, source hashing. iptables supports only random weighted selection.

For large production clusters — which LinkedIn would operate — IPVS mode is typically recommended. The tradeoff is slightly more complex setup and debugging (IPVS rules are not as easy to inspect as iptables rules).

## Service Types

**ClusterIP (default):** A virtual IP reachable only from within the cluster. This is what most internal services use — microservices talking to databases, backend services talking to caches. External traffic cannot reach a ClusterIP directly.

**NodePort:** Exposes the Service on a static port on every node's physical IP. External traffic can reach `NodeIP:NodePort` and kube-proxy redirects it to the Service's backing Pods. Useful for development and simple external access, but not appropriate for production traffic at scale — every request hits a specific node before being load-balanced.

**LoadBalancer:** Provisions an external load balancer (cloud provider LB, MetalLB on bare-metal) with a stable external IP. External traffic hits the LB, which distributes to nodes, which then forward to Pods. This is the production model for exposing services externally.

**ExternalName:** Maps a Service to an external DNS name. No proxy, just DNS CNAME. Useful for gradually migrating external services into the cluster.

## DNS in Kubernetes

Kubernetes runs a cluster DNS server (typically CoreDNS) that resolves Service names to their ClusterIPs. Applications in Pods can reach a Service named `my-service` in the same namespace simply by using the hostname `my-service` — the DNS search domain adds the full qualified name.

Services are reachable at: `<service-name>.<namespace>.svc.cluster.local`

Pods' `/etc/resolv.conf` is configured by Kubernetes to use the cluster DNS server and include the appropriate search domains. This DNS resolution is how microservices discover each other in Kubernetes — not through hardcoded IPs, not through service registries, but through standard DNS with the cluster DNS server as the authoritative resolver for the cluster's domain.

## What This Means for DC Network Engineers

When Kubernetes Services are used in a DC environment, the DC network team needs to understand:

**ClusterIPs are virtual — they do not appear on the DC fabric.** Traffic to 10.96.1.100 is intercepted by iptables or IPVS on the node before it ever hits the physical NIC. The DC fabric never sees ClusterIP addresses. Trying to route to a ClusterIP from outside the cluster will fail.

**NodePort and LoadBalancer traffic does appear on the DC fabric.** External traffic enters through a real node IP or a load balancer IP — both visible to the DC fabric. Network engineers need to ensure the fabric can route to these addresses and that appropriate ACLs and QoS policies are applied.

**Service load balancing is separate from DC load balancing.** kube-proxy load-balances among Pods inside the cluster. External load balancers (F5, AVI, cloud LBs) distribute traffic among nodes outside the cluster. These are two independent layers of load balancing, and they need to coexist correctly.

**Pod networking health affects Service behavior.** If a Pod's CNI setup is broken, traffic routed to that Pod by kube-proxy will be dropped — but the Service will keep routing to it until the Pod's health check fails and Kubernetes removes it from the Endpoints. Understanding the relationship between Pod network health and Service availability is essential for troubleshooting production issues.
