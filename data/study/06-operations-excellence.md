---
id: d6-operations
title: "Section 6: Ensuring solution and operations excellence"
domain: 6
order: 7
minutes: 23
summary: Operational excellence pillar, SRE fundamentals, the Cloud Observability suite (Monitoring, Logging, Trace, Profiler, Error Reporting), alerting strategy with burn-rate math, release management, support, quality control and production reliability practices.
---

Section 6 is ~12.5% of the exam and is the most "SRE-flavored" domain. Expect questions phrased as "the operations team is overwhelmed by alerts," "leadership wants to know if we met our availability target," or "how should logs be retained for 5 years at lowest cost." The answers come from the Well-Architected Framework's operational excellence pillar and the Cloud Observability suite.

## 6.1 The operational excellence pillar

The current Well-Architected Framework states operational excellence as five core principles; questions map onto them directly:

| Principle | What it asks for | Google Cloud enablers |
|---|---|---|
| Ensure operational readiness and performance using CloudOps | Define SLOs before launch, comprehensive observability, capacity planning, load testing, production readiness reviews | Cloud Monitoring SLOs, Cloud Logging, load testing, Active Assist |
| Manage incidents and problems | Clear incident command, on-call, runbooks, blameless postmortems, problem management to eliminate recurring causes | Alerting policies, Personalized Service Health, Gemini Cloud Assist investigations, Customer Care |
| Manage and optimize cloud resources | Rightsizing, autoscaling, cost visibility, quota management, cleanup of idle resources | Recommender, FinOps hub, budgets, Cloud Quotas |
| Automate and manage change | IaC, CI/CD, progressive delivery, automated rollback, change tracking | Terraform/Infrastructure Manager, Cloud Build, Cloud Deploy, Config Sync, Audit Logs |
| Continuously improve and innovate | Retrospectives, experimentation, adopting managed services, sharing knowledge | Postmortem action tracking, game days, Gemini Code/Cloud Assist |

Concrete recommendations the exam draws from: treat operations as code; instrument everything with metrics, logs and traces; define ownership per service; automate toil away; measure toil and keep it below ~50% of SRE time; practice failure (DiRT-style exercises); and align dashboards to SLOs rather than raw resource metrics.

## SRE fundamentals

### SLI, SLO, SLA and error budgets

- **SLI**: a ratio of good events to valid events. Availability SLI = successful requests / total requests; latency SLI = requests faster than threshold / total requests; freshness, correctness and durability SLIs for data pipelines.
- **SLO**: the target for an SLI over a window (rolling 28/30 days is standard). Choose the loosest target that keeps users happy — a 99.99% SLO for an internal batch report is wasted money.
- **SLA**: external promise with penalties; set below the SLO so a breached SLO does not immediately breach the SLA.
- **Error budget** = 100% − SLO. Over 30 days: 99% → 7.2 h; 99.9% → 43.2 min; 99.95% → 21.6 min; 99.99% → 4.32 min; 99.999% → 26 s.
- **Error budget policy**: agreed in advance — when the budget is exhausted, releases pause except reliability fixes; when the budget is healthy, the team is encouraged to ship faster and take risks.

### Golden signals, toil, on-call, postmortems

- **Four golden signals**: latency, traffic, errors, saturation (mnemonic LETS). Related frameworks: RED (rate, errors, duration) for services, USE (utilization, saturation, errors) for resources.
- **Toil**: manual, repetitive, automatable, tactical work that scales linearly with service growth. Track it; automate it.
- **On-call**: sustainable rotations (Google guidance ~25% of time), no more than about two paging incidents per shift, every page actionable with a runbook link, compensation and handoffs.
- **Blameless postmortems** with action items tracked to completion; share widely; postmortem for any SLO-impacting incident or pager event that required manual intervention.

> **Remember:** SLOs are about *user-visible* behaviour. A CPU-at-80% alert is not an SLO; "99.9% of checkout requests succeed under 500 ms" is.

