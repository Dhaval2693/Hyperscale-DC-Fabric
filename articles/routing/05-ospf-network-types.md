## OSPF Network Types

The DR/BDR election is not mandatory component of OSPF. It depend on the type of network interface is connected to.

In P2P link, we do not need to select the DR/BDR election and this is common use in leaf-spine links in clos archiecture and it simplify the hyperscaler network. <But in clos there are multiple p2p links in the network - so we have ospf running different areas for each p2p link in leaf-spine? How does one inter link between leaf-spine share information with neighbor leaf-spine routers>
In broadcast network where routers are sharing same segment, like in enterprise use-case with <>, then DR/BDR election happen to avoid adjacency explosion.
In NBMA (Non-broadcast multi-access) network - like MPLS hub-and-spoke model - where multicast is not supported, DR/BDR still happen with manual guidance. <But why we need OSPF here & how we we do manual guidance?>
In P2MultiPoint (P2MP), <give me clear example>, DR/BDR not required. <Explain briefly why?>
There is another concept in OSPF which need to understand called Virtual linkns because <>. Virtual links are tunnes created inside OSPF to restore backbone connectivity for <reason#1 & 2>

<Transition smoothly why we need to understand stub vs transit area during OSPF network type discussion> <Explain briefly with an example>
