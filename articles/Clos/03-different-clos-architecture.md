## Why Do We Need Different Tiers in Clos Architecture?

If you work in a hyperscale environment long enough, you eventually hear people casually say “2-tier,” “3-tier,” or even “5-tier” Clos fabric. At some point you probably pause and wonder: what exactly are we counting? If you feel confused, you are not alone.

In Clos architecture, every switching stage counts. If servers connect to a ToR, that ToR connects to a leaf layer, and the leaf connects to spines, you are operating a **3-tier** architecture. If the ToR itself acts as the leaf and connects directly to spines, then you effectively have a **2-tier** design. The distinction is not marketing terminology — it is simply the number of switching layers between the server and the top of the fabric.

So which one should you deploy? The honest answer is: it depends.

It depends on workload characteristics, total server count, traffic patterns inside the data center, and long-term growth expectations. For a small or mid-size deployment, a 2-tier architecture is often sufficient. Even environments with tens of thousands of servers can operate comfortably within a 2-tier or 3-tier design, depending on port density and capacity planning. As the number of servers grows and port limits are reached, additional tiers become necessary. Some hyperscalers scale this pattern up to four, five, or even six tiers — not because the design changes, but because scale demands another stage of replication.

The moment you start designing a fabric, you are forced to think about bandwidth economics. Imagine you have a 48-port switch with 25G interfaces. If you allocate 32 ports for servers, that gives you 800 Gbps of downlink capacity under a single leaf. Now you must decide how much uplink capacity to provision using the remaining ports. Should you match the full 800 Gbps? Not necessarily.

Most cloud workloads rely on **statistical multiplexing**, which assumes that not all servers will transmit at full line rate at the same time. Because of that assumption, you might allocate the remaining 16 ports as uplinks, also at 25G each, providing 400 Gbps of uplink capacity. This creates a **2:1 oversubscription ratio**, meaning the total server-facing bandwidth is twice the available uplink bandwidth. Hyperscalers make this decision deliberately. It reduces cost, power consumption, and optical requirements while still delivering acceptable performance for typical web and microservices workloads.

But what happens when the workload changes?

Now imagine the AI wave arrives and you want to onboard large-scale training workloads into the same fabric. Would you deploy those GPU clusters on a network designed with a 2:1 oversubscription ratio? Most likely not.

AI training behaves differently from traditional web workloads. GPUs exchange gradients continuously. Synchronization phases such as all-reduce create bursts of **east–west traffic** where many nodes transmit at the same time. The assumption behind statistical multiplexing begins to break down. Congestion becomes visible. **Tail latency** increases. Training efficiency drops.

In this scenario, a different design philosophy is required. Instead of oversubscribing uplinks, you move toward a **non-blocking** architecture, where uplink capacity matches or exceeds downlink capacity. The goal shifts from cost efficiency to predictable performance. GPU clusters often demand near non-blocking fabrics to maintain high utilization and consistent iteration times.

Clos architecture is flexible enough to support both models. You can design an oversubscribed fabric optimized for cloud economics, or you can design a non-blocking fabric optimized for synchronized AI workloads. The number of tiers and the oversubscription strategy are not arbitrary decisions — they are reflections of workload behavior and scale requirements.

In future sections, we will explore the different variants of Clos fabrics used specifically for ML and AI clusters, and how their design principles differ from traditional cloud deployments.


