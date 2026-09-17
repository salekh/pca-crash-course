---
id: d4d5-processes
title: "Sections 4 & 5: Optimizing processes and managing implementation"
domain: 4
order: 6
minutes: 30
summary: Technical and business process optimization (SDLC, CI/CD, DR, adoption framework, cost, SRE contracts) plus how architects guide dev/ops teams and interact with Google Cloud programmatically.
---

Sections 4 (~15%) and 5 (~12.5%) together are more than a quarter of the exam. Questions here are rarely about a single product; they describe a team, a process problem, or a business constraint and ask which *practice* or *tool chain* fixes it. Read for patterns: "manual" → automate; "no visibility" → observability + SLOs; "outage recurred" → blameless postmortem; "cost surprise" → budgets + CUDs + rightsizing; "long approval cycles" → Service Catalog / project factory.

## 4.1 Technical processes

### SDLC, DevOps and the DORA metrics

The exam treats DevOps as culture + automation + measurement. Google's DORA research defines four key metrics you must know cold:

| DORA metric | Measures | Elite performers (order of magnitude) |
|---|---|---|
| Deployment frequency | Throughput: how often code reaches production | On demand, multiple per day |
| Lead time for changes | Throughput: commit → production | Less than a day |
| Change failure rate | Stability: % of deployments causing incidents/rollbacks | ~5% |
| Time to restore service (MTTR) | Stability: incident start → resolved | Less than an hour |

Newer DORA reports add **reliability** (meeting SLOs) as a fifth dimension. Throughput and stability improve *together* when teams use small batches, trunk-based development, CI, and automated tests — the exam never asks you to trade speed for stability.

> **Exam tip:** If a question says "the team deploys monthly and each release has many defects," the answer pattern is smaller, more frequent releases with automated testing and progressive rollout — not a longer QA phase.

### CI/CD reference pipeline on Google Cloud

Memorize the managed chain and what each stage guarantees:

- **Source** – Cloud Source Repositories (legacy) / GitHub / GitLab connected via Cloud Build repositories or Developer Connect.
- **Cloud Build** – serverless CI. `cloudbuild.yaml` steps run in containers; private pools for VPC-only access; builds run as a user-specified service account. Produces SLSA provenance attestations.
- **Artifact Registry** – regional/multi-regional repos for containers, Maven, npm, Python, OS packages, Helm; CMEK; remote and virtual repositories; replaces Container Registry.
- **Artifact Analysis** – automatic vulnerability scanning on push for containers and language packages, plus on-demand scanning; results stored as occurrences/notes (Grafeas).
- **Binary Authorization** – admission control for GKE, Cloud Run and GKE Enterprise: only images with required **attestations** (signed by attestors, e.g. "passed vulnerability scan", "QA approved") may deploy. Supports dry-run mode and break-glass annotations that are audit-logged.
- **Cloud Deploy** – managed continuous delivery: a **delivery pipeline** with ordered **targets** (dev → staging → prod), **releases** rendered with Skaffold, **rollouts** per target, manual **approvals**, **canary** strategies with **automated verification**, one-click **rollback**, and **deploy policies** (e.g. no prod rollouts on weekends).
- **Runtime** – GKE, Cloud Run, or GKE Enterprise fleets. Assured Open Source Software and Software Delivery Shield are the umbrella names for supply-chain hardening.

Design notes tied to the Well-Architected Framework (security pillar): sign everything, verify at admission, never let humans push directly to prod, and keep the deploy service account distinct from the build service account (separation of duties).

### Deployment strategies

| Strategy | How | Rollback | Cost / complexity | Use when |
|---|---|---|---|---|
| Recreate | Stop old, start new | Redeploy old | Cheapest; downtime | Dev, batch, single-instance |
| Rolling | Replace instances gradually (MIG `maxSurge`/`maxUnavailable`, Kubernetes Deployment) | Roll back version gradually | Low extra capacity | Stateless services tolerant to mixed versions |
| Blue/green | Full parallel environment, switch traffic (LB backend, Cloud Run traffic 100%) | Instant: switch back | 2× capacity during release | Need instant rollback, DB schema compatible |
| Canary | Small % of real traffic to new version, expand on metrics | Route 100% back to stable | Modest extra capacity, needs good SLIs | Default for prod services; Cloud Deploy canary, Cloud Run traffic split, Istio/Cloud Service Mesh weights |
| A/B testing | Route by user attribute (header, cookie, geo) to compare *business* outcomes | Remove routing rule | Needs L7 routing (external ALB URL map, Apigee) | Product experiments, not reliability testing |
| Shadow / dark launch | Mirror traffic to new version; responses discarded | Nothing to roll back | 2× backend load; side effects must be suppressed | Validate performance of rewrites with zero user risk |

> **Trap:** Blue/green with a *shared database* is not an instant rollback if the new version ran destructive migrations. Pair it with expand/contract schema changes (see module 6).

### GitOps with Config Sync

