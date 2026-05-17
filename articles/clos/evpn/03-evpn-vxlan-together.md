# EVPN and VXLAN Working Together

VXLAN and EVPN are often mentioned in the same breath, but they are solving different problems. VXLAN is the data plane — it defines how frames are encapsulated and tunneled across an IP underlay. EVPN is the control plane — it defines how VTEPs discover each other, distribute host reachability, and build forwarding tables without flooding.

Understanding how they work together, step by step, is what separates someone who knows the definitions from someone who can actually design and troubleshoot these fabrics.

## The Setup

In a typical hyperscale DC fabric:

- The **underlay** runs BGP with ECMP — every leaf has equal-cost paths to every spine, and the spines have equal-cost paths to every leaf. IP reachability across the fabric is handled entirely by the underlay.
- The **overlay** runs VXLAN for encapsulation and EVPN as the control plane. VTEPs are the leaf switches — each one has a loopback address that serves as its VTEP IP, reachable via the underlay.
- **Route reflectors** — typically the spine switches — reflect EVPN BGP routes between all leaves without requiring a full mesh of leaf-to-leaf BGP sessions.

This two-layer design is deliberate. The underlay does not need to know anything about VNIs, MAC addresses, or tenants. It just needs to deliver IP packets between VTEP loopbacks. The overlay handles everything above that.

## What Happens When a Host Comes Online

Walk through this sequence carefully — it is the sequence you need to be able to narrate in an interview.

**Step 1 — Host connects to a leaf.**
Server A connects to Leaf-1 with IP 10.1.1.10 and MAC aa:bb:cc:dd:ee:01. The server is part of VNI 10010.

**Step 2 — Leaf-1 learns the host.**
Leaf-1 sees the host's MAC through a data-plane event (the host sends an ARP or any frame). Some implementations also learn the IP-to-MAC binding from the ARP itself. The leaf now knows: MAC aa:bb:cc:dd:ee:01, IP 10.1.1.10, locally reachable on VNI 10010.

**Step 3 — Leaf-1 generates EVPN routes.**
Leaf-1 advertises into BGP:
- A **Type 2 route**: MAC aa:bb:cc:dd:ee:01 + IP 10.1.1.10, VTEP IP = 192.168.1.1 (Leaf-1's loopback), VNI 10010
- A **Type 3 route** (if not already present): "I am participating in VNI 10010 — include me in the BUM list"

**Step 4 — Route reflector distributes the routes.**
The spine route reflectors receive Leaf-1's Type 2 and Type 3 advertisements and reflect them to all other leaves in the fabric.

**Step 5 — Remote leaves install forwarding entries.**
Leaf-2, Leaf-3, and every other leaf in the fabric receives the Type 2 route. Each one installs a forwarding entry: "To reach MAC aa:bb:cc:dd:ee:01 / IP 10.1.1.10, encapsulate in VXLAN with VNI 10010 and send to VTEP 192.168.1.1."

This happens entirely in the control plane, before any traffic is sent from Server B to Server A.

## What Happens When Server B Sends Traffic to Server A

Server B (connected to Leaf-2) wants to reach 10.1.1.10.

**Without EVPN:** Server B sends an ARP request. Leaf-2 has no ARP table entry for 10.1.1.10, so it floods the ARP request to every VTEP in VNI 10010. Every leaf receives and processes the flooded frame. Leaf-1 sees the ARP, replies, and Leaf-2 learns the MAC through the reply. Only then can Leaf-2 send unicast traffic.

**With EVPN:** Server B sends an ARP request. Leaf-2 intercepts it, looks up 10.1.1.10 in its BGP-populated ARP table, and responds locally with MAC aa:bb:cc:dd:ee:01. Server B gets its answer immediately. Leaf-2 never floods the ARP. The fabric never sees it.

Server B then sends an IP packet to 10.1.1.10. Leaf-2 already has the forwarding entry from the BGP Type 2 route:
1. Leaf-2 looks up the destination MAC in its MAC table — found, points to VTEP 192.168.1.1
2. Leaf-2 encapsulates the original Ethernet frame in a VXLAN header: inner frame + VXLAN header with VNI 10010 + outer IP header with dst=192.168.1.1
3. The underlay routes the outer IP packet across the spine-leaf fabric to Leaf-1's loopback
4. Leaf-1 receives the VXLAN-encapsulated packet, strips the outer header, and delivers the inner Ethernet frame to Server A

End to end, no flooding. No wasted fabric bandwidth. Deterministic forwarding from the first packet.

## The Underlay's Role

An important detail: the underlay only ever sees the outer IP headers. From the underlay's perspective, this is just IP traffic between two loopback addresses — 192.168.1.2 (Leaf-2's VTEP) to 192.168.1.1 (Leaf-1's VTEP). The underlay has no concept of VNIs, MAC addresses, or tenants. BGP ECMP in the underlay spreads this traffic across all available spine paths based on the outer IP headers.

This separation means you can change your overlay segmentation — add VNIs, move hosts between segments, change VXLAN policies — without touching a single configuration on the spine switches. The underlay remains stable. Only the leaves need to be updated.

## Key Operational Implications

**ARP table scale:** In a fabric without EVPN, the ARP flooding problem grows with the number of hosts. With EVPN, each leaf's BGP table grows with the number of hosts, but the fabric's data-plane noise does not. BGP is a control-plane protocol designed to hold millions of routes. ARP flooding is a data-plane mechanism that was never designed to scale.

**VM mobility:** When a VM migrates from Leaf-1 to Leaf-3, Leaf-3 generates a new Type 2 route with its own VTEP IP. That route propagates through the route reflectors to every other leaf, which updates its forwarding entry. The old entry pointing to Leaf-1's VTEP is withdrawn. The entire fabric converges through BGP — the same mechanism used to handle any routing change.

**Troubleshooting:** When traffic is not forwarding correctly in an EVPN fabric, the first question is always: is the Type 2 route present on the remote leaf? If the BGP route is there and the forwarding entry is installed, the problem is in the data plane. If the route is missing, the problem is in the control plane — a BGP session is down, a route is being filtered, or the originating leaf failed to generate the advertisement. This systematic split between control plane and data plane is what makes EVPN fabrics significantly easier to troubleshoot than flood-and-learn deployments.
