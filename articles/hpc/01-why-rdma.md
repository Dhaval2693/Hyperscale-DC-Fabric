# Why RDMA Exists

Training a large language model requires distributing computation across thousands of GPUs. Each GPU processes a partition of the training data and computes gradients. At regular intervals, those gradients must be aggregated across all GPUs — each GPU needs to know the sum of gradients from every other GPU before it can update its model weights and continue to the next training step.

This gradient synchronization step is the bottleneck. The time spent waiting for gradients to arrive from other GPUs is time that the GPUs are idle — massively expensive hardware sitting unused. At the scale of thousands of GPUs, even a millisecond of extra latency in the synchronization step multiplies into significant training slowdown.

Standard TCP/IP networking — the same networking used for web requests and file transfers — is not fast enough for this use case. Not because the bandwidth is insufficient (100GbE and 400GbE links are common), but because the **software overhead of the network stack** introduces latency that GPU training cannot tolerate.

**RDMA (Remote Direct Memory Access)** eliminates that overhead.

## The Problem with Standard TCP/IP

When a server sends data via TCP:
1. The application calls `send()` — data is copied from the application's buffer to a kernel socket buffer
2. The TCP stack adds headers, performs congestion control calculations, manages the send window
3. The data is copied from the kernel buffer to the NIC's transmit buffer
4. The NIC sends the packet

On the receiving side:
1. The NIC receives the packet and copies it to the kernel receive buffer (DMA)
2. The kernel TCP stack processes the packet — validates checksums, sends ACKs, manages receive window
3. The application calls `recv()` — data is copied from the kernel buffer to the application's buffer
4. The application is notified that data is available

This path involves multiple data copies and multiple kernel context switches. For small, frequent messages (like gradient updates), the overhead per message is significant relative to the actual data being transferred. The CPUs on both sides are spending a large fraction of their cycles on network stack processing rather than useful computation.

**The kernel is the bottleneck.** Every network operation goes through the kernel, and the kernel adds latency that is measured in microseconds to tens of microseconds — unacceptable when the goal is GPU synchronization at nanosecond-level compute rates.

## What RDMA Does Differently

RDMA moves data **directly between the memory of two remote machines, bypassing the operating system kernel on both sides**.

With RDMA:
1. The application registers a memory region with the RDMA NIC (called an HCA — Host Channel Adapter, in InfiniBand terminology, or RNIC in RoCEv2 terminology)
2. The application posts a send operation: "send the contents of memory address X, length Y, to remote memory address Z on machine B"
3. The RDMA NIC reads the data directly from the application's memory (no kernel involvement, no copy to kernel buffer)
4. The NIC sends the data across the network
5. The remote RDMA NIC receives the data and writes it directly to the pre-registered remote memory address — without waking the remote CPU
6. The remote application is notified via a completion queue entry that data has arrived

**What is eliminated:**
- No kernel system calls for each send/receive
- No data copies between application memory and kernel buffers
- No CPU involvement on the receive side for the actual data movement
- No TCP connection management overhead

The result: RDMA latency is measured in single-digit microseconds (versus tens of microseconds for kernel-bypass TCP, and hundreds of microseconds for standard TCP). Throughput saturates the wire because the NIC, not the CPU, drives data movement.

## The Two RDMA Verbs

RDMA operations come in two fundamental types:

**Two-sided operations (Send/Receive):** Both sides participate. The sender posts a Send; the receiver must have posted a Receive ahead of time. When the Send arrives, it is placed in the pre-registered receive buffer. Both sides are involved. Used for message-passing communication patterns.

**One-sided operations (Read/Write):** Only the initiator is involved. A remote Read fetches data from another machine's memory without the remote CPU being notified or involved. A remote Write places data into another machine's memory without remote CPU involvement. The remote CPU only sees the data after it has already arrived. One-sided operations are the most powerful capability of RDMA — they enable true zero-copy, zero-CPU data movement.

For distributed AI training, the allreduce collective (the primary gradient synchronization operation) is implemented using RDMA Send/Receive or one-sided operations in high-performance communication libraries like NCCL (NVIDIA Collective Communications Library) and MPI.

## The Two RDMA Transport Technologies

There are two major families of RDMA networking:

**InfiniBand:** A network technology purpose-built for RDMA from the ground up. InfiniBand has its own physical layer (different from Ethernet), its own switches (InfiniBand switches, not Ethernet switches), its own addressing, and its own protocols. It is the highest-performance RDMA option and has been the dominant interconnect in HPC and AI clusters for two decades. NVIDIA's acquisition of Mellanox (the dominant InfiniBand vendor) and the explosive growth of GPU training clusters has made InfiniBand ubiquitous in AI infrastructure.

**RoCEv2 (RDMA over Converged Ethernet v2):** RDMA semantics carried over standard Ethernet (802.3) and UDP/IP. The network layer is the same Ethernet fabric used for general compute traffic. RoCEv2 eliminates the need for dedicated InfiniBand switches and allows GPU clusters to share the general-purpose DC fabric — significantly reducing infrastructure cost and complexity for organizations that do not need InfiniBand's absolute peak performance.

The choice between InfiniBand and RoCEv2 involves performance, cost, and operational complexity tradeoffs that are covered in the next article. For the network engineer, the key implication is: RoCEv2 is your problem. The Ethernet fabric must be configured correctly — with PFC and ECN — to support lossless RDMA operation. Get the network wrong, and the RDMA stack fails in ways that are difficult to diagnose.