- **Config Sync** (GKE and GKE Enterprise) continuously reconciles cluster state from a Git repo/OCI image/Helm chart; drift is reverted automatically. **Policy Controller** (OPA Gatekeeper based) enforces constraints such as "no privileged containers" and "required labels" at admission and in audit mode.
- Pattern: platform team owns a fleet-level repo (namespaces, RBAC, quotas); app teams own namespace repos. Multi-cluster consistency across hybrid/multicloud comes free.
- For non-Kubernetes resources, **Config Connector** lets you declare Google Cloud resources (buckets, Cloud SQL, IAM) as Kubernetes CRDs so the same GitOps loop manages infrastructure.

### Troubleshooting and root cause analysis

- **Blameless postmortems** for every incident that breached an SLO or paged a human. Structure: impact, timeline, root cause(s), trigger, detection, contributing factors, action items with owners and due dates, lessons learned. Blame individuals and you get hidden incidents.
- **Five whys** and fishbone diagrams to move from symptom ("checkout latency") to systemic cause ("no connection pool limit → DB saturation → retries amplified load").
- Observability tools by question: latency across services → **Cloud Trace**; CPU/heap hotspots → **Cloud Profiler**; exception grouping → **Error Reporting**; "what changed" → **Cloud Audit Logs** and Cloud Deploy/Config Sync history; network path → **Connectivity Tests** (Network Intelligence Center); firewall drops → firewall rules logging; packet-level → Packet Mirroring.
- **Gemini Cloud Assist investigations**: from an alert, log entry or resource page, Gemini correlates logs, metrics, config changes and known issues to propose likely root causes and remediation, and can open a support case pre-populated with the investigation. Natural-language queries also work in Logs Explorer and Metrics Explorer.

> **Exam tip:** "Reduce MTTR" answers combine three things: SLO-based alerting (detect fast), runbooks linked from alerts (act fast), and automated rollback in Cloud Deploy (recover fast).

### Testing and validation of software and infrastructure

| Test type | Where in pipeline | Google Cloud tooling |
|---|---|---|
| Unit | Every commit, Cloud Build step | Language frameworks; emulators for Pub/Sub, Firestore, Bigtable, Spanner |
| Integration | Post-build, ephemeral environment | Cloud Build + Terraform-created namespace/project; Testcontainers |
| End-to-end / UI | Staging target in Cloud Deploy | Synthetic monitors (Puppeteer), Selenium on GKE |
| Load / performance | Pre-prod and periodic prod | Locust or k6 on GKE, Distributed load testing pattern, JMeter |
| Chaos / resilience | Game days | Chaos Mesh / Litmus on GKE, Gremlin, simulated zone loss |
| Canary analysis | During rollout | Cloud Deploy verify job, Cloud Monitoring SLO comparison, Kayenta |
| Security | Pipeline gates | Artifact Analysis, Web Security Scanner, Binary Authorization |

Infrastructure validation: `terraform fmt` → `terraform validate` → `terraform plan` (review in PR) → policy-as-code (`gcloud beta terraform vet` with the Policy Library, Checkov, OPA/Conftest) → apply from CI only. Test infra modules with Terratest or Kitchen-Terraform in a sandbox project. Use Cloud Build triggers on pull requests and require plan output in the review.

### Service catalog and provisioning

- **Service Catalog** (Google Cloud): admins publish approved solutions (Terraform configs, Deployment Manager templates, links) to a catalog shared at org/folder level; developers self-serve compliant deployments without owning IAM to build them. Solves "every team builds its own insecure thing" and "central team is a bottleneck."
- **Project factory**: Terraform module (Cloud Foundation Toolkit `project-factory`, Fabric FAST) that creates projects with billing linked, APIs enabled, default network deleted, Shared VPC attached, budgets, labels and standard IAM — enforced consistency.
- **Golden images**: build hardened VM images with Packer via Cloud Build, store in image families, enforce with `constraints/compute.trustedImageProjects`; rotate on a schedule and use **OS patch management** (VM Manager) for in-place patching. Container equivalent: base images in Artifact Registry with policy-enforced provenance.

### Disaster recovery

Two numbers drive every DR design: **RTO** (how long you can be down) and **RPO** (how much data you can lose). Cost rises steeply as both approach zero.

| DR tier | Typical RTO | Typical RPO | Relative cost | Pattern on Google Cloud |
|---|---|---|---|---|
| Backup & restore (cold) | Hours to days | Hours (last backup) | $ | Backup and DR Service, PD snapshots to multi-region, Cloud SQL backups, IaC to rebuild |
| Pilot light | Tens of minutes to hours | Minutes | $$ | Minimal core (DB replica, images, IaC) always running in DR region; scale out on failover |
| Warm standby | Minutes | Seconds to minutes | $$$ | Scaled-down full stack in second region, cross-region replicas, DNS/LB failover |
| Hot / multi-site active-active | Near zero | Near zero | $$$$ | Global external ALB across regions, Spanner multi-region, Bigtable replication, multi-region GCS |

DR building blocks per service:

- **Compute Engine**: regional PD (synchronous two-zone replication), scheduled snapshots stored multi-regionally, custom images copied to DR region, regional MIGs, Backup and DR Service for application-consistent backups.
- **GKE**: multi-cluster with Multi Cluster Ingress/Gateway, Backup for GKE (namespaces + PVs), Config Sync to rebuild.
- **Cloud SQL**: HA is *zonal* failover, not DR; use cross-region read replicas promoted on disaster, automated backups + PITR (binary logs / WAL). Enterprise Plus offers advanced DR (switchover/replica failover).
- **Spanner / Bigtable / Firestore**: choose multi-region configuration for near-zero RPO/RTO.
- **Cloud Storage**: dual-region with **turbo replication** (~15-minute RPO target) or multi-region; Object Versioning and soft delete protect against deletion.
- **BigQuery**: multi-region datasets; cross-region dataset replication; snapshots and time travel.
- **Networking**: pre-provision VPC/subnets/firewalls in DR region via IaC; Cloud DNS with health-checked failover routing policies; global LB handles region loss automatically.

DR testing: run DR drills on a schedule (at least annually, quarterly for tier 1), automate failover with runbooks-as-code, test *restores* not just backups, and record results as evidence for compliance. The Well-Architected reliability pillar phrase: "untested DR is a hypothesis."

> **Remember:** HA protects against zone/instance failure inside a region; DR protects against region loss or logical corruption. Cloud SQL HA does not satisfy a "survive region outage" requirement.

## 4.2 Business processes

### Stakeholder and change management

- Identify stakeholders (sponsor, security, finance, operations, application owners, end users) and map them on an influence/interest grid. Translate technical proposals into their metrics: uptime and cost for the CFO, audit evidence for compliance, developer velocity for engineering leads.
- Facilitation techniques: workshops for requirement discovery, RACI matrices for ownership, decision logs for traceability.
- Change management (organizational): communicate the *why*, form a Cloud Center of Excellence (CCoE), pick early wins, provide training paths, define new operating model roles (platform team, SRE, FinOps). Change management (technical): change advisory that is automated via pipelines and policy, not weekly meetings — CI/CD *is* the change control record.

### Google Cloud Adoption Framework

Four **themes** (assess maturity in each) and three **phases** of maturity:

| Theme | Question it answers | Tactical | Strategic | Transformational |
|---|---|---|---|---|
| Learn | Are people skilled? | Ad hoc, third-party led | Structured training, certifications | Continuous learning culture, internal experts |
| Lead | Is leadership sponsoring and teams cross-functional? | IT-driven, siloed teams | Executive sponsor, CCoE | Product-centric teams, business-led innovation |
| Scale | Are services automated and cloud-native? | Lift-and-shift, manual ops | IaC, managed services, CI/CD | Fully automated, self-healing, serverless-first |
| Secure | Is security identity-centric and automated? | Perimeter controls, manual review | Centralized IAM, policy as code | Zero trust, continuous compliance, automated response |

The framework's **epics** (e.g., resource management, IAM, networking, logging/monitoring, billing, architecture, data, people) become the workstreams of a cloud program. Exam questions describe an organization and ask which phase it is in or which theme is weakest — match the vocabulary.

### Skills readiness and team assessment

Assess current skills against target roles, then close gaps with role-based learning paths (Google Cloud Skills Boost), certifications, hands-on labs, embedded partners, and pairing. Prefer upskilling ops teams into SRE/platform roles over replacing them. Migrate the least critical workload first as a learning vehicle.

### Decision-making processes

- **Architecture Decision Records (ADRs)**: short documents capturing context, options, decision, consequences; stored in the repo. They answer "why did we choose Spanner?" two years later.
- **Trade-off / weighted decision matrix**: list criteria (cost, latency, ops burden, compliance, lock-in), weight them, score options. Present the top two with the trade-offs, not a single "right" answer.
- **Proof of concept / pilot**: time-boxed, with explicit success criteria (e.g., p99 < 200 ms at 10k QPS, cost under $X). Use Spot VMs and a sandbox project; delete when done.
- Buy vs build vs modify vs retire (workload disposition): retire unused systems first, buy SaaS for undifferentiated capabilities, build only where it differentiates.

### Customer success management: SLA, SLO, SLI

| Term | Definition | Who owns | Example |
|---|---|---|---|
| SLI | A measured indicator of service health (ratio of good events / valid events) | Engineering | 99.93% of requests served < 300 ms last 28 days |
| SLO | Internal target for an SLI over a window | Product + SRE | 99.9% availability over 30 days |
| SLA | External contract with consequences (credits) — always looser than the SLO | Business/legal | 99.5% monthly or 10% credit |

**Error budget** = 1 − SLO. At 99.9% over 30 days that is 43.2 minutes of full downtime. An **error budget policy** defines what happens when the budget is spent: freeze feature launches, prioritize reliability work, require senior approval for risky changes. This is the mechanism that aligns dev velocity with ops stability.

Google Cloud support plans (Customer Care):

| Plan | Price shape | Response targets (P1) | Highlights |
|---|---|---|---|
| Basic | Free | None (billing/community only) | Documentation, community, billing support |
| Standard | Low monthly fee + % of spend | 4-hour P2 response, business hours | Unlimited cases, Active Assist recommendations |
| Enhanced | Higher monthly fee + % of spend | 1-hour P1 response, 24/7 | Third-party technology support, Event Management Service add-on |
| Premium | Highest monthly fee + % of spend | 15-minute P1 response, 24/7 | Technical Account Manager, operational health reviews, Assured Support add-on for regulated industries |