## 6.2 Cloud Observability suite

### Cloud Monitoring

- **Metrics scopes**: a scoping project can view metrics from many monitored projects (multi-project dashboards and alerts). Put the metrics scope in a dedicated ops project. Grant `roles/monitoring.viewer` there rather than in every project.
- **Metric sources**: Google Cloud system metrics (free), agent metrics via the **Ops Agent** (single agent for logs + metrics, built on Fluent Bit and the OpenTelemetry Collector; replaces the legacy Logging and Monitoring agents), custom metrics via OpenTelemetry/OTLP, and **log-based metrics** (counter or distribution derived from a log filter; user-defined ones are billable). Metric data is retained 24 months (1-minute points kept ~6 weeks then downsampled).
- **Managed Service for Prometheus**: Google-managed, globally scaled Prometheus backend (Monarch). Managed collection on GKE via PodMonitoring CRDs, self-deployed collectors or the OTel collector elsewhere. Query with **PromQL** across projects; Grafana connects through the Prometheus API. **MQL** is the older Cloud Monitoring query language; PromQL is now supported everywhere (Metrics Explorer, dashboards, alerting).
- **GKE observability**: system metrics and logs on by default; opt-in control-plane metrics, kube state metrics, workload metrics via managed Prometheus; GKE dashboards; Cloud Service Mesh telemetry for per-service golden signals.
- **Dashboards**: prebuilt per service, custom dashboards as JSON/Terraform (`google_monitoring_dashboard`), dashboard-scoped filters; share via metrics scopes.
- **Uptime checks**: HTTP(S)/TCP probes from multiple geographic checker locations (minimum three regions) every 1–15 minutes for public endpoints, private uptime checks for internal endpoints via Service Directory. **Synthetic monitors** run a Cloud Run function (Node.js Puppeteer/Mocha) on a schedule for multi-step user journeys; the broken-link checker is a prebuilt synthetic.
- **Alerting policies**: condition types — metric threshold, metric absence, forecast (predicts crossing within a window), rate of change, log-based (match a log filter), PromQL, SLO burn rate. Conditions have a **retest window** (duration the condition must hold) to suppress flapping. Notification channels: email, SMS, mobile app, Slack, PagerDuty, Webhooks, **Pub/Sub** (for automated remediation via Cloud Run functions). Snooze and alert policy severity labels support routing.

### SLO monitoring and burn-rate alerting (with math)

Cloud Monitoring lets you define a **service** (auto-discovered for GKE, Cloud Run, App Engine, Istio, or custom), attach **SLIs** (request-based: availability or latency from LB/Istio/custom metrics; window-based: good minutes), set an **SLO** and a compliance period, and create **burn-rate alerts**.

**Burn rate** = observed error rate ÷ error rate allowed by the SLO. Burn rate 1 spends exactly the whole budget by the end of the window.

Worked example — SLO 99.9% over 30 days:

- Allowed error rate = 0.1%. Error budget = 30 d × 24 h × 60 min × 0.001 = **43.2 minutes** of total failure equivalent.
- Observed error rate of 1.44% ⇒ burn rate = 1.44 / 0.1 = **14.4**. At that rate the budget lasts 30 d / 14.4 ≈ **50 hours**; in **1 hour** you consume 14.4/720 ≈ **2%** of the monthly budget.
- Observed error rate 0.6% ⇒ burn rate **6**; over **6 hours** that is 5% of the budget.
- Observed error rate 0.1% ⇒ burn rate **1**; over **3 days** that is 10% of the budget.

Google's recommended **multi-window, multi-burn-rate** policy therefore is:

| Budget consumed | Long window | Short window | Burn rate | Action |
|---|---|---|---|---|
| 2% | 1 h | 5 min | 14.4 | Page |
| 5% | 6 h | 30 min | 6 | Page |
| 10% | 3 days | 6 h | 1 | Ticket |

