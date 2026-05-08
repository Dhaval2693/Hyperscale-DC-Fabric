# Why Network Automation Exists

In 2010, a network engineer managing fifty switches could log into each one individually, apply a configuration change, verify it, and move on. The work was repetitive and tedious, but it was feasible. The scale was human-manageable.

A hyperscale data center in 2024 might have ten thousand network devices. A single AWS Availability Zone can have hundreds of spine and leaf switches, thousands of top-of-rack switches, and thousands more management and console devices. A new data center launch requires provisioning hundreds of devices correctly, consistently, and without impacting traffic on adjacent live facilities.

No team of network engineers can do this manually. Not because they are not skilled — but because the combinatorial math of manual configuration at that scale is simply wrong. A ten-device change with one human error per hundred operations produces a 10% failure rate. A ten-thousand-device change with the same error rate produces catastrophic outcomes.

This is why network automation exists. Not as a nice-to-have improvement but as a foundational requirement for operating at hyperscale.

## The Three Problems Automation Solves

**1. Scale.** The number of devices a team manages grows faster than the team does. In a hyperscale environment, headcount cannot grow proportionally with infrastructure. The only way to scale operations is to automate the repetitive, well-defined work so that engineers can focus on the work that requires judgment.

At AWS, I built automation that provisioned thousands of network devices for new data center launches. The alternative — manual provisioning — would have required a team many times larger and still would have produced more configuration drift and human error.

**2. Consistency.** Manual configuration is inherently inconsistent. Even the same engineer, configuring the same feature on fifty switches, will introduce variation — a typo here, a wrong interface there, a misremembered default value somewhere. Automation generates configuration from a single source of truth, ensuring that every device configured by the same template is identical. Consistency is not a luxury; inconsistency is the source of a large category of production incidents.

**3. Speed and Safety.** Automated workflows can include pre-flight validation, staged rollout, automated testing, and automatic rollback. A manual change applied to a wrong device by a tired engineer at 2am is irreversible in the moment. An automated workflow with guardrails catches errors before they execute and reverts changes that fail validation. The speed of automation combined with programmatic safety checks produces better outcomes than careful manual work at scale.

## The Automation Spectrum

Network automation is not a single thing. It spans a range from simple scripting to full intent-based networking:

**Configuration Generation (templating):** Taking a source of truth (a database, a YAML file, a spreadsheet) and generating device-specific configurations from templates. Tools: Jinja2 with Python, Ansible templates. This is the entry point for most network automation programs.

**Configuration Deployment (push automation):** Connecting to devices and pushing generated configurations. Tools: Netmiko, NAPALM, Ansible modules, Paramiko. Requires decision about how to connect (SSH, NETCONF, gRPC) and how to verify success.

**State Validation (testing automation):** After a configuration is deployed, automatically verifying that the device is in the expected state. Is BGP up? Are the expected routes in the routing table? Is the interface carrying traffic? Tools: custom Python with Netmiko/NAPALM, pyATS/Genie, Batfish for pre-deployment validation.

**Event-Driven Automation (reactive automation):** Triggering automated actions in response to network events. A link goes down → automatically run diagnostics → notify on-call → attempt remediation. Tools: streaming telemetry consumers, event processors, Ansible-AWX/Tower, custom Lambda functions. This is where I built the most impactful work at AWS.

**Orchestration (multi-system automation):** Coordinating changes across multiple systems — network devices, IPAM, CMDB, ticketing systems, monitoring platforms. A single logical operation ("provision a new rack") triggers changes across ten different systems in the correct sequence. Tools: AWS Lambda workflows, Temporal, Prefect, Airflow.

## What Changed: The Shift from CLI to APIs

Traditional network automation was built on CLI scraping — SSH into a device, send commands as if you were a human typing, parse the unstructured text output. This worked but was fragile. CLI output format changes between software versions. Commands that work on one platform fail on another. Parsing human-readable text with regular expressions is error-prone and unmaintainable.

Modern network automation is built on **structured APIs and data models**:

- **NETCONF/YANG:** An XML-based protocol (RFC 6241) for configuration and state operations, combined with YANG data models that define what configuration exists and what format it takes. Devices speak NETCONF; you get structured XML, not screen-scraped text.
- **gRPC/gNMI:** A modern, high-performance RPC framework used for streaming telemetry and configuration management. gNMI (gRPC Network Management Interface) is increasingly common for real-time state retrieval and configuration push, especially in open networking environments.
- **REST APIs:** Most modern network controllers and cloud infrastructure APIs use REST/JSON. OpenConfig-based controllers, SDN controllers, and cloud provider APIs all expose REST endpoints.
- **OpenConfig:** A vendor-neutral data model for network devices. An OpenConfig YANG model for BGP looks the same whether the device is Arista, Cisco, or Juniper. Writing automation against OpenConfig means the same code works across vendors.

The progression of my automation work at AWS followed this arc: early work used SSH-based Python automation for speed, but as the tooling matured, everything moved toward structured APIs and generated configurations from a source-of-truth database — eliminating the CLI parsing fragility entirely.

## The Automation Mindset for a Senior Engineer

A junior engineer thinks about automation as "how do I do this faster." A senior engineer thinks about automation as "how do I make this operation safe to delegate to a system."

The distinction matters. Faster-but-unsafe automation is worse than manual operation — it fails faster and at larger scale. Automation built with safety primitives — validation before execution, staged rollout, automated rollback, idempotency, audit logging — produces outcomes that are both faster and more reliable than manual work.

At LinkedIn's scale, where the DC & Core team manages infrastructure across multiple regions and is growing rapidly, this safety-first automation mindset is exactly what the role requires. The specific tools matter less than the engineering discipline behind them.
