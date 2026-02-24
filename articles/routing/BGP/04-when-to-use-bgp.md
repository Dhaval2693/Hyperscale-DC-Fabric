# When Do You Really Need BGP? (And When Static Routing Is Enough)

There is a common misconception in networking that the moment you connect to an ISP, you must run **BGP**. That is not true.
In fact, many small and even medium-sized networks run perfectly fine without BGP. Imagine you are a company connected to a single ISP. You have one public prefix. All you want is simple internet access and for the world to reach your website. There is no need to influence traffic. No need to manipulate paths. No need to receive the full internet routing table.
In this case, life is simple. You can configure a static default route pointing toward your ISP. The ISP can statically route your public prefix back to you. Traffic flows. No dynamic negotiation. No session maintenance. No path attributes. It works.
**Static routing is quiet, predictable, and lightweight.** It consumes almost no CPU and does not require maintaining large route tables.

So when does BGP enter the picture? The moment your design stops being simple. Now imagine you are connected to two ISPs. Suddenly, you care about questions like:

- Which ISP should handle outbound traffic?
- What happens if one ISP fails?
- Can I prefer one provider for certain prefixes?
- Can I influence how inbound traffic reaches me?
- Can I filter what routes I receive?

Static routing can handle very basic failover using floating static routes with higher administrative distance. But the moment policy becomes important - static routing becomes rigid.

**BGP exists for policy.** It allows you to:
- Advertise selectively  
- Filter inbound routes  
- Manipulate path preference  
- Control traffic symmetry  
- Scale cleanly across multiple providers  

In summary, static routing is enough when reachability is simple and BGP becomes necessary when control matters. Therefore we even use BGP in modern data centers because we want scalable, policy-driven, distributed control. But that is a different story.
