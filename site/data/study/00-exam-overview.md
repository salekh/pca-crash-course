## What the exam is

The Google Cloud **Professional Cloud Architect (PCA)** certification tests whether you can design, plan, provision, secure, and operate solutions on Google Cloud that meet *business* goals, not just technical ones. The current exam guide is organized around the **Google Cloud Well-Architected Framework** and includes generative-AI topics (Gemini models, Vertex AI / Agent Builder, Model Garden, AI Hypercomputer, Model Armor) alongside classic infrastructure, networking, storage, security, and operations.

### Logistics at a glance

| Item | Detail |
|---|---|
| Length | 2 hours |
| Questions | 50–60 (multiple choice and multiple select) |
| Delivery | Online proctored (remote, webcam, clean desk) or in-person test center |
| Fee | USD 200 (plus tax where applicable) |
| Languages | English, Japanese |
| Recommended experience | 3+ years industry experience including 1+ year designing/managing solutions on Google Cloud |
| Prerequisites | None (recommendations only) |
| Validity | 2 years; recertify by passing the current exam again (recertification window opens 60 days before expiry) |
| Result | Pass/Fail; no numeric score published; no published passing threshold |
| Case studies | Some questions refer to one of four published case studies (Altostrat Media, Cymbal Retail, EHR Healthcare, KnightMotives Automotive). Typically about 2 case studies appear in any given sitting |

> **Remember:** There is **no penalty for guessing**. An unanswered question is simply wrong. Never leave a question blank.

> **Exam tip:** Questions are weighted and scored statistically; the exact cut score is not published and may differ between exam forms. Aim to be comfortably right on about 80% of practice questions before you sit it.

## The six sections and their weights

| Section | Weight | What it really tests |
|---|---|---|
| 1. Designing and planning a cloud solution architecture | ~25% | Business + technical requirements → architecture; HA/DR; compute/storage/network/AI choices; migration planning (Migration Center); future improvements |
| 2. Managing and provisioning a cloud solution infrastructure | ~17.5% | Network topologies (hybrid, multicloud, Shared VPC, PSC, LB); storage configuration; compute provisioning (Spot, GKE, Cloud Run, VMware Engine); Vertex AI / Agent Platform pipelines; prebuilt AI APIs, Model Garden |
| 3. Designing for security and compliance | ~17.5% | IAM, resource hierarchy, KMS/CMEK, org policy, VPC Service Controls, IAP, Chrome Enterprise Premium, Workload Identity Federation, supply-chain security, securing AI (Model Armor, Sensitive Data Protection), regulations (HIPAA, GDPR, COPPA, PCI DSS, SOC 2), audit logs |
| 4. Analyzing and optimizing technical and business processes | ~15% | SDLC, CI/CD, RCA/post-mortems, testing, service catalog, DR, stakeholder/change management, skills readiness, CapEx/OpEx, business continuity |
| 5. Managing implementation | ~12.5% | Advising dev/ops teams; Apigee API management; load/unit/integration testing; migration tooling; Gemini Cloud Assist; gcloud/bq/gsutil, Cloud Shell, Cloud Code, emulators, Terraform, client libraries |
| 6. Ensuring solution and operations excellence | ~12.5% | Operational-excellence pillar; Cloud Observability (Logging, Monitoring, Trace, Profiler); alerting strategy; release management; support; quality control; chaos engineering, pen testing, load testing |

Section 1 alone is a quarter of the exam and Sections 1–3 together are 60%. Spend your revision time proportionally.

## How case studies appear

- The exam UI shows the case study in a **split screen** (or a tab/pane you can open) next to the question. You can scroll it, but re-reading it for every question burns time.
- Questions state something like "For this question, refer to the EHR Healthcare case study." Then a scenario adds a *new* constraint and asks what you should do.
- The correct answer must satisfy **both** the new constraint **and** the case study's stated business/technical requirements (e.g., EHR's 99.9% availability, Altostrat's cost priority, KnightMotives' EU data-protection concern).
- Know each case study's *existing environment*, *business requirements*, *technical requirements*, and *executive statement* well enough that you only glance at the pane to confirm a detail. The companion module `07-case-studies.md` maps every requirement to services.

