# Automation Interview Scenarios — Practice and Frameworks

You cannot predict the exact automation question an interviewer will ask. You *can* predict the shape of the question — they will be open-ended scenarios designed to see how you think about systems, safety, and scale. This article walks through five realistic scenarios with a framework for how to answer each.

Read each scenario. Try to answer it in your head before reading the framework. Then compare your answer to the framework — not to memorize it, but to spot what you forgot.

---

## Scenario 1: Greenfield Deployment

**The Question:**
> "How would you design a system to automate the network configuration deployment for a brand-new data center?"

**What they're really testing:**
- Do you think about source of truth, or do you jump straight to scripts?
- Do you think about validation and rollback, or just "push the configs"?
- Do you understand the difference between generation, deployment, and verification?

**Answer Framework (5 layers):**

1. **Source of Truth** — Start here. "Before I push any config, I need a system that defines what the network *should* look like. IPAM for IPs, a topology database for rack/role/links, and structured data for routing policy."

2. **Configuration Generation** — "From the source of truth, I'd use Jinja2 templates to generate per-device configs. Templates are version-controlled. The same input always produces the same output (deterministic)."

3. **Pre-flight Validation** — "Before any device sees the config, I'd validate: syntax (with a tool like Batfish), structure (does this look like a complete spine config?), and policy (does it match our standards for BGP, VLANs, etc.)."

4. **Deployment** — "Push in stages. Start with one device, verify it comes up clean, then expand. Each push has a defined rollback (previous config saved). Telemetry confirms BGP sessions come up, interfaces are forwarding, no errors."

5. **Observability and Audit** — "Every action logged with who/what/when/why. Telemetry dashboards confirm the fabric is healthy post-deployment. Drift detection compares device state vs. source of truth continuously."

**Common follow-ups:**
- "What if your template has a bug that gets generated to 100 devices?" → Pre-flight validation should catch it. If it slips through, staged rollout limits blast radius.
- "How do you handle vendor differences?" → OpenConfig YANG models, or vendor-specific templates abstracted behind a common generator.
- "What tools would you use?" → Ansible for push (or NETCONF/gNMI), Python for orchestration, NetBox for source of truth, Batfish for validation, Grafana for telemetry.

**Red flags to avoid:**
- "I'd write a Python script that loops through devices and SSHes in." — too junior.
- Skipping the source-of-truth conversation.
- Not mentioning safety mechanisms at all.

---

## Scenario 2: Configuration Drift Detection

**The Question:**
> "We have 10,000 network devices. How would you detect and remediate configuration drift?"

**What they're really testing:**
- Do you understand drift as a continuous problem, not a one-shot check?
- Can you reason about scale (10,000 devices is not 10)?
- Do you think about remediation safely, or just "auto-fix"?

**Answer Framework:**

1. **Define drift precisely** — "Drift is when actual device state differs from the intended state in source of truth. I need to know both."

2. **Collect actual state at scale** — "gNMI streaming telemetry from every device, continuously. Or periodic polls every N minutes via NETCONF if gNMI isn't available."

3. **Compare to intended state** — "Run a comparison job: pull intended config from source of truth, compare to streamed actual state, flag any deltas."

4. **Categorize drift** — "Not all drift is equal. A manual hostfile edit during an incident is acceptable temporary drift. An unauthorized BGP policy change is critical. Categorize by severity and intent."

5. **Remediation** — "Auto-remediation only for safe categories (e.g., reverting unauthorized cosmetic changes). For meaningful drift, generate a ticket, notify on-call, let humans decide. Auto-remediating critical state without context is how outages happen."

6. **Reporting** — "Dashboard showing drift rate over time, top drifting devices, top drifting config sections. Drift trends reveal process issues (engineers bypassing automation)."

**Common follow-ups:**
- "What if comparing 10K devices takes too long?" → Parallelize the comparison. Use incremental diffs (only check what changed since last poll). Sharding by region.
- "How do you handle planned exceptions?" → Annotations in source of truth marking a device/segment as 'maintenance mode' — drift checks skip annotated regions.

---

## Scenario 3: Safe Rollout of a BGP Policy Change

**The Question:**
> "You need to push a BGP policy change to 500 routers in production. Walk me through how you'd do it safely."

**What they're really testing:**
- Are you afraid of production? (You should be, in a healthy way.)
- Do you know what "staged rollout" actually means?
- Do you have a rollback story?

**Answer Framework:**

1. **Pre-deployment**
   - Generate the change in source of truth (not on devices).
   - Diff against current config — make sure the change is what you expect.
   - Validate with Batfish or equivalent (does the change leave any prefix unreachable?).
   - Get peer review — the change is reviewed before it deploys.

2. **Canary stage**
   - Push to 1 router. Wait. Verify BGP sessions, prefix counts, no error logs, traffic still flowing.
   - Push to 5 more routers (different parts of the fabric). Verify the same.
   - Acceptance gate: if any canary fails, abort, do not proceed.

3. **Staged production rollout**
   - Push to 10% of fleet. Wait 10 minutes. Verify.
   - Push to next 25%. Wait. Verify.
   - Push to remaining 65%. Verify.

4. **Verification at each stage**
   - Telemetry-driven, not "did the SSH return 0." BGP session count, prefix count per peer, error counters, traffic volume.
   - If any metric goes wrong, halt the rollout immediately.

