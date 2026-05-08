# My Dashboard and Metrics Work at AWS

Building dashboards is not glamorous engineering work, but it is work with outsized operational impact. A team that cannot see its own network makes decisions in the dark — reacting to incidents instead of preventing them, guessing at root causes instead of diagnosing them, making capacity decisions based on intuition instead of data.

At AWS, I built Amazon QuickSight dashboards to address specific visibility gaps in our DC fabric deployment and operations workflows. This article covers what I built, what metrics mattered, and the operational decisions those dashboards enabled.

## The Visibility Problem We Had

My team managed network device deployments across new DC launches — spine switches, leaf switches, management networks, ML/AI fabric. The deployment process involved many steps across many devices, and the status of any given launch was not visible without querying multiple internal systems, running CLI commands on specific devices, and synthesizing the results mentally.

This meant that during a launch, the on-call engineer needed to know answers to questions like:
- How many devices in this launch have completed initial provisioning vs. are still pending?
- What percentage of spine switches have their BGP sessions up?
- Are there devices in a degraded state (partially configured, failed health checks)?
- What is the overall security patch compliance rate across the fleet?
- Which devices are overdue for patching?

Without dashboards, answering each of these required manual queries to multiple systems. With dashboards, the answers were visible at a glance, updated continuously, and shareable with management for goal setting and tracking.

## What I Built in QuickSight

**Launch Progress Dashboard**

The core use case: real-time visibility into the state of an active DC launch.

Data sources: the internal deployment tracking database (DynamoDB tables updated by my Lambda orchestration service) joined with the device inventory database.

Key metrics displayed:
- Total devices in scope vs. devices in each state (not started, in-progress, completed, failed)
- Completion percentage per project type (spine, leaf, management, ML/AI)
- Timeline of state transitions — a chart showing devices completing over time, useful for detecting if deployment velocity slowed or stalled
- Error log for failed devices with device identity and failure reason — allowing targeted intervention without manual log searches

The dashboard updated every 5 minutes via QuickSight's scheduled refresh. During an active launch, the team could check the dashboard instead of querying the state from the command line.

**Fleet Security Compliance Dashboard**

The second major dashboard addressed the security patching problem. Before automation, compliance was tracked manually in a spreadsheet that was always outdated. After automation, we had real-time state in a database — but a database without visualization is still difficult to act on.

Key metrics:
- Fleet-wide compliance percentage: the headline number. Went from 30% to 90% through my patching automation.
- Devices by OS version: a bar chart showing the distribution of OS versions across the fleet. Spikes at older versions indicated devices that had missed patching cycles.
- Devices by days since last patch: a histogram identifying devices that were significantly overdue, sorted by age.
- Compliance trend over time: a line chart showing how the fleet compliance rate moved week-over-week — essential for demonstrating progress to management and identifying if the rate was declining (indicating the automation was not keeping up with new device additions).

**Monthly Business Review Metrics**

Beyond the operational dashboards, I maintained summary metrics for monthly business reviews — aggregated data that showed the team's progress against goals.

Key metrics for MBR:
- Devices launched vs. target for the quarter
- Mean time to provision a new device (comparing automated vs. manual baseline)
- Fleet compliance rate (current vs. target)
- Number of incidents requiring manual intervention vs. automated resolution
- Hours saved through automation (tracked cumulatively — the 1,000+ hours and 3,000+ hours figures came from this tracking)

Presenting these metrics monthly required them to be accurate and reproducible — which meant the underlying data pipeline needed to be reliable, not just the dashboard.

## What I Learned About Building Operational Dashboards

**The consumer of the dashboard determines its design.** An on-call engineer during an active incident needs different information than a manager in a quarterly review. The incident dashboard needs real-time granularity, device-level specificity, and immediate visibility into what is broken. The management dashboard needs aggregated trends, percentage metrics, and comparison to targets. Building one dashboard for both audiences produces a dashboard that serves neither well.

**Ratio metrics are more useful than absolute counters.** "37 devices are non-compliant" is less useful than "fleet compliance is at 87%, down from 90% last week." The ratio provides context; the trend provides urgency. Raw counts are useful for drilling into specific devices, but they should not be the headline metric on a dashboard that is supposed to convey status at a glance.

**Alerts from dashboards must be specific and actionable.** QuickSight's alerting feature allows threshold-based notifications. I configured alerts for: compliance rate dropping below a threshold (indicating the patching automation had stopped working), any launch with devices stuck in "in-progress" state for more than a defined time (indicating a deployment failure), and any device with a failed health check that was not in a known maintenance state.

Every alert I configured had a defined owner and a defined first-response action. Alerts that generate a notification without a clear action are noise — and noise trains the team to ignore alerts.

**Data quality matters more than visualization quality.** A beautiful dashboard built on inaccurate data is worse than a plain table of accurate data. Before building the visualization layer, I spent significant time ensuring the underlying data sources were correctly populated by the automation systems — that state transitions were being recorded correctly, that device identifiers were consistent across systems, and that the data was being refreshed at the appropriate frequency for the use case.

## The Connection to LinkedIn's Work

LinkedIn's DC & Core team is managing a growing, multi-region infrastructure. The same visibility challenges exist at LinkedIn's scale: how do you know the state of your fleet? How do you track progress against deployment goals? How do you demonstrate compliance with security requirements? How do you detect degradation in your network fabric before it becomes an incident?

The tools differ (LinkedIn is not using AWS QuickSight internally), but the operational problems and the dashboard design principles are the same. This is the experience that makes the "Dashboard/Metrics" line on my resume directly applicable to the LinkedIn role — not just "I know how to use QuickSight," but "I built operational visibility systems that enabled data-driven decisions and proactive fleet management."
