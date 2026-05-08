# Multicast Validation at Arista Networks

Testing a protocol in a lab is different from running it in production — but testing at a hardware vendor is different again. At Arista Networks, I validated PIM-SM IPv6 multicast routing across multiple hardware platforms. The goal was not just to confirm that multicast worked, but to understand the failure modes, the scale limits, and the behavioral differences across different hardware ASICs.

This article documents what that testing looked like, what I learned, and how to think about multicast validation as a senior network engineer.

## The Testing Context

Arista's network operating system (EOS) runs on multiple hardware platforms — each with a different forwarding ASIC, different TCAM capacity, and different implementation of the multicast forwarding pipeline. A software feature that behaves correctly on one platform may have subtle differences on another due to the hardware's implementation of multicast replication, TCAM organization, or rate-limiting behavior.

My role was to validate that PIM-SM IPv6 multicast functioned correctly across these platforms — not just baseline functionality, but failure scenarios, scale behavior, and inter-platform consistency.

## What We Tested

**Baseline PIM-SM functionality:**
- IGMP/MLD (Multicast Listener Discovery — the IPv6 equivalent of IGMP) membership reports from simulated hosts
- PIM neighbor discovery and DR election on multi-access segments
- RP configuration (static and BSR-based) and RP reachability via the underlying unicast routing table
- (*, G) shared tree construction: Joins propagating from receiver FHR to RP, multicast state created at each hop
- Source registration: PIM Register encapsulation from the source FHR to the RP, Register-Stop after SPT establishment
- SPT switchover: Transition from (*, G) shared tree to (S, G) source tree, RP Prune sent after switchover

**Failure scenarios:**
- RP failure mid-stream: Verified that multicast traffic resumed after RP failover, measured convergence time from RP failure to restored delivery
- Upstream link failure: Simulated link failures on PIM-enabled interfaces mid-stream, confirmed Join messages triggered on alternate paths and traffic recovered within expected time bounds
- DR failure on a multi-access segment: Verified Assert mechanism correctly elected a new forwarder when the current forwarder failed
- Receiver departure: IGMP/MLD Leave processing, confirmed that Prune messages were sent upstream when the last receiver on a segment departed

**Scale testing:**
- Increased the number of multicast groups simultaneously active to identify where hardware TCAM capacity limits were hit and how the platform behaved at the limit (graceful degradation vs. traffic drops)
- Measured replication rate at line speed for platforms with multiple downstream interfaces to confirm the hardware multicast replication engine could sustain line-rate forwarding to all downstream interfaces simultaneously
- Tested high group join/leave rates to identify any rate-limiting behavior on PIM state creation

## Key Observations and Lessons

**TCAM capacity is the real scale limit, not software state.** In software-only implementations, multicast state (the (S,G) and (*, G) entries) lives in RAM — essentially unlimited for practical group counts. In hardware platforms, multicast forwarding state is installed in TCAM — a fixed-size, fast memory that supports wire-speed lookups. When TCAM is exhausted, new multicast groups cannot be forwarded in hardware and fall back to the CPU — with significant throughput degradation.

Understanding the TCAM capacity for multicast on a given platform, and designing group addressing to stay within bounds, is essential for production deployments. Different Arista platforms had significantly different multicast TCAM capacities, and the test suite helped establish the practical limits for each.

**Convergence time varies significantly between failure modes.** RP failure convergence depends on how quickly the BSR re-elects a new RP and how quickly receivers detect the loss and re-join. Link failure convergence on a PIM-enabled interface depends on whether BFD is configured (milliseconds) or PIM dead timers (default 105 seconds — an eternity for production use). The lesson: always configure BFD on PIM-enabled interfaces in production. The default hello timer-based failure detection is too slow for real-time traffic applications.

**IPv6 multicast has the same mechanics, different scoping.** IPv6 uses MLD (Multicast Listener Discovery) instead of IGMP, and multicast addresses use the ff00::/8 range. The PIM mechanics are identical. The scope rules are slightly stricter: ff02::/16 is link-local (not routed), ff05::/16 is site-local, ff0e::/16 is global. Router alerts in IPv6 hop-by-hop extension headers serve the same function as the Router Alert option in IPv4 multicast.

**Assert behavior on multi-access segments needs careful testing.** In a lab with multiple routers on the same VLAN, Assert elections sometimes produced counter-intuitive results when metrics were equal — the tiebreaking behavior (higher IP address wins) is specified in RFC 4601 but is not always intuitively obvious. Testing Assert behavior explicitly before deploying in a multi-router segment environment prevents surprises.

## The Testing Methodology That Transfers

The testing approach I used at Arista is directly applicable to validating any new hardware platform or software release in a production DC context:

**Baseline → Edge cases → Failure scenarios → Scale:**
1. Confirm baseline functionality works correctly under ideal conditions
2. Test edge cases (equal-cost paths, simultaneous Join/Prune, group address boundary conditions)
3. Inject failures deliberately — link failures, process restarts, device reboots — and measure behavior and convergence
4. Increase load to scale limits and identify how the system degrades

**Instrument before testing.** Before injecting failures, ensure you have counters, logs, and packet captures in place to observe the behavior. A failure test where you cannot see what happened is just confirming that something broke — not producing actionable data about how and why.

**Compare against the RFC.** When behavior is surprising, go back to the protocol RFC (RFC 4601 for PIM-SM). If the implementation matches the RFC, the behavior may be correct but surprising — document it as a known behavior. If it diverges from the RFC, it is a bug.

**Document everything.** At Arista, every test result was documented: platform, EOS version, test case, expected behavior, observed behavior, and pass/fail. This documentation becomes the baseline for regression testing on future software releases — confirming that a known-good behavior still works correctly after a code change.

This systematic approach to hardware and protocol validation is directly what LinkedIn's preferred qualifications describe: "Experience in hardware and software testing using IXIA or other testing platforms." The methodology transfers; the specific tool (IXIA vs. scripted traffic generators vs. Arista's own test tooling) is secondary.
