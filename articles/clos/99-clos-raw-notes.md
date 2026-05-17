## VxLAN

<Difference in overlay vs underlay>
VXLAN (Virtual Extensible LAN) is a network virtualization technology that addresses the scalability issues of large cloud and data center environments by extending Layer 2 networks over Layer 3 infrastructure. Understanding VXLAN is important for network engineers working with modern data centers or cloud environments that require high flexibility, scalability, and isolation. VXLAN uses a MAC-in-UDP encapsulation technique, enabling the creation of overlay networks that run on top of a physical underlay network.

With overlay networking, we create an overlay network, which is a virtual network on top of the underlay network, which is the physical network.

Limitation of an underlay physical network:

    Forwarding limitations: Data forwarding is tied to physical paths. If you want traffic engineering, you need to reconfigure the physical network, such as changing IGP metrics, policy-based routing, or even re-cabling.
    Slow deployments: If you want to add a new tenant or isolated segment, you need to configure VLANs, ACLs, and routing policies on many devices, which is time-consuming and prone to errors.
    Scalability issues: VLANs have limits (4094 usable VLANs), which is not enough for large-scale cloud providers or data centers.

There are forms of overlay networking exist like VLAN, GRE, VPN, DMVPN, VXLAN, LISP, SD-WAN 
Advantages of overlay: Decoupling, Agility, and Scalability -  VLAN (4094) but VxLAN (16 million unique segments due to 23-bit VNI)
Disadvantages: Complexity, Overhead (consume processes for encap/decap - affect throughput/latency)
Troubleshooting: More difficult, traceroute shows only logical path

<intro to vxlan>
Virtual eXtensible Local Area Network (VXLAN) is a tunneling protocol that tunnels Ethernet (layer 2) traffic over an IP (layer 3) network.
Traditional network issues: STP (paying for the links that can't be used), limited no of vlans, large MAC address tables due to virtualiaztion

VNI, VTEP

    VTEP IP interface: Connects the VTEP to the underlay network with a unique IP address. This interface encapsulates and de-encapsulates Ethernet frames.
    VNI interface: A virtual interface that keeps network traffic separated on the physical interface. Similar to an SVI interface.


VXLAN Frame format

The VXLAN header looks similar to the LISP header. This is not by accident. The idea was to add layer 2 support to LISP and call it layer 2 LISP. Instead, they came up with the name VXLAN.

Packet walkthrough

How VTEP learn mapping information. Different methods: Static unicast VxLAN tunnels, multicast underlay, MP-BGP EVPN, VxLAN with LISP
The MP-BGP EVPN solution is popular in data centers and private clouds. VXLAN with LISP is a popular choice for campus networks.