5. **Rollback plan**
   - Defined before deployment, not invented during an incident.
   - Every stage has a defined revert (previous config saved, automation can re-push it).
   - Rollback is itself tested in a lab, not first run in production.

**Common follow-ups:**
- "What if the change works on 400 devices but fails on the last 100?" → The 400 stay deployed (rolling back doesn't help, they're fine). The 100 are investigated. Could be device-specific issues — bad config, hardware quirk, version mismatch.
- "What if the change cascades into a problem 30 minutes later?" → Telemetry alerts on anomalies trigger automatic rollback of recent changes via the same automation.

---

## Scenario 4: Automation-Caused Outage

**The Question:**
> "Your automation just pushed bad config to 200 production switches. Walk me through the next hour."

**What they're really testing:**
- Do you panic, or do you have a process?
- Do you understand incident response — communication, not just fixing?
- Do you focus on root cause vs. just remediation?

**Answer Framework (in order):**

1. **Stop the bleeding (0-2 min)**
   - Halt the automation pipeline immediately so no more devices are affected.
   - Identify the blast radius: which 200 devices? Are they still reachable?

2. **Communicate (2-5 min)**
   - Page on-call leadership.
   - Open an incident channel (Slack/Teams) and post status. "Bad config pushed to 200 switches in DC-X via automation. Investigating impact."
   - If customer-visible impact, engage comms / customer-facing teams.

3. **Assess impact (5-10 min)**
   - Are the 200 devices forwarding traffic correctly despite the bad config?
   - Is the bad config a no-op (cosmetic) or causing failures?
   - Are alerts firing for traffic loss, BGP flaps, link errors?

4. **Decide: rollback or remediate (10-15 min)**
   - If devices are actively failing: rollback to known-good config immediately.
   - If devices are stable: schedule rollback for change window. Don't make it worse by piling more changes.

5. **Execute rollback (15-30 min)**
   - Use the automation's rollback path (same staged rollout pattern, in reverse).
   - Verify each batch with telemetry before proceeding.

6. **Post-incident (next 24-72 hours)**
   - Write a blameless post-mortem.
   - Identify root cause: was it bad template, bad source-of-truth data, missing validation?
   - Fix the system so the same class of failure cannot happen again. (Not "fire the engineer.")

**Red flags to avoid:**
- "I'd rush to fix the configs manually on each device." — manual changes during automation incidents make things worse and lose audit trail.
- Not mentioning communication.
- Going straight to root cause without stopping the bleeding first.

---

## Scenario 5: Tell Me About an Automation Project You Built

**The Question:**
> "Walk me through an automation project you built end-to-end. What was the problem, what did you build, what did you learn?"

**What they're really testing:**
- Can you tell a story with structure?
- Do you talk about engineering decisions, or just tools you used?
- Did you learn from the project, or just complete it?

**Answer Framework (use this structure):**

1. **The Problem** (30 seconds)
   - What was painful or broken? Quantify if possible: "Provisioning a new rack took 4 hours of manual work by two engineers, and we did this 50 times per quarter."

2. **The Constraints** (15 seconds)
   - What couldn't change? "We had to work with existing vendor gear (no API standardization), and the source of truth was a legacy CMDB we couldn't replace."

3. **The Approach** (1 minute)
   - At a high level: "I built a Python service that pulled device data from the CMDB, generated configs via Jinja2 templates, validated them, and pushed via Netmiko in parallel batches."
   - Name the patterns: source of truth driven, idempotent, pre-flight validated, staged rollout.

4. **The Hard Parts** (1 minute)
   - What went wrong or was surprising? "Initial parallel SSH overwhelmed devices — they rate-limited us. I had to add a configurable concurrency cap per device class."
   - The hard parts are the most interesting part of your answer. Don't skip them.

5. **The Outcome** (15 seconds)
   - Quantify: "Provisioning time dropped from 4 hours to 15 minutes. Failed deployments dropped by 80% (the template validation caught most errors before they hit devices)."

6. **What You'd Do Differently** (30 seconds)
   - Show self-reflection: "If I rebuilt it today, I'd use gNMI instead of Netmiko for the modern devices, and add streaming telemetry-driven post-deployment verification rather than my static polling check."

**Red flags to avoid:**
- Listing tools without context ("I used Python, Ansible, and Jinja2.")
- Saying "everything went smoothly." Interviewers know nothing goes smoothly. They're suspicious of perfect stories.
- Taking credit for a team's work — say "we" when accurate, "I" when truly your contribution.

---

## Universal Tips That Apply to Every Automation Question

**Use the vocabulary.** When you say "idempotent," "source of truth," "staged rollout," "blast radius," "pre-flight validation," "rollback path," "drift detection" — you sound like a senior engineer. The vocabulary signals depth.

**Always think about failure.** Whatever the question, ask yourself: "What happens when this breaks?" The senior engineer's mental model is failure-first. Junior engineers think about the happy path; seniors think about the failure modes.

**Quantify when you can.** "Reduced deployment time" is weak. "Reduced deployment time from 4 hours to 15 minutes" is strong. Numbers signal that you measure your work.

**Acknowledge tradeoffs.** No design is free. Saying "this is faster but uses more memory" or "this adds complexity but enables rollback" shows you understand engineering is about choices.

**End with what you'd do differently.** Every project has lessons. Sharing them shows growth and self-awareness — both highly valued at senior level.
