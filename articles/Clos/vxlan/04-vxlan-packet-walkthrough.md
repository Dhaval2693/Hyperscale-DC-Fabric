# How a Packet Travels Through a VXLAN Fabric

The best way to understand VxLAN encapsulation is to follow a single packet through the entire journey — from the moment a virtual machine sends a frame to the moment the destination virtual machine receives it. The path reveals exactly what each layer of the stack does and why.

Imagine a simple fabric. Two leaf switches — Leaf 1 and Leaf 2 — each connect to two spine switches for redundancy. Leaf 1 hosts a server running a virtual machine, VM-A, with IP address 10.1.1.10 and MAC address AA:AA:AA:AA:AA:AA. Leaf 2 hosts VM-B, with IP 10.1.1.20 and MAC BB:BB:BB:BB:BB:BB. Both VMs belong to VNI 10001. The VTEP IP of Leaf 1 is 192.168.1.1, and the VTEP IP of Leaf 2 is 192.168.1.2. The underlay has already distributed these loopback addresses via BGP — every leaf and spine knows how to reach every VTEP IP.

VM-A wants to send a packet to VM-B. It constructs a standard Ethernet frame:

```text
[ Src MAC: AA:AA:AA:AA:AA:AA | Dst MAC: BB:BB:BB:BB:BB:BB | IP: 10.1.1.10 → 10.1.1.20 | Payload ]
```

This frame arrives at Leaf 1's VTEP. The VTEP looks at the destination MAC address and checks its MAC-to-VTEP mapping table. It finds that BB:BB:BB:BB:BB:BB belongs to VNI 10001 and is reachable via the remote VTEP at 192.168.1.2. With that information in hand, the VTEP begins encapsulation — wrapping the original frame in four additional headers, working from the inside out.

First, the **VxLAN header** is prepended. This 8-byte header contains the VNI (10001) in a 24-bit field, along with a flags byte that marks the VNI field as valid. This is the header that identifies which virtual segment the frame belongs to.

Next, a **UDP header** wraps the VxLAN header. The destination UDP port is 4789 — the standard VxLAN port. The source UDP port is calculated as a hash of the inner frame's fields: source MAC, destination MAC, source IP, destination IP, and L4 protocol. This hash varies per flow, which is critical — it means different flows between the same pair of VTEPs will generate different source ports, and the underlay's ECMP hashing will distribute them across different physical paths. VxLAN gets ECMP utilization essentially for free, without any changes to the underlay.

Then an **outer IP header** wraps the UDP header. The source IP is Leaf 1's VTEP address (192.168.1.1). The destination IP is Leaf 2's VTEP address (192.168.1.2). This is the header the underlay actually uses to forward the packet — the spine switches see nothing but a normal IP packet destined for 192.168.1.2 and route it accordingly.

Finally, an **outer Ethernet header** is added for the first physical hop. This contains Leaf 1's MAC as the source and the MAC of whichever spine switch is the next hop toward 192.168.1.2.

The complete encapsulated packet looks like this:

```text
[ Outer Eth | Outer IP: 192.168.1.1→192.168.1.2 | UDP: src=hash, dst=4789 | VxLAN: VNI=10001 | Inner Eth | Inner IP | Payload ]
```

This packet is sent onto the physical fabric. The spine switches receive it, look at the outer IP destination (192.168.1.2), and forward it toward Leaf 2. They update the outer Ethernet header at each hop — changing the source and destination MAC to match the next physical link — but the outer IP header, the UDP header, the VxLAN header, and the inner frame all pass through untouched. The spines have no idea there is a VxLAN tunnel inside. They see an ordinary IP packet.

When the packet arrives at Leaf 2, the VTEP recognizes UDP port 4789 and begins decapsulation. It strips the outer Ethernet header, the outer IP header, the UDP header, and the VxLAN header. It checks the VNI (10001) to confirm the frame belongs to the correct segment. What remains is the original inner Ethernet frame that VM-A sent:

```text
[ Src MAC: AA:AA:AA:AA:AA:AA | Dst MAC: BB:BB:BB:BB:BB:BB | IP: 10.1.1.10 → 10.1.1.20 | Payload ]
```

Leaf 2 delivers this frame to VM-B's port. VM-B receives it exactly as if VM-A were plugged into the same switch. The entire encapsulation and transit across the physical fabric is invisible to both virtual machines.

A secondary benefit happens as a side effect of this exchange: Leaf 2's VTEP now learns that MAC AA:AA:AA:AA:AA:AA is reachable via VTEP 192.168.1.1. It adds this to its mapping table. The next time VM-B replies to VM-A, Leaf 2 already knows where to send the return traffic. This is **data-plane learning** — the VTEP learns remote MAC-to-VTEP mappings by observing the outer IP source address on incoming encapsulated frames. It is the same mechanism Ethernet switches use to learn MAC-to-port mappings, extended to work across the VxLAN fabric.

Data-plane learning works, but it has a cost: the first frame to an unknown destination must be flooded across the fabric before the mapping is known. Flooding in a VxLAN fabric means sending the frame to every remote VTEP, which consumes bandwidth and processing on every leaf. As fabrics grow, the amount of BUM traffic — **Broadcast, Unknown unicast, and Multicast** — can become significant. The control plane approaches covered in the next article exist specifically to eliminate this flooding by distributing MAC and IP reachability information before traffic flows, rather than learning it reactively from data-plane traffic.