> **Exam tip:** Typically two of the four case studies show up in a sitting, with several questions each. Prepare all four; you do not get to choose.

## Question anatomy

Almost every PCA question is built the same way:

1. **Scenario** — who you are ("You are the architect for…"), what exists today, and what the organization wants.
2. **Constraint(s)** — the discriminator: "with the least operational overhead," "while minimizing cost," "without exposing public IPs," "following Google-recommended practices," "within 30 minutes RTO."
3. **Ask** — "What should you do?" / "Which two actions should you take? (Choose two.)" / "How should you design…?"

Four (sometimes five) options follow. Usually **two are clearly wrong** (they violate a hard requirement or use the wrong product), and **two are plausible**. The constraint decides between the plausible pair.

### Reading protocol (use every time)

- Read the **last sentence first** to learn what is actually being asked and how many options to select.
- Underline (mentally) every constraint word: *least*, *most*, *minimize*, *without*, *must*, *only*, *quickly*, *globally*, *regulated*.
- Identify the **hard requirements** (anything that makes an option disqualifying) versus **soft preferences** (tie-breakers).
- Eliminate options that violate a hard requirement, even if they sound sophisticated.
- Among survivors, pick the one that is most **managed**, most **Google-recommended**, and most aligned with the constraint.

## Keyword decoding table

The exam uses a consistent vocabulary. Translate these phrases automatically.

