---
id: d1-design
title: "Section 1: Designing and planning a cloud solution architecture"
domain: 1
order: 2
minutes: 22
summary: How to turn business and technical requirements into a Google Cloud architecture, plan a migration, and design for HA, DR and future modernization.
---

## Why this section matters

Section 1 is the largest slice of the exam (~25%). Almost every scenario question is really a Section 1 question in disguise: *"Given these business constraints and these technical constraints, which design is best?"* The exam rewards you for reading requirements carefully, mapping each one to a pillar of the Well-Architected Framework, and choosing the **simplest managed service that satisfies every stated constraint**.

> **Remember:** The six Well-Architected Framework pillars are **operational excellence, security (privacy & compliance), reliability, cost optimization, performance optimization, and sustainability**. When two answers both "work", the exam usually prefers the one that better serves the pillar the question emphasises (e.g. "minimize operational overhead" → operational excellence → pick the more managed service).

## 1.1 Designing for business requirements

### Functional vs non-functional requirements

| Type | What it describes | Examples in exam wording | Drives the choice of |
|---|---|---|---|
| Functional | *What* the system must do | "Users upload videos", "Generate a nightly report", "Expose a REST API to partners" | Services, APIs, data model |
| Non-functional (NFR) | *How well* it must do it | "99.99% availability", "p99 latency under 100 ms", "Data must stay in the EU", "Reduce ops burden", "RPO 15 minutes" | Topology (zonal/regional/multi-regional), tiers, replication, managed vs self-managed |

Read every case study or scenario twice: once to list functional requirements, once to extract NFRs. NFRs almost always decide the answer.

### Success measurements: KPIs, ROI, TCO

- **KPI (key performance indicator)** – measurable business or technical goal: conversion rate, checkout latency, MTTR, cost per transaction, model accuracy. Technical KPIs should map to **SLIs** (measured) and **SLOs** (targets); SLAs are contractual consequences.
- **ROI** = (gain − cost) / cost. Exam answers that "increase ROI" typically reduce cost (managed services, right-sizing, CUDs) or accelerate time-to-market.
- **TCO** includes hardware, licences, facilities, power, staff, downtime and migration cost — not just the cloud bill. Migration Center produces TCO reports comparing on-prem to Google Cloud.

### CapEx vs OpEx

| | CapEx (on-prem) | OpEx (cloud) |
|---|---|---|
| Spending | Large upfront purchases, depreciated over years | Pay-as-you-go, expensed monthly |
| Capacity | Sized for peak; idle most of the time | Elastic; autoscale to demand |
| Risk | Over/under-provisioning | Bill shock without budgets/quotas |
| Exam signal | "Data centre lease expires", "hardware refresh due" → migrate | "Predictable spend" → CUDs; "variable spend" → autoscaling + Spot |

> **Exam tip:** Cost-optimization tools to name: **Budgets & alerts** (Cloud Billing), **billing export to BigQuery**, **Recommender** (idle VMs, rightsizing), **Committed use discounts** (1- or 3-year, resource- or spend-based), **Sustained use discounts** (automatic on some Compute Engine families), **Spot VMs** (60–91% cheaper, preemptible any time), **Autoclass** and **lifecycle rules** for storage, **BigQuery slot reservations / editions**, **Gemini Cloud Assist** cost insights.

### Workload disposition: build, buy, modify, deprecate

| Disposition | When | Google Cloud example |
|---|---|---|
| **Buy** (SaaS / managed) | Commodity capability, no differentiation | Google Workspace, Apigee, Looker, a Marketplace SaaS |
| **Build** | Core differentiator, unique requirements | Custom service on Cloud Run / GKE with Vertex AI |
| **Modify / modernize** | Valuable but ageing app | Refactor monolith to containers; move DB to Cloud SQL / AlloyDB |
| **Deprecate / retire** | Redundant or unused (often 10–20% of a portfolio) | Decommission during migration assessment |

The exam's "six Rs" of migration (below) overlap with this: *retire* = deprecate, *retain* = keep on-prem, *rehost/replatform/refactor* = modify, *repurchase* = buy.

### Integration patterns with external systems

