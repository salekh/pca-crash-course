---
id: case-studies
title: The Four Case Studies Decoded
domain: 0
order: 8
minutes: 30
summary: Requirement-by-requirement service mapping, target architecture, rollout phasing, risks, and likely question themes for EHR Healthcare, Cymbal Retail, Altostrat Media, and KnightMotives Automotive.
---

## How to use this module

Roughly two of these four case studies will appear in your sitting, each with several questions. Every case-study question adds a new constraint on top of the published requirements, so the winning answer must fit **both**. For each case below you get: a summary, a requirement → service → rationale → exam-angle table, a target architecture in text, phasing, risks, and likely question themes with the expected answer direction.

> **Exam tip:** Read the *executive statement* of each case as the tie-breaker. EHR's is about outages from misconfiguration and inconsistent monitoring; Altostrat's says "reliability and cost management are our top priorities"; Cymbal's is about automation and revenue; KnightMotives' is about safety, data, and a consistent experience across models.

## EHR Healthcare

### Summary

SaaS provider of electronic health record software to multinational medical offices, hospitals, and insurers. Growing exponentially; currently in multiple colocation facilities and one lease is expiring. Customer-facing apps are web-based and mostly containerized on Kubernetes. Data in MySQL, Microsoft SQL Server, Redis, and MongoDB. Legacy file- and API-based insurer integrations stay on-prem for several years. Identity is Microsoft Active Directory. Monitoring is a mix of open-source tools; alerts go by email and are ignored. Google Cloud replaces the colos.

### Requirement mapping

| Requirement | Recommended service(s) | Rationale | Likely exam angle |
|---|---|---|---|
| **B:** On-board new insurance providers as quickly as possible | Apigee (API management, developer portal), Cloud Run / GKE for adapter services, Pub/Sub + Dataflow for file/event ingestion, Storage Transfer Service for SFTP | Standardized, self-service APIs with quotas, security, and analytics shorten onboarding; managed ingestion removes custom plumbing | "Which product lets partners onboard via published, secured APIs?" → Apigee |
| **B:** Minimum 99.9% availability for customer-facing systems | Regional GKE clusters (multi-zone control plane and nodes), regional Cloud SQL HA, Memorystore Standard tier, global external Application Load Balancer, multi-region for DR | 99.9% needs at least zonal redundancy inside a region; regional GKE and Cloud SQL HA deliver it | Trap options use zonal clusters or single Cloud SQL instances |
| **B:** Centralized visibility and proactive action on performance and usage | Cloud Observability: Cloud Monitoring (metrics scopes across projects), Cloud Logging with aggregated sinks, Managed Service for Prometheus, SLO monitoring, alert policies with notification channels (PagerDuty/Slack/SMS) and escalation | Replaces disparate open-source tools and ignored email alerts with SLO-based, routed alerting | "Alerts are ignored" → burn-rate alerts routed to on-call, not more emails |
| **B:** Increase insights into healthcare trends; predictions and reports on industry trends | BigQuery (data warehouse), Dataflow/Datastream for ingestion, BigQuery ML or Vertex AI (AutoML/custom training), Looker/Looker Studio for reports, Cloud Healthcare API for FHIR/HL7v2/DICOM | Serverless analytics at scale; BigQuery ML for in-warehouse predictions; Healthcare API normalizes clinical data and exports to BigQuery | "Least effort predictions on data already in BigQuery" → BigQuery ML |
| **B:** Reduce latency to all customers | Global external Application LB with anycast IP, Cloud CDN for static content, multi-region deployment of GKE workloads, read replicas near users, Premium Tier networking | Global LB routes users to nearest healthy backend; CDN caches at the edge | Trap: regional LB per region with DNS round robin when a global LB is asked for |
| **B:** Maintain regulatory compliance (HIPAA, GDPR for multinational) | Sign a BAA, use HIPAA-covered services, Assured Workloads (where required), CMEK via Cloud KMS, Data Access audit logs, VPC Service Controls, Sensitive Data Protection, org policies (resource location, external IP restriction) | Compliance is process + controls: BAA, in-scope services, encryption, auditability, data residency | "Which first step for HIPAA?" → accept the BAA and restrict to covered services |
| **B:** Decrease infrastructure administration costs | Managed services (GKE Autopilot, Cloud SQL, Memorystore), autoscaling, CUDs, rightsizing recommendations, decommission colos | Pay for managed ops instead of staff time; scale-to-need | "Least operational overhead" phrasing |
| **T:** Maintain legacy interfaces to insurers with connectivity to on-prem and other clouds | Dedicated or Partner Interconnect (primary) + HA VPN (backup), Cloud Router/BGP, Cloud DNS forwarding zones, Cloud NAT for egress; Cross-Cloud Interconnect if insurers sit in other clouds | Legacy systems stay on-prem for years, so hybrid connectivity is long-term and needs redundancy | Bandwidth/SLA questions: 99.99% → 4 VLAN attachments in 2 metros |
| **T:** Consistent way to manage container-based customer-facing apps | GKE (regional, Autopilot where possible), GKE Enterprise fleets + Config Sync + Policy Controller for multi-cluster consistency, Artifact Registry, Cloud Build, Cloud Deploy | Fleets give one policy/config plane across clusters and environments | "Consistent config across many clusters" → Config Sync (GitOps) |
| **T:** Secure, high-performance connection on-prem ↔ Google Cloud | Dedicated Interconnect (10/100 Gbps), VLAN attachments, MACsec where needed, HA VPN as encrypted fallback, Private Google Access for on-prem hosts | Interconnect is private and high-throughput; VPN adds encryption/backup | Trap: Classic VPN as primary "high-performance" link |
| **T:** Consistent logging, log retention, monitoring, alerting | Cloud Logging with organization-level aggregated sinks to a central log bucket (custom retention up to 3650 days) and BigQuery; Log Analytics; Cloud Monitoring with multi-project metrics scope; uniform alert policies | Centralizes retention for compliance and one pane of glass | Retention question: `_Default` bucket is 30 days; set custom retention or sink to Cloud Storage with Bucket Lock |
| **T:** Maintain and manage multiple container-based environments; dynamically scale and provision new environments | Terraform / Config Connector / Infrastructure Manager, Cloud Build pipelines, GKE cluster autoscaler + node auto-provisioning, HPA/VPA, namespaces per tenant or environment, Config Sync | IaC creates environments on demand; autoscaling handles traffic spikes that caused outages | "Provision a new environment identically" → IaC in CI/CD |
| **T:** Interfaces to ingest and process data from new providers | Pub/Sub, Dataflow (streaming and batch), Cloud Storage landing buckets, Storage Transfer Service (SFTP sources), Cloud Healthcare API, Apigee for API ingestion | Decoupled, autoscaling ingestion regardless of provider format | "File-based today, API-based tomorrow" → Cloud Storage + Pub/Sub notifications + Dataflow |
| **Data tier** (MySQL, SQL Server, Redis, MongoDB) | Cloud SQL for MySQL and for SQL Server (HA, read replicas), Memorystore for Redis, MongoDB Atlas on Google Cloud via Marketplace (or self-managed on GKE with StatefulSets if required), Database Migration Service for MySQL/SQL Server | Like-for-like managed engines minimize app change; DMS supports continuous replication for low-downtime cutover | "Migrate MySQL with minimal downtime" → DMS continuous migration |
| **Identity** (Microsoft Active Directory) | Managed Service for Microsoft Active Directory (trust with on-prem AD) for Windows/SQL Server auth; Google Cloud Directory Sync + SAML SSO (AD FS or Entra ID) or Cloud Identity federation for console/IAM access; Google Groups for role grants | Keeps AD as source of truth; users sign in with corporate credentials; IAM bound to groups | "Users should use existing AD credentials for the console" → GCDS + SAML federation |