> **Exam tip:** Questions demanding "15-minute response" or "a named Technical Account Manager" always point to Premium Support. "Support for third-party software (e.g., Kubernetes, MongoDB)" starts at Enhanced.

### Cost optimization and resource optimization

CapEx (owned hardware, depreciated) versus OpEx (pay-as-you-go) is the headline business argument; the architect's job is to keep OpEx predictable. Tools, in the order the cost optimization pillar recommends them (visibility → accountability → optimization → governance):

**Visibility.** Export billing to **BigQuery** (standard usage, detailed usage with resource-level data, and pricing exports) and build **Looker Studio** dashboards; **FinOps hub** in the console surfaces savings opportunities and a FinOps score; cost table and reports for quick breakdowns by project/SKU/label.

**Accountability.** **Labels** (key-value on resources, propagate to billing export) for team/env/cost-center; **tags** (Resource Manager, hierarchical, IAM-conditioned) for governance such as org policy scoping; folders per business unit; one billing account per legal entity, subaccounts for resellers.

**Budgets and alerts.** Budgets scoped by project/service/label; thresholds on actual or *forecasted* spend; notifications by email and **Pub/Sub**, which can trigger a Cloud Run function to cap spend (e.g., disable billing, scale down). Budgets *never* stop spend by themselves — that is a classic trap.

**Commitment discounts.**

| Discount | Applies to | Commit unit | Term | Typical saving | Notes |
|---|---|---|---|---|---|
| Resource-based CUD | Compute Engine vCPU/memory/GPU/local SSD per region and machine family; also Cloud SQL, AlloyDB, Memorystore, Bigtable, Spanner (resource CUDs vary) | Amount of resources | 1 or 3 years | ~37%/~55% for general-purpose (up to ~70% memory-optimized) | Region and family specific; sole-tenant eligible |
| Spend-based CUD | Compute Flexible CUD, Cloud Run, GKE, Cloud SQL, Spanner, BigQuery editions, AlloyDB, Bigtable, Dataflow, Memorystore… | $/hour of spend | 1 or 3 years | ~28% (1 yr) / ~46% (3 yr) flexible compute | Applies across regions and machine families; best for changing shapes |
| Sustained use discount | N1, N2, N2D, C2, M1 (not E2, N4, C3, A-series) | Automatic | Monthly | Up to 30% (N1) / ~20% (N2/N2D/C2) | No action needed; not stackable on top of CUD-covered usage |
| Spot VMs | Any workload tolerant of preemption | None | None | 60–91% off on-demand | 30-second notice, can be reclaimed any time, no SLA, no live migration; GKE Spot node pools, Batch, Dataproc secondary workers |

**Rightsizing and Active Assist.** Recommender surfaces idle VMs, rightsizing (based on 8 days of metrics), idle PDs and IPs, unattended projects, CUD purchase recommendations, and IAM role reductions. Apply via console, `gcloud recommender`, or Recommender API in automation.

**Service-level levers.**

- **BigQuery**: on-demand (per TiB scanned; first 1 TiB/month free) vs **editions** (Standard/Enterprise/Enterprise Plus slots with autoscaling and optional 1-/3-year slot commitments). Reduce scans with partitioning, clustering, `SELECT` only needed columns, `--dry_run`, custom quotas per user; long-term storage discount after 90 days untouched; physical vs logical storage billing.
- **Cloud Storage**: match classes to access frequency (Standard / Nearline 30-day / Coldline 90-day / Archive 365-day minimums; retrieval fees on the cold tiers); **Autoclass** when access patterns are unknown; lifecycle rules to transition and delete; delete incomplete multipart uploads; avoid early-deletion charges.
- **Networking**: egress dominates surprises. Keep traffic in-region, use **Cloud CDN** and Media CDN for cacheable content, Private Google Access/PSC to avoid NAT costs, Standard Tier networking for non-latency-sensitive egress, and Interconnect for steady large hybrid flows (cheaper egress than internet).
- **Compute**: custom machine types, E2 for cost, autoscaling with schedules, shut down dev at night (Instance Schedules), preemptible/Spot for batch, serverless (Cloud Run scale-to-zero) for spiky workloads, Autopilot GKE to pay per pod.
- **Ops**: log exclusions and shorter retention, sampled VPC Flow Logs, metric cardinality control.

> **Trap:** "Predictable steady-state VMs for 3 years" → resource-based CUD, not Spot. "Unpredictable which machine family we will use next year" → spend-based flexible CUD.

### Business continuity

- **Business Impact Analysis (BIA)**: for each process, determine impact of downtime over time, dependencies, and derive RTO/RPO and Maximum Tolerable Downtime. This is the input to DR tiering — critical processes get hot standby, back-office gets backup/restore.
- **BCP vs DR**: BCP covers people, facilities, suppliers, communications and manual workarounds — how the *business* keeps running; DR is the IT subset — how *systems* recover. A BCP references DR plans, escalation trees, and alternate work arrangements.
- Validate continuity plans with tabletop exercises and full failover tests; align with compliance requirements (ISO 22301, SOC 2 availability criteria).

## 5.1 Advising development and operations teams

### Deployment specifics per platform