| Pattern | Characteristics | Google Cloud services | Use when |
|---|---|---|---|
| **Synchronous API** (REST/gRPC) | Request/response, tight coupling, low latency | Apigee (external partner APIs, monetization, quotas), Cloud Endpoints / API Gateway (lightweight), Cloud Load Balancing | Caller needs an immediate answer |
| **Asynchronous messaging** | Decoupled, buffered, fan-out, retries | **Pub/Sub** (global, at-least-once, ordering keys, 7-day default / up to 31-day retention, exactly-once delivery on pull subscriptions), Cloud Tasks (targeted, rate-limited task queues), Eventarc (event routing to Cloud Run/GKE/Workflows) | Spiky loads, multiple consumers, tolerance for eventual consistency |
| **File / batch transfer** | Periodic bulk exchange | Cloud Storage + Storage Transfer Service, SFTP on GCE, Transfer Appliance, Workflows/Composer to orchestrate | Legacy partners, nightly extracts |
| **Change data capture (CDC)** | Stream DB changes with low latency | **Datastream** (serverless CDC from Oracle, MySQL, PostgreSQL, SQL Server → BigQuery, Cloud Storage, Spanner via Dataflow templates) | Keep an analytical copy fresh; near-zero-downtime migration; event sourcing off legacy DB |
| **Workflow orchestration** | Multi-step business processes | **Workflows** (serverless, HTTP-based steps), **Cloud Composer** (Apache Airflow, data pipelines), Application Integration | Long-running, conditional processes |

> **Trap:** Pub/Sub vs Cloud Tasks. Pub/Sub is publisher-driven fan-out ("something happened"); Cloud Tasks is a work queue where the *sender* controls the target, rate and scheduling ("do this later, at most N/s"). Both are wrong answers when the question asks for *streaming analytics windows* — that is Dataflow consuming Pub/Sub.

### Movement of data

Estimate transfer time first; the network is the bottleneck far more often than the tool.

| Data size | 10 Mbps | 100 Mbps | 1 Gbps | 10 Gbps |
|---|---|---|---|---|
| 1 GB | ~14 min | ~1.5 min | ~8 s | <1 s |
| 100 GB | ~1 day | ~2.5 h | ~15 min | ~1.5 min |
| 1 TB | ~10 days | **~1 day** | ~2.5 h | ~15 min |
| 10 TB | ~3 months | ~10 days | ~1 day | ~2.5 h |
| 100 TB | ~2.5 years | **~3 months** | ~10 days | ~1 day |
| 1 PB | ~25 years | ~2.5 years | ~3 months | ~10 days |

(Rule of thumb: 1 TB over 100 Mbps ≈ 1 day; every 10× in size or ÷10 in bandwidth moves you one cell.)

| Tool | Use when | Avoid when | Key facts |
|---|---|---|---|
| **gcloud storage / gsutil** (online, self-managed) | < ~1 TB, one-off, scriptable | Large, recurring, or must be scheduled/retried | `gcloud storage cp -r`; parallel composite uploads; resumable |
| **Storage Transfer Service** | Online transfer from S3, Azure Blob, HTTP lists, other buckets, **or on-prem file systems (agent-based)** — scheduled, incremental, managed | Bandwidth is the constraint | Agents run in Docker near the data; supports bandwidth caps; manifest files; > 1 TB from on-prem is its sweet spot |
| **Transfer Appliance** | Tens of TB to PB with insufficient bandwidth (weeks/months online), or no connectivity | Small datasets; tight day-scale deadlines (shipping + ingest takes ~weeks) | Rackable device (~40 TB & ~300 TB usable classes; larger via multiple units); data encrypted with customer-managed keys; uploaded to Cloud Storage bucket |
| **BigQuery Data Transfer Service** | SaaS/warehouse → BigQuery (Teradata, Redshift, S3, Google Ads, YouTube, etc.) on schedule | Row-level transactional DBs | Managed, scheduled, no code |
| **Database Migration Service (DMS)** | Homogeneous (MySQL→Cloud SQL for MySQL, PostgreSQL→Cloud SQL/AlloyDB) and heterogeneous (Oracle/SQL Server→PostgreSQL) migrations, continuous replication for minimal downtime | NoSQL sources; ad-hoc analytics copies | Serverless, free for homogeneous; uses native replication; cut-over when lag ≈ 0 |
| **Datastream** | Continuous CDC into BigQuery/Cloud Storage/Spanner; keep source running | Full lift of a DB into Cloud SQL (use DMS) | Serverless; connects via IP allowlist, forward SSH tunnel or Private connectivity (VPC peering) |
| **Dedicated/Partner Interconnect** | Ongoing hybrid traffic, repeated large transfers | One-time transfer only | See Section 1 deep-dive for bandwidths |

> **Exam tip:** Look for wording like "*the office has a 100 Mbps connection and must move 200 TB within a month*" → Transfer Appliance. "*Keep the on-prem database as system of record while analysts query it in BigQuery*" → Datastream. "*Migrate MySQL to Cloud SQL with minimal downtime*" → DMS.

### Security, compliance and observability as business requirements