| Phrase in the question | What it signals | Typical answer direction |
|---|---|---|
| "least operational overhead" / "minimal management" | Managed or serverless | Cloud Run, Cloud Run functions, BigQuery, Cloud SQL, Spanner, Firestore, Dataflow, GKE Autopilot, Memorystore |
| "minimize cost" | Cheapest compliant option | Spot VMs, committed use discounts (CUDs), right-sizing, Nearline/Coldline/Archive, Autoclass, serverless scale-to-zero, BigQuery slots/partitioning |
| "Google-recommended practice" / "best practice" | Documented Architecture Center / Well-Architected pattern | Least privilege, groups not users, service accounts with narrow roles, Shared VPC, IaC, CMEK where required, regional resources for HA |
| "as quickly as possible" / "minimal changes" | Lift-and-shift, rehost | Migrate to Virtual Machines, Google Cloud VMware Engine, Database Migration Service, Storage Transfer Service |
| "modernize" / "cloud-native" | Refactor/replatform | Containers on GKE or Cloud Run, managed databases, Pub/Sub decoupling |
| "globally consistent" / "strong consistency across regions" / "horizontal scale relational" | Spanner | Spanner (multi-region 99.999% SLA) |
| "analytics at petabyte scale" / "data warehouse" / "SQL over historical data" | BigQuery | BigQuery (+ partitioning/clustering, BI Engine, Looker) |
| "low-latency, high-throughput, wide-column" / "time series, IoT, ad-tech" / "single-digit ms" | Bigtable | Bigtable (NoSQL, key design matters, no SQL joins) |
| "relational, regional, lift-and-shift MySQL/PostgreSQL/SQL Server" | Cloud SQL | Cloud SQL with HA (regional) and read replicas; AlloyDB for PostgreSQL when you need higher performance |
| "document database, mobile/web sync, offline" | Firestore | Firestore (Native mode) |
| "sub-millisecond cache / session store" | Memorystore | Memorystore for Redis (Cluster for scale) or Memcached |
| "objects / media / backups / data lake" | Cloud Storage | Cloud Storage with storage classes, lifecycle rules, Autoclass |
| "shared POSIX file system / NFS" | Filestore | Filestore (Basic/Zonal/Regional/Enterprise tiers) |
| "no public IP" / "private access to Google APIs" | Private connectivity | Private Google Access, Private Service Connect, VPC Service Controls, IAP for TCP/SSH |
| "SSH/RDP without external IP or bastion" | IAP TCP forwarding | `gcloud compute ssh --tunnel-through-iap`, role `roles/iap.tunnelResourceAccessor` |
| "on-prem connectivity with 99.99% SLA" | Redundant dedicated connectivity | Dedicated Interconnect with 4 VLAN attachments across 2 metros / 2 edge availability domains (99.99%); 2 attachments = 99.9%; HA VPN = 99.99% when both interfaces/tunnels used |
| "10 Gbps+ / 100 Gbps private link" | Dedicated Interconnect | 10 Gbps or 100 Gbps circuits; Partner Interconnect 50 Mbps–50 Gbps |
| "connect to another cloud provider privately" | Cross-Cloud Interconnect | Cross-Cloud Interconnect (10/100 Gbps) + Network Connectivity Center |
| "encrypted over the internet, quick to set up" | VPN | HA VPN (two tunnels, BGP via Cloud Router) |
| "many VPCs / spokes / hub" | NCC | Network Connectivity Center hub-and-spoke |
| "central network team, project-level separation" | Shared VPC | Shared VPC host project + service projects |
| "prevent data exfiltration from managed services" | VPC Service Controls | Service perimeters around BigQuery, Cloud Storage, etc. |
| "restrict where resources can be created / which services" | Organization Policy | Org policy constraints (resource locations, restrict VM external IPs, domain-restricted sharing) |
| "customer controls keys" / "key rotation" | CMEK | Cloud KMS; Cloud HSM for FIPS 140-2 Level 3; Cloud EKM for keys held outside Google |
| "regulated: HIPAA / FedRAMP / EU sovereignty" | Assured Workloads | Assured Workloads folder + data residency org policies; sign BAA for HIPAA |
| "PII / credit cards in logs or datasets" | Sensitive Data Protection | Sensitive Data Protection inspection, de-identification, tokenization |
| "prompt injection / unsafe model output" | Model Armor | Model Armor + Vertex AI safety filters |
| "only run trusted container images" | Binary Authorization | Binary Authorization with attestations from Cloud Build; Artifact Analysis scanning |
| "external workloads need Google credentials without keys" | Workload Identity Federation | WIF (AWS/Azure/OIDC/SAML → short-lived tokens); GKE Workload Identity for pods |
| "employees access internal apps without VPN / zero trust" | IAP + Chrome Enterprise Premium | Identity-Aware Proxy, context-aware access levels, Access Context Manager |
| "temporary elevated access" / "act as another identity" | Impersonation | Service account impersonation (`roles/iam.serviceAccountTokenCreator`), short-lived credentials |
| "global HTTP(S) with CDN and WAF" | Global external Application LB | Global external Application Load Balancer + Cloud CDN + Cloud Armor |
| "TCP/UDP non-HTTP, preserve client IP, global anycast" | External proxy Network LB / passthrough NLB | Proxy Network LB (TCP/SSL) or regional external passthrough Network LB |
| "internal microservice traffic in one region" | Internal LB | Regional internal Application LB or internal passthrough Network LB |
| "RPO near zero, RTO minutes" | Hot/warm multi-region | Spanner multi-region, Cloud SQL cross-region replica, active-active with global LB |
| "RPO hours, minimal cost DR" | Cold/backup-restore | Scheduled backups to multi-region Cloud Storage, Backup and DR Service, IaC to rebuild |
| "handle spikes / decouple producers and consumers" | Pub/Sub | Pub/Sub (+ Dataflow for streaming ETL) |
| "streaming and batch ETL, exactly-once, windowing" | Dataflow | Dataflow (Apache Beam) |
| "existing Hadoop/Spark jobs, lift with minimal change" | Dataproc | Dataproc (ephemeral clusters, Cloud Storage connector) |
| "orchestrate workflows / DAGs" | Composer | Cloud Composer (Airflow); Workflows for lightweight serverless orchestration |
| "large offline data transfer, 100s of TB, slow link" | Transfer Appliance | Transfer Appliance; Storage Transfer Service for online transfers and SFTP/S3 sources |
| "discover and assess on-prem estate / TCO" | Migration Center | Migration Center discovery, assessment, cost estimates |
| "VMware without refactoring" | VMware Engine | Google Cloud VMware Engine |
| "batch, fault-tolerant, interruptible" | Spot VMs | Spot VMs (up to 60–91% discount, can be preempted any time, no SLA) |
| "predictable steady-state usage 1–3 years" | CUDs | Resource- or spend-based committed use discounts |
| "GPU/TPU large-scale training" | AI Hypercomputer | AI Hypercomputer (TPU/GPU clusters, Vertex AI training), Dynamic Workload Scheduler for capacity |
| "grounded answers over enterprise docs" | Vertex AI Search / RAG | Vertex AI Search, Vertex AI Agent Builder, grounding with Google Search or your data |
| "chatbot / virtual agent / replace IVR" | Conversational Agents | Conversational Agents (Dialogflow CX) and Contact Center AI / Customer Engagement Suite |
| "explain why the model predicted X" | Explainable AI | Vertex Explainable AI, Model Monitoring, audit logs |
| "who did what, when, tamper-evident" | Audit logs | Cloud Audit Logs (Admin Activity always on; enable Data Access), log sinks to locked buckets, retention up to 3650 days, Bucket Lock |
| "trace slow requests across services" | Cloud Trace | Cloud Trace + Cloud Profiler for CPU/memory hotspots |
| "alerts ignored / email fatigue" | Alerting strategy | SLO-based alerting on burn rate, route to PagerDuty/Slack/on-call, severity tiers |
| "progressive rollout / rollback" | Cloud Deploy | Cloud Deploy canary/blue-green targets; traffic splitting on Cloud Run / GKE |
| "manage API partners / monetization / quotas" | Apigee | Apigee API management (developer portal, quotas, analytics, monetization) |
| "repeatable environments / self-service" | IaC + Service Catalog | Terraform, Config Connector, Infrastructure Manager, Service Catalog |
| "AI help in the console for troubleshooting/cost/design" | Gemini Cloud Assist | Gemini Cloud Assist; Gemini Code Assist for coding |