The short window confirms the problem is still happening (fast reset once fixed); the long window guarantees significance. In MQL the condition is `select_slo_burn_rate(SLO, "1h")`; in the console you pick "SLO burn rate" and enter the lookback and threshold.

> **Exam tip:** "Alert only when reliability is truly at risk and stop paging on transient blips" → SLO burn-rate alerts with multiple windows, not static thresholds on CPU or 5xx counts.

### Cloud Logging

- **Ingestion path**: every log entry enters the **Log Router**, which evaluates **sinks** (inclusion and **exclusion** filters) and routes copies to destinations: **Logging buckets** (in the same or another project), **BigQuery** datasets, **Cloud Storage** buckets, **Pub/Sub** topics (→ Splunk, Datadog, SIEM), or another project's log bucket.
- **Buckets**: `_Required` holds Admin Activity, System Event and Access Transparency audit logs for **400 days**, non-configurable, free. `_Default` holds everything else for **30 days** by default; retention configurable from **1 to 3650 days** (about 10 years). Retention beyond 30 days is billed per GiB-month. Buckets can be **regional** for data residency and can be **locked** (immutable retention for compliance — irreversible). Custom buckets let you segregate teams or apply CMEK.
- **Aggregated sinks** at folder or organization level with `--include-children` route logs from all current and future child projects; **intercepting** aggregated sinks prevent the logs from also landing in child projects — the pattern for central SIEM export and for hiding audit logs from project owners.
- **Log Analytics**: upgrade a bucket to run SQL over logs directly (BigQuery-backed) and optionally create a **linked dataset** for joins in BigQuery without a separate export.
- **Views** and IAM: `roles/logging.viewer` for non-Data-Access logs, `roles/logging.privateLogViewer` for Data Access and Access Transparency logs; log views restrict access within a bucket.
- **Costs**: ingestion billed per GiB beyond a free monthly allotment per project (`_Required` logs are free); reduce with exclusion filters (exclude health-check and debug noise), sampling (`sample(insertId, 0.1)`), shorter retention, and routing bulky logs straight to Cloud Storage. **Data Access audit logs** are off by default (except BigQuery), can be voluminous and expensive, and are enabled per service/permission type (ADMIN_READ, DATA_READ, DATA_WRITE) via IAM audit config or org-level default.
- **Audit log types and retention**: Admin Activity 400 days (always on), Data Access 30 days (opt-in), System Event 400 days, Policy Denied 30 days (VPC Service Controls denials), Access Transparency 400 days (Google staff access, requires an eligible support plan).
- **Network logs**: **VPC Flow Logs** enabled per subnet with sampling (default 50% sample rate, 5-second aggregation; lower sampling to cut cost), 5-tuple flows for forensics, capacity planning and cost attribution; **firewall rules logging** per rule (allow/deny records, includes hierarchical policies); **Cloud Load Balancing logs** per backend service with configurable sample rate; Cloud NAT logs (translation and drops); Cloud Armor request logs; Cloud DNS query logging. Use **Packet Mirroring** for full packet capture.
- Log entries are capped at 256 KB; write structured JSON to get indexed fields; use the `severity` field and `trace` field for log-trace correlation.

### Cloud Trace, Cloud Profiler, Error Reporting

- **Cloud Trace**: distributed tracing via OpenTelemetry (or auto-instrumented on App Engine, Cloud Run with LB traces). Shows latency per span, service dependency graphs, latency distribution heatmaps and analysis reports comparing time ranges. Use for "which service in the chain adds latency."
- **Cloud Profiler**: continuous, low-overhead (typically under 1–5%) sampling profiler for CPU time, heap, wall time, contention and threads across Go, Java, Node.js, Python; flame graphs; compare versions to catch performance regressions after a deploy. Use for "reduce compute cost by finding hot code paths."
- **Error Reporting**: aggregates and deduplicates stack traces from logs (auto for App Engine, Cloud Run, Cloud Run functions, GKE with structured errors), shows first/last seen, occurrence trends and notifies on new error groups. (Cloud Debugger was retired; use Snapshot Debugger open source or logs.)

