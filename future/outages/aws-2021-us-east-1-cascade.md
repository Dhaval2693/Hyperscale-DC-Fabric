# AWS US-EAST-1 Cascading Failure — December 7, 2021

*How a routine capacity operation overwhelmed the internal DNS infrastructure of the world's largest cloud provider, cascading into a 7-hour outage affecting hundreds of services and millions of users.*

---

## What Users Experienced

At approximately 10:45 AM EST on December 7, 2021, services began failing across AWS US-EAST-1 — the Virginia region that underpins a significant fraction of the internet. EC2 instances became unreachable. S3 buckets returned errors. Lambda functions stopped executing. Amazon Connect dropped calls. The AWS management console itself became unavailable.

By midday, the failure had spread far beyond AWS's own services. Netflix, Disney+, Slack, Flickr, Tinder, and hundreds of other companies built on AWS infrastructure began reporting degraded service to their users. Third-party monitoring services that tracked AWS's health status could not reach AWS — because their monitoring infrastructure was also hosted in US-EAST-1.

Most strikingly: the AWS Service Health Dashboard — the page AWS maintains to communicate the status of its services during outages — went down. It was hosted on S3, which was one of the failing services. Users trying to understand why their applications were broken could not get information from AWS about why their applications were broken.

The outage lasted approximately seven hours before services were substantially restored. Some services took longer. The post-incident analysis that AWS published revealed a cascade that started with a single automated operation and propagated through an architectural assumption that had been invisible until it failed.

---

## Timeline

| Time (EST) | Event |
|-----------|-------|
| 10:45 AM | Automated capacity expansion begins on the AWS front-end network in US-EAST-1 |
| 10:50 AM | Internal network traffic from the automation exceeds the capacity of a shared internal path |
| 10:55 AM | AWS internal DNS resolvers begin experiencing high latency and packet loss |
| 11:05 AM | EC2 instance metadata service (IMDS) becomes unreachable for instances relying on internal DNS |
| 11:15 AM | Cascading service failures begin: Lambda, SQS, SES, Amazon Connect |
| 11:30 AM | AWS management console becomes degraded — S3 is unavailable |
| 11:45 AM | Third-party services built on AWS begin widespread user-facing failures |
| 12:00 PM | AWS engineers identify the root cause — internal network congestion caused by the automation |
| 12:30 PM | Automation is halted; manual recovery of internal DNS begins |
| 1:00–5:30 PM | Staged recovery of services, in order of dependency |
| 5:30 PM | Most services restored; post-incident analysis begins |

---

## The Architecture in Normal Operation

To understand how this failure happened, you first need to understand how the AWS internal architecture is structured in a healthy state.

![AWS US-EAST-1 normal architecture — internal network, DNS, service layers in healthy state](./diagrams/aws-normal-architecture.svg)

AWS's internal architecture in a region like US-EAST-1 has several distinct planes:

**The external data plane:** This is what users interact with. Route 53 resolves DNS for external customers. CloudFront handles CDN and edge traffic. API calls to AWS services (create an EC2 instance, put an object in S3, invoke a Lambda function) arrive at the AWS front-end (FE) fleet — a layer of servers whose job is to authenticate, authorise, and route these API requests to the correct internal service.

**The internal service mesh:** Behind the FE fleet, hundreds of AWS services communicate with each other. EC2 orchestration services talk to networking services. S3 talks to authentication services. Lambda talks to EC2. This communication is entirely internal, using internal IP addresses and internal DNS for service discovery.

**The internal DNS layer:** This is the critical infrastructure that makes the internal service mesh work. Every time an internal service needs to communicate with another internal service, it resolves that service's internal hostname through AWS's internal DNS resolvers. These resolvers are, in effect, the phonebook for the entire internal architecture.

**The control plane / capacity management layer:** Separate from the data plane, AWS runs automated systems for capacity management, health checking, and operational changes. These systems manage the fleet — adding servers, removing them, rerouting traffic during maintenance. They also use internal network paths to communicate with the services they manage.

Under normal operation, these planes are logically separated. Capacity operations on the FE fleet should not affect internal DNS. Internal DNS degradation should not cascade to every service simultaneously. That is what the architecture was *designed* to do. What it *actually* did was different.

---

## How the Failure Cascaded

The cascade began with a legitimate and routine operation: AWS engineers were expanding capacity in the front-end network in US-EAST-1. The FE fleet handles external API traffic, and capacity expansion is a normal operational activity — it happens regularly as demand grows.

This particular expansion used an automated tool. That tool, when executed, generated a large volume of internal control-plane traffic as part of the expansion process. This traffic flowed through an internal network path that the tool's authors had assumed had sufficient capacity.

It did not.