> **Trap:** Two options may both "work." The exam wants the one that satisfies the constraint *most directly*. "Works" is not the standard; "best given the constraint" is.

## Elimination strategy

- **Product-fit kill:** Does the option use a product for something it cannot do (Bigtable with SQL joins, Cloud SQL scaling globally with strong consistency, Cloud Storage as a POSIX file system, Cloud CDN in front of an internal LB)? Eliminate.
- **Constraint kill:** Does it violate an explicit requirement ("no public IP" but uses external IPs; "minimal changes" but proposes a rewrite; "99.99%" but uses a single zone)? Eliminate.
- **Anti-pattern kill:** Options that grant `roles/owner`, use user-managed service account keys, put everything in one project, or rely on manual steps are almost never the intended answer.
- **Scope check:** Is the resource at the right scope? Global LB vs regional; multi-region storage vs region; org policy vs project IAM.
- **Managed beats self-managed** when the question does not require control over the OS/runtime.
- **The "and" test for multi-select:** For "choose two," each selected option must independently be correct and together cover the requirement; do not pick two options that are mutually exclusive alternatives.

> **Exam tip:** When two survivors remain and one is a Google-managed service and the other is "install X on Compute Engine," the managed service wins unless the question specifically requires OS-level control, a licensing constraint, or an unsupported feature.

## Time management and flagging

- 120 minutes ÷ ~55 questions ≈ **2 minutes per question**. Case-study questions take longer; budget 3 minutes and make it back on quick ones.
- First pass: answer everything you are confident about; **flag** (mark for review) anything that takes more than 2.5 minutes. Always record a provisional answer before moving on.
- Second pass: revisit flagged items with remaining time. Do not change first-pass answers without a concrete reason (a misread constraint, a product limit you remembered).
- Leave 5 minutes to confirm no question is unanswered.
- For multi-select, re-read the required count ("Choose two" vs "Choose three") before submitting; selecting the wrong number is scored as wrong.
- Online proctoring: you cannot use paper or a second monitor; you may not read aloud. Do a system test the day before and clear the desk.

## The Well-Architected Framework as the grading lens

Answers are effectively judged by the six pillars. When stuck, ask which pillar the question is emphasizing.

