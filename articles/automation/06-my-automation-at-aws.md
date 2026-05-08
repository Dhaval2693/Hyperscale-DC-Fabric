# My Automation Work at AWS

The most valuable way to understand network automation is not through abstractions but through real problems that required real solutions. This article walks through the three main automation systems I built at AWS, the problems they solved, and the engineering decisions behind each.

These are also the stories I tell in interviews when asked about automation, impact, or technical leadership. The numbers are real. The architecture decisions reflect what actually works at hyperscale.

## Project 1: DC Launch Deployment Orchestration (1,000+ Hours/Year)

**The Problem**

AWS launches new data centers continuously. Each launch involves deploying multiple independent network projects in a specific sequence: spine switches first, then leaf switches, then management networks, then ML/AI fabric. Each project's deployment is initiated by an engineer who needs to know the correct parameters (data center ID, rack assignments, IP ranges, project phase) and trigger the right internal tools in the right order.

Before automation, this looked like: an engineer opens a runbook, reads the parameters from a spreadsheet, logs into multiple internal systems, triggers each workflow manually, waits for completion, verifies, triggers the next. Multiple engineers coordinating across a launch that could span days. Any parameter error — wrong DC ID, wrong phase flag — either caused the deployment to fail or, worse, caused it to succeed with wrong configuration.

The blast radius of a wrong parameter in a network deployment is significant. A misconfigured spine in a new DC can mean rework that delays the launch by days.

**The Solution**

I designed and built a Python-based AWS Lambda service that orchestrated the entire deployment sequence automatically.

The architecture:
- **Source of truth in DynamoDB:** Every DC launch was registered in a DynamoDB table with all parameters — DC identity, rack topology, project list, sequencing rules, prerequisite checks.
- **Lambda state machine:** The Lambda function read the current state of the launch from DynamoDB, determined the next step (based on sequencing rules and completion status of previous steps), validated prerequisites, and triggered the appropriate deployment workflow.
- **Prerequisites as code:** Before triggering any step, the Lambda checked that all upstream dependencies were complete. Leaf deployment would not trigger until spine deployment reported success. This eliminated the human judgment call of "is it safe to start the next step?"
- **Idempotency:** Every step could be re-triggered safely — it would check the current state and skip steps already completed, resume from the failure point.
- **Observability:** Every state transition was logged to CloudWatch with enough context for an engineer to understand what happened without re-running the sequence.

**The Outcome**

Deployment initiation for a complete DC launch went from a multi-day coordinated human process to a single trigger that ran to completion automatically. Engineers were freed from monitoring progress and triggering steps — they were notified only if something failed and needed human intervention. Over a year, across dozens of DC launches, this eliminated over 1,000 hours of deployment delay.

The hidden benefit: because the sequence was now defined in code rather than in a runbook, it could be reviewed, tested, and version-controlled. When the sequencing logic needed to change — a new project type was added, a prerequisite check was tightened — it was a code change with a review and an audit trail, not an untracked runbook edit.

## Project 2: Automated Cabling Connection Generation (3,000+ Hours/Year)

**The Problem**

Every physical network device in a data center has cables connecting it to other devices. The connections — which port on which device connects to which port on which other device — are defined by the rack topology, the cabling standards for each device type, and the spatial layout of the rack. This information needs to be in the network management system before devices can be provisioned.

Before automation, a team of engineers would take the rack topology design, manually look up the cabling standard for each device type, calculate the specific connections, and enter them one by one into the tooling system. For a large DC with hundreds of racks and thousands of devices, this was weeks of work, prone to transposition errors.

**The Solution**

I built a Python service that automated cabling connection generation.

The architecture:
- **Input:** Rack topology data (which devices, which rack positions, which device types) from the source-of-truth database. Cabling standards for each device type from a standards library.
- **Logic:** For each device, the service looked up the cabling standard, resolved the physical positions of peer devices from the topology data, and computed the exact port-to-port connections.
- **Integration:** The generated connections were written directly into the network management tooling via its API — no human copy-paste, no intermediate spreadsheet.
- **Validation:** Before writing, the service validated that all referenced devices existed in the system, that port assignments were within the valid range for the device type, and that no connections were duplicated. Invalid outputs were rejected with a structured error report.

**The Outcome**

What previously took engineers weeks of manual data entry — for a single large DC — became a process that ran in minutes. The error rate dropped dramatically because the service applied cabling standards consistently, without the fatigue-driven transposition errors of manual data entry. Over a year, across all DC launches, this eliminated over 3,000 engineering hours of manual work.

The more important outcome: because the generation was automated and validated, the cabling data in the management system became reliable enough to build further automation on top of. Systems that previously could not trust the cabling data to be accurate could now use it as a trusted input.

## Project 3: Security Patching Fleet Automation (30% → 90% Compliance)

**The Problem**

Network devices need regular OS and configuration patching — security vulnerabilities are disclosed continuously, and keeping a fleet of thousands of devices current is an ongoing operational burden. Before automation, patching required engineers to manually identify which devices needed a specific patch, schedule maintenance windows, apply patches, verify success, and update tracking. The result: only 30% of devices were current on security patches at any given time — not because engineers were not trying, but because the manual process could not keep up with the volume and rate of patches.

**The Solution**

I built an automated patching pipeline that handled the entire patching workflow.

The architecture:
- **Inventory integration:** The system continuously read the device fleet from the source of truth, enriching each device record with its current OS version and patch state.
- **Gap identification:** For each device, the system compared the current OS version against the required version (from the security team's patch requirements database) and identified which devices needed which patches.
- **Staged rollout:** Rather than patching all devices simultaneously (which would be catastrophic if a patch caused issues), the system patched devices in cohorts — a small pilot group first, then progressively larger groups, with validation between stages. If the pilot group showed anomalies (unexpected BGP session drops, interface errors, CPU spikes after patching), the system paused and alerted engineers.
- **Maintenance window awareness:** The system read the network's maintenance window schedule and only applied patches during approved windows — no patching during peak traffic periods or active incidents.
- **Rollback triggers:** After patching, the system monitored key health indicators for each device. If a device showed degraded health post-patch, automated rollback restored the previous OS version.

**The Outcome**

Fleet compliance went from 30% to 90% within months of deployment — not because engineers were suddenly working faster, but because the process was now automated and continuous. The system ran every day, identifying gaps and scheduling patches, without requiring human initiation. The security team could now see real-time compliance metrics on a dashboard rather than getting a monthly report that was already outdated by the time it was published.

## What These Three Projects Have in Common

Looking across them, three patterns appear consistently:

**Source of truth as the foundation.** Every system reads its inputs from a source of truth and writes its outputs back. There is no floating state, no parameters stored only in an engineer's head or in a one-off spreadsheet. The source of truth is the single source of record for what the network should look like.

**Validation before execution.** Every system validates its inputs and outputs before taking action. Wrong inputs are rejected with clear error messages. Outputs that would create invalid state are blocked before they reach the device.

**Observability from the start.** Every action is logged with enough context for an engineer to reconstruct what happened, why, and with what result — without running anything again. This is not just debugging convenience; at the scale of thousands of devices across hundreds of DC launches, audit trails are an operational necessity.

These are not incidental properties of these specific systems. They are the engineering discipline that makes automation safe to deploy at scale, where the consequence of an undetected error is measured in hours of customer impact, not minutes of engineer inconvenience.