Even in Section 1, note the requirements that cascade into design: data residency (pick regions + **organization policy** `constraints/gcp.resourceLocations`, **Assured Workloads** for FedRAMP/CJIS/IL4/EU sovereignty), PCI-DSS (network segmentation, Cloud Armor, tokenization, Sensitive Data Protection), HIPAA (BAA, audit logs), and observability (Cloud Logging/Monitoring, SLO-based alerting). Say "designed in from day one", never "added after migration".

## 1.2 Designing for technical requirements

### Well-Architected Framework quick map

| Pillar | Ask yourself | Typical design levers |
|---|---|---|
| Operational excellence | Can we deploy, observe and roll back safely? | IaC (Terraform), CI/CD (Cloud Build, Cloud Deploy), SLOs, Cloud Observability, runbooks, Gemini Cloud Assist |
| Security | Least privilege? Encrypted? Auditable? | IAM, VPC-SC, CMEK, Secret Manager, Binary Authorization, SCC |
| Reliability | What is the failure domain and the SLO? | Regional/multi-regional, MIGs, health checks, DR tiers, chaos testing |
| Cost optimization | Are we paying for idle capacity? | Autoscaling, Spot, CUDs, storage classes, rightsizing |
| Performance optimization | Where is latency introduced? | Region placement, CDN, caching, network tier, machine family |
| Sustainability | Can we use low-carbon regions and fewer idle resources? | Carbon Footprint export, region choice, serverless |

### High availability and failover design

**Failure domains:** zone (single data-centre-ish facility) → region (3+ zones, typically ≥100 km apart from other regions) → multi-region (continent). Design so that the loss of one domain below your required SLO does not cause an outage.

| Service | Zonal option | Regional option | Multi-regional / global option |
|---|---|---|---|
| Compute Engine | Single VM, zonal MIG | Regional MIG (spread across ≥3 zones) | Global LB across regional MIGs |
| Persistent Disk / Hyperdisk | Zonal PD | Regional PD (synchronous replication across 2 zones), Hyperdisk Balanced HA | Snapshots (multi-regional storage) |
| GKE | Zonal cluster | Regional cluster (control plane + nodes across 3 zones) — Autopilot is always regional | Multi-cluster Ingress / Gateway, Fleet |
| Cloud SQL | Single zone | HA config (synchronous standby in 2nd zone, automatic failover ~60 s) | Cross-region read replicas (manual promote) |
| AlloyDB | — | Primary instance is regional HA by default; read pools | Cross-region replication (secondary cluster) |
| Spanner | — | Regional (3 read-write replicas) 99.99% | Multi-region / dual-region configs 99.999% |
| Bigtable | Single-cluster instance | Multi-cluster replication within a region | Multi-cluster across regions (eventually consistent, app profiles for routing) |
| Firestore | — | Regional 99.99% | Multi-region (nam5, eur3) 99.999% |
| Cloud Storage | — | Regional | Dual-region (turbo replication RPO 15 min), Multi-region |
| Memorystore for Redis | Basic tier | Standard tier (replica in another zone), Redis Cluster | Cross-region replication (Redis Cluster/Valkey, limited) |
| BigQuery | — | Regional dataset | Multi-region dataset (US/EU); cross-region replication for DR |
| Pub/Sub, Cloud Run, Cloud Load Balancing | — | Cloud Run is regional (multi-region via global LB + serverless NEGs) | Pub/Sub is global; global external ALB is global |

**Failover patterns to recognise:**

- **Active-passive with health-checked failover**: regional MIG behind a load balancer; a failed instance is recreated by autohealing (health check → recreate).
- **Active-active multi-region**: global external Application Load Balancer routes to the nearest healthy backend; stateless services + globally replicated data (Spanner multi-region, Firestore multi-region, Cloud Storage multi-region).
- **Database failover**: Cloud SQL HA (automatic, same region, synchronous, no data loss), read replica promotion (cross-region, manual/scripted, possible data loss = replication lag), Spanner (automatic, transparent).
- **DNS-based failover**: Cloud DNS routing policies (geolocation, weighted, failover with health checks) when backends are not behind a single global LB (e.g., hybrid).
- **Graceful degradation**: circuit breakers, retries with exponential backoff and jitter, load shedding, queues (Pub/Sub) to absorb bursts.

### SLAs to remember