| Pillar | Core principles to apply in answers |
|---|---|
| **Operational excellence** | Automate everything (IaC, CI/CD, Cloud Deploy); observe with SLIs/SLOs and actionable alerts; manage change safely (canary, rollback); learn from incidents (blameless post-mortems) |
| **Security, privacy, and compliance** | Zero trust and least privilege (IAM, IAP, Chrome Enterprise Premium); defense in depth (org policy, VPC-SC, Cloud NGFW, Cloud Armor); protect data (CMEK, Sensitive Data Protection, Secret Manager); secure the software and AI supply chain (Binary Authorization, Model Armor) |
| **Reliability** | Define SLOs and error budgets; design for failure with redundancy across zones/regions; automate recovery and test DR; scale horizontally; avoid single points of failure |
| **Cost optimization** | Align spend to business value; right-size and use Spot/CUDs; use serverless and autoscaling; choose the right storage class; monitor with budgets, billing export to BigQuery, FinOps practices |
| **Performance optimization** | Plan capacity and autoscale; place resources near users (multi-region, CDN); pick the right machine family/storage (Hyperdisk, Local SSD); measure with Profiler/Trace; optimize data models (partitioning/clustering) |
| **Sustainability** | Choose low-carbon regions; use managed services with higher utilization; scale to zero; delete idle resources; use Carbon Footprint reporting |

> **Remember:** When a question says "Google-recommended," it is asking for the Well-Architected or Architecture Center pattern, not the cheapest or fastest option.

## Top 25 traps

1. Picking a zonal resource (single Cloud SQL instance, single-zone GKE, zonal MIG) when the requirement is ≥99.9% or "highly available."
2. Choosing Cloud SQL for a workload that needs multi-region strong consistency or horizontal write scaling — that is Spanner.
3. Choosing Bigtable when the workload needs SQL, joins, or ad-hoc analytics — that is BigQuery (analytics) or Spanner/Cloud SQL (relational).
4. Picking BigQuery as a transactional (OLTP) database.
5. Forgetting that Cloud Storage storage classes have **minimum storage durations** (Nearline 30 days, Coldline 90 days, Archive 365 days) and retrieval fees — moving hot data to Archive costs more.
6. Using multi-region storage for a workload that requires data residency in one country.
7. Granting primitive/basic roles (`roles/owner`, `roles/editor`) when a predefined or custom role satisfies least privilege.
8. Granting roles to individual users instead of Google Groups; or creating and downloading service account keys instead of using Workload Identity / impersonation.
9. Assuming a VPC firewall rule protects Cloud Storage or BigQuery — those need IAM + VPC Service Controls.
10. Confusing VPC Network Peering (non-transitive, no overlapping CIDRs) with Shared VPC (one host project, centralized admin) and NCC (hub-and-spoke, transitive).
11. Picking a single Dedicated Interconnect VLAN attachment and expecting 99.99% — you need 4 attachments across 2 metros (99.99%) or 2 attachments (99.9%).
12. Choosing Classic VPN when HA VPN is required for a 99.99% SLA.
13. Choosing an external load balancer for east-west internal traffic; or a regional LB when the requirement is a single global anycast IP.
14. Placing Cloud CDN or Cloud Armor on a load balancer type that does not support them (they attach to external Application LBs; Cloud Armor also supports proxy Network LBs).
15. Treating Spot VMs as suitable for stateful, SLA-bound services — they can be reclaimed at any time.
16. Recommending a rewrite when the question says "as quickly as possible" or "minimal changes" — rehost first (Migrate to Virtual Machines / VMware Engine), modernize later.
17. Missing that Admin Activity audit logs are always on but **Data Access audit logs are off by default** (except BigQuery) and must be enabled.
18. Assuming default log retention (30 days in `_Default`) satisfies a multi-year compliance requirement — configure a log bucket with longer retention or sink to Cloud Storage with Bucket Lock.
19. Meeting "encrypt data" with CMEK when the question only requires encryption at rest (Google-managed default already does that); or meeting "customer must hold keys outside Google" with CMEK instead of Cloud EKM.
20. Ignoring the "human in the loop" or "explainability" requirement in gen-AI questions and picking a fully automated pipeline.
21. Choosing to fine-tune a model when grounding/RAG with Vertex AI Search is cheaper and satisfies "use our own documents."
22. Confusing RPO (data loss tolerance) with RTO (downtime tolerance) and picking a DR tier that fits one but not the other.
23. Solving alert fatigue by adding more email alerts rather than SLO/burn-rate alerting with proper routing and severity.
24. Using Cloud Run functions for long-running or stateful jobs beyond their limits — Cloud Run jobs, GKE, or Batch fit better.
25. Answering from a generic-cloud mindset (e.g., "use a NAT gateway on a VM") when Google has a managed equivalent (Cloud NAT).

