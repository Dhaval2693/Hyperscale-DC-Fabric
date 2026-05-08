# Host Networking and TCP Tuning in Kubernetes

The default Kubernetes networking model gives each Pod its own network namespace — its own IP, its own routing table, its own interface. This isolation is fundamental to Kubernetes' security and multi-tenancy model.

But there are cases where isolation is the wrong choice. High-performance workloads — particularly HPC applications and some network-intensive services — cannot afford the overhead of the Pod network stack. These workloads use **host networking**, where the Pod shares the node's network namespace directly, operating as if it were a process running on the host itself.

Understanding host networking, its tradeoffs, and how to tune the host TCP stack for these workloads is important for any network engineer working with modern DC infrastructure.

## Host Networking Mode

When a Pod is configured with `hostNetwork: true`, it shares the node's network namespace:

```yaml
spec:
  hostNetwork: true
  containers:
  - name: high-performance-app
    image: my-hpc-app:latest
```

A Pod running in host networking mode:
- Uses the node's IP address (not a Pod IP)
- Sees all of the node's network interfaces
- Can bind to ports on the node's real IP
- Communicates with the DC fabric without going through any pod overlay

**Why this matters for performance:** Every network packet in a standard Pod traverses the veth pair (two virtual interfaces), goes through the host's routing stack, and may traverse a VXLAN overlay. For workloads running RDMA, for network monitoring daemons that need to capture traffic, or for performance-critical services where even a few microseconds of extra latency matter, this extra processing is unacceptable.

Workloads that commonly use host networking:
- **Network monitoring and telemetry agents** (need direct access to host interfaces)
- **CNI plugins themselves** (must configure host networking; cannot use pod networking to do so)
- **RDMA workloads** (need direct access to RDMA-capable NICs without overlay)
- **High-frequency trading or latency-critical applications**
- **DaemonSets for infrastructure operations** (log collectors, node agents, monitoring)

**The security tradeoff:** A Pod in host networking mode has elevated access to the host's network stack. A compromised container in host networking mode can affect the host's network configuration, listen on privileged ports, and potentially interact with other pods' traffic. Host networking should be restricted to trusted, infrastructure-level workloads — not arbitrary application containers.

## TCP Tuning: Why Defaults Are Wrong for HPC

Linux's default TCP settings were designed for general-purpose networking — a mix of latency-sensitive interactive traffic and bulk transfers on networks ranging from slow DSL connections to Gigabit Ethernet. In a modern DC with 100GbE links and sub-millisecond RTTs, the defaults are severely conservative.

The most impactful parameters:

**TCP Buffer Sizes**

The TCP receive and send buffers determine how much data can be in flight per connection. On a 100GbE link with 500-microsecond RTT:

```
Bandwidth-delay product = 100Gbps × 0.0005s = 50Mbits = 6.25MB
```

If the TCP receive buffer is smaller than 6.25MB, TCP cannot fully utilize the 100GbE link because the sender must wait for ACKs before sending more data.

Linux defaults are `rmem_max = 131072` (128KB) and `wmem_max = 131072` (128KB) — orders of magnitude below the bandwidth-delay product of a 100GbE link.

Tuning for DC networks:
```bash
# Maximum socket receive and send buffer sizes
sysctl -w net.core.rmem_max=134217728   # 128MB
sysctl -w net.core.wmem_max=134217728   # 128MB

# TCP-specific buffer autotuning range (min, default, max)
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"
```

**TCP Backlog and Connection Queue**

Under high connection rates (thousands of new connections per second, common in microservices architectures), the TCP SYN backlog queue can become a bottleneck.

```bash
sysctl -w net.core.somaxconn=65535          # Max pending connections
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
sysctl -w net.core.netdev_max_backlog=5000  # NIC receive queue depth
```

**TCP Congestion Control**

For DC environments running DCTCP, the congestion control algorithm must be set explicitly:

```bash
sysctl -w net.ipv4.tcp_congestion_control=dctcp
sysctl -w net.ipv4.tcp_ecn=1  # Enable ECN
```

For general DC traffic where DCTCP is not in use, `cubic` (the Linux default) is reasonable. `bbr` (Bottleneck Bandwidth and RTT) is an alternative congestion control algorithm from Google that performs well in high-bandwidth environments and can be used when DCTCP is not appropriate (e.g., for traffic that crosses WAN links where ECN is not available end-to-end).

**TCP Keepalive**

Long-lived connections in DC environments (persistent microservice connections, gRPC streams, NETCONF sessions) should use TCP keepalive to detect dead connections:

```bash
sysctl -w net.ipv4.tcp_keepalive_time=60      # Start keepalive after 60s idle
sysctl -w net.ipv4.tcp_keepalive_intvl=10     # Probe every 10s
sysctl -w net.ipv4.tcp_keepalive_probes=3     # 3 failures before declaring dead
```

The Linux default `tcp_keepalive_time=7200` (2 hours) is far too long for a DC environment where dead connections should be detected in under a minute.

## Applying Tuning in Kubernetes

TCP tuning parameters are kernel parameters — they apply to the host, not to individual containers (except in host networking mode). There are two approaches:

**Node-level tuning via DaemonSet:** Deploy a privileged DaemonSet that runs `sysctl` commands on every node at startup. This is the most common approach — it runs automatically as nodes join the cluster and applies consistently across all nodes.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: sysctl-tuner
spec:
  selector:
    matchLabels:
      name: sysctl-tuner
  template:
    spec:
      hostNetwork: true
      hostPID: true
      initContainers:
      - name: sysctl
        image: busybox
        command: ["sysctl", "-w", "net.core.rmem_max=134217728"]
        securityContext:
          privileged: true
```

**Pod-level sysctl (for namespaced parameters):** Some sysctl parameters are namespaced — they apply per network namespace rather than globally. For these, Kubernetes supports pod-level `sysctls` in the pod spec:

```yaml
spec:
  securityContext:
    sysctls:
    - name: net.ipv4.tcp_keepalive_time
      value: "60"
```

Note: most of the high-impact parameters (buffer sizes, congestion control) are non-namespaced and must be set at the node level.

## Kubernetes and HPC Workloads

For HPC workloads in Kubernetes — GPU training jobs, MPI-based simulation clusters, distributed model serving — the networking requirements are extreme: near-zero latency, maximum throughput, and in many cases RDMA capability.

The configuration stack for HPC pods in Kubernetes:
1. **RDMA-capable NICs** on nodes (Mellanox/NVIDIA ConnectX, or similar)
2. **Device plugin** that exposes RDMA resources to Kubernetes (kubernetes/device-plugins or NVIDIA's GPU Operator)
3. **Host networking mode** for pods that need direct RDMA access
4. **SR-IOV** (Single Root I/O Virtualization) to give pods direct access to NIC hardware queues without going through the host kernel
5. **TCP stack tuning** on nodes for any remaining TCP traffic
6. **PFC + ECN** on the DC fabric (covered in the congestion control articles)

This full stack — DC fabric, host networking, TCP tuning, RDMA device access — is what the LinkedIn JD means by "Knowledge in Kubernetes, host networking, host TCP tuning, and HPC networking." It is not a software developer's concern. It is a network engineering concern, because every layer of it intersects with the physical DC network.