| Platform | Deployment unit | Rollout controls | Config & secrets | Notes |
|---|---|---|---|---|
| Cloud Run (services/jobs) | Container image or source (`gcloud run deploy --source .`) | Immutable **revisions**, traffic splitting, revision **tags** for preview URLs, `--no-traffic` for dark deploys | Env vars, mounted **Secret Manager** secrets (as env or volume), Cloud Storage/NFS volume mounts | Concurrency up to 1000 per instance, timeouts up to 60 min, min instances to cut cold starts, direct VPC egress |
| Cloud Run functions | Function source (2nd gen runs on Cloud Run) | Same revision model | Secret Manager env/volumes | Event triggers via Eventarc; HTTP functions up to 60-minute timeout, event-driven 9 min |
| GKE | Deployment/StatefulSet/Job manifests, Helm, Kustomize | Rolling update `maxSurge`/`maxUnavailable`, Argo Rollouts/Cloud Deploy canary, Gateway API traffic splitting | ConfigMaps, Kubernetes Secrets (encrypt with Cloud KMS application-layer encryption), Secret Manager add-on / External Secrets, **Workload Identity Federation for GKE** for credentials | Autopilot vs Standard, node auto-provisioning, PDBs for safe upgrades |
| Compute Engine MIG | Instance template + image | Rolling update policy (proactive/opportunistic, `maxSurge`, `maxUnavailable`, canary by template version), autohealing | Metadata server, startup scripts, Secret Manager via SDK, OS Config | Stateful MIGs for per-instance disks; regional MIGs across zones |
| App Engine | `app.yaml` service versions | Version traffic splitting (IP or cookie), `--no-promote` | Env vars in `app.yaml`, Secret Manager | Standard (sandboxed, scale to zero) vs Flexible (containers on VMs); prefer Cloud Run for new work |

Twelve-factor guidance for teams: build once, promote the same artifact through environments; configuration in environment, never in the image; secrets in Secret Manager with per-version IAM and rotation; health endpoints (`/healthz`, `/readyz`); structured JSON logs to stdout picked up by Cloud Logging; graceful shutdown on SIGTERM (Cloud Run gives up to 10 s, GKE `terminationGracePeriodSeconds`).

### API management: Apigee vs API Gateway vs Cloud Endpoints

| Capability | Apigee | API Gateway | Cloud Endpoints |
|---|---|---|---|
| Positioning | Full-lifecycle enterprise API management | Lightweight managed gateway for serverless backends | Self-managed proxy (ESPv2/Envoy) you deploy with your service |
| Backends | Anything: on-prem, multicloud, Google Cloud | Cloud Run, Cloud Run functions, App Engine, Compute/GKE via HTTP | Cloud Run, GKE, Compute Engine, App Engine Flexible |
| Spec | OpenAPI, GraphQL, gRPC, SOAP mediation | OpenAPI 2.0 | OpenAPI 2.0, gRPC |
| Policies | 50+: SpikeArrest, Quota, VerifyAPIKey, OAuthV2, JWT, JSON/XML threat protection, AssignMessage, ServiceCallout, JavaScript/Java/Python callouts, ResponseCache, mediation | API keys, JWT/Firebase/Google ID token auth, rate limiting via quota in spec | API keys, JWT, service account auth, quota via spec |
| Analytics & monetization | Rich analytics, developer portal, monetization, Advanced API Security (abuse detection), API hub for cataloguing | Cloud Logging/Monitoring only | Cloud Logging/Monitoring, Endpoints portal |
| Deployment | Apigee X (Google-managed, PSC/VPC peering), Apigee hybrid (runtime on your GKE), Apigee Edge (legacy) | Fully managed regional | You run the ESP container |
| Pricing | Subscription or pay-as-you-go | Per call | Free proxy; pay for compute |

Apigee best practices the exam likes: put **SpikeArrest** (smooth bursts) and **Quota** (business limits per app/developer) at the proxy pre-flow; terminate OAuth 2.0 at Apigee and pass an internal identity to backends; version APIs in the base path (`/v1/`); use **target servers** and **key value maps** for environment-specific config; enable **Advanced API Security** for bot detection; expose via a **developer portal** with API products bundling proxies; cache with **ResponseCache**/Populate-Cache; protect backends with **mTLS** or PSC southbound.

> **Exam tip:** "Monetize APIs to partners" or "need a developer portal and analytics" → Apigee. "Add auth and rate limits in front of Cloud Run functions cheaply" → API Gateway. "gRPC service already on GKE, want transcoding" → Cloud Endpoints/ESPv2.

### Testing frameworks (what to recommend)

Unit tests inside the container build (fail fast in Cloud Build); integration tests against emulators or ephemeral projects; contract tests for APIs (OpenAPI validation); load tests with Locust/k6 driven from GKE with results in Cloud Monitoring; soak tests before big launches; canary analysis comparing SLIs between baseline and canary; chaos experiments in staging first, then production during game days.

### Data and system migration tooling