## Crash study plans

### 7-day plan (about 3–4 hours/day)

| Day | Focus | Deliverable |
|---|---|---|
| 1 | Exam guide + this module; Well-Architected pillars; read all four case studies once | One-page cheat sheet per case study (requirements → services) |
| 2 | Section 1: compute (Compute Engine, GKE Standard/Autopilot, Cloud Run, Cloud Run functions, Batch), storage decision tree, database decision tree | Fill in a comparison table from memory, check against docs |
| 3 | Networking: VPC, Shared VPC, peering, NCC, PSC, Private Google Access, Cloud NAT, LB types, Interconnect/VPN SLAs, Cloud Armor, Cloud NGFW | Draw the hybrid connectivity decision tree |
| 4 | Section 3: IAM, resource hierarchy, org policy, KMS/HSM/EKM, Secret Manager, VPC-SC, IAP, Chrome Enterprise Premium, WIF, Binary Authorization, Model Armor, Sensitive Data Protection, compliance regimes | 30 flashcards on roles, defaults, and limits |
| 5 | Data and AI: BigQuery, Dataflow, Dataproc, Pub/Sub, Composer, Vertex AI (training, pipelines, Model Garden, Agent Builder, Vertex AI Search, Conversational Agents), AI Hypercomputer | Map each case study's AI requirement to a product |
| 6 | Sections 4–6: SDLC, CI/CD (Cloud Build, Artifact Registry, Cloud Deploy), DR patterns and RPO/RTO, Cloud Observability, SLOs, release strategies, chaos/load/pen testing; official sample questions | Review every wrong answer and write the "why" |
| 7 | Full timed practice set; re-read case studies; review Top 25 traps and keyword table; logistics check (ID, system test) | Rest; no new material after mid-afternoon |

### 14-day plan (about 2 hours/day)

| Days | Focus |
|---|---|
| 1–2 | Exam guide, this module, Well-Architected Framework overview; first read of case studies |
| 3–4 | Compute and storage selection; Cloud Storage classes/lifecycle/Autoclass; Filestore; Persistent Disk vs Hyperdisk vs Local SSD; machine families |
| 5–6 | Databases (Cloud SQL, AlloyDB, Spanner, Bigtable, Firestore, Memorystore, BigQuery); migration tooling (Database Migration Service, Storage Transfer Service, Transfer Appliance, Migration Center, Migrate to Virtual Machines) |
| 7–8 | Networking end to end: VPC design, hybrid connectivity SLAs and bandwidths, LB catalog, PSC, VPC-SC, Cloud NAT, DNS, Cloud Armor, Cloud NGFW |
| 9 | Security: IAM design, org policy, KMS family, Secret Manager, IAP, WIF, supply chain, securing AI |
| 10 | Compliance: HIPAA, GDPR, PCI DSS, COPPA, SOC 2, data residency, Assured Workloads, audit logs and retention |
| 11 | Data processing and AI: Pub/Sub, Dataflow, Dataproc, Composer, BigQuery advanced; Vertex AI platform, Gemini, Agent Builder, Model Garden, prebuilt APIs |
| 12 | Operations: CI/CD, Cloud Deploy strategies, DR tiers, Cloud Observability, SLO alerting, Gemini Cloud Assist, gcloud/bq/Terraform shapes |
| 13 | Case-study deep dive: rebuild target architecture for each from memory; practice 40+ questions timed |
| 14 | Review misses, Top 25 traps, keyword table; light review only |

## Official resources