### Profiling and benchmarking approaches

- Benchmark before migration and after: capture baseline latency/throughput with the same load tool and dataset, then compare in the new environment.
- Use PerfKit Benchmarker for standardized infrastructure benchmarks (disk, network, database) across machine types.
- Profile in production continuously (Profiler) rather than in synthetic environments only; validate improvements with A/B or canary comparisons.
- For databases, use Query Insights (Cloud SQL, AlloyDB), Spanner Key Visualizer and query statistics, Bigtable Key Visualizer for hotspots, and BigQuery `INFORMATION_SCHEMA.JOBS` plus the query execution graph.

## Alerting strategies

- **Symptom-based over cause-based**: alert on what users experience (SLO burn, error ratio, latency percentiles); keep cause metrics (CPU, disk, queue depth) on dashboards for diagnosis. Cause-based alerts are acceptable for imminent saturation (disk 90% full, quota 80% consumed, certificate expiry).
- **Multi-window, multi-burn-rate** as above; long-window alerts for slow burns should create tickets, not pages.
- **Severity routing**: label alerts P1/P2/P3; P1 → PagerDuty/SMS 24/7 on-call; P2 → chat channel and ticket during business hours; P3 → weekly review. Use distinct notification channels per severity and per team; use Pub/Sub channels to trigger automated remediation (restart, scale, rollback via Cloud Deploy).
- **Reduce alert fatigue**: every alert must be actionable and link to a runbook; delete alerts nobody acts on; use retest windows and aggregation; snooze during maintenance; group by resource; review alert volume in postmortems; prefer one SLO alert per user journey over dozens of per-host alerts.
- **Coverage**: uptime checks from outside (detect DNS/LB/cert failures), synthetic journeys for critical flows, log-based alerts for security signals (e.g., IAM policy changes, `SetIamPolicy` on org), quota alerts, budget alerts, Personalized Service Health alerts for Google-side incidents.
- **Testing alerts**: fire them in staging, run game days, verify escalation paths and that channels are not stale.

> **Trap:** A per-VM CPU alert across 200 autoscaled instances creates a page storm during a legitimate traffic spike. Autoscaling handles saturation; the SLO alert tells you if users are hurt.

## 6.3 Deployment and release management

- **Release cadence**: small, frequent, decoupled from marketing launches; use feature flags to separate deploy from release; keep a changelog and versioned artifacts.
- **Progressive delivery with Cloud Deploy**: pipeline stages dev → staging → prod (optionally multiple regions in parallel via multi-target); canary strategy with percentages (e.g., 10 → 50 → 100) and automated **verify** steps; manual approvals for prod; **rollback** to the previous release in one command; **deploy policies** for freeze windows; automation rules for auto-promotion; audit trail of who promoted what.
- **GKE**: **release channels** Rapid, Regular (default), Stable, and **Extended** (longer support for a minor version, at additional cost) control control-plane and node auto-upgrade cadence. **Maintenance windows** and **maintenance exclusions** (including "no minor upgrades" scopes) control timing. Node upgrade strategies: **surge upgrades** (`max-surge`, `max-unavailable`) or **blue-green node pool upgrades** with soak time and rollback. Protect workloads with **PodDisruptionBudgets**, readiness probes, multiple replicas across zones, and topology spread constraints. Regional clusters keep the control plane available during upgrades.
- **Cloud Run**: every deploy creates an immutable **revision**; traffic split by percentage across revisions; **revision tags** give stable URLs (`tag---service-hash.run.app`) for testing without traffic; `--no-traffic` deploys dark; roll back by shifting 100% to the previous revision. Cloud Run jobs for batch releases (migrations) with retries and parallelism.
- **MIG update policies**: `type=PROACTIVE` (roll now) or `OPPORTUNISTIC` (apply on next recreate/scale); `maxSurge` and `maxUnavailable` (absolute or percent); `minimalAction` REFRESH/RESTART/REPLACE; `replacementMethod` SUBSTITUTE or RECREATE (keeps names, stateful); **canary** by setting a target size for the new instance template version; automatic **autohealing** using health checks; `most-disruptive-allowed-action` caps disruption.
- **Managed databases**: Cloud SQL maintenance windows and deny periods (up to 90 days), Enterprise Plus near-zero-downtime planned maintenance; Spanner and Bigtable have no maintenance downtime; AlloyDB maintenance windows.
- **Database schema changes — expand/contract**: (1) *expand*: add new nullable column/table, deploy code that writes both and reads old; (2) *migrate*: backfill in batches; (3) switch reads to new; (4) *contract*: drop old column after a full release cycle. Never make a release depend on a destructive migration; this is what makes blue/green and rollbacks safe. Tools: Liquibase/Flyway in Cloud Build or Cloud Run jobs; Spanner schema updates are online and non-blocking.
- Change record: every production change should be traceable to a commit, a pipeline run and an audit log entry; emergency changes go through the same pipeline with an expedited approval path (break-glass with logging).