| Service / configuration | Monthly uptime SLA |
|---|---|
| Compute Engine single instance (memory-optimized excluded) | 99.9% |
| Compute Engine instances in ≥2 zones / regional MIG | 99.99% |
| Cloud SQL HA: Enterprise edition / Enterprise Plus edition | 99.95% / 99.99% (Enterprise Plus also has near-zero-downtime planned maintenance) |
| AlloyDB (HA primary) | 99.99% |
| Spanner regional | 99.99% |
| Spanner multi-region | 99.999% |
| Firestore regional / multi-region | 99.99% / 99.999% |
| Bigtable single cluster / multi-cluster replication | 99.9% / 99.999% |
| Cloud Storage Standard: regional / dual-region / multi-region | 99.9% / 99.95% / 99.95% (designed durability 11 nines for all classes) |
| BigQuery | 99.99% |
| GKE zonal control plane / regional control plane / Autopilot pods | 99.5% / 99.95% / 99.9% |
| Cloud Run (regional) | 99.95% |
| Cloud Load Balancing (global) | 99.99% |
| HA VPN / Classic VPN | 99.99% / 99.9% |
| Dedicated & Partner Interconnect (99.9% topology / 99.99% topology) | 99.9% / 99.99% |
| Cloud DNS | 100% |
| Memorystore Redis Standard tier | 99.9% |

> **Remember:** A **zonal** anything has no availability SLA to speak of by itself (single VM ~99.9%). If the requirement says **99.99%**, you need multi-zone (regional). If it says **99.999%**, you need multi-region and Spanner/Firestore/Bigtable multi-region-style replication.

> **Trap:** SLAs do not add up by picking the best component; the composite availability of serially dependent services is the *product* of their availabilities. Two 99.9% services in series ≈ 99.8%. Redundant parallel paths raise it.

### Scalability and flexibility

- **Horizontal (scale out)** is preferred: MIG autoscaling (CPU, LB utilization, Cloud Monitoring metrics, schedules, predictive autoscaling), GKE Horizontal Pod Autoscaler + Cluster Autoscaler/Node Auto-Provisioning (Autopilot does this for you), Cloud Run 0→N instances with concurrency up to 1000 per instance, Cloud Run functions per-request scaling.
- **Vertical (scale up)** for stateful legacy: bigger machine type, custom machine types, Cloud SQL edition upgrade — requires restart/downtime, upper bound.
- **Data layer scalability**: Spanner (horizontal, add nodes/processing units without downtime), Bigtable (add nodes, autoscaling), BigQuery (serverless slots), Firestore (automatic), Cloud SQL (vertical + read replicas — write bottleneck).
- **Decoupling**: put Pub/Sub or Cloud Tasks between producers and consumers so each tier scales independently; use Memorystore to shield databases from read amplification.
- **Stateless services**: keep session state in Memorystore/Firestore, files in Cloud Storage, so instances are interchangeable and autoscaling/rolling updates are safe.
- **Quotas**: know that regional quotas (CPUs, IPs) can block scale; request increases *before* migration waves.

### Performance and latency

| Lever | What it does | When it is the answer |
|---|---|---|
| **Region selection** | Put compute next to users and/or data; keep data in the same region as compute to avoid egress and latency | "Users are in Europe" → europe-west*; "must stay in country" → single region + org policy |
| **Cloud CDN** | Caches cacheable HTTP(S) content at Google edge; backed by global external ALB, supports Cloud Storage buckets and any backend, signed URLs/cookies, cache modes | Static assets, video segments, API responses with `Cache-Control` |
| **Media CDN** | Deep-edge CDN for large-scale streaming | Video-on-demand/live at broadcast scale |
| **Premium vs Standard Network Service Tier** | Premium: traffic enters Google's backbone at the nearest edge (cold-potato), global anycast IPs, required for global LB. Standard: hot-potato via public ISPs, regional IPs only, cheaper | Choose Standard only for cost-sensitive, regional, latency-tolerant workloads |
| **Caching** | Memorystore for Redis/Valkey/Memcached (sub-ms), application-level caches, BigQuery result cache and BI Engine | Read-heavy DB load, session stores, leaderboards |
| **Machine family / accelerators** | C3/C4 for compute-bound, M-series for in-memory, A3/GPUs & TPUs for ML, Local SSD for scratch IOPS, Hyperdisk Extreme for DB IOPS | Explicit throughput/IOPS numbers in the question |
| **Placement policies** | Compact placement puts VMs physically close (HPC/low-latency), spread placement across hosts (availability) | HPC, tightly coupled MPI |
| **Cross-region reads** | Read replicas, Spanner multi-region read-only replicas, Bigtable multi-cluster routing, Cloud Storage dual/multi-region | Global read latency requirements |

### Backup and recovery

**Definitions**

- **RPO (Recovery Point Objective)** – maximum tolerable data loss measured in time ("we can lose at most 15 minutes of transactions"). Drives *backup/replication frequency*.
- **RTO (Recovery Time Objective)** – maximum tolerable time to restore service. Drives *how "warm" the standby is*.
- Lower RPO/RTO = higher cost. The exam expects you to pick the cheapest tier that meets the stated numbers.