- **Exam guide** — the section list above; re-read it before the exam to see whether each bullet triggers a product name in your head.
- **Sample questions** — the official web-based sample set; mimics real phrasing. Do it twice: once cold, once after studying.
- **Google Cloud Skills Boost** — the "Cloud Architect" learning path (courses + hands-on labs) and the PCA "Preparing for" course.
- **Architecture Center** — reference architectures for hybrid/multicloud, DR, landing zones, gen-AI RAG, and migration; the source for "Google-recommended."
- **Well-Architected Framework** — the six pillars; read the summary pages for each pillar and the AI/ML perspective.
- **Case study PDFs** — Altostrat Media, Cymbal Retail, EHR Healthcare, KnightMotives Automotive; print or annotate them.
- **Product documentation "Overview" and "Quotas & limits" pages** for Cloud Storage, Cloud SQL, Spanner, Bigtable, BigQuery, Interconnect, Cloud Load Balancing, IAM, Cloud KMS, Cloud Logging.
- **Google Cloud release notes / blog** for name changes (Cloud Run functions, GKE Enterprise, Chrome Enterprise Premium, Sensitive Data Protection, Cloud Observability).

## Key takeaways

- 2 hours, 50–60 questions, multiple choice/select, USD 200, English or Japanese, pass/fail with no published cut score; valid 2 years.
- Guessing is free — never leave a blank; answer everything on the first pass and flag doubtful items.
- Weights: Design 25%, Provision 17.5%, Security 17.5%, Processes 15%, Implementation 12.5%, Operations 12.5%.
- Every question is scenario + constraint + ask; the constraint decides between the two plausible options.
- Decode the vocabulary: "least operational overhead" → managed/serverless; "globally consistent" → Spanner; "petabyte analytics" → BigQuery; "no public IP" → Private Google Access/PSC/IAP; "on-prem 99.99%" → redundant Dedicated Interconnect or HA VPN.
- Managed beats self-managed unless the question needs OS control, licensing, or an unsupported feature.
- Judge answers through the Well-Architected pillars: operational excellence, security, reliability, cost, performance, sustainability.
- Case studies: about two per sitting, shown split-screen; the right answer must fit the case's stated requirements as well as the new constraint.
- Multi-select: confirm the count, and make sure each selected option is independently correct.
- Know SLA-driving numbers: Interconnect 99.9% (2 attachments) vs 99.99% (4 attachments, 2 metros); HA VPN 99.99%; Spanner multi-region 99.999%; storage class minimums 30/90/365 days.
- Security defaults matter: Data Access audit logs off by default; `_Default` log bucket retains 30 days; basic roles are never least privilege.
- Migration speed hierarchy: rehost (Migrate to VMs / VMware Engine) → replatform (managed DBs, containers) → refactor (serverless, microservices).
- Gen-AI questions reward grounding/RAG, human-in-the-loop, safety filters + Model Armor, and explainability/audit logging over "just fine-tune it."
- Budget ~2 minutes per question, 3 for case studies; leave 5 minutes for an unanswered-check.

## Quick self-check

- Q: How many questions and how long is the PCA exam, and what happens if you leave a question unanswered? — **A:** 50–60 questions in 2 hours; an unanswered question is scored as wrong and there is no guessing penalty.
- Q: Which section has the largest weight and what does it cover? — **A:** Section 1, Designing and planning a cloud solution architecture (~25%): business/technical requirements, HA/DR, compute/storage/network/AI selection, migration planning.
- Q: A question says "with the least operational overhead" and offers Cloud SQL on a VM versus Cloud SQL managed. Which wins and why? — **A:** The managed Cloud SQL service; "least operational overhead" always points to managed/serverless.
- Q: What connectivity design meets a 99.99% SLA for on-prem to Google Cloud over dedicated links? — **A:** Dedicated Interconnect with four VLAN attachments across two metros (two edge availability domains each) with Cloud Router in each region; HA VPN also offers 99.99%.
- Q: Which six pillars form the Well-Architected Framework? — **A:** Operational excellence; security, privacy and compliance; reliability; cost optimization; performance optimization; sustainability.
- Q: What is the minimum storage duration for Coldline and Archive? — **A:** Coldline 90 days, Archive 365 days (Nearline 30 days).
- Q: A "choose two" question: what is the most common way candidates lose the point? — **A:** Picking two mutually exclusive alternatives, or selecting the wrong number of options; each choice must be independently correct.
- Q: How long is the certification valid and how do you renew? — **A:** Two years; recertify by passing the current version of the exam (window opens 60 days before expiry).