## 6.4 Supporting deployed solutions

- **Support plans**: Basic (free), Standard (business hours, 4-hour P2), Enhanced (24/7, 1-hour P1, third-party technology support), Premium (15-minute P1, Technical Account Manager, operational health reviews, Event Management Service for launches). Customer Care cases are opened from the console; Premium/Enhanced support Cloud Support API integration with ticketing tools.
- **Runbooks**: procedure per alert, linked from the alert's documentation field (Markdown with variables like `${resource.label.instance_id}`); convert runbooks into automation (Cloud Run functions triggered by Pub/Sub notification channels, Workflows) — runbooks-as-code reduce toil.
- **Gemini Cloud Assist**: investigations that correlate logs, metrics, recent changes and known issues into ranked hypotheses; natural-language log and metric queries; explain an error; generate gcloud commands; hand off the investigation to a support case. Treat as a first responder that accelerates humans.
- **Active Assist recommenders**: IAM role recommender (least privilege from 90-day usage), VM rightsizing and idle resource recommenders, CUD recommender, security (firewall insights, unattended projects), reliability (e.g., regional PD suggestions, GKE version), cost (idle IPs/disks/images). Consume through console hubs, Recommender API, or BigQuery export of recommendations for fleet-wide review.
- **Personalized Service Health**: shows Google Cloud incidents relevant to *your* projects and locations, with alerting policies and Pub/Sub/log integration — the answer to "know when a Google-side incident affects us before customers tell us." The public Status Dashboard remains for global view.
- **Quota monitoring**: quotas are per project per region; view in IAM & Admin → Quotas & System Limits; alert on `serviceruntime.googleapis.com/quota/allocation/usage` vs limit (quota alerting), request increases through Cloud Quotas/API well before launches, set **quota overrides** to lower limits as guardrails, and watch rate quotas (API requests per minute) for bursty clients.
- **Operational handover**: production readiness review (PRR) checklist — SLOs defined, dashboards, alerts, runbooks, on-call, capacity plan, DR tested, backups verified, security review, cost budget, ownership documented.

## 6.5 Quality control measures

