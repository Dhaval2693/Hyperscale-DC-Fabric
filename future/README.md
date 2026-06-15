# Future of Network Engineering

This section covers where the discipline is going — and what it already demands at hyperscale today.

## Contents

### [Next-Gen Network Engineer](./next-gen-network-engineer.md)
What the role looks like when code is no longer the bottleneck. Characteristics, responsibilities, and priorities for engineers at AWS, Google, and Microsoft.

### [Outages](./outages/)
Deep-dive post-mortems on real infrastructure failures. Written to extract architectural lessons, not assign blame.

Each analysis covers: what happened, the underlying architecture that made the failure possible, the exact cascade, what the post-mortem missed, and how to design differently.

| Outage | Date | Root Cause | Impact |
|--------|------|-----------|--------|
| [AWS US-EAST-1 — Oct 2025](./outages/aws-oct2025-us-east-1-cascade.md) | Oct 20, 2025 | NLB health monitor → DNS failures → DynamoDB cascade | 100+ services, global, 7+ hours |

---
*The goal of studying failures is not to feel superior to the teams who caused them. It is to recognise the same patterns in your own architecture before they occur.*