### Target architecture

- **Landing zone:** Organization → folders (prod, non-prod, shared-services) → projects per environment/app. Shared VPC host project owned by the network team; GKE and data workloads in service projects. Org policies: restrict external IPs, domain-restricted sharing, resource location constraints, require OS Login.
- **Connectivity:** Two Dedicated Interconnect circuits in two metros with four VLAN attachments to Cloud Routers in two regions (99.99%), HA VPN as backup path, Cloud DNS private zones with forwarding to on-prem AD DNS. Private Google Access and Private Service Connect endpoints for Google APIs. Cloud NAT for controlled egress.
- **Compute:** Regional GKE clusters (Autopilot where images allow) in two regions, registered to a GKE Enterprise fleet; Config Sync pushes namespaces, RBAC, network policies, and Policy Controller constraints from Git. Cloud Build builds images into Artifact Registry with Artifact Analysis scanning; Binary Authorization enforces signed images; Cloud Deploy promotes dev → staging → prod with canary.
- **Traffic:** Global external Application LB with Cloud Armor (WAF, rate limiting) and Cloud CDN → GKE Gateway/Ingress backends in both regions. Internal Application LB for service-to-service traffic where needed; Cloud Service Mesh optional for mTLS.
- **Data:** Cloud SQL for MySQL and SQL Server (regional HA, cross-region read replicas for DR), Memorystore for Redis (Standard tier, replicas), MongoDB Atlas via Marketplace with private connectivity (PSC), CMEK from Cloud KMS on all stores, automated backups with retention.
- **Integration and ingestion:** Apigee X exposes provider APIs (OAuth, quotas, analytics, developer portal). Storage Transfer Service pulls SFTP drops into Cloud Storage; Pub/Sub notifications trigger Dataflow pipelines that validate and load into Cloud SQL/BigQuery; Cloud Healthcare API for FHIR/HL7 where applicable.
- **Analytics and AI:** Datastream/Dataflow CDC into BigQuery; de-identification with Sensitive Data Protection; BigQuery ML and Vertex AI for trend prediction; Looker for reports.
- **Observability:** Central logging project with aggregated org sink; log buckets with 7-year retention where regulation requires; Cloud Monitoring metrics scope across projects; SLOs per customer-facing service; alert policies to PagerDuty with severity routing; Cloud Trace/Profiler enabled in apps.
- **Security/compliance:** BAA signed; VPC Service Controls perimeter around data projects; IAP for admin access; Security Command Center Premium/Enterprise; Data Access audit logs enabled.

### Migration and rollout phasing

1. **Assess** with Migration Center; inventory clusters, DBs, dependencies, and the expiring colo first.
2. **Foundation:** landing zone via Terraform, Interconnect + HA VPN, identity federation, central logging/monitoring.
3. **Move the expiring colo's workloads first:** containers to GKE (images already exist), databases via DMS with continuous replication, Redis to Memorystore, MongoDB to Atlas.
4. **Cut over traffic** behind the global LB with weighted DNS/traffic splitting; validate SLOs.
5. **Modernize integrations:** Apigee for new providers while legacy on-prem interfaces stay reachable over Interconnect.
6. **Analytics layer:** BigQuery + Vertex AI once data is in cloud.
7. **Decommission** remaining colos; second region for DR.

### Key risks

- Interconnect lead times can exceed the lease deadline → start with HA VPN or Partner Interconnect, migrate to Dedicated later.
- SQL Server licensing (BYOL vs license-included) and AD-dependent auth.
- Latency between cloud apps and on-prem legacy integrations → cache, asynchronous integration via Pub/Sub.
- PHI exposure during migration and in logs → Sensitive Data Protection, VPC-SC, audit logs.
- Alert fatigue persisting if only the tool changes → SLO-based alerting and on-call process.

### Likely question themes

1. **Container platform consistency** across environments → GKE Enterprise fleet with Config Sync and Policy Controller (not per-cluster manual config).
2. **99.9% availability** for a stateful service → regional GKE + Cloud SQL HA (regional) + multi-zone Memorystore; DR via cross-region replica.
3. **Connectivity for legacy insurer integrations** with high performance and security → Dedicated/Partner Interconnect with HA VPN backup; encryption via VPN or MACsec if mandated.
4. **Identity** → federate AD (GCDS + SAML) for user access; Managed Microsoft AD for Windows workloads; grant IAM to groups.
5. **Alerts ignored** → define SLIs/SLOs, alert on burn rate, route to an on-call tool with escalation, reduce noise.
6. **Log retention for compliance** → aggregated sink to a log bucket with extended retention or Cloud Storage with Bucket Lock; Data Access audit logs enabled.
7. **Trend predictions** → land data in BigQuery, use BigQuery ML or Vertex AI; de-identify PHI first.
8. **Fast provider onboarding** → Apigee with a developer portal and standardized API products.
9. **Ingesting new provider data** → Cloud Storage/Pub/Sub → Dataflow → BigQuery/Cloud SQL, autoscaling, schema validation.
10. **Reduce latency globally** → global external Application LB, Cloud CDN, multi-region deployments.
11. **Database migration with minimal downtime** → Database Migration Service (MySQL, SQL Server), then Cloud SQL HA.
12. **Decrease admin cost** → Autopilot, managed DBs, autoscaling, CUDs, remove self-managed monitoring.

## Cymbal Retail

### Summary