| Tool | Migrates | Mode | Choose when |
|---|---|---|---|
| Migration Center | Discovery, assessment, TCO, grouping, migration planning (formerly StratoZone) | Agentless/agents, discovery client | Start of any migration program; includes Database Migration Assessment |
| Migrate to Virtual Machines | VMware, AWS EC2, Azure VMs, physical → Compute Engine | Continuous replication, test clones, cut-over waves | Lift-and-shift with minimal downtime |
| Migrate to Containers | Linux/Windows VMs → containers on GKE, GKE Autopilot or Cloud Run | Fit assessment, extraction, generated Dockerfile/manifests | Modernize VM apps without rewriting |
| Google Cloud VMware Engine | Whole vSphere environments | Native VMware SDDC on Google Cloud, HCX migration | Keep VMware tooling, quick datacenter exit |
| Database Migration Service (DMS) | MySQL, PostgreSQL, SQL Server → Cloud SQL/AlloyDB (homogeneous); Oracle/SQL Server → PostgreSQL/AlloyDB (heterogeneous with conversion workspace) | Continuous CDC with minimal-downtime cut-over | Managed database migration; homogeneous migrations to Cloud SQL are free |
| Datastream | Oracle, MySQL, PostgreSQL, SQL Server, MongoDB, Salesforce → BigQuery, Cloud Storage (and Spanner/Cloud SQL via Dataflow templates) | Serverless CDC/replication | Analytics replication, event-driven pipelines |
| Storage Transfer Service | S3, Azure Blob, HTTP lists, other buckets, on-prem POSIX (agents) → Cloud Storage or Filestore | Scheduled/one-time managed transfer, bandwidth caps | Large online transfers with sufficient bandwidth |
| Transfer Appliance | Offline bulk data (tens of TB to PB) | Shipped rack-mountable appliance (e.g., TA40 ~40 TB, TA300 ~300 TB usable) | Network transfer would take more than about a week or bandwidth is poor |
| BigQuery Data Transfer Service | SaaS (Google Ads, YouTube, Campaign Manager), S3, Redshift, Teradata, other BigQuery datasets → BigQuery | Scheduled | Recurring warehouse loads |
| gcloud storage / `rsync` | Ad-hoc files | CLI, parallel composite uploads | Small/medium transfers, scripting |

Rule of thumb for transfer time: 1 TB takes about 2.5 hours at 1 Gbps, about 30 hours at 100 Mbps. If the estimate exceeds a week, choose Transfer Appliance.

### Gemini Cloud Assist and Gemini Code Assist

- **Gemini Cloud Assist** (console): explains architectures, generates designs, cost optimization and reliability recommendations, troubleshooting investigations from logs/alerts, FinOps insights, natural-language Cloud Logging/Monitoring queries, and gcloud command generation in Cloud Shell. Advise teams to use it for first-pass RCA and design reviews, with human verification.
- **Gemini Code Assist** (IDE, Cloud Shell Editor, Cloud Workstations): code completion and generation, unit-test generation, code explanation, chat with codebase awareness; enterprise tier supports code customization from private repos. Also assists in BigQuery (SQL generation), Colab Enterprise, Apigee (spec generation), Application Integration and Database Studio.

## 5.2 Interacting with Google Cloud programmatically

### Developer environments

- **Cloud Shell**: free ephemeral VM with 5 GB persistent `$HOME`, gcloud/kubectl/terraform preinstalled, web preview on ports 8080–8084, times out after inactivity; boost mode available.
- **Cloud Shell Editor**: browser-based VS Code (Theia/Code OSS) with Cloud Code built in.
- **Cloud Code**: IDE plugins (VS Code, JetBrains) for Kubernetes/Cloud Run development: Skaffold-based deploy loops, Secret Manager integration, API explorer, Duet/Gemini integration, YAML linting.
- **Cloud Workstations**: managed, VPC-resident dev environments with preconfigured images, IAP access, idle timeouts, persistent disks; the answer for "developers must not have source code on laptops" or "standardized secure IDEs behind VPC Service Controls."

### gcloud essentials cheat sheet

```bash
# configuration
gcloud init                                  # interactive setup
gcloud config set project PROJECT_ID
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud config configurations create prod && gcloud config configurations activate prod
gcloud config list

# authentication modes
gcloud auth login                            # user credentials for gcloud
gcloud auth application-default login        # ADC for local client libraries
gcloud auth activate-service-account --key-file=key.json   # avoid; last resort
gcloud auth list
gcloud config set auth/impersonate_service_account SA@PROJECT.iam.gserviceaccount.com
gcloud compute instances list --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com

# projects, APIs, IAM
gcloud projects create PROJECT_ID --folder=FOLDER_ID
gcloud services enable compute.googleapis.com run.googleapis.com
gcloud projects add-iam-policy-binding PROJECT_ID --member=user:a@example.com --role=roles/viewer
gcloud iam service-accounts create deployer --display-name="Deployer"
gcloud iam service-accounts add-iam-policy-binding SA --member=group:devs@example.com --role=roles/iam.serviceAccountTokenCreator

# compute, GKE, Cloud Run
gcloud compute instances create web-1 --machine-type=e2-medium --image-family=debian-12 --image-project=debian-cloud
gcloud compute ssh web-1 --tunnel-through-iap
gcloud container clusters get-credentials CLUSTER --region us-central1     # writes kubeconfig
gcloud run deploy api --image REGION-docker.pkg.dev/PROJECT/repo/api:1.2 --region us-central1 --no-allow-unauthenticated
gcloud run services update-traffic api --to-revisions api-00012-xyz=10

# build & deploy
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT/repo/api:1.2
gcloud deploy releases create rel-001 --delivery-pipeline=api --region=us-central1 --images=api=IMAGE

# output control
gcloud compute instances list --filter="zone:us-central1-a AND status=RUNNING" --format="table(name,networkInterfaces[0].networkIP,status)"
gcloud projects list --format="value(projectId)"
gcloud compute instances list --format=json | jq '.[].name'
gcloud logging read 'resource.type="gce_instance" severity>=ERROR' --limit 20 --freshness=1h
```