- **Review gates**: mandatory code review, branch protection, pipeline stages that cannot be skipped (build → test → scan → sign → deploy with approvals in Cloud Deploy).
- **Static analysis and coverage**: linters and SAST in Cloud Build (SonarQube, Semgrep, language-native tools); enforce coverage thresholds; **Gemini Code Assist** for suggested fixes and test generation.
- **Security scanning**: Artifact Analysis (containers, OS packages, language packages), on-demand scanning in the pipeline with a severity threshold to fail builds, Binary Authorization attestations requiring "scan passed," Web Security Scanner for deployed web apps, Security Command Center findings (misconfigurations, vulnerabilities, threats) with Premium/Enterprise tiers, Sensitive Data Protection scans of buckets/BigQuery for PII leakage.
- **Infrastructure quality**: `terraform validate`/`plan` review, policy-as-code (`gcloud beta terraform vet`, Policy Controller), **drift detection** with scheduled `terraform plan`, Infrastructure Manager, Config Sync drift correction, and Cloud Asset Inventory feeds alerting on manual console changes; org policies as preventive guardrails.
- **Capacity planning**: forecast from traffic trends (Monitoring forecast conditions), load test against expected peak ×1.5–2, verify quotas and regional capacity (reservations for guaranteed capacity, future reservations for big events), autoscaling limits, and headroom for N+1/N+2 zone loss.
- **Cost anomaly detection**: Cloud Billing anomaly detection surfaces unexpected spend spikes; complement with budget alerts on forecasted spend, BigQuery billing export queries with day-over-day deltas, and labels to attribute anomalies quickly.
- **Data quality**: Dataplex Universal Catalog data quality tasks and data profiling; Dataform assertions; schema validation in Pub/Sub; Dataflow dead-letter handling.
- **Definition of done** for operations: an SLO dashboard exists, alerts route to an owner, runbook written, postmortem template ready, cost tagged.

## 6.6 Reliability in production

- **Chaos engineering and game days**: form a hypothesis ("losing zone b keeps the SLO"), define blast radius and abort criteria, run in staging then production with observers, measure, fix, repeat. Tools: Chaos Mesh, LitmusChaos on GKE, Gremlin; simulate zone outages by draining node pools or removing a MIG zone; kill Cloud SQL primary to test failover (`gcloud sql instances failover`); revoke a dependency with firewall rules. Google's internal DiRT exercises are the model.
- **Penetration testing**: you may pen test your own Google Cloud workloads **without prior approval** from Google, provided you comply with the Acceptable Use Policy and Terms of Service and target only your own resources. DDoS-style load simulations against Google infrastructure are restricted — follow Google's documented process (e.g., approved testing partners) rather than launching volumetric attacks. Complement with Web Security Scanner, Security Command Center attack path simulation, and third-party red teams; feed findings into SCC or an issue tracker with SLAs for remediation.
- **Load testing**: run distributed load generators (Locust/k6 on GKE, Cloud Run jobs, Artillery) from a separate project; test against production-like environments with production-scale data; test steady state, spikes, soak (memory leaks) and failover under load; pre-warm quotas; watch golden signals and downstream dependencies (databases, third-party APIs). Cloud Load Balancing needs no pre-warming, but backend autoscaling has ramp time — configure autoscaler cool-down and min instances accordingly.
- **Resilience patterns to recommend**:
  - **Timeouts** on every outbound call; shorter than the caller's timeout so failures cascade predictably.
  - **Retries with exponential backoff and jitter**, capped attempts, only for idempotent operations, with a retry budget to prevent retry storms.
  - **Circuit breakers** (Cloud Service Mesh/Envoy outlier detection, client libraries) to stop hammering a failing dependency; **bulkheads** to isolate resource pools per dependency.
  - **Load shedding and backpressure**: return 429/503 early when saturated (Cloud Armor rate limiting, API Gateway/Apigee quotas, Pub/Sub as a buffer, autoscaler max limits protecting databases).
  - **Graceful degradation**: serve cached or partial results (Cloud CDN stale-while-revalidate, Memorystore), disable non-critical features via flags, static fallback pages from Cloud Storage behind the load balancer.
  - **Regional isolation / cell architecture**: deploy independent stacks per region, avoid global synchronous dependencies, roll changes region by region, use global external ALB with health-checked failover; keep control planes separate from data planes.
  - **Idempotency and deduplication** with request IDs; exactly-once semantics where supported (Pub/Sub exactly-once, Dataflow).
