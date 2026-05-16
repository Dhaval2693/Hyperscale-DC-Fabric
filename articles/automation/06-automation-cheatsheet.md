# Automation Cheat Sheet — Quick Glance Before an Interview

This article is a fast reference for the terminology and tools covered in the rest of the automation folder. The goal is not depth — the other articles handle that. The goal is to read this once before an interview and walk in knowing what each term means, when each tool is used, and how to talk about them at a senior engineering level.

---

## The One-Line Definitions

| Term | What it is, in one line |
|---|---|
| **Python** | The dominant language for network automation — used for scripting, orchestration, and API integrations |
| **Ansible** | Agentless configuration management tool — YAML playbooks describe desired state, Ansible enforces it |
| **Jinja2** | Python templating language — generates device configs from variables and templates |
| **Netmiko** | Python library for SSH-based interaction with network devices (CLI scraping done well) |
| **NAPALM** | Multi-vendor Python library that abstracts CLI/API differences into a common interface |
| **Paramiko** | Lower-level Python SSH library that Netmiko is built on |
| **NETCONF** | XML-based protocol (RFC 6241) for structured device configuration and state operations |
| **YANG** | Data modeling language — defines the *schema* for what NETCONF/gNMI configures |
| **OpenConfig** | Vendor-neutral YANG models — same model works across Arista, Cisco, Juniper |
| **gRPC** | Modern RPC framework over HTTP/2, uses Protocol Buffers — fast, binary, streaming-capable |
| **gNMI** | gRPC-based protocol for network management — the modern way to stream telemetry |
| **REST API** | HTTP+JSON request/response — the standard for controllers, cloud APIs, NetBox, etc. |
| **Protocol Buffers (protobuf)** | Binary serialization format used by gRPC — smaller and faster than JSON |
| **Boto3** | AWS Python SDK — wraps AWS REST APIs |
| **IPAM** | IP Address Management — system that allocates and tracks IP space (NetBox, Infoblox) |
| **Source of Truth (SoT)** | Database/system that holds the intended network state — automation reads from it |
| **Idempotency** | Property of an operation that produces the same result when run multiple times |
| **CI/CD** | Continuous Integration / Continuous Deployment — pipelines that validate and deploy changes |

---

## Quick Comparison: When to Use What

### Configuration Push: CLI vs API

| Method | When to use | Tradeoff |
|---|---|---|
| **SSH + Netmiko** | Legacy gear, quick scripts, one-off changes | Fragile to CLI format changes |
| **NETCONF/YANG** | Production automation, structured config | Steeper learning curve, vendor-specific YANG models |
| **gRPC/gNMI** | Modern fabrics, streaming telemetry | Newer ecosystem, fewer mature tools |
| **REST API** | Controllers, IPAM systems, cloud | Works well when device exposes one |

### Python vs Ansible

| Use Python when... | Use Ansible when... |
|---|---|
| Logic is complex (loops, conditionals, state) | Tasks are mostly declarative (push these configs) |
| You need orchestration across multiple systems | You need standardized, repeatable runs |
| Custom integration with internal APIs | Team comfort with YAML > Python |
| Real-time event processing | Periodic state enforcement |

In practice: **both** — Ansible for config push, Python for orchestration logic.

### SNMP vs Streaming Telemetry (gNMI)

| SNMP (old way) | gNMI (modern) |
|---|---|
| Pull-based (polling) | Push-based (streaming) |
| Polling interval = latency | Sub-second updates |
| Per-OID requests, MIB-based | Structured paths, YANG-based |
| High overhead at scale | Single persistent connection per device |

---

## The Mental Model: Layers of Automation

```
Layer 5: Orchestration       (Lambda workflows, Temporal, Airflow)
Layer 4: Event-Driven         (Triggered by telemetry events, alarms)
Layer 3: State Validation     (pyATS, NAPALM, custom Python checks)
Layer 2: Config Deployment    (Ansible, Netmiko, NETCONF push)
Layer 1: Config Generation    (Jinja2 + source-of-truth data)
Layer 0: Source of Truth      (NetBox, internal DB, IPAM)
```

Junior engineers operate at Layer 1-2. Senior engineers design systems that span Layer 0 through Layer 5.

---

## Key Terminology That Comes Up in Interviews

**Idempotency** — Run the same automation twice → same final state, no side effects. If your script crashes mid-run, you can safely re-run it.

**Source of Truth** — The system that holds *intended* state. The network must converge to match it, not the other way around. Manual edits to device configs are forbidden — they create drift.

**Configuration Drift** — When actual device state diverges from intended state (manual changes, failed pushes, version mismatches). Automation must detect and remediate drift.

**Declarative vs Imperative** — Declarative: "this device should have BGP neighbor X." Imperative: "SSH in and type `neighbor X remote-as Y`." Ansible is declarative, raw Netmiko scripts are imperative.

**Pre-flight Validation** — Check the network state *before* making changes. Are prerequisites met? Is the change safe? Catch errors before they execute.

**Staged Rollout** — Deploy changes to a small subset first, validate, then expand. Catches blast-radius problems before they hit the whole fleet.

**Rollback** — Defined plan to undo a change. Automation should know how to revert, not just how to apply.

**Audit Logging** — Every automation action logged with who/what/when/why. Required for compliance and post-incident analysis.

**Schema-Driven Configuration** — Config is validated against a schema (YANG) before being applied. Invalid config is caught at generation time, not at device push time.

**Closed-Loop Automation** — Telemetry feeds back into automation. Alarm fires → automation runs diagnostics → automation remediates → telemetry confirms fix.

---

## How to Talk About This in an Interview

When asked about automation experience, structure the answer around:

1. **The problem** — "We had X manual operation that took Y hours and was error-prone."
2. **The approach** — "We built automation that used Z tools to..."
3. **The safety mechanisms** — "Pre-flight validation, staged rollout, automatic rollback, audit logging."
4. **The outcome** — Quantify: time saved, errors prevented, incidents avoided.

Avoid:
- Listing tools without context ("I know Python, Ansible, NETCONF, gNMI...")
- Describing automation as "I wrote scripts" — that signals junior thinking
- Skipping the safety story — senior engineers always talk about how automation fails safely

Use:
- "Source of truth driven" — signals systems thinking
- "Idempotent" — signals production-grade thinking
- "Pre-flight validation and rollback" — signals operational maturity
- "We measured drift before and after" — signals data-driven engineering

---

## The 30-Second Summary

Network automation is a stack: structured data (YANG, OpenConfig) → structured protocols (NETCONF, gNMI, REST) → orchestration (Python, Ansible) → systems thinking (source of truth, idempotency, validation, rollback). Modern automation moves work away from CLI scraping and toward APIs and data models. The hard part is not the tools — it is the engineering discipline that makes automation safe at scale.

If you walk into an interview knowing this much, you can hold a serious conversation about automation without having written a line of NETCONF code in years.