Notes: `--filter` uses key operators (`=`, `:` (contains), `~` (regex), `>`), `--format` supports `table`, `json`, `yaml`, `csv`, `value`, `flattened` and projections; `gcloud alpha`/`gcloud beta` expose pre-GA surfaces; `gcloud components update` maintains the SDK (package-manager installs use apt/yum instead).

### gsutil vs gcloud storage, bq, kubectl

- **`gcloud storage`** is the current CLI (parallel by default, faster, consistent flags): `gcloud storage cp -r ./dir gs://bucket/`, `gcloud storage rsync --delete-unmatched-destination-objects`, `gcloud storage buckets create gs://b --location=US --uniform-bucket-level-access`, `gcloud storage ls -l`, `gcloud storage objects update --storage-class=NEARLINE`. **gsutil** is legacy (`gsutil -m cp`, `gsutil rsync`, `gsutil iam ch`, `gsutil lifecycle set`); it still works but new features land in `gcloud storage`.
- **bq**: `bq query --use_legacy_sql=false 'SELECT ...'`, `bq query --dry_run` to estimate bytes, `bq mk --dataset --location=EU proj:ds`, `bq load --source_format=CSV --autodetect ds.tbl gs://b/file.csv`, `bq extract ds.tbl gs://b/out-*.csv`, `bq show --schema ds.tbl`, `bq ls`, `bq cp` for table copies/snapshots.
- **kubectl**: obtain credentials via `gcloud container clusters get-credentials`; GKE uses the `gke-gcloud-auth-plugin`; `kubectl config get-contexts` for multiple clusters; Connect Gateway for fleet clusters without direct network access.

### Cloud emulators

| Emulator | Start command | Env var to point clients | Limits to know |
|---|---|---|---|
| Pub/Sub | `gcloud beta emulators pubsub start --project=demo` then `$(gcloud beta emulators pubsub env-init)` | `PUBSUB_EMULATOR_HOST` | No IAM, no persistence across restarts, limited feature parity (e.g., no BigQuery subscriptions) |
| Firestore | `gcloud emulators firestore start` (also in Firebase Local Emulator Suite) | `FIRESTORE_EMULATOR_HOST` | In-memory (optional export/import), supports security rules, no IAM |
| Bigtable | `gcloud beta emulators bigtable start` | `BIGTABLE_EMULATOR_HOST` | In-memory, single node, no replication/backup/IAM |
| Spanner | `gcloud emulators spanner start` (Docker image also available) | `SPANNER_EMULATOR_HOST` | Single instance config, no IAM/audit logs, limited concurrency & no performance fidelity, GoogleSQL and PostgreSQL dialects supported |
| Datastore | `gcloud beta emulators datastore start` | `DATASTORE_EMULATOR_HOST` | Legacy; prefer Firestore emulator |

Emulators are for unit/integration tests and offline development — never for performance testing or security validation.

### Infrastructure as Code best practices (Terraform and friends)

- **Remote state** in a Cloud Storage bucket (`backend "gcs"`) with **Object Versioning** enabled; the GCS backend provides state **locking** natively. One state per environment/component to limit blast radius; never commit state (contains secrets).
- **Modules**: use **Cloud Foundation Toolkit** (`terraform-google-modules/*` on the Terraform Registry) and **Cloud Foundation Fabric** (FAST stages) for opinionated, tested modules — project factory, network, GKE, log export, org policies. Pin provider (`google`, `google-beta`) and module versions.
- Workflow: PR → `fmt`/`validate`/`plan` in Cloud Build → policy check (`gcloud beta terraform vet`, Policy Library constraints) → approval → `apply` from CI using a dedicated SA with least privilege (impersonation, no keys). Use `prevent_destroy` lifecycle rules on stateful resources, `terraform import`/`import` blocks to adopt existing resources, and `moved` blocks for refactors.
- **Infrastructure Manager**: Google-managed Terraform execution (`gcloud infra-manager deployments apply --git-source-repo=...`), stores state, records revisions and drift; good when you want no self-hosted runners.
- **Config Connector / Config Controller**: manage Google Cloud resources as Kubernetes objects, reconciled continuously (drift correction). Config Controller is the hosted version (GKE + Config Connector + Config Sync + Policy Controller).
- Deployment Manager is legacy — choose Terraform in exam answers unless the question explicitly names it.
- Detect drift with periodic `terraform plan` in CI or Infrastructure Manager; use Cloud Asset Inventory feeds to alert on out-of-band changes.

### Accessing Google APIs: best practices

