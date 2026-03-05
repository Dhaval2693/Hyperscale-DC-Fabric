# BGP State Machine: From TCP to Established

Consider two routers — R1 in AS 65001 and R2 in AS 65002. They are configured as neighbors. Unlike OSPF, BGP does not discover neighbors automatically. There is no hello multicast, no automatic peer detection. A BGP router must be explicitly told who to talk to, what AS they belong to, and how to reach them. The relationship is deliberate by design.

With that configuration in place, R1 starts the process of forming a session with R2. That process moves through six defined states before a single route is exchanged.

```text
  [Idle] ──TCP SYN──> [Connect] ──TCP OK──> [OpenSent] ──OPEN OK──> [OpenConfirm] ──KEEPALIVE──> [Established]
              │                                                                                          │
          TCP fails                                                                               Error / timer
              │                                                                                          │
          [Active] ──retry──> [Connect]                                                            [Idle]
```

R1 begins in **Idle**. This is not inactivity — it is the initialization state where BGP checks its configuration and prepares to bring up the session. From Idle, R1 initiates a TCP connection to R2 on port 179.

While that TCP handshake is in progress, R1 is in the **Connect** state. If the TCP three-way handshake succeeds, R1 immediately sends an OPEN message to R2 and moves forward. If TCP fails — R2 is unreachable, a firewall is blocking port 179, or the address is wrong — R1 falls into the **Active** state.

Active is one of the most misunderstood states in BGP. The name implies something positive, but it signals a problem. A router in the Active state means TCP could not be established and BGP is retrying. R1 attempts a new TCP connection. If that succeeds, it moves forward. If it fails again, it may return to Idle and start the timer before trying again. When you see a BGP neighbor stuck in Active during troubleshooting, that is always a signal to check IP reachability, port 179 access, and neighbor configuration — not a sign that the session is healthy.

The TCP session itself has an active and passive side that is separate from the BGP state machine — and easy to confuse. The **active** router acts as the TCP client: it picks a random source port and initiates the connection to port 179 on the remote router. The **passive** router acts as the TCP server: it listens on port 179 and waits for an incoming connection. By default, routers use their BGP Router ID to determine which plays which role, though behavior can vary by platform. This is usually transparent, but engineers configure a router explicitly as passive in specific scenarios — when firewall rules need a deterministic source to write rules against, or when a Route Reflector serving many clients should listen rather than proactively attempt connections to routers that have not yet come online.

Once TCP is established, R1 enters **OpenSent**. It has already sent its OPEN message and is now waiting for R2's OPEN in return. The OPEN carries R1's AS number, BGP version, Hold Time, Router ID, and any optional capabilities. R1 reads R2's OPEN and validates that the parameters are compatible — correct AS number, agreeable Hold Time, supported capabilities. If anything does not match, R1 sends a NOTIFICATION and the session resets to Idle.

If both OPENs are valid, R1 moves to **OpenConfirm**. At this point both routers have agreed on session parameters and R1 sends a KEEPALIVE to confirm. It is now waiting for R2's KEEPALIVE in return. The Hold Time clock is running. If R2's KEEPALIVE arrives before the timer expires, the session advances. If it does not, a NOTIFICATION goes out and the session resets.

When both KeepaliveS are exchanged successfully, the session reaches **Established**. This is the only state where routing information flows. R1 and R2 exchange their full BGP tables in UPDATE messages, and from that point forward they send only incremental changes — new prefixes advertised, old ones withdrawn. The session stays in Established as long as KeepaliveS continue to arrive within the Hold Time interval.

If anything disrupts the Established session — a hold timer expiry, a TCP failure, a malformed UPDATE, a configuration error — BGP sends a NOTIFICATION and the session drops back to Idle. The entire sequence begins again from scratch.

Understanding the state machine matters beyond theory. When a BGP session is not coming up, the state it is stuck in tells you exactly where in the process the failure is occurring. Connect or Active points to a TCP problem. OpenSent points to a parameter mismatch. OpenConfirm points to a KEEPALIVE timing issue. Established with routes not appearing points to a policy or advertisement problem. The state machine is the first diagnostic tool in any BGP troubleshooting workflow.

With the protocol mechanics in place — how messages work, how sessions form — the next question is practical: when does a network actually need to run BGP, and when is static routing enough? In the next article, we will look at exactly where that line is.