Fast-growing online retailer with a huge, multi-vertical product catalog. Three initiatives: (1) **catalog and content enrichment** with gen AI (attributes, descriptions, images from supplier data), (2) **conversational commerce with product discovery** (virtual agents on web/mobile using Google's Discovery AI / retail search), (3) **technical stack modernization** (cloud infrastructure, secure data handling, third-party integrations, proactive monitoring and security). Environment: mixed on-prem and cloud; MySQL, SQL Server, Redis, MongoDB; Kubernetes; SFTP file transfers and ETL batch; a custom catalog web app querying relational DBs; an IVR routing calls to agents who key in orders manually; Grafana, Nagios, Elastic for monitoring. Pain: manual processes, data silos, hard to integrate new tech.

### Requirement mapping

| Requirement | Recommended service(s) | Rationale | Likely exam angle |
|---|---|---|---|
| **B:** Automate product catalog enrichment (less manual effort, fewer errors, consistency) | Vertex AI with Gemini models (multimodal: read supplier text + images → structured attributes, descriptions), Imagen on Vertex AI for image generation/editing, Vertex AI Pipelines for orchestration, BigQuery/Cloud SQL as catalog store, Pub/Sub triggers | Gemini extracts attributes aligned to a category taxonomy via structured (JSON) output; pipelines make it repeatable | "Generate attributes from supplier images and text" → Gemini multimodal, not Vision API labels alone |
| **B:** Improve product discoverability; **T:** automate product discovery in natural language | Vertex AI Search for commerce (retail search, browse, recommendations), Vertex AI Agent Builder for conversational layer, embeddings in Vertex AI Vector Search if custom | Purpose-built retail relevance, personalization, and natural-language query understanding; replaces SQL name/category lookups | Trap: "add full-text index to MySQL" when semantic retail search is asked |
| **B:** Increase customer engagement; personalized interactive experience | Conversational Agents (Dialogflow CX) integrated with Vertex AI Search for commerce and Gemini for generative responses; Recommendations AI (part of Vertex AI Search for commerce) | Agents on web and mobile; grounded responses reduce hallucination; personalization from browsing/purchase events | Grounding and data-store agents vs pure LLM chat |
| **B:** Drive sales conversion | Recommendations, "frequently bought together," conversational cart completion via agent tools/webhooks calling order APIs (Cloud Run) | Agent completes transactions customers previously abandoned to call center | "Let the agent place an order" → webhook/tool calling to a secured API |
| **B:** Reduce call center staffing costs and data-center hosting costs | Customer Engagement Suite / Contact Center AI (Conversational Agents for voice replacing IVR, Agent Assist for humans, Insights), migrate on-prem to Google Cloud (GKE, Cloud SQL, managed services), decommission DC | Automates first-line calls and order entry; cloud removes hosting | "Replace IVR with natural-language self-service" → Conversational Agents (voice) |
| **T:** Attribute generation aligned to category and existing catalog structure | Gemini with structured output/function calling, few-shot examples from existing catalog, Vertex AI Search or Vector Search for retrieving similar existing products (RAG), Sensitive Data Protection if supplier data contains PII | Grounding in existing catalog keeps attributes consistent; schema enforcement | "Ensure attributes match Cymbal's taxonomy" → constrain output schema + RAG over catalog |
| **T:** Image generation and enhancement (color variants, background change, text overlays) | Imagen on Vertex AI (generation, editing/inpainting/outpainting, product recontextualization), Cloud Storage for assets, Cloud Run functions for post-processing | Imagen supports mask-based editing and background replacement; text overlays can be templated | Trap: Vision API (analysis only) offered for generation |
| **T:** Scalability and performance for a huge, growing catalog | Vertex AI Search for commerce scales managed; Cloud Run/GKE autoscaling for front ends; Spanner or Cloud SQL with read replicas for catalog; Memorystore cache; Cloud CDN | Managed search and serverless remove capacity planning | "Search latency under load" → managed search + CDN + cache |
| **T:** Human-in-the-loop review UI | Web app on Cloud Run (or GKE) with IAP, review queue in Firestore/Cloud SQL, Pub/Sub for events, approvals written back to catalog; Cloud Tasks for workflow steps; optional Looker dashboard for throughput | Gen-AI output must be approved/modified before publishing; IAP secures associates' access | "Prevent unreviewed AI content reaching the catalog" → staging state + approval workflow, not direct writes |
| **T:** Data security and compliance (customer data, agent interactions, PCI for payments) | Sensitive Data Protection (redact PII in transcripts/prompts), Model Armor (prompt injection, sensitive data, harmful output), Vertex AI safety filters, CMEK, VPC Service Controls, IAM least privilege, Cloud Armor, PCI DSS scoping (tokenize card data, keep card data out of agents/logs), Data Access audit logs; Vertex AI does not train on customer data | Conversational data is sensitive; PCI demands minimal cardholder-data footprint | "Card numbers appear in chat logs" → Sensitive Data Protection de-identification + Model Armor |
| **Stack modernization:** databases | Database Migration Service to Cloud SQL (MySQL, SQL Server), Memorystore for Redis, MongoDB Atlas via Marketplace; consider Spanner for global catalog/inventory if scale requires | Managed engines with minimal app change | "Migrate MySQL with minimal downtime" → DMS |
| **Stack modernization:** SFTP file transfers and ETL batch | Storage Transfer Service (SFTP/S3/on-prem agents → Cloud Storage), Cloud Storage event notifications → Pub/Sub → Dataflow, Cloud Composer for orchestration, Datastream for CDC | Managed, scheduled, retried transfers replace scripts; Dataflow replaces batch ETL with streaming or batch | "Suppliers deliver via SFTP" → Storage Transfer Service, not a VM running cron + sftp |
| **Stack modernization:** third-party integrations | Apigee (supplier/partner APIs), Application Integration / Integration Connectors (SaaS connectors), Pub/Sub, Workflows | Standard API layer with security, quotas, analytics | "Integrate suppliers and marketplaces" → Apigee + Pub/Sub |
| **Stack modernization:** proactive monitoring and security | Cloud Observability (Monitoring, Logging, Managed Service for Prometheus, Grafana connector), SLOs and alert routing, Security Command Center, Cloud Armor, Cloud NGFW | Consolidates Grafana/Nagios/Elastic; adds security posture and threat detection | "Consolidate monitoring tools" → Cloud Monitoring + Managed Prometheus (keep Grafana dashboards if desired) |
| **Stack modernization:** Kubernetes | GKE (Autopilot) or GKE Enterprise fleets for hybrid period; Cloud Run for stateless services | Managed, autoscaled containers | "Least operational overhead for containers" → Autopilot / Cloud Run |

### Target architecture

- **Ingestion:** Supplier feeds arrive via SFTP (Storage Transfer Service into a landing bucket) and via Apigee-managed APIs. Object-finalize events publish to Pub/Sub; Dataflow validates, normalizes, and writes raw records to BigQuery and a work queue.
- **Enrichment pipeline:** Vertex AI Pipelines (or Cloud Run jobs triggered by Pub/Sub) call Gemini with the supplier text and images plus retrieved similar catalog items (RAG via Vertex AI Search/Vector Search) to produce category-aligned attributes and descriptions as structured JSON; Imagen creates color variants, background changes, and overlays; Sensitive Data Protection scans inputs; Model Armor screens prompts/responses; outputs are written to a **staging** table with confidence scores.
- **Human-in-the-loop:** Cloud Run web UI behind IAP where associates approve/reject/edit; approvals publish to Pub/Sub; a Cloud Run service writes to the catalog system of record (Cloud SQL or Spanner) and re-indexes Vertex AI Search for commerce; metrics on acceptance rate feed prompt tuning.
- **Discovery and conversation:** Website and mobile app call Vertex AI Search for commerce for search/browse/recommendations. Conversational Agents (Dialogflow CX) with data-store grounding handle chat; tools/webhooks on Cloud Run manage cart and orders; voice channel via Contact Center AI replaces the IVR, escalating to human agents with Agent Assist.
- **Data platform:** BigQuery as the unified customer/catalog analytics store (events streamed from Pub/Sub), Looker for KPIs (conversion, returns, agent deflection), BigQuery ML for demand and returns prediction.
- **Security and compliance:** IAM groups, CMEK on catalog and transcripts, VPC Service Controls around BigQuery/Cloud Storage/Vertex AI, Cloud Armor on external LB, PCI: payments handled by a tokenizing PSP so the agent never sees PANs; Data Access audit logs; Security Command Center.
- **Observability:** Cloud Monitoring with Managed Service for Prometheus for GKE, Cloud Logging, SLOs on search latency and agent success rate, alerts routed to on-call.

### Rollout phasing

1. Foundation and connectivity (VPN/Interconnect to on-prem), central observability replacing Nagios/Elastic.
2. Data migration: DMS for MySQL/SQL Server, Storage Transfer Service jobs for SFTP, BigQuery landing.
3. Enrichment pilot on one product vertical with HITL; measure acceptance rate and error reduction; expand.
4. Vertex AI Search for commerce behind the existing web app (swap search backend first), then conversational agent on web, then voice/IVR replacement.
5. Decommission on-prem hosting; optimize with CUDs, Autopilot, and lifecycle policies.

### Key risks

- Hallucinated or off-taxonomy attributes → structured output, grounding, HITL gate, evaluation datasets.
- Brand/legal issues from generated images → Imagen safety filters, SynthID watermarking awareness, HITL approval.
- Prompt injection through supplier text or customer chat → Model Armor, input sanitization, least-privilege tools.
- PCI scope creep if agents handle payments → tokenization by PSP, never store PANs, redact logs.
- Search relevance regressions → A/B testing and offline evaluation before full cutover.

### Likely question themes

1. **Generate product attributes from supplier text and images** → Gemini (multimodal) on Vertex AI with structured output, grounded on existing catalog; not Vision API label detection alone.
2. **Generate image variants / change backgrounds / add text** → Imagen on Vertex AI editing capabilities.
3. **Natural-language product discovery at scale** → Vertex AI Search for commerce (Discovery AI) + Conversational Agents; not custom SQL LIKE queries.
4. **Human review before publishing** → staging + approval UI (Cloud Run + IAP), events via Pub/Sub; automation must not bypass review.
5. **Replace IVR and reduce call-center cost** → Conversational Agents voice + Contact Center AI / Agent Assist; escalate to humans with context.
6. **SFTP/batch modernization** → Storage Transfer Service → Cloud Storage → Pub/Sub → Dataflow; Composer for scheduling.
7. **Database migration** → Database Migration Service to Cloud SQL; Memorystore for Redis; MongoDB Atlas.
8. **Protect PII/PCI in prompts, transcripts, logs** → Sensitive Data Protection de-identification, Model Armor, CMEK, VPC-SC; keep card data with a tokenizing processor.
9. **Consolidate Grafana/Nagios/Elastic** → Cloud Observability with Managed Service for Prometheus; SLO alerting.
10. **Ensure AI answers are accurate about products** → grounding with data stores (RAG), not fine-tuning as a first step.
11. **Measure success** → conversion rate, return rate, catalog time-to-publish, agent deflection rate in BigQuery/Looker.
12. **Third-party integrations** → Apigee for partner APIs; Application Integration/connectors for SaaS.

## Altostrat Media

### Summary

Media company with a large audio/video library (podcasts, interviews, news, documentaries). Already on Google Cloud: GKE for the content platform, Cloud Storage for media, BigQuery as the warehouse, Cloud Run functions for event-driven transcoding, metadata extraction, and recommendations. Legacy on-prem systems remain for content ingestion and archival (to be migrated). Identity is Google Identity plus third-party IdPs. Monitoring mixes Cloud Monitoring and Prometheus; alerts by email. Wants gen AI for recommendations, natural-language interaction, 24/7 self-service support, summaries, metadata extraction, harmful-content detection, and analytics for content strategy and revenue (dynamic pricing, targeted marketing). Executive statement: **reliability and cost management are top priorities**.

### Requirement mapping

| Requirement | Recommended service(s) | Rationale | Likely exam angle |
|---|---|---|---|
| **B:** Accelerate and improve reliability of operational workflows across cloud + on-prem | GKE Enterprise fleets (cloud GKE + Google Distributed Cloud / GKE on bare metal or VMware on-prem), Config Sync, Policy Controller, Cloud Service Mesh; Workflows/Composer for pipelines; SLOs | One management plane and GitOps for both environments removes drift | "Same config and policies on-prem and cloud" → fleet + Config Sync |
| **B:** Simplify infrastructure management for rapid deployment | GKE Autopilot, Cloud Run for stateless services, Terraform/Config Connector, Cloud Build + Cloud Deploy | Managed control planes and declarative pipelines | "Least operational overhead" |
| **B/T:** Optimize storage costs for growing media while keeping HA and scalability | Cloud Storage **Autoclass** (automatic transitions) or Object Lifecycle Management rules (Standard → Nearline 30d → Coldline 90d → Archive 365d minimums), dual-region/multi-region buckets for hot content, Cloud CDN for delivery, soft delete/retention tuning | Media has predictable access decay; Autoclass avoids early-deletion fees when patterns are unknown | Trap: Archive for content still streamed; forgetting min durations and retrieval fees |
| **B:** Natural-language interaction with 24/7 support; **T:** advanced chatbots | Vertex AI Agent Builder / Conversational Agents grounded on Altostrat's content and help articles (Vertex AI Search data stores), Gemini for generation, Contact Center AI for voice | Grounded agents give accurate self-service support around the clock | Grounding vs ungrounded LLM |
| **B/T:** Automatically generate concise summaries of audio and video | Gemini multimodal on Vertex AI (long-context audio/video understanding), Speech-to-Text (Chirp) for transcripts, Cloud Run functions/jobs triggered by Cloud Storage events, results to BigQuery/Firestore | Gemini handles long media natively; event-driven pipeline fits existing pattern | "Summarize hour-long videos" → Gemini long-context multimodal, batch prediction for backlog |
| **B/T:** Extract rich metadata using NLP and computer vision | Video Intelligence API (labels, shots, OCR, faces/logos, explicit content), Vision API, Speech-to-Text, Natural Language API (entities, sentiment), Gemini for custom schema extraction; store in BigQuery; embeddings in Vertex AI Vector Search | Prebuilt APIs are cheapest for standard metadata; Gemini for bespoke fields | "Differentiate prebuilt APIs vs Gemini" → prebuilt for standard labels/transcripts, Gemini for reasoning/custom |
| **B/T:** Detect and filter inappropriate/harmful content | Video Intelligence explicit content detection, Vision SafeSearch, Natural Language moderation, Vertex AI safety filters on generated content, **Model Armor** on prompts/responses, human review queue for borderline cases | Layered detection for uploaded media and generated text | "Harmful content in user prompts and model outputs" → Model Armor + safety settings |
| **T:** AI systems auditable and explainable | Vertex Explainable AI (feature attributions for tabular/image models), Vertex AI Model Registry and Model Monitoring (drift), Vertex AI Experiments/metadata lineage, Cloud Audit Logs (Data Access) for Vertex AI, logging prompts/responses with consent, safety scores stored | Regulators and editors need to know why content was flagged/recommended | "Explain why an asset was flagged" → Explainable AI + logged decision metadata |
| **B:** Analyze media content for trends; inform content strategy with data | BigQuery (partitioned event tables), BigQuery ML (forecasting, clustering), Looker dashboards, Dataflow streaming of engagement events, Analytics Hub for partner data | Existing BigQuery footprint; in-warehouse ML avoids data movement | "Trend forecasting with least effort" → BigQuery ML ARIMA_PLUS |
| **Revenue:** dynamic pricing, targeted marketing, personalized suggestions | Vertex AI (custom models or Recommendations via Vertex AI Search for media), BigQuery ML propensity models, Gemini for personalized copy, Pub/Sub real-time events | Media recommendations product tuned for watch-time/conversion | "Personalized recommendations for media" → Vertex AI Search for media (recommendations) |
| **T:** Modernize CI/CD for containers with a centralized management platform | Cloud Build (triggers, buildpacks), Artifact Registry (with Artifact Analysis), Cloud Deploy (delivery pipelines, canary, approvals), Binary Authorization, GKE Enterprise fleet as target set | End-to-end managed pipeline with policy enforcement | "Progressive delivery to many clusters" → Cloud Deploy targets + fleet |
| **T:** Secure, high-performance hybrid connectivity for ingestion | Dedicated Interconnect (10/100 Gbps) or Partner Interconnect with HA VPN backup; Storage Transfer Service with on-prem agents for large file moves; Transfer Appliance for the archive backlog | Large media files need bandwidth; archive backlog may be petabytes | "Move 2 PB archive with a 1 Gbps link" → Transfer Appliance |
| **T:** Scalable, performant Kubernetes on-prem and in cloud | GKE (cloud) + Google Distributed Cloud (on-prem) managed as one GKE Enterprise fleet; Cloud Service Mesh; Managed Service for Prometheus across both | Consistent Kubernetes with central visibility | "Kubernetes on-prem managed from Google Cloud" → Google Distributed Cloud / GKE Enterprise |
| **Identity:** Google Identity + third-party IdPs | Workforce Identity Federation for third-party IdP users accessing Google Cloud without Cloud Identity accounts; Cloud Identity SSO (SAML/OIDC) for the primary workforce; Identity Platform for customer identities | Removes duplicate account management | "Contractors in Okta need console access" → Workforce Identity Federation |
| **Observability:** Cloud Monitoring + Prometheus, email alerts | Managed Service for Prometheus (keeps PromQL), Cloud Monitoring dashboards, SLOs, alert policies to on-call channels, Cloud Logging, Error Reporting, Cloud Trace | Consolidates without discarding Prometheus investment; fixes alert fatigue | "Keep PromQL but centralize" → Managed Service for Prometheus |

### Target architecture

- **Platform:** GKE Enterprise fleet spanning regional GKE clusters (cloud) and Google Distributed Cloud clusters (on-prem ingestion/archival while they exist). Config Sync from a Git repo for namespaces, RBAC, quotas, network policies; Policy Controller for guardrails; Cloud Service Mesh for mTLS and telemetry. Stateless services and event handlers on Cloud Run / Cloud Run functions.
- **Delivery:** Cloud Build builds and signs images into Artifact Registry; Artifact Analysis scans; Binary Authorization enforces; Cloud Deploy pipelines promote through dev/staging/prod with canary analysis and manual approvals for prod.
- **Media storage:** Cloud Storage buckets by tier: hot dual-region bucket with Autoclass for new releases behind Cloud CDN/Media CDN; lifecycle rules move stale masters to Coldline/Archive; on-prem archive migrated via Transfer Appliance then Storage Transfer Service for deltas; CMEK where contractually required.
- **Ingestion:** Dedicated Interconnect from studios/on-prem with HA VPN backup; uploads land in Cloud Storage; Pub/Sub notifications fan out to Cloud Run functions (transcode via Transcoder API), Video Intelligence/Speech-to-Text for metadata, Gemini for summaries and custom metadata, safety scoring; results to BigQuery and Firestore; embeddings to Vertex AI Vector Search.
- **AI experiences:** Vertex AI Agent Builder chatbot grounded on catalog metadata, transcripts, and help content; Vertex AI Search for media powering recommendations; Gemini generating personalized marketing copy; Model Armor in front of all prompt paths; safety filters on outputs; human review queue for flagged content.
- **Analytics and revenue:** engagement events streamed via Pub/Sub → Dataflow → BigQuery; BigQuery ML for churn/propensity and demand forecasting to drive dynamic pricing; Looker for content strategy dashboards.
- **Governance:** Vertex AI Model Registry, Experiments, Model Monitoring; Explainable AI for classifier decisions; Data Access audit logs for Vertex AI and BigQuery; decision metadata stored with each asset.
- **Identity and access:** Cloud Identity SSO for staff, Workforce Identity Federation for partner IdPs, IAP for internal tools, IAM via groups.
- **Observability and reliability:** Managed Service for Prometheus + Cloud Monitoring, SLOs on playback start time and API availability, burn-rate alerts to PagerDuty, Cloud Logging with central sink, chaos and load testing before major releases; cost dashboards from billing export, budgets and alerts, CUDs for steady GKE nodes.

### Rollout phasing

1. Observability and alert routing fix (fast win, supports reliability priority).
2. Storage cost optimization: enable Autoclass/lifecycle on existing buckets, analyze access patterns with Storage Insights.
3. CI/CD modernization with Cloud Deploy and Binary Authorization; register clusters to a fleet; Config Sync.
4. Hybrid: Interconnect + Google Distributed Cloud for on-prem ingestion; migrate archive via Transfer Appliance.
5. AI features: metadata extraction and summarization pipeline (batch backlog then streaming), harmful-content detection, chatbot with grounding, recommendations, pricing models.
6. Continuous: Model Monitoring, evaluation datasets, cost reviews.

### Key risks

- Early-deletion fees from moving frequently accessed media to cold classes → Autoclass or analyze access first.
- Gemini/API costs at library scale → batch prediction, prebuilt APIs for standard metadata, cache results, process once and store.
- Content moderation false positives/negatives → thresholds + human review + explainability.
- Hybrid Kubernetes complexity → fleet-level policies; limit on-prem footprint to what must stay.
- Identity sprawl → Workforce Identity Federation instead of duplicate accounts.

### Likely question themes

1. **Store growing media at minimum cost with high availability** → Cloud Storage Autoclass or lifecycle rules; dual-region for hot content; watch minimum storage durations.
2. **Consistent Kubernetes across on-prem and cloud** → GKE Enterprise fleet + Config Sync + Policy Controller; Google Distributed Cloud on-prem.
3. **Centralized CI/CD with progressive delivery** → Cloud Build → Artifact Registry → Cloud Deploy, Binary Authorization.
4. **Summarize long audio/video** → Gemini multimodal (long context), batch for backlog; Speech-to-Text for transcripts.
5. **Extract metadata cheaply** → Video Intelligence, Vision, Speech-to-Text, Natural Language; Gemini only for custom reasoning.
6. **Detect harmful content and protect the chatbot** → Video Intelligence explicit detection + Vertex AI safety filters + Model Armor.
7. **Auditability and explainability** → Explainable AI, Model Registry lineage, Data Access audit logs, stored decision metadata.
8. **Third-party IdP access to Google Cloud** → Workforce Identity Federation.
9. **Keep Prometheus but consolidate and fix email alerts** → Managed Service for Prometheus, SLO burn-rate alerts to on-call.
10. **High-throughput ingestion from on-prem** → Dedicated Interconnect; Transfer Appliance for the archive backlog.
11. **Trend analysis and pricing** → BigQuery + BigQuery ML + Looker; Vertex AI Search for media recommendations.
12. **Reliability testing** → load tests, chaos engineering on GKE, DR runbooks; reliability is explicitly a top priority.

## KnightMotives Automotive

### Summary

Manufacturer of autonomous BEV, hybrid, and ICE vehicles. BEVs have a modern in-vehicle experience; hybrid/ICE do not, hurting sales. Goals within five years: consistent AI-powered experience across all models, better shopping/buying/service experiences, reliable online build-to-order for dealers, data monetization to finance investment, fully autonomous driving (starting in favorable regulatory regions). Environment: mostly on-prem with some apps on other major clouds; mainframe supply chain; outdated ERP; dealers have no budget for new equipment; multiple code bases and heavy technical debt; poor connectivity to plants and rural vehicles. Security is paramount after past breaches; EU data-protection compliance is critical. Also: upskilling, talent, better business–tech communication.

### Requirement mapping

| Requirement | Recommended service(s) | Rationale | Likely exam angle |
|---|---|---|---|
| **B:** Personalized driver relationship; cohesive experience across all models | Vertex AI (Gemini) for in-vehicle assistant via APIs, Firebase/Identity Platform for driver identity, Pub/Sub + Dataflow for telemetry, Bigtable for time-series vehicle data, BigQuery for analytics, single shared codebase delivered through Cloud Build/Artifact Registry | Cloud-hosted AI features reach legacy models via connectivity rather than per-model hardware rewrites | "Consistent UX across code bases" → common APIs behind Apigee, shared services |
| **B:** Better build-to-order model; transparency for dealers and customers; **T:** improve unreliable online ordering | Spanner (globally consistent orders/inventory), Cloud Run or GKE microservices, Pub/Sub event backbone, Apigee for dealer APIs, global external Application LB + Cloud Armor, SLOs | Reliability and consistency across regions/dealers; Spanner 99.999% multi-region SLA | "Order data inconsistent between dealers and HQ" → Spanner + event-driven integration |
| **B:** Monetize corporate data; break silos; **T:** robust data management platform, strict security/privacy, scalable AI/ML | BigQuery (lakehouse, BigLake), Dataplex Universal Catalog (governance, lineage, quality), Analytics Hub (share/monetize datasets), Sensitive Data Protection (de-identify PII/VIN), BigQuery column-level security and policy tags, Datastream for CDC from ERP | Analytics Hub lets you publish governed listings to partners without copying; Dataplex gives catalog and quality | "Sell anonymized driving data to insurers/cities" → Analytics Hub with de-identified datasets |
| **B:** Security paramount after breaches; **T:** comprehensive security framework, incident response, awareness | Security Command Center Enterprise (posture, threat detection, case management), zero trust with Chrome Enterprise Premium + IAP, VPC Service Controls, org policies, Cloud KMS/HSM CMEK, Secret Manager, Cloud NGFW, Cloud Armor, Binary Authorization, Workload Identity Federation (no keys), Data Access audit logs, Mandiant services for IR planning | Layered controls plus centralized detection/response; identity-centric access replaces perimeter VPN | "Detect misconfigurations and threats across projects" → Security Command Center |
| **B:** EU data-protection compliance (GDPR), especially for autonomous platforms | Assured Workloads (EU regions and support controls), org policy resource-location constraints, Sovereign Controls options, regional resources in EU, CMEK with Cloud EKM/HSM held in EU, Sensitive Data Protection, data subject request tooling via BigQuery, Access Transparency/Access Approval | Enforces residency, personnel, and key controls | "Keep EU vehicle data in EU with restricted Google support access" → Assured Workloads + Access Approval |
| **B:** Fully autonomous driving investment; **T:** AV development, simulation, regulatory compliance | AI Hypercomputer (TPU/GPU clusters, Vertex AI training, Dynamic Workload Scheduler), Vertex AI Pipelines and Model Registry, Cloud Storage/Parallelstore/Filestore for datasets, GKE with GPU node pools or Batch for simulation, Model Monitoring, Explainable AI | Large-scale training and simulation need elastic accelerator capacity and MLOps governance | "Train perception models on petabytes at lowest cost" → Spot/DWS flex capacity, TPU/GPU on Vertex AI |
| **B:** Upskilling, talent, business–tech communication | Cloud Center of Excellence, Google Cloud Skills Boost and certification paths, Gemini Cloud Assist and Gemini Code Assist to raise productivity, Architecture Center reference designs, agile squads with product owners | Section 4 topics: change management, skills readiness, stakeholder facilitation | "Teams lack cloud skills" → CoE + training plan + partner support, not "hire only" |
| **T:** Update legacy in-vehicle hardware/software; reliable rural connectivity for real-time AI | Edge inference on-vehicle with models trained on Vertex AI, over-the-air updates via Cloud Storage + signed artifacts, store-and-forward telemetry to Pub/Sub, Google Distributed Cloud edge at plants/dealers, offline-capable Firestore sync for dealer apps | Rural connectivity cannot be assumed; design for intermittent links | "Real-time features with unreliable connectivity" → local inference + async sync |
| **T:** Network upgrades between plants and HQ | Dedicated/Partner Interconnect per plant, HA VPN backup, Network Connectivity Center hub with site-to-site data transfer, Cloud Router BGP, Cross-Cloud Interconnect to existing other-cloud apps | NCC connects sites and clouds through Google's backbone | "Connect plants, HQ, and AWS workloads" → NCC + Cross-Cloud Interconnect |
| **T:** Hybrid cloud strategy; gradually modernize legacy (mainframe, ERP) | Mainframe: Dual Run / Mainframe Assessment Tool, Mainframe Connector to BigQuery, incremental strangler pattern via Apigee; ERP: SAP on Google Cloud or SaaS ERP; Migration Center for assessment; Google Cloud VMware Engine for rehost; GKE Enterprise for hybrid apps | Gradual, risk-managed modernization; keep mainframe running while offloading data and functions | "Offload mainframe data for analytics first" → Mainframe Connector → BigQuery |
| **T:** Modern dealer tools (sales, service, inventory) with no dealer budget | Web/mobile apps on Cloud Run, Firebase, Firestore offline sync, Vertex AI Search over service manuals, Gemini assistants for technicians, Chrome-based access | Runs on existing browsers/phones; no new equipment | "Dealers cannot buy hardware" → browser/mobile SaaS on Cloud Run |
| **T:** Comprehensive CRM | Salesforce or other SaaS CRM integrated via Apigee, Application Integration/Integration Connectors, Pub/Sub; customer 360 in BigQuery; Gemini for personalization | Buy (SaaS) rather than build; integrate via APIs — "workload disposition" | "Build vs buy CRM" → buy SaaS, integrate with Apigee |
| **Telemetry ingestion** (implicit: driving, road, behavioral, crash data) | Pub/Sub (global ingestion), Dataflow streaming, Bigtable (hot time-series), BigQuery (analytics), Cloud Storage (raw), IoT gateway patterns with mTLS device identity | Handles millions of vehicles with autoscaling and exactly-once processing | "Ingest telemetry from millions of vehicles" → Pub/Sub + Dataflow → Bigtable/BigQuery |

### Target architecture

- **Foundation and security:** Organization with folders per region/regulatory domain (EU folder under Assured Workloads), Shared VPC per environment, org policies (resource locations, no external IPs, CMEK required), Security Command Center Enterprise, Chrome Enterprise Premium + IAP for workforce zero trust, Cloud KMS/HSM with EKM for EU-controlled keys, Secret Manager, VPC Service Controls around data platform and Vertex AI, Workload Identity Federation for CI/CD and other-cloud workloads.
- **Network:** Network Connectivity Center hub; Dedicated Interconnect from HQ and major plants, Partner Interconnect for smaller plants, HA VPN backup, Cross-Cloud Interconnect to existing AWS/Azure apps, Google Distributed Cloud edge appliances at plants for local processing; Cloud NGFW for east-west inspection; Cloud Armor on public endpoints.
- **Commerce and dealer platform:** Build-to-order service on Cloud Run/GKE with Spanner (multi-region) for orders, configurations, and inventory; Pub/Sub events to ERP/CRM; Apigee exposes dealer and partner APIs with quotas and analytics; dealer web/mobile apps on Cloud Run + Firebase with offline capability; Salesforce CRM integrated via Apigee/Application Integration; Vertex AI Search and Gemini assistants for technicians and sales staff.
- **Legacy modernization:** Mainframe Connector streams supply-chain data to BigQuery; strangler pattern peels functions to Cloud Run behind Apigee; ERP replaced/modernized on Google Cloud; VMware Engine for rehosting remaining VMs; Migration Center drives waves.
- **Vehicle data platform:** Vehicles publish telemetry via mTLS to Pub/Sub (store-and-forward for rural gaps); Dataflow enriches and writes to Bigtable (real-time features) and BigQuery (analytics, BigLake over Cloud Storage raw); Dataplex Universal Catalog governs, classifies (with Sensitive Data Protection), and monitors quality; Analytics Hub publishes de-identified datasets for monetization; Looker for internal insight.
- **AI/AV:** Vertex AI with AI Hypercomputer (TPU/GPU pods, Dynamic Workload Scheduler) for perception/planning model training; GKE GPU pools or Batch for simulation at scale; Vertex AI Pipelines, Model Registry, Model Monitoring, Explainable AI; Gemini models (via Vertex AI) power the in-vehicle assistant and dealer tools; Model Armor and safety filters on all conversational paths; EU training/inference kept in EU regions.
- **Operations:** Cloud Observability with SLOs for ordering and API availability, alerting to on-call; Cloud Deploy for releases; Backup and DR Service; multi-region DR for Spanner-backed ordering; FinOps with billing export, budgets, CUDs; Gemini Cloud Assist for troubleshooting and cost insights.
- **People:** Cloud CoE, role-based Skills Boost paths, platform team offering golden paths (Service Catalog/Terraform modules), partner-led mainframe program.

### Rollout phasing

1. **Security and foundation first** (past breaches): landing zone, Assured Workloads EU, Security Command Center, zero-trust access, key management, central logging.
2. **Network**: NCC hub, Interconnects to HQ/plants, Cross-Cloud Interconnect to existing cloud apps.
3. **Build-to-order reliability**: rebuild ordering on Spanner + Cloud Run behind Apigee; integrate dealers; measure order accuracy and uptime.
4. **Data platform and monetization**: telemetry ingestion, BigQuery/Dataplex, Mainframe Connector, Analytics Hub listings — revenue funds later phases.
5. **AI experiences**: Gemini assistant for BEVs first, extend to hybrid/ICE via OTA and connectivity upgrades; dealer/technician tools; CRM.
6. **Autonomous driving program**: AI Hypercomputer training, simulation, MLOps and compliance in favorable regions; scale as regulation allows.
7. **Continuous**: upskilling, ERP/mainframe retirement, cost optimization.

### Key risks

- Data residency violations when EU vehicle data is processed globally → Assured Workloads, location constraints, regional Vertex AI endpoints.
- Re-identification in monetized datasets → Sensitive Data Protection, aggregation, k-anonymity checks, policy tags.
- Mainframe big-bang failure → incremental strangler and data offload first.
- Accelerator capacity/cost for AV training → reservations, Dynamic Workload Scheduler, Spot for tolerant jobs, checkpointing.
- Dealer adoption with zero hardware budget → browser/mobile-first tools, offline mode.
- Multi-cloud sprawl → NCC, consistent IAM via WIF, GKE Enterprise policies.

### Likely question themes

1. **Unreliable build-to-order system with global dealers** → Spanner for consistent orders/inventory, Cloud Run/GKE services, Apigee, SLOs; not sharded Cloud SQL.
2. **Connect plants, HQ, and workloads in another cloud** → Network Connectivity Center + Dedicated/Partner Interconnect + Cross-Cloud Interconnect, HA VPN backup.
3. **EU data protection for autonomous platform data** → Assured Workloads EU folder, resource-location org policy, CMEK/EKM, Access Approval; EU-region Vertex AI.
4. **Monetize corporate data securely** → BigQuery + Dataplex governance + Sensitive Data Protection de-identification + Analytics Hub listings.
5. **Security posture after breaches** → Security Command Center Enterprise, zero trust (Chrome Enterprise Premium/IAP), VPC-SC, incident response plan, security training.
6. **Train autonomous-driving models at scale** → Vertex AI with AI Hypercomputer (TPUs/GPUs), Dynamic Workload Scheduler, Vertex AI Pipelines and Model Registry.
7. **Mainframe modernization approach** → assess, offload data via Mainframe Connector to BigQuery, strangler pattern behind Apigee; not immediate rewrite.
8. **Rural connectivity and real-time features** → on-vehicle inference, store-and-forward telemetry, Pub/Sub, Google Distributed Cloud edge where needed.
9. **Telemetry from millions of vehicles** → Pub/Sub → Dataflow → Bigtable (hot) and BigQuery (analytics).
10. **CRM decision** → buy SaaS (e.g., Salesforce), integrate via Apigee/Application Integration; customer 360 in BigQuery.
11. **Dealers with no budget** → browser/mobile apps on Cloud Run/Firebase with offline sync.
12. **Upskilling and business–tech alignment** → Cloud CoE, Skills Boost paths, Gemini Cloud Assist/Code Assist, platform team with golden paths.

## Cross-case patterns worth memorizing

| Pattern | EHR | Cymbal | Altostrat | KnightMotives |
|---|---|---|---|---|
| Container platform | GKE + fleets | GKE/Cloud Run | GKE Enterprise fleet + Google Distributed Cloud | GKE/Cloud Run, GDC edge |
| Hybrid connectivity | Dedicated Interconnect + HA VPN | VPN/Interconnect during migration | Dedicated Interconnect, Transfer Appliance | NCC + Interconnect + Cross-Cloud Interconnect |
| Databases | Cloud SQL, Memorystore, MongoDB Atlas | Cloud SQL (via DMS), Memorystore, Atlas, maybe Spanner | Firestore/BigQuery | Spanner, Bigtable, BigQuery |
| Identity | AD federation, Managed AD | Cloud Identity, IAP for HITL UI | Workforce Identity Federation | Zero trust, WIF |
| Observability fix | Central Cloud Observability, SLO alerts | Consolidate Grafana/Nagios/Elastic | Managed Prometheus + SLO alerts | SLOs for ordering |
| Gen AI | BigQuery ML/Vertex AI predictions | Gemini + Imagen + Vertex AI Search for commerce + Conversational Agents | Gemini summaries, prebuilt media APIs, grounded chatbot | Gemini assistant, AI Hypercomputer training |
| AI safety/governance | PHI de-identification | Model Armor, HITL, PCI | Model Armor, Explainable AI, audit logs | Model Armor, EU residency |
| Compliance | HIPAA BAA, GDPR | PCI DSS, privacy | Content safety, auditability | GDPR/EU sovereignty via Assured Workloads |

> **Trap:** Do not import a solution from one case into another. Cymbal's "replace IVR" answer is Conversational Agents; EHR has no IVR. Altostrat's storage-cost answer is Autoclass; KnightMotives' cost story is data monetization and FinOps.

## Key takeaways

- Every case-study answer must satisfy the published requirements plus the question's new constraint; the executive statement is the tie-breaker.
- EHR: regional GKE + Cloud SQL HA for 99.9%, Dedicated/Partner Interconnect + HA VPN for long-lived legacy integrations, AD federation, central Cloud Observability with SLO-routed alerts, BigQuery + Vertex AI for trends, Apigee for provider onboarding, HIPAA BAA and audit logs.
- Cymbal: Gemini (multimodal) for attributes/descriptions, Imagen for image variants, Vertex AI Search for commerce + Conversational Agents for discovery and IVR replacement, mandatory human-in-the-loop UI, DMS and Storage Transfer Service for modernization, Sensitive Data Protection + Model Armor + PCI scoping.
- Altostrat: GKE Enterprise fleets with Config Sync across cloud and on-prem, Cloud Build/Artifact Registry/Cloud Deploy, Cloud Storage Autoclass/lifecycle for cost, prebuilt media APIs plus Gemini for summaries, safety filters + Model Armor, Explainable AI + audit logs, Managed Service for Prometheus, Workforce Identity Federation.
- KnightMotives: Spanner-backed build-to-order on Cloud Run/GKE behind Apigee, NCC + Cross-Cloud Interconnect for hybrid/multicloud, BigQuery + Dataplex + Analytics Hub for data monetization, Vertex AI + AI Hypercomputer for AV training, Security Command Center Enterprise + zero trust, Assured Workloads for EU, mainframe strangler pattern, CoE and upskilling.
- "Alerts ignored by email" appears in three cases; the answer is always SLO/burn-rate alerting routed to an on-call channel, not more email.
- Same database mix (MySQL, SQL Server, Redis, MongoDB) appears in EHR and Cymbal: Cloud SQL via DMS, Memorystore, MongoDB Atlas via Marketplace.
- Gen-AI questions favor grounding/RAG over fine-tuning, prebuilt APIs over custom models for standard tasks, and always include human review, safety filters, and explainability where the case asks for accuracy or auditability.
- Hybrid connectivity SLA numbers (99.9% with 2 attachments, 99.99% with 4 across 2 metros; HA VPN 99.99%) are testable in EHR, Altostrat, and KnightMotives contexts.
- Compliance anchors: EHR → HIPAA BAA; Cymbal → PCI DSS and PII; Altostrat → content safety and auditability; KnightMotives → GDPR/EU sovereignty via Assured Workloads.
- Cost levers by case: EHR admin cost (managed services), Altostrat storage classes/Autoclass, Cymbal call-center automation, KnightMotives data monetization and accelerator scheduling.
- Section 4 "soft" topics show up through KnightMotives (upskilling, CoE, build-vs-buy CRM) and EHR (change from colos, reducing outages from misconfiguration through IaC).

## Quick self-check

- Q: EHR must keep 99.9% availability for a MySQL-backed customer app. What is the minimum database design? — **A:** Cloud SQL for MySQL with regional HA (synchronous standby in another zone), plus read replicas as needed; add a cross-region replica for DR.
- Q: Cymbal wants to create color variants of a product image and swap the background. Which service? — **A:** Imagen on Vertex AI (image editing/generation), not the Vision API.
- Q: Altostrat's media access patterns are unknown and they want the lowest storage cost without early-deletion fees. What do you enable? — **A:** Cloud Storage Autoclass on the bucket.
- Q: KnightMotives wants to sell de-identified driving data to partners without copying it. Which services? — **A:** BigQuery datasets de-identified with Sensitive Data Protection, governed in Dataplex Universal Catalog, shared via Analytics Hub listings.
- Q: Contractors at Altostrat authenticate with a third-party IdP and need Google Cloud console access without new accounts. Which feature? — **A:** Workforce Identity Federation.
- Q: EHR wants users to sign in to Google Cloud with their Active Directory credentials. What do you set up? — **A:** Google Cloud Directory Sync to provision users/groups into Cloud Identity and SAML single sign-on against AD FS (or Entra ID); grant IAM to groups.
- Q: Cymbal's generated descriptions must never reach the live catalog without associate approval. What is the architectural control? — **A:** Write gen-AI output to a staging store, expose an approval UI (Cloud Run behind IAP), and only an approval event triggers the write to the catalog and search re-index.
- Q: KnightMotives needs vehicle data for EU customers to stay in the EU with controlled Google support access. What do you use? — **A:** An Assured Workloads folder with EU data residency/sovereignty controls, resource-location org policies, CMEK (optionally Cloud EKM), and Access Approval.
