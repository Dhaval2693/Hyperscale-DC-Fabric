# BGP message types

Before understanding how BGP chooses paths, let's understand the BGP language. Unlike OSPF, BGP does not flood topology information. It does not rely on multicast.
BGP is polite. It establishes a **TCP session on port 179** first — and only then begins to speak. Everything BGP does is built on just four message types.

Firstly, the **OPEN** message is the handshake. When Router R1 connects to Router R2 over TCP, the first BGP message it sends is an **OPEN**.
Inside that OPEN message, R1 includes:
- Its **Autonomous System Number (ASN)**
- The **BGP version** (typically version 4)
- The **Hold Time**
- Its **BGP Router ID**
- Optional capabilities (such as multiprotocol support for IPv6, VPNv4, etc.)

It is essentially saying:

> "Hello, I am AS 65001. I support these capabilities. Do we agree?"

If R2 accepts the parameters, it replies with its own OPEN message. If something is wrong - wrong ASN, incompatible parameters - the session will not proceed.

Once OPEN messages are accepted, **KEEPALIVE** messages maintain the relationship. They are small and contain no routing information.

Their purpose is reassurance:

> "I am still here."

If the hold timer expires without receiving a KEEPALIVE (or UPDATE), the session is terminated.


Next comes the **UPDATE** messages which carries:

- New route advertisements  
- Withdrawals of previously advertised routes  
- Path attributes such as:
  - **AS_PATH**
  - **NEXT_HOP**
  - **LOCAL_PREF**
  - **MED**

BGP does not flood the entire topology. It sends incremental updates only when something changes.

If something goes wrong - malformed message, hold timer expiry, capability mismatch - BGP sends a **NOTIFICATION** message and immediately tears down the session. There is no negotiation after that. The session resets.