![AWS failure cascade — how the internal network congestion propagated through DNS to service failures](./diagrams/aws-failure-cascade.svg)

**Stage 1 — Network congestion:** The automation's control-plane traffic saturated a shared internal network segment. Packets began queueing. Latency spiked. Some packets were dropped entirely.

**Stage 2 — DNS degradation:** AWS's internal DNS resolvers were reachable through that same internal network path. As the path became congested, DNS queries from internal services began timing out or returning after unacceptably long delays. DNS resolvers that should have responded in <5ms were taking 500ms or not responding at all.

**Stage 3 — Service discovery failure:** Every internal service that needed to communicate with another internal service sends a DNS query first. With DNS degraded, these queries began failing. Services started receiving connection errors when they tried to reach other services — not because those other services were unhealthy, but because they couldn't look up their addresses.

**Stage 4 — The bootstrap dependency problem:** Here the cascade became severe. Many AWS services have a startup sequence that involves DNS queries. EC2 instances use the Instance Metadata Service (IMDS), which is reachable via an internal address that requires... internal DNS resolution. Instances that rebooted or needed to refresh their credentials could not reach IMDS. They failed.

Lambda functions that were invoked required the Lambda execution environment to initialise. Initialisation involved DNS queries. Those queries timed out. Lambda invocations failed not because Lambda itself was broken, but because the environment in which Lambda functions run could not bootstrap correctly.

**Stage 5 — S3 and the console:** S3's internal service health checking and metadata operations also depended on internal DNS. As DNS degraded, S3 began experiencing internal errors. API calls to S3 started failing. The AWS management console, which uses S3 to serve its static assets and stores session state in DynamoDB (which also experienced degradation), became unavailable. AWS's own tooling for diagnosing and responding to the outage was impaired.

**Stage 6 — Third-party cascade:** Every company that had built on these AWS services experienced failures proportional to their dependency on the affected services. The failure was not contained to a single service or a single availability zone. It was region-wide, because the internal DNS infrastructure is regional — a single degraded DNS layer affected all services across all AZs in US-EAST-1.

**Stage 7 — Recovery complexity:** Recovery was not simply a matter of stopping the automation and waiting. Services had to be restored in dependency order — the services that other services depend on had to come back first. Internal DNS had to be stabilised before services that use DNS could recover. Services that use those services had to wait further. The 7-hour recovery duration reflects the depth of the dependency graph, not the complexity of any individual service's recovery.

---

## The Architectural Problems This Exposed

### Problem 1: Control Plane and Data Plane Sharing a Network Path

The automation that caused the congestion was a control-plane operation — capacity management. Internal DNS is critical data-plane infrastructure. They should not share a network path with no isolation between them.

The principle of separation between control plane and data plane is fundamental to resilient network design. It exists precisely to prevent control-plane operations (which are operational, not customer-facing) from affecting data-plane operations (which serve customers directly). In this case, that separation was incomplete. A control-plane operation had a data-plane blast radius.

### Problem 2: Internal DNS as an Undiscovered Single Point of Failure

Internal DNS was not treated with the same redundancy and isolation that AWS applies to its customer-facing services. It was a shared resource that every internal service depended on, and it had a single network path through which it was reachable.

At hyperscale, any resource that every service depends on is a potential region-wide single point of failure. The list of such resources is rarely as short as people assume. Internal DNS was on that list, and it was not adequately hardened.

### Problem 3: Circular Bootstrap Dependencies

The most insidious problem exposed by this outage is the circular dependency in service bootstrapping. Service A needs DNS to start. Service B provides authentication, which is itself a DNS-resolution-dependent service. Service A therefore cannot authenticate without DNS, and DNS cannot be verified as healthy without authentication services that depend on DNS.

These circular bootstrap dependencies are a class of failure that is almost impossible to detect through normal operational testing, because under normal operation, everything is already running. They only become visible when the system needs to restart from scratch — exactly the conditions that occur during a recovery from an outage.

### Problem 4: The Health Dashboard Was On the Failing Infrastructure

The AWS Health Dashboard, the mechanism by which AWS communicates outage status to customers, was hosted on S3 — one of the failing services. This is a version of the "the fire alarm is inside the burning building" problem. When S3 failed, the dashboard that was supposed to tell customers S3 had failed also failed.

This is not a novel mistake. It is a specific and well-known class of resilience failure — observer dependency — and it requires explicit architectural work to prevent: the observability and communication infrastructure must be independent of the systems it observes.

### Problem 5: US-EAST-1 Concentration Risk

US-EAST-1 hosts a disproportionate fraction of AWS's global infrastructure, including many control-plane systems that manage resources in other regions. Its historical significance as AWS's original region means it has accumulated dependencies from other regions that create asymmetric blast radius. A failure in US-EAST-1 can affect operations in regions that appear geographically separate.