| DR tier | Standby state | Typical RTO | Typical RPO | Relative cost | Google Cloud pattern |
|---|---|---|---|---|---|
| **Cold** (backup & restore) | Nothing running; only backups/snapshots/images and IaC | Hours to a day+ | Hours (last backup) | $ | Snapshots + Cloud Storage backups + Terraform to rebuild; Backup and DR Service vault |
| **Warm** (pilot light / minimal standby) | Core data tier replicating; minimal compute pre-provisioned, scaled up on failover | Minutes to ~1 hour | Minutes (replication lag) | $$ | Cross-region Cloud SQL read replica, small regional MIG scaled to 0–1, DNS failover |
| **Hot** (active-active / multi-site) | Full capacity in ≥2 regions serving traffic | Seconds to minutes (often near zero) | Near zero | $$$ | Global external ALB + regional MIGs/GKE/Cloud Run in 2+ regions; Spanner or Firestore multi-region; Cloud Storage multi-region |

Backup mechanisms per layer:

| Layer | Mechanism | Notes |
|---|---|---|
| VM disks | PD/Hyperdisk snapshots (incremental, schedules via resource policies), machine images, **Backup and DR Service** (agentless VM backups, backup vaults, immutable/indelible retention) | Snapshots stored regionally or multi-regionally; can be restored cross-region |
| Cloud SQL | Automated daily backups (retained 7 by default, up to 365), on-demand backups, point-in-time recovery via binary/WAL logs, cross-region backup location | PITR requires binary logging; HA ≠ backup |
| AlloyDB | Continuous backup & PITR (up to 35 days), on-demand backups | |
| Spanner | Backups (retained up to 1 year), PITR via version retention (up to 7 days), import/export via Dataflow | |
| Bigtable | Backups (up to 90 days), replication | |
| Firestore | Scheduled backups (daily/weekly, retention up to 14 weeks), PITR (7 days), managed export to Cloud Storage | |
| BigQuery | Time travel (2–7 days), table snapshots, cross-region dataset replication | |
| Cloud Storage | Object versioning, soft delete (default 7 days, configurable 0–90), retention policies with **bucket lock** (irreversible), Turbo replication (dual-region, 15 min RPO), Storage Transfer Service copies | Bucket lock = WORM compliance |
| GKE | Backup for GKE (cluster state + PV data), GitOps for config | |

> **Exam tip:** "Backups must be immutable / protected from a compromised admin" → Backup and DR Service backup vault (enforced retention) or Cloud Storage retention policy + bucket lock. "Recover a table dropped yesterday" → BigQuery time travel. "Restore DB to 5 minutes before the bad deploy" → PITR.

### Gemini Cloud Assist

Gemini Cloud Assist is the AI assistant embedded in the Google Cloud console and CLI. For architects the relevant capabilities are: generating architecture designs and diagrams from natural-language requirements (Application Design Center integration), explaining and troubleshooting errors/logs, cost and optimization recommendations, and suggesting gcloud commands. Exam positioning: it *assists* design and operations; it is not a runtime component and does not replace IAM review or architecture decisions.

## Decision trees

### Compute selection

- Is the workload an event-driven function (single purpose, short-lived, triggered by HTTP/Pub/Sub/Storage/Eventarc)?
  - Yes → **Cloud Run functions**.
  - No ↓
- Can it be packaged as a stateless container that serves requests or runs jobs to completion, with no need for privileged kernel access or GPUs beyond what Cloud Run offers?
  - Yes, and you want minimal ops → **Cloud Run** (services for request/response, jobs for batch; scale to zero; up to 60-min request timeout).
  - Yes, but you need Kubernetes APIs, service mesh, DaemonSets, stateful sets, custom scheduling, multi-tenant clusters, or portability across clouds/on-prem ↓
    - Prefer Google-managed nodes, pay per pod → **GKE Autopilot**.
    - Need node-level control (custom kernels, specific machine families, local SSD, GPU sharing configs) → **GKE Standard**.
    - Need consistent Kubernetes + policy across on-prem/multicloud → **GKE Enterprise** (fleets, Config Sync, Policy Controller, Cloud Service Mesh).
  - No ↓
- Is it a batch/HPC job that can run as containers or scripts on many VMs with queueing and retries?
  - Yes → **Batch** (managed job scheduling on Compute Engine, Spot-friendly).
- Does it require a specific OS, licensed software tied to a VM/host, kernel modules, or lift-and-shift with no code changes?
  - Yes → **Compute Engine** (MIGs for stateless; stateful MIGs or single VMs for stateful). Licensing tied to physical cores → **sole-tenant nodes**.
