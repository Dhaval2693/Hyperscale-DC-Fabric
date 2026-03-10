# VNI and VTEP: The Building Blocks of VXLAN

Every VXLAN deployment is built on two core concepts. The **VNI** defines which virtual network a piece of traffic belongs to. The **VTEP** is the device that moves traffic between the virtual network and the physical underlay. Understanding how they work — and how they relate to each other — is the foundation of everything that follows in VxLAN.

Start with the VNI. The **VXLAN Network Identifier** is a 24-bit value carried in the VxLAN header of every encapsulated packet. It plays the same conceptual role as a VLAN tag: it identifies which isolated segment a frame belongs to. Two virtual machines in VNI 10001 can communicate with each other freely. A virtual machine in VNI 10001 is completely isolated from one in VNI 10002, even if they are running on the same physical server. The VNI is how multi-tenancy is expressed at the packet level — it is the segment identifier that travels with the traffic all the way from ingress VTEP to egress VTEP.

Each VNI maps to a virtual network interface on the VTEP device — conceptually similar to a VLAN's SVI interface. That interface represents the Layer 2 broadcast domain for that segment. Local traffic within the same VNI on the same VTEP stays local. Traffic destined for a MAC address on a remote VTEP gets encapsulated with the appropriate VNI and sent across the underlay.

Now the **VTEP** — the **VXLAN Tunnel Endpoint**. This is the device that sits at the boundary between the overlay and the underlay. In a data center with a Clos fabric, the VTEP is typically the leaf switch — the top-of-rack device that connects directly to servers. In some architectures, particularly with software-defined networking, the VTEP function can live in the server's hypervisor or NIC, eliminating the need for hardware VTEPs at the leaf. But conceptually the role is the same regardless of where it runs.

A VTEP has two logical faces. The first faces the underlay: a unique IP address assigned to the VTEP that the physical routing protocol — typically BGP in a Clos fabric — advertises and makes reachable across the fabric. This is the address that other VTEPs send encapsulated traffic to. Every leaf switch has its own VTEP IP, usually configured on a loopback interface, and the underlay ensures that every VTEP can reach every other VTEP by IP. The VTEP does not care how many physical hops separate it from its peer — as long as the IP is reachable, the tunnel can be built.

The second face looks toward the servers. Here the VTEP maintains a table that maps local MAC addresses to their VNIs, and remote MAC addresses to the remote VTEP IPs where those endpoints live. This is the **MAC-to-VTEP mapping table** — the VxLAN equivalent of a MAC address table, but instead of mapping MAC addresses to ports, it maps them to remote tunnel endpoints. When a server sends a frame to a MAC address the VTEP knows, the VTEP looks up the VNI and the remote VTEP IP, encapsulates the frame, and sends it. When a frame arrives for a local server, the VTEP decapsulates it and delivers it to the correct port.

```
                   ┌─────────────────────────────────────┐
                   │              Leaf Switch              │
                   │                 (VTEP)                │
                   │                                       │
  Servers ────────►│  VNI Interfaces   Underlay IP         │────► Spine
                   │  (per-segment)    (Loopback)          │
                   │                                       │
                   │  MAC-to-VTEP mapping table            │
                   │  MAC A → VNI 100 → VTEP 10.0.0.2     │
                   │  MAC B → VNI 200 → VTEP 10.0.0.3     │
                   └─────────────────────────────────────┘
```

The design creates a clear separation of concerns. The underlay routing protocol only needs to distribute VTEP loopback addresses — a small, stable set of IP prefixes that changes only when leaf switches are added or removed. It does not carry any tenant information, any MAC addresses, or any VNI mappings. All of that lives in the overlay control plane. The underlay stays lean; the overlay carries the complexity.

The critical question that follows from this design is: how does a VTEP learn the mapping between a remote MAC address and the remote VTEP IP where that MAC lives? A server on Leaf 1 sends a frame to a MAC address on Leaf 3. Leaf 1's VTEP needs to know that the destination MAC is behind Leaf 3's VTEP IP — and it needs to learn this without flooding the entire fabric. That learning problem is what the VxLAN control plane solves, and it can be solved in several different ways. In the next article, we will trace exactly what happens to a packet as it travels from one server to another through a VxLAN fabric.
