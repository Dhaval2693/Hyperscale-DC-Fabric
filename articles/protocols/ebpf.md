# eBPF for Networking

eBPF is one of the most significant additions to the Linux kernel in the last decade. For network engineers, it represents a fundamental shift in how network policy, observability, and data-plane processing can be implemented — moving from kernel modules and iptables to a programmable, safe, high-performance in-kernel execution environment.

Understanding what eBPF is and what it enables is becoming a basic literacy requirement for network engineers working with modern Linux-based DC infrastructure.

## What eBPF Is

**eBPF (extended Berkeley Packet Filter)** is a technology that allows you to run sandboxed programs inside the Linux kernel without modifying the kernel source code or loading kernel modules.

Before eBPF, the only way to add custom logic to the kernel's network processing path was to:
- Write a kernel module (complex, dangerous — bugs can kernel panic the system)
- Modify the kernel source and recompile (requires following a release cycle)
- Use user-space packet processing frameworks (high performance but misses kernel-space events)

eBPF provides a middle path: write a program in a restricted C-like language, compile it to eBPF bytecode, and load it into the kernel. The kernel's eBPF verifier checks the program before loading — ensuring it cannot crash the kernel, cannot access arbitrary memory, and will terminate. If it passes verification, the program runs inside the kernel with near-native performance, hooked into specific kernel events.

**eBPF programs are attached to hooks** — specific points in the kernel where the program is called when an event occurs. Network-relevant hooks include:

- **XDP (eXpress Data Path):** The earliest possible point in the network receive path, before the kernel's networking stack. XDP programs run in the NIC driver context and can drop, redirect, or pass packets with minimal overhead. Used for DDoS mitigation, load balancing, and packet filtering at wire speed.
- **TC (Traffic Control):** Both ingress and egress. Runs after XDP on ingress, and on the egress path before the packet leaves the host. Used for packet classification, marking, and modification.
- **Socket hooks:** Intercept socket-level system calls and operations. Used by Cilium for socket-based load balancing.
- **Tracepoints and kprobes:** Instrument any kernel function call for observability.

## eBPF for Network Policy: Replacing iptables

The most operationally significant use of eBPF in networking is **replacing iptables** for network policy enforcement.

iptables has been the Linux firewall mechanism for two decades. Its problems at scale:
- Rules are evaluated linearly — O(n) per packet as rule count grows
- Adding or removing rules locks the entire iptables ruleset (briefly pauses traffic in some implementations)
- No per-flow state awareness beyond basic connection tracking
- Not observable — you cannot see which rules are matching without adding logging

**Cilium's eBPF data plane** replaces iptables entirely. Kubernetes NetworkPolicy is implemented as eBPF programs attached at TC hooks on each network interface. eBPF's hash-map data structures allow O(1) rule lookup regardless of policy count. Rule updates are atomic — a new policy is loaded and the old one swapped out without interrupting traffic. Each packet's policy decision is made in eBPF, in the kernel, without system call overhead.

The result: Cilium clusters with 10,000 NetworkPolicy rules have the same per-packet overhead as clusters with 10 rules. iptables clusters degrade measurably as rule counts grow.

## eBPF for Observability: Seeing Everything

Traditional network monitoring on a Linux host is limited: tcpdump captures on specific interfaces, iptables logging adds rules for specific flows, application-level metrics are only as good as what the application exposes.

eBPF enables monitoring that was previously impossible without invasive kernel instrumentation:

**Per-flow network metrics:** An eBPF program attached to socket hooks can measure every TCP connection's throughput, retransmit count, and RTT — without modifying the application, without adding userspace overhead, and without sampling.

**Kernel networking events:** An eBPF program attached to kernel tracepoints can observe every packet drop, every TCP state transition, every socket buffer overflow — in real time, with full context (source/destination, port, PID, process name).

**Cilium Hubble:** A network observability tool built on Cilium's eBPF foundation. Hubble provides per-flow network visibility across the entire Kubernetes cluster — which pods are talking to which, at what rate, with what error rates — without any application modifications. This is network observability at Layer 7 (HTTP, gRPC, DNS) implemented entirely in eBPF.

## eBPF for Congestion Control

eBPF can implement custom TCP congestion control algorithms as kernel programs. The Linux kernel's congestion control framework exposes hooks that eBPF can attach to, allowing experiments with new congestion control algorithms without kernel patches.

For DC environments running DCTCP or custom congestion control, eBPF provides a path to:
- Deploy experimental congestion control on specific hosts without kernel upgrades
- A/B test congestion control algorithms on production traffic
- Implement host-based queue management (complementing switch-based ECN)

Facebook (Meta) developed a congestion control algorithm called **CCP (Congestion Control Plane)** that uses eBPF as the mechanism to implement datacenter-specific TCP behavior. This is the leading edge of where eBPF's network capabilities are being explored.

## eBPF for Load Balancing: XDP

Facebook's **Katran** project implements a high-performance L4 load balancer using eBPF and XDP. Traditional software load balancers run in user space — each packet crosses the kernel boundary twice (NIC → kernel → user space → kernel → NIC). XDP load balancers run at the NIC driver level — packets are classified and redirected without ever reaching the kernel networking stack.

The performance difference is significant: XDP load balancers can forward at line rate (100 Gbps+) on commodity servers with minimal CPU overhead. User-space load balancers saturate CPUs at much lower throughput.

## What This Means for the DC Network Engineer

eBPF is increasingly a tool in the network engineer's toolbox, not just the kernel developer's. Specifically:

**Cilium is replacing kube-proxy in many Kubernetes deployments.** When you operate Kubernetes on the DC fabric, you need to understand what Cilium's eBPF data plane is doing — how it implements Services, how it enforces NetworkPolicy, and how to debug it when something goes wrong.

**Hubble provides network observability that was previously unavailable.** For diagnosing microservice communication issues, Hubble's per-flow visibility is invaluable. Operating it is part of the DC network team's toolkit in Cilium-based Kubernetes environments.

**Host-based congestion control is eBPF-based.** Any future work on DCTCP deployment, host-based ECN, or custom congestion control in your DC fabric will involve eBPF. The network engineer who understands eBPF can participate in these deployments; the one who does not must rely entirely on the kernel team.

LinkedIn's DC team, which operates large-scale Kubernetes infrastructure and is building AI/ML networking capabilities, is an environment where eBPF knowledge is directly applicable and increasingly expected.