- Is it an existing VMware estate (vSphere, vSAN, NSX-T) that must move fast unchanged?
  - Yes → **Google Cloud VMware Engine**.
- Does it need bare metal (Oracle RAC, specialised hardware, licences that forbid virtualisation)?
  - Yes → **Bare Metal Solution** (regional extension colocated with Google Cloud; note Google has been steering Oracle workloads to Oracle Database@Google Cloud).
- Legacy PaaS already on **App Engine**? Keep it if it works; new designs go to Cloud Run.

### Database selection

- Is the data primarily analytical (aggregations over large scans, BI, SQL over TB–PB, columnar)?
  - Yes → **BigQuery** (serverless warehouse; streaming inserts / Storage Write API; BigLake for lakehouse; BI Engine for sub-second dashboards).
  - No ↓
- Relational with transactions / SQL joins?
  - Yes ↓
    - Needs horizontal write scale, global/multi-region strong consistency, or 99.999% → **Spanner** (PostgreSQL or GoogleSQL dialect).
    - PostgreSQL compatible, needs > Cloud SQL performance (HTAP, columnar engine, faster than standard PostgreSQL) or 99.99% single-region with low replica lag → **AlloyDB**.
    - Standard MySQL / PostgreSQL / SQL Server, regional, lift-and-shift, < ~64 TB → **Cloud SQL**.
  - No ↓
- Key-value / wide-column, very high throughput (millions of QPS), single-digit-ms latency, time series, IoT, ad-tech, petabytes?
  - Yes → **Bigtable** (no SQL joins, no multi-row transactions; row-key design is everything; HBase API; SQL support is limited).
  - No ↓
- Document store for mobile/web apps, real-time sync, offline, flexible schema, serverless scaling?
  - Yes → **Firestore** (Native mode; Datastore mode for server-side workloads; strong consistency, ACID transactions, up to 99.999% multi-region).
  - No ↓
- Sub-millisecond in-memory cache, session store, leaderboard, pub/sub?
  - Yes → **Memorystore** (Redis, Redis Cluster, Valkey, Memcached).
- Graph, search, or other specialised engines → Marketplace / self-managed on GKE, or Spanner Graph, or Vertex AI Search / Vector Search for semantic retrieval.

> **Trap:** "Global users, strongly consistent, relational" is Spanner, not Cloud SQL with read replicas (replicas are asynchronous). "Petabyte-scale analytics with SQL" is BigQuery, not Bigtable — despite the name similarity. "Existing MySQL app, minimal changes" is Cloud SQL, not Spanner (Spanner is not wire-compatible with MySQL).

## 1.4 Creating a migration plan

### Migration phases

1. **Assess / discover** – inventory apps, servers, databases, dependencies, utilisation, licences; classify workloads; estimate TCO. Tool: **Migration Center** (discovery client for vSphere/physical/AWS/Azure, import from RVTools/CSV, asset grouping, TCO and pricing reports, Migrate to VMs/containers fit assessment, database assessment).
2. **Plan** – landing zone (org hierarchy, folders, projects, IAM, Shared VPC, hybrid connectivity, logging/monitoring baseline, org policies), migration **waves**, target architecture per workload, success criteria, rollback plans.
3. **Migrate** – execute waves; run pilots first; test; cut over.
4. **Optimize** – rightsizing, CUDs, managed services, autoscaling, modernization; retire source hardware.

### The 6 Rs (workload disposition strategies)

| R | Meaning | Google Cloud path | Pick when |
|---|---|---|---|
| **Rehost** (lift & shift) | Move VMs as-is | **Migrate to Virtual Machines** (from vSphere, AWS, Azure, physical via connector; test clones; wave-based; continuous replication then cut-over) or **VMware Engine** | Time pressure, DC exit, no source code changes possible |
| **Replatform** (lift & optimize / "move and improve") | Small changes to use managed services | VM → MIG; self-managed MySQL → Cloud SQL via DMS; Windows file share → Filestore/NetApp Volumes | Quick wins with low risk |
| **Refactor / re-architect** | Change the code and architecture | Monolith → containers on GKE/Cloud Run (**Migrate to Containers** for Tomcat/Java/Windows IIS/Linux apps), microservices, event-driven | Long-term agility is the goal; app is strategic |
| **Repurchase** | Replace with SaaS | Move to Workspace, Salesforce, Marketplace SaaS | Commodity function |
| **Retire** | Turn it off | Decommission after assessment | Unused/duplicate |
| **Retain** | Keep on-prem (for now) | Connect via Interconnect/VPN; GKE Enterprise on-prem | Latency to factory floor, compliance, hardware dependencies, licence restrictions |