- **Zero-downtime maintenance**: Compute Engine **live migration** for host maintenance (set `onHostMaintenance=MIGRATE`; GPUs/Spot terminate instead); regional MIGs and rolling updates; GKE surge upgrades with PDBs; Cloud SQL Enterprise Plus near-zero-downtime maintenance and planned failover for testing; Spanner/Bigtable/Firestore have no maintenance windows; Cloud Run/Cloud Run functions handle platform maintenance transparently; use connection draining (LB `connectionDraining.drainingTimeoutSec`) and graceful SIGTERM handling.
- **Verify recovery, not just failure**: after each experiment confirm SLIs returned to baseline, autoscalers scaled back, and no orphaned resources or alerts remain.

> **Exam tip:** When a question lists "chaos engineering, penetration testing, load testing," it is checking that you (a) run them regularly, (b) run them in production-like conditions with safeguards, and (c) know pen tests need no Google approval but must respect the AUP.

## Key takeaways

- Operational excellence principles: operational readiness with CloudOps, incident and problem management, manage/optimize resources, automate and manage change, continuous improvement.
- SLI measures, SLO targets, SLA contracts; 99.9% over 30 days = 43.2 minutes of error budget; error budget policies govern release pace.
- Golden signals: latency, traffic, errors, saturation; alert on symptoms, dashboard the causes.
- Burn rate = observed error rate ÷ allowed error rate; multi-window alerts: 14.4× over 1 h/5 min, 6× over 6 h/30 min (page), 1× over 3 d/6 h (ticket).
- Metrics scopes centralize multi-project monitoring; Ops Agent for VMs; Managed Service for Prometheus with PromQL for Kubernetes and beyond.
- Log Router → sinks → Logging buckets/BigQuery/Cloud Storage/Pub/Sub; `_Required` 400 days free and immutable; `_Default` 30 days, configurable 1–3650 days; buckets can be locked and regional.
- Aggregated (and intercepting) sinks at org/folder level for central SIEM export; exclusions and sampling cut cost; Data Access audit logs are opt-in and billable.
- Audit retention: Admin Activity and System Event 400 days; Data Access and Policy Denied 30 days.
- Trace for cross-service latency, Profiler for code hotspots, Error Reporting for grouped exceptions.
- Progressive delivery with Cloud Deploy (canary, verify, approvals, rollback, deploy policies); GKE release channels, maintenance windows, surge/blue-green upgrades; Cloud Run revisions and tags; MIG update policies; expand/contract schema migrations.
- Support: Premium for 15-minute P1 and TAM; runbooks linked from alerts; Personalized Service Health for Google-side incidents; quota alerting before launches.
- Quality gates: reviews, static analysis, Artifact Analysis + Binary Authorization, drift detection, capacity planning, cost anomaly detection.
- Reliability practice: chaos game days, pen tests without Google pre-approval but within the AUP, load tests at 1.5–2× peak, timeouts/retries with jitter/circuit breakers/load shedding/graceful degradation, regional isolation, live migration and connection draining for zero-downtime maintenance.

## Quick self-check

- Q: An SLO of 99.95% over 30 days allows how much downtime? — **A:** 21.6 minutes.
- Q: Error rate is 1.44% against a 99.9% SLO. What is the burn rate and how much budget burns in one hour? — **A:** Burn rate 14.4; about 2% of the 30-day budget per hour.
- Q: Which Logging bucket stores Admin Activity audit logs, and for how long? — **A:** `_Required`, 400 days, not configurable.
- Q: How do you export logs from all current and future projects in an org to a SIEM without them remaining in the source projects? — **A:** An org-level intercepting aggregated sink to Pub/Sub (or a central bucket).
- Q: Which agent collects both logs and metrics from Compute Engine VMs today? — **A:** The Ops Agent.
- Q: A team wants to test a new Cloud Run revision at a stable URL with no production traffic. — **A:** Deploy with `--no-traffic` and a revision tag.
- Q: Do you need Google's approval before penetration testing your own Google Cloud resources? — **A:** No, but you must comply with the Acceptable Use Policy and Terms of Service and only target your own resources.
- Q: What schema-change pattern keeps blue/green rollbacks safe? — **A:** Expand/contract (additive change first, backfill, switch, remove later).
