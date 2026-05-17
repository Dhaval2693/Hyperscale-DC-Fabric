# Intent-Based Networking

Intent-Based Networking (IBN) is the evolution of network automation: instead of describing **what to configure** (imperative — "set BGP neighbor X to remote-as Y"), you describe **what you want** (declarative — "these tenants should be reachable to each other on these subnets") and the system figures out the configuration to make it true.

This article covers the concept, what real IBN systems look like, and why the JD asks for it ("extend our intent-based network configuration systems").

## Intent vs Imperative Automation

| | Imperative | Declarative / Intent |
|---|---|---|
| **You describe** | Steps to execute | Desired end state |
| **The system** | Runs your steps | Computes diff, makes it true |
| **Example tool** | Ansible playbook | Cisco NSO, Apstra, internal IBN system |
| **Idempotency** | You must implement it | Built in |
| **State drift** | Possible — actual diverges from intended | Continuously reconciled |
| **Failure handling** | You handle it | System rolls back or alerts |

The Kubernetes analogy: a `kubectl apply -f deployment.yaml` doesn't say "run these commands"; it says "make the cluster look like this." That's intent.

## What a Real IBN System Does

A mature IBN system has these components:

### 1. Intent Definition Layer

You express what you want, usually in structured form (YAML, JSON, a custom DSL):

```yaml
fabric: dc-west-1
tenants:
  - name: research-team
    vrf: research
    subnets:
      - 10.10.0.0/24
    bgp_communities: [65000:100]
external_peers:
  - region: dc-east-1
    routes_imported: research/10.10.0.0/24
```

This says nothing about *how* to achieve it. No BGP neighbor commands, no VLAN IDs, no specific switches.

### 2. Compilation Layer

The system reads the intent and the **topology model** (what switches exist, how they're connected), then computes the per-device configuration that implements the intent.

This is the hard part. It's essentially a compiler that takes high-level intent + topology and produces device configs.

### 3. Validation Layer

Before deployment, the candidate config is checked:
- Syntactic correctness
- Constraint compliance (no overlapping subnets, no IP exhaustion)
- Simulation (Batfish-style: would routing actually work?)

### 4. Deployment Layer

Push the configs to devices, using ordering that maintains forwarding (e.g., bring up new BGP sessions before deactivating old ones).

### 5. Reconciliation Layer

Continuously compare actual device state to intended state. Drift triggers alerts or auto-remediation.

## Real-World Examples

| System | Vendor | Notes |
|---|---|---|
| **Cisco NSO** (Network Services Orchestrator) | Cisco | Multi-vendor, YANG-driven; common in service providers |
| **Apstra** (now Juniper) | Juniper | Intent + telemetry-based validation for DC fabrics |
| **Google's Capirca / B4** | Internal | Google's backbone uses intent-based config and TE |
| **Meta's Open/R / FBOSS** | Internal | Facebook's network uses intent-driven fabric |
| **OpenConfig + custom orchestrator** | Open standard | Many hyperscalers build on OpenConfig YANG |

Most hyperscaler IBN is built internally, around OpenConfig YANG models plus a custom compiler that knows their fabric topology.

## Why It Matters at Scale

At small scale, imperative automation (Ansible playbooks, Python scripts) works fine. At hyperscaler scale, it doesn't:

1. **Combinatorial complexity.** 10,000 switches × 50 features × N vendors = an impossible number of imperative scripts.

2. **State drift.** With no continuous reconciliation, devices slowly diverge from intent. Imperative scripts only fire when you run them.

3. **Vendor diversity.** OpenConfig (one model, many vendors) lets the IBN system speak one "intent language" and translate to vendor-specific configs.

4. **Auditable change.** Intent change = single diff in a YAML file. Imperative change = a pile of commands no one can review at-a-glance.

5. **Safer rollouts.** The IBN system can validate the intent change, simulate impact, and stage rollout — none of which raw Ansible gives you.

## How IBN Systems Get Built

The pattern (over years, in stages):

1. **Source of truth first.** A clean, queryable database of intent (devices, links, IPs, policies).
2. **Templates next.** Jinja2 or equivalent, generating per-device config from intent data.
3. **Validation harness.** Pre-deployment checks (syntax, policy compliance).
4. **Push automation.** Staged rollout with telemetry verification.
5. **Reconciliation loop.** Periodic comparison of actual vs intended, drift remediation.
6. **Higher-level abstractions.** Stop thinking in terms of devices; think in terms of fabric, tenants, reachability.

Most companies are stuck at step 2-3. Real IBN is steps 5-6, and only the largest hyperscalers (and a few enterprises with serious investment) have it.

## How to Talk About It

For "what's intent-based networking":
> "Intent-based networking is declarative network automation — you describe what the network should *be*, the system computes the configs that make it true, and continuously reconciles drift. Compare to imperative automation (Ansible scripts) where you describe what *to do*. The intent layer is built on a source-of-truth model of the network, a compiler that translates intent + topology into per-device configs, validation before push, and a reconciliation loop after."

For "have you built/operated one":
> "At scale, yes — \[describe the pattern from your experience\]. Even where the full IBN stack didn't exist, the pieces (source of truth, config generation, validation, staged deployment) are the building blocks of any safe network automation. The hardest part is always the topology model and the source-of-truth identity mapping."

## What to Memorize

- Intent vs imperative: declarative end-state vs commands to run
- Five layers: intent → compile → validate → deploy → reconcile
- OpenConfig as the common YANG model enabling multi-vendor IBN
- Examples: NSO (multi-vendor), Apstra (DC), in-house at hyperscalers
- The reconciliation loop is what distinguishes IBN from "just better Ansible"

## Connection to Other Topics

- **Builds on:** [01-why-network-automation.md](01-why-network-automation.md), [04-netconf-and-yang.md](04-netconf-and-yang.md), [06-automation-cheatsheet.md](06-automation-cheatsheet.md)
- **Bridges to:** SLO/SLI work (intent makes drift detection possible), cost optimization (intent enables systematic policy changes)
- **Relevant for:** any senior network role at hyperscaler; this role specifically asks for it

## Anthropic-Specific Framing

The JD line "extend our intent-based network configuration systems" tells you they have one. You won't be designing it from scratch — you'll be:

- Adding new intent primitives (a new tenant type, a new QoS policy)
- Extending validation to catch new failure modes
- Tying the intent system to your cost attribution data ("when intent changes, what's the cost implication?")
- Wiring telemetry into the reconciliation loop

Your job is to be conversational about the architecture — not a vendor expert. The interviewer wants to know you've thought beyond "Ansible push" and understand why intent + reconciliation is qualitatively different.