Some Google material adds **relocate** (VMware → VMware Engine without changes) and **rebuild** (rewrite from scratch).

### Migration tooling summary

| Need | Tool |
|---|---|
| Discovery, grouping, TCO, fit assessment | Migration Center |
| Move VMs (vSphere/AWS/Azure/physical) | Migrate to Virtual Machines (in Migration Center) |
| Move VM-based apps into containers on GKE/Cloud Run | Migrate to Containers |
| Move whole VMware environment | Google Cloud VMware Engine (HCX for live migration) |
| Relational DB migration | Database Migration Service |
| Continuous CDC / analytics feed | Datastream |
| Bulk files/objects | Storage Transfer Service, Transfer Appliance |
| Warehouse to BigQuery | BigQuery Data Transfer Service, BigQuery Migration Service (SQL translation from Teradata/Oracle/Snowflake etc.) |
| Mainframe | Mainframe Connector / Dual Run / partner tooling |

### Waves, dependency mapping and testing

- Build a **dependency map** (Migration Center discovery captures network connections; also use application owners, CMDB, network flow logs). Migrate tightly coupled systems in the **same wave** to avoid chatty traffic crossing the hybrid link.
- Order waves by **risk and value**: start with low-risk, internal, stateless apps (pilot), then business apps, then the hardest (databases, licensing-bound, mainframes) last.
- **Testing**: Migrate to VMs *test clones* let you boot a copy in Google Cloud without disturbing the source; run functional, performance/load, and failover tests before cut-over; define rollback (source kept in sync until sign-off).
- Cut-over approaches: **big bang** (short outage window), **phased** (DNS/traffic split, strangler-fig pattern for apps), **continuous replication with brief final sync** (DMS, Migrate to VMs).

### Network planning for migration

- Choose hybrid connectivity by bandwidth and SLA: HA VPN (quick, encrypted, ~up to 3 Gbps per tunnel, 99.99% with 2 interfaces/4 tunnels), Partner Interconnect (50 Mbps–50 Gbps), Dedicated Interconnect (10/100 Gbps circuits). Provision *before* wave 1 — Dedicated lead time is weeks.
- Plan **non-overlapping IP ranges** for VPC subnets vs on-prem; reserve ranges for GKE pods/services and Private Service Access.
- Decide **Shared VPC** (central network team owns networking; service projects host workloads) vs per-team VPCs with peering/NCC.
- DNS: Cloud DNS private zones + **forwarding zones** and **inbound/outbound server policies** so on-prem and cloud resolve each other during coexistence.
- Keep chatty tiers together; latency across the interconnect is typically single-digit to tens of ms and egress is billed.
- Firewall: replicate on-prem segmentation with hierarchical firewall policies and network tags/service accounts; use Cloud NGFW for IDS/IPS if required.

### Licensing and financial impact

| Software | Options on Google Cloud | Notes |
|---|---|---|
| **Windows Server / SQL Server** | Pay-as-you-go (premium image, billed per vCPU-hour) or **BYOL on sole-tenant nodes** (per-core licences require dedicated hardware; "bring your own licence" images, `--license` flag). Licence Mobility for SQL Server with Software Assurance | Hyper-threading affects core counting; sole-tenant *in-place restart* and *host maintenance policy* matter for licence stability |
| **RHEL / SLES** | PAYG images or BYOS (Red Hat Cloud Access) | |
| **Oracle** | Not licensable per vCPU in a normal VM according to Oracle policy; use **Bare Metal Solution**, **Oracle Database@Google Cloud** (Exadata/Autonomous inside Google regions), or migrate off (DMS Oracle→PostgreSQL/AlloyDB) | Exam answer for "keep Oracle, minimal change" is Bare Metal Solution / Oracle Database@Google Cloud |
| **SAP** | Certified machine types (M-series memory-optimized for HANA), BYOL; SAP on Google Cloud reference architectures | |
| **VMware** | VMware Engine includes VMware licences in the node price | |
| **Databases** | Replacing licensed DB engines with Cloud SQL for PostgreSQL / AlloyDB is a typical "reduce licence cost" answer | |

Financial modelling: compare current TCO to projected cloud cost including egress, support plan, and migration effort; use Migration Center's pricing reports; note that **CUDs** should be bought *after* rightsizing, and that the migration itself is temporary OpEx (double-running).

## 1.5 Envisioning future solution improvements

