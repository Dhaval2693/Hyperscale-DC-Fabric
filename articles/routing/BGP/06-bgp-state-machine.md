# BGP State Machine: A Conversation Between R1 and R2

Now imagine two routers.

- R1 in AS 65001  
- R2 in AS 65002  

They are configured as neighbors. Unlike OSPF, BGP does not discover neighbors automatically. It must be told explicitly who to talk to. 

When R1’s BGP process starts, it begins in the **Idle** state. In Idle:
- BGP checks configuration.
- It attempts to initiate a TCP connection to the neighbor.
R1 sends a TCP SYN packet to port 179 on R2. If TCP succeeds, R1 moves forward. If TCP fails, it retries based on timers.

If the TCP handshake is in progress, R1 is in the **Connect** state. If TCP succeeds, R1 immediately sends an OPEN message and transitions to the next state. If TCP fails, R1 enters the **Active** state.
Active does not mean the session is working. It means BGP failed to establish TCP and is trying again. In Active:
- R1 retries the TCP connection.
- If successful, it moves forward.
- If unsuccessful, it may return to Idle and retry later.

Seeing a neighbor stuck in Active usually indicates connectivity or configuration issues. 

Once TCP is established, R1 enters into **OpenSent** where it sends an **OPEN** message to R2 and waits for R2’s OPEN message. If R2’s OPEN message is valid and parameters match expectations, R1 responds with a **KEEPALIVE**. At this stage, both routers confirm the session parameters and goes into **OpenConfirm** state.
Once KEEPALIVE messages are exchanged successfully, the session enters the **Established** state. In Established:
- UPDATE messages flow.
- Routes are advertised.
- Withdrawals are processed.
- The routing table is populated.
If anything goes wrong - hold timer expiry, TCP failure, protocol error - a NOTIFICATION is sent and the session drops back to Idle.

In summary:

Idle → Connect → Active (if TCP fails) → OpenSent → OpenConfirm → Established