- **Application Default Credentials (ADC)** lookup order: (1) `GOOGLE_APPLICATION_CREDENTIALS` env var pointing at a credential file (SA key or WIF config), (2) user ADC file from `gcloud auth application-default login` (`~/.config/gcloud/application_default_credentials.json`), (3) the **attached service account** obtained from the metadata server on Compute Engine, GKE (via Workload Identity Federation for GKE), Cloud Run, Cloud Run functions, App Engine. Write code once against ADC; it works everywhere.
- **Avoid service account keys.** Prefer attached SAs, Workload Identity Federation (for AWS/Azure/OIDC/SAML/GitHub Actions), and short-lived token impersonation. Enforce with `constraints/iam.disableServiceAccountKeyCreation` and key-rotation alerts.
- **Scopes vs IAM**: access scopes on VMs are a legacy coarse filter; set the `cloud-platform` scope and control access with IAM roles on the service account. Both must allow the call.
- **Retries**: idempotent operations retry on 429/5xx with truncated **exponential backoff plus jitter**; use client-library default retry policies; honor `Retry-After`; make writes idempotent with request IDs.
- **Quotas**: per-project rate and allocation quotas; monitor `serviceruntime.googleapis.com/quota/*` metrics, set alerts, request increases ahead of launches through Cloud Quotas; use a **quota project** for user-credential calls (`gcloud auth application-default set-quota-project`).
- **Client libraries vs raw REST/gRPC**: Cloud Client Libraries (Java, Python, Go, Node.js, .NET, Ruby, PHP, C++) handle auth, retries, pagination, gRPC channels and streaming. Use REST directly only for unsupported languages or lightweight scripting; gRPC gives lower latency and streaming (Spanner, Bigtable, Pub/Sub).
- **API keys** identify a *project*, not a user — appropriate only for public, low-risk APIs (Maps, some Vertex AI/Gemini Developer API usage); restrict by API, HTTP referrer, IP or app; never use for data-plane access to Cloud Storage/BigQuery.
- Enable only needed APIs per project, use **Private Google Access**/**Private Service Connect** endpoints for API traffic from private networks, and log Data Access audit logs where compliance requires.

> **Remember:** "Application runs on GKE and needs to call BigQuery securely" → Workload Identity Federation for GKE mapping a Kubernetes service account to an IAM service account; no key files, no node-level SA sharing.

## Key takeaways

- DORA four keys: deployment frequency, lead time, change failure rate, time to restore — improve all four with small batches, CI/CD and progressive delivery.
- Reference pipeline: Cloud Build → Artifact Registry + Artifact Analysis → Binary Authorization → Cloud Deploy → GKE/Cloud Run; sign, scan, verify at admission.
- Canary is the default production strategy; blue/green for instant rollback; shadow for risk-free performance validation; A/B for business experiments.
- Config Sync + Policy Controller = GitOps with drift correction and policy enforcement; Config Connector extends it to Google Cloud resources.
- Blameless postmortems, five whys, SLO-based alerts and Gemini Cloud Assist investigations drive MTTR down.
- DR tiers: backup/restore → pilot light → warm standby → hot multi-site; cost climbs as RTO/RPO fall. Cloud SQL HA is not DR.
- Adoption Framework: themes Learn/Lead/Scale/Secure; phases Tactical/Strategic/Transformational.
- SLI measures, SLO targets, SLA contracts; error budget = 1 − SLO; error budget policies gate launches.
- Support: Premium for 15-minute P1 and TAM; Enhanced for 1-hour P1 and third-party tech; Standard for business-hours.
- Cost: billing export to BigQuery + Looker Studio, labels, budgets with Pub/Sub actions (budgets don't cap spend), resource vs spend CUDs, SUD automatic, Spot 60–91% off with 30-second notice.
- Apigee for full lifecycle/monetization; API Gateway for serverless fronting; Cloud Endpoints for self-run ESPv2 proxies.
- Migration tools: Migration Center to assess, Migrate to VMs/Containers for compute, DMS for databases, Datastream for CDC, STS online, Transfer Appliance offline.
- ADC order: env var → gcloud ADC → attached service account; avoid keys, use WIF and impersonation; retries with exponential backoff and jitter.
- Terraform: GCS remote state with versioning and locking, CFT/Fabric modules, policy checks in CI, Infrastructure Manager for managed runs.

## Quick self-check

- Q: Which DORA metric captures how quickly a commit reaches production? — **A:** Lead time for changes.
- Q: Which service blocks deployment of container images lacking a required signed attestation? — **A:** Binary Authorization.
- Q: A team needs instant rollback and can afford double capacity briefly; which strategy? — **A:** Blue/green.
- Q: RTO of minutes and RPO of seconds at moderate cost — which DR tier? — **A:** Warm standby (scaled-down stack plus cross-region replication).
- Q: Which Adoption Framework theme covers IaC, CI/CD and managed services maturity? — **A:** Scale.
- Q: Which support plan provides a Technical Account Manager and 15-minute P1 response? — **A:** Premium Support.
- Q: Workload machine types will change unpredictably but spend is steady — which discount? — **A:** Spend-based (flexible) CUD.
- Q: In ADC, what is checked before the metadata server's attached service account? — **A:** `GOOGLE_APPLICATION_CREDENTIALS` env var, then the gcloud user ADC file.