- **Cloud-first design approach**: new workloads default to managed, serverless, API-driven services; infrastructure expressed as code; security and observability built in; assume multi-zone by default.
- **Modernization path**: VM → container (Migrate to Containers, GKE) → serverless (Cloud Run, Cloud Run functions, Eventarc, Workflows) → managed data (Cloud SQL → AlloyDB/Spanner; Hadoop → Dataproc → BigQuery/Dataflow serverless) → AI-augmented (Vertex AI, Gemini models, Agent Builder).
- **Evolution of business needs**: design for change — loosely coupled services, APIs managed with Apigee (versioning, monetization), event-driven integration so new consumers can be added, data in BigQuery to enable analytics and ML later.
- **Technology improvements to anticipate**: newer machine families (C4/N4, Hyperdisk) for price-performance; GKE Autopilot and Cloud Run reducing ops; Gemini Cloud Assist and Gemini Code Assist for productivity; AI Hypercomputer for training at scale; Cross-Cloud Interconnect and NCC for multicloud.
- **Sustainability**: choose low-carbon regions (console shows the "Low CO₂" badge), use autoscaling and serverless to reduce idle capacity, export Carbon Footprint to BigQuery.

> **Exam tip:** When a question asks for the "long-term" or "future-proof" answer, prefer the design that removes undifferentiated heavy lifting (managed services), enables independent scaling (decoupled services, events), and keeps data portable (open formats in Cloud Storage/BigQuery, Kubernetes for portability).

## Key takeaways

- Section 1 is ~25% of the exam; every scenario is "map requirements → simplest managed design that meets all NFRs".
- Separate functional from non-functional requirements; NFRs (availability, latency, residency, RPO/RTO, ops burden) decide the answer.
- Zonal ≈ 99.9%, regional (multi-zone) ≈ 99.99%, multi-region ≈ 99.999% — Spanner, Firestore and Bigtable multi-region hit five nines; Cloud SQL HA does not go beyond a region.
- Composite availability multiplies across dependencies; add redundancy in parallel, not more nines in series.
- RPO drives replication/backup frequency; RTO drives standby warmth. Cold (hours, cheap) → warm/pilot light (minutes) → hot/active-active (seconds, expensive).
- Data transfer: 1 TB @ 100 Mbps ≈ 1 day; 100 TB @ 100 Mbps ≈ 3 months → Transfer Appliance for tens-of-TB+ with limited bandwidth; Storage Transfer Service for managed online transfers; DMS for relational DB migration; Datastream for CDC.
- Integration: Pub/Sub for async fan-out, Cloud Tasks for controlled work queues, Apigee for external API management, Datastream for CDC, Workflows/Composer for orchestration.
- Migration = assess (Migration Center) → plan (landing zone, waves, dependencies, network) → migrate (Migrate to VMs / Containers, DMS) → optimize (rightsizing, CUDs, managed services).
- 6 Rs: rehost, replatform, refactor, repurchase, retire, retain — choose by time pressure, strategic value and change tolerance.
- Licensing: per-core Windows/SQL BYOL needs sole-tenant nodes; Oracle → Bare Metal Solution / Oracle Database@Google Cloud or migrate off; VMware Engine bundles VMware licences.
- Performance levers: region proximity, Cloud CDN, Premium tier, Memorystore caching, right machine family, compact placement.
- Gemini Cloud Assist helps design, troubleshoot and optimize; it is an assistant, not a runtime dependency.
- Cloud-first future path: VM → container → serverless; self-managed DB → Cloud SQL/AlloyDB/Spanner; data in BigQuery to unlock analytics and AI.

## Quick self-check

- Q: A company must move 150 TB to Cloud Storage within three weeks over a 200 Mbps link. Which tool? — **A:** Transfer Appliance (150 TB at 200 Mbps would take roughly two months online).
- Q: Requirement: relational, strongly consistent, users on three continents, 99.999% availability. Which database? — **A:** Spanner multi-region.
- Q: What is the difference between RPO and RTO? — **A:** RPO = maximum acceptable data loss (time since last consistent copy); RTO = maximum acceptable time to restore service.
- Q: Cheapest DR tier that gives an RTO of minutes and RPO of minutes for a Cloud SQL–backed app? — **A:** Warm standby / pilot light: cross-region read replica plus minimal pre-provisioned compute, promote and scale on failover.
- Q: Which service performs discovery, dependency grouping and TCO estimation before a migration? — **A:** Migration Center.
- Q: The on-prem Oracle DB must remain Oracle with minimal change. Where does it run? — **A:** Bare Metal Solution or Oracle Database@Google Cloud (not standard Compute Engine VMs).
- Q: A service needs to hand off work to be processed later at no more than 50 requests/second to a specific endpoint. Pub/Sub or Cloud Tasks? — **A:** Cloud Tasks (rate-controlled, targeted queue).
- Q: Two dependent services each have a 99.9% SLA. What is the approximate composite availability? — **A:** About 99.8% (0.999 × 0.999).