---

## What the Post-Mortem Said (and What It Understated)

AWS's public post-mortem was unusually detailed for a hyperscaler. It acknowledged the shared network path between the capacity automation and internal DNS, identified the DNS dependency as the propagation vector, and listed several corrective actions: network path isolation for control-plane operations, improved DNS redundancy, better tooling for testing automation impact before running it on production systems.

What the post-mortem understated: the depth of the bootstrap dependency problem. The circular dependency between DNS and the services that depend on DNS is a structural issue that cannot be fully resolved by adding DNS redundancy. It requires rethinking how services establish their initial state — and that is significantly harder than adding another DNS resolver cluster.

It also understated the concentration risk. The corrective actions described were primarily about hardening US-EAST-1, not about reducing the fraction of global AWS infrastructure that depends on US-EAST-1 being healthy.

---

## How a Next-Gen Network Engineer Thinks About This

### The question is not "how do we prevent this exact failure?"

The exact failure is already prevented — AWS fixed the specific path isolation problem. The useful question is: "What *class* of failure does this represent, and where else does that class exist in our architecture?"

The class is: **a shared critical resource with a single network path, depended upon by every service in the system, that can be made unreachable by an unrelated operational event.**

Every architecture has a version of this. The next-gen engineer's job is to find it before the outage does.

### Mapping your own dependency graph

AWS did not know that their internal DNS had this failure mode because nobody had drawn the complete dependency graph from "capacity automation" through "internal network path" to "DNS" to "every service in the region." The graph was implicit in the architecture but never made explicit.

The discipline of explicitly mapping dependency graphs — every service, every dependency, every shared resource — is unglamorous work. It does not produce visible output until it prevents an outage. At hyperscale, that prevention is worth more than almost anything else the team could be doing.

### Blast radius as a design constraint, not an afterthought

In the AWS outage, a single automated operation had a blast radius of the entire US-EAST-1 region. That blast radius was not designed. It was the accidental result of architectural decisions made over many years, each of which seemed reasonable in isolation.

The next-gen engineer treats blast radius as an explicit design constraint from the beginning. Not "how big is our blast radius?" but "what is the maximum blast radius we will accept for this type of operation, and how do we enforce that constraint architecturally?"

### The observer-dependency rule

The system that tells you the network is broken cannot be on the network that is broken. The incident management system that you use during an outage cannot be hosted in the region that is experiencing the outage. The health checks that verify DNS is working cannot themselves require DNS to function.

This rule sounds obvious stated plainly. It is violated constantly in practice, because the observability and communication infrastructure is almost always built as an afterthought rather than a primary design requirement.

### Testing the restart, not just the running state

Bootstrap dependencies are invisible under normal operation. The only way to find them is to test recovery from cold — deliberately shutting down a service (or a region simulation) and verifying that it can restart correctly without any pre-existing state.

Most teams test that their systems continue running correctly. Far fewer test that their systems can restart correctly from scratch. The bootstrap is the moment when circular dependencies become catastrophic.

---

## Designing the System That Avoids This Failure Class

If you were designing a regional cloud infrastructure from scratch, knowing what this outage revealed, the architectural principles would be:

**1. Physical network isolation for control-plane traffic.** Capacity operations, deployment automation, and management traffic run on a physically separate network path from the data plane. Not logically separate — physically separate. A saturated control-plane network cannot congest a data-plane network that shares no physical links.

**2. DNS infrastructure treated as first-class critical infrastructure.** Internal DNS has the same redundancy requirements as the most critical service in the region. Multiple independent clusters. Multiple independent network paths to reach them. Capacity reserved exclusively for DNS — not shared with any other workload.

**3. Bootstrap dependency mapping.** Every service documents its startup dependencies. The dependency graph is automatically checked for cycles. Any service that cannot start without a service that also cannot start without it is a design defect that must be resolved before the service ships.

**4. Observer independence.** Status dashboards, incident management systems, and communication tools are hosted outside the region they monitor. Their availability is structurally independent of the availability of the systems they observe.

**5. Capacity operation blast radius limits.** Any automated capacity operation has an explicit blast radius limit. If executing the operation would affect a resource that serves more than N percent of regional traffic, the automation requires a manual approval gate and a blast-radius assessment.

**6. Regional independence for control planes.** Control-plane systems that manage global resources are not concentrated in a single region. The failure of any region should not impair the ability of other regions to operate or recover.

None of these principles are novel. They appear in academic papers on fault-tolerant distributed systems going back decades. The gap is not knowledge — it is the discipline of applying these principles consistently in an architecture that is constantly evolving under operational pressure. That discipline is one of the defining characteristics of the next-generation network engineer.
