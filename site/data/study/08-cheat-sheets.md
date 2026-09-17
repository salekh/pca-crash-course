Use this module the night before the exam. Every row is a fact that has appeared, in some form, in PCA questions. Where a figure varies by configuration, the table says so — do not memorize false precision.

## Service SLAs (monthly uptime, Google-published)

| Service / configuration | SLA | Notes |
|---|---|---|
| Compute Engine — instances across multiple zones | 99.99% | Single instance 99.9% |
| Compute Engine live migration | n/a | Host maintenance without reboot (not for Spot/GPU) |
| GKE regional cluster control plane | 99.95% | Zonal cluster 99.5%; Autopilot pods across zones 99.9% |
| Cloud Run / Cloud Run functions / App Engine | 99.95% | Serverless family |
| Cloud Storage Standard multi-/dual-region | 99.95% | Standard regional 99.9%; Nearline/Coldline/Archive 99.9% multi, 99.0% regional; 11 nines durability (design) |
| Cloud SQL Enterprise with HA | 99.95% | Enterprise Plus with HA 99.99% |
| AlloyDB (HA primary) | 99.99% | Enterprise Plus-class Postgres |
| Spanner multi-region | 99.999% | Regional 99.99% |
| Bigtable multi-cluster, multi-cluster routing | 99.999% | Single-cluster 99.9% |
| Firestore multi-region | 99.999% | Regional 99.99% |
| BigQuery | 99.99% | |
| Memorystore for Redis Standard tier | 99.9% | Redis Cluster / Valkey multi-zone 99.99% |
| Pub/Sub | 99.95% | |
| Filestore Regional / Enterprise | 99.99% | Basic and Zonal 99.9% |
| Cloud Load Balancing | 99.99% | |
| Cloud DNS | 100% | The only 100% SLA |
| Dedicated / Partner Interconnect | 99.9% or 99.99% | 99.9% = 2 connections in 1 metro; 99.99% = 4 connections across 2 metros and 2 regions with global routing |
| HA VPN | 99.99% | Classic VPN 99.9% |
| Direct / Carrier Peering | none | No SLA |

> **Remember:** Five nines (99.999%) appears only for multi-region Spanner, multi-cluster Bigtable and multi-region Firestore. If a question demands 99.999% for a relational workload, it is Spanner.

## Cloud Storage classes

| Class | Min storage duration | Retrieval fee | Typical access | Availability SLA (multi / regional) |
|---|---|---|---|---|
| Standard | None | None | Hot, frequent | 99.95% / 99.9% |
| Nearline | 30 days | Yes (low) | About once a month | 99.9% / 99.0% |
| Coldline | 90 days | Yes (higher) | About once a quarter | 99.9% / 99.0% |
| Archive | 365 days | Yes (highest) | Less than once a year | 99.9% / 99.0% |
| Autoclass | n/a | None (managed) | Unknown/changing patterns | Transitions automatically among classes |

Other facts: single object up to 5 TiB; Object Versioning, soft delete (default 7-day window), retention policies with Bucket Lock (WORM), object holds; dual-region turbo replication targets ~15-minute RPO; lifecycle rules by age, versions, class, custom time; uniform bucket-level access recommended; signed URLs for time-limited access; Requester Pays; CMEK/CSEK supported.

## Persistent Disk, Hyperdisk and Local SSD

| Disk | Media | Performance shape | Max size | Notes |
|---|---|---|---|---|
| pd-standard | HDD | ~0.75 read / 1.5 write IOPS per GiB, throughput-oriented | 64 TiB | Cheapest; boot/bulk |
| pd-balanced | SSD | 6 IOPS/GiB, per-VM caps by vCPU | 64 TiB | Default general choice |
| pd-ssd | SSD | 30 IOPS/GiB, up to ~100k IOPS per VM | 64 TiB | Databases |
| pd-extreme | SSD | Provisioned IOPS up to ~120k | 64 TiB | Large N2/M-series only |
| Hyperdisk Balanced / Extreme / Throughput / ML | SSD, decoupled | Provision IOPS and throughput independently; Extreme up to ~350k IOPS | 64 TiB | Newer machine series (C3, N4, M3…) |
| Local SSD | NVMe/SCSI, attached to host | Very high IOPS, lowest latency | 375 GiB per device (larger on Z3) | Ephemeral: lost on stop/host error; not for durable data |
| Regional PD | pd-balanced/ssd/standard | Synchronous replication across two zones | 64 TiB | Force-attach on failover; HA for stateful VMs |

Snapshots are incremental and can be stored multi-regionally, scheduled via resource policies, and restored across regions; instant snapshots for fast in-place recovery; archive snapshots for cheaper long-term retention. Images and machine images capture full VMs.

## Load balancer family

| Load balancer | Layer | Scope | Proxy or passthrough | Client IP | Key features |
|---|---|---|---|---|---|
| Global external Application LB | L7 HTTP(S) | Global anycast (Premium Tier) | Proxy (Envoy) | In `X-Forwarded-For` | Cloud Armor, Cloud CDN, IAP, URL maps, serverless/hybrid NEGs, multi-region failover |
| Classic Application LB | L7 | Global (Premium) or regional (Standard) | Proxy | XFF | Legacy; fewer advanced traffic features |
| Regional external Application LB | L7 | Regional | Proxy | XFF | Standard Tier allowed, regional compliance |
| Regional internal Application LB | L7 | Regional, RFC 1918 | Proxy (proxy-only subnet) | XFF | Internal microservices, header routing |
| Cross-region internal Application LB | L7 | Multi-region internal | Proxy | XFF | Global internal frontend with failover |
| Global external proxy Network LB | L4 TCP/SSL | Global | Proxy | Lost unless PROXY protocol | TCP/SSL offload for non-HTTP |
| Regional external / internal proxy Network LB | L4 TCP | Regional (and cross-region internal) | Proxy | PROXY protocol | Hybrid backends |
| External passthrough Network LB | L4 TCP/UDP/ESP/GRE/ICMP | Regional | Passthrough (DSR) | Preserved | Gaming, VoIP, any protocol; backend services with health checks |
| Internal passthrough Network LB | L4 TCP/UDP/any | Regional, RFC 1918 | Passthrough | Preserved | Next hop for NVAs, internal databases, global access option |

Health checks come from the ranges 35.191.0.0/16 and 130.211.0.0/22 (proxy LBs) and must be allowed by firewall rules. Only global external ALB and proxy NLB (Premium Tier) get a single anycast IP worldwide.

## Hybrid connectivity

| Option | Bandwidth | SLA | Encryption | Use when |
|---|---|---|---|---|
| Dedicated Interconnect | 10 Gbps or 100 Gbps per circuit; up to 8×10 or 2×100 per interconnect | 99.9% / 99.99% by topology | None by default (add MACsec or HA VPN over Interconnect) | Large steady traffic, own colocation presence |
| Partner Interconnect | 50 Mbps to 50 Gbps per VLAN attachment | 99.9% / 99.99% by topology | Same | No presence in a Google colocation facility |
| Cross-Cloud Interconnect | 10 or 100 Gbps | Same model | Same | Direct to AWS, Azure, OCI, Alibaba |
| HA VPN | ~3 Gbps per tunnel (sum of both directions), scale with tunnels/ECMP | 99.99% with two tunnels to matching gateways | IPsec | Quick start, low volume, encryption required |
| Classic VPN | ~3 Gbps per tunnel | 99.9% | IPsec | Legacy; static routing use cases |
| Direct / Carrier Peering | Varies | None | None | Access Google public services, not VPC |
| Network Connectivity Center | n/a | n/a | n/a | Hub-and-spoke for VPCs, VPNs, Interconnects, router appliances, site-to-site transit |

Cloud Router provides BGP with dynamic routing mode regional or global; VLAN attachments default to 10 Gbps and go up to 50 Gbps. Interconnect egress is cheaper than internet egress.

## Database decision table

| Need | Pick | Why / limits |
|---|---|---|
| Relational, regional, MySQL/PostgreSQL/SQL Server compatibility, up to tens of TB | Cloud SQL | Managed, HA zonal failover, read replicas, PITR; 99.99% on Enterprise Plus |
| PostgreSQL with higher throughput, analytics on transactional data, AI vectors | AlloyDB | Columnar engine, up to ~4× Postgres OLTP, AlloyDB Omni runs anywhere |
| Global relational, horizontal scale, strong consistency, 99.999% | Spanner | TrueTime, GoogleSQL and PostgreSQL dialects, no maintenance downtime |
| Wide-column, petabyte, single-digit ms, time-series/IoT/adtech | Bigtable | No SQL joins (has SQL/GoogleSQL surface now), row-key design critical, replication for 99.999% |
| Document DB for mobile/web, real-time sync, offline | Firestore | Native mode; Datastore mode for server apps; multi-region 99.999% |
| Analytics warehouse, SQL over petabytes, serverless | BigQuery | Not OLTP; long-term storage discount after 90 days |
| Sub-millisecond cache, sessions, leaderboards | Memorystore (Redis/Valkey/Memcached) | In-memory; Redis Cluster for scale-out and 99.99% |
| Time-series metrics at scale for Prometheus | Managed Service for Prometheus | Monarch backend |
| Lift-and-shift Oracle or unsupported engines | Compute Engine / Bare Metal Solution | Self-managed; consider DMS to PostgreSQL/AlloyDB |
| Graph, search, vector | Spanner Graph, Vertex AI Vector Search, AlloyDB/pgvector, Firestore vector search | Choose by primary data model |

## Cloud Audit Logs retention

| Log type | Enabled by default | Retention in `_Required`/`_Default` | Cost |
|---|---|---|---|
| Admin Activity | Always on | 400 days | Free |
| System Event | Always on | 400 days | Free |
| Access Transparency | Enable per org (needs eligible support) | 400 days | Free |
| Data Access | Off (except BigQuery) | 30 days (configurable to 3650) | Billed ingestion |
| Policy Denied | On | 30 days | Billed ingestion |

## Most-tested organization policy constraints

| Constraint | Effect |
|---|---|
| `iam.allowedPolicyMemberDomains` | Domain restricted sharing: only identities from listed Cloud Identity customer IDs |
| `iam.disableServiceAccountKeyCreation` | Blocks user-managed SA keys |
| `iam.automaticIamGrantsForDefaultServiceAccounts` | Stops default SAs getting Editor |
| `compute.vmExternalIpAccess` | Deny/allow external IPs on VMs |
| `compute.skipDefaultNetworkCreation` | No default VPC in new projects |
| `compute.restrictVpcPeering` / `compute.restrictSharedVpcSubnetworks` | Control peering and Shared VPC usage |
| `compute.requireOsLogin` | Enforce OS Login |
| `compute.requireShieldedVm` | Shielded VMs only |
| `compute.trustedImageProjects` | Only approved image projects |
| `compute.disableSerialPortAccess` | Blocks serial console |
| `compute.restrictLoadBalancerCreationForTypes` | Allow only specific LB types (e.g., internal only) |
| `compute.restrictCloudNATUsage` | Limit which subnets can use NAT |
| `gcp.resourceLocations` | Data residency: allowed regions/multi-regions |
| `gcp.restrictServiceUsage` | Allow-list of services usable in scope |
| `gcp.restrictCmekCryptoKeyProjects` / `gcp.restrictNonCmekServices` | Enforce CMEK from approved key projects |
| `storage.uniformBucketLevelAccess` | Force uniform IAM on buckets |
| `storage.publicAccessPrevention` | No public buckets |
| `sql.restrictPublicIp` / `sql.restrictAuthorizedNetworks` | Private Cloud SQL only |
| `run.allowedIngress` / `cloudfunctions.allowedIngressSettings` | Restrict serverless ingress to internal/LB |
| `essentialcontacts.allowedContactDomains` | Contacts only from approved domains |

Org policies are inherited down the hierarchy, can be overridden or merged at folder/project, support tags for conditional scoping, and custom constraints (CEL) for many services. Org policy is *preventive*; IAM is *who*, org policy is *what is allowed at all*.

## Most-tested IAM roles

| Area | Role | Grants |
|---|---|---|
| Basic | `roles/owner`, `roles/editor`, `roles/viewer`, `roles/browser` | Avoid basic roles in prod; browser = see hierarchy only |
| Resource Manager | `roles/resourcemanager.organizationAdmin`, `folderAdmin`, `projectCreator`, `projectIamAdmin`, `projectMover` | Hierarchy and IAM administration |
| Billing | `roles/billing.admin`, `billing.user` (link projects), `billing.viewer`, `billing.projectManager` | Separation of finance vs engineering |
| Service accounts | `roles/iam.serviceAccountUser` (act as), `serviceAccountTokenCreator` (impersonate), `serviceAccountAdmin`, `serviceAccountKeyAdmin`, `workloadIdentityUser` | Impersonation chain |
| Compute | `roles/compute.admin`, `instanceAdmin.v1`, `networkAdmin`, `securityAdmin` (firewalls, certs), `networkUser` (use Shared VPC subnets), `osLogin`, `osAdminLogin`, `compute.viewer` | Network vs instance separation |
| Storage | `roles/storage.objectViewer`, `objectCreator`, `objectUser`, `objectAdmin`, `storage.admin` | Object roles do not list buckets |
| BigQuery | `roles/bigquery.dataViewer`, `dataEditor`, `dataOwner`, `jobUser` (run queries), `user`, `admin`, `metadataViewer` | dataViewer + jobUser = read-only analyst |
| Logging / Monitoring | `roles/logging.viewer`, `privateLogViewer` (Data Access logs), `logWriter`, `logging.admin`, `configWriter` (sinks), `monitoring.viewer`, `monitoring.editor`, `monitoring.metricWriter` | Agents need logWriter + metricWriter |
| GKE / Cloud Run | `roles/container.admin`, `container.developer`, `container.clusterViewer`, `roles/run.invoker`, `run.developer`, `run.admin` | run.invoker for service-to-service auth |
| Data / security | `roles/cloudsql.client`, `cloudsql.admin`, `pubsub.publisher`, `pubsub.subscriber`, `secretmanager.secretAccessor`, `cloudkms.cryptoKeyEncrypterDecrypter`, `cloudkms.admin`, `iap.tunnelResourceAccessor`, `iap.httpsResourceAccessor`, `orgpolicy.policyAdmin`, `securitycenter.admin`, `artifactregistry.reader`/`writer`, `deploy.releaser`/`approver` | Common least-privilege picks |

## gcloud commands most tested

| Task | Command shape |
|---|---|
| Set project/region/zone | `gcloud config set project|compute/region|compute/zone VALUE` |
| Named configs | `gcloud config configurations create|activate|list` |
| Login / ADC / impersonate | `gcloud auth login`; `gcloud auth application-default login`; `--impersonate-service-account=SA` |
| Enable API | `gcloud services enable SERVICE.googleapis.com` |
| IAM binding | `gcloud projects add-iam-policy-binding PROJECT --member=... --role=...` (also `folders`, `organizations`, `iam service-accounts`) |
| VM | `gcloud compute instances create|list|ssh --tunnel-through-iap|stop|delete` |
| MIG | `gcloud compute instance-groups managed create|rolling-action start-update|set-autoscaling` |
| GKE creds | `gcloud container clusters get-credentials NAME --region|--zone` |
| Cloud Run | `gcloud run deploy|services update-traffic|jobs execute` |
| Storage | `gcloud storage cp|rsync|ls|buckets create|objects update --storage-class` (legacy `gsutil`) |
| BigQuery | `bq query --use_legacy_sql=false`, `bq load`, `bq mk --dataset`, `bq extract`, `bq show --schema` |
| Logs | `gcloud logging read FILTER --limit N`, `gcloud logging sinks create NAME DEST --log-filter=...` |
| Build/deploy | `gcloud builds submit --tag IMAGE`, `gcloud deploy releases create|rollouts promote|rollback` |
| Org policy | `gcloud org-policies set-policy policy.yaml`, `gcloud resource-manager org-policies describe` |
| Output shaping | `--filter="key=value AND name~regex" --format="table(a,b)|json|yaml|csv|value(x)"` |
| Recommender | `gcloud recommender recommendations list --recommender=google.compute.instance.MachineTypeRecommender --location=ZONE` |

## DR tiers: RPO/RTO at a glance

| Tier | RTO | RPO | Cost | Signature services |
|---|---|---|---|---|
| Backup & restore | Hours–days | Hours | $ | Backup and DR Service, snapshots, IaC rebuild |
| Pilot light | 10s of minutes–hours | Minutes | $$ | DB replica in DR region, images and IaC ready |
| Warm standby | Minutes | Seconds–minutes | $$$ | Scaled-down stack in region 2, DNS/LB failover |
| Hot / active-active | ~0 | ~0 | $$$$ | Global ALB, Spanner/Bigtable multi-region, multi-region GCS |

## Discounts and commitments

| Mechanism | Flexibility | Saving | Notes |
|---|---|---|---|
| Resource-based CUD (1/3 yr) | Region + machine family fixed | ~37% / ~55% general-purpose; up to ~70% memory-optimized | Compute Engine vCPU/memory/GPU/SSD; also some databases |
| Spend-based CUD (1/3 yr) | Any region/family for a service; $/hour commit | ~28% / ~46% (flexible compute) | Cloud Run, GKE, Cloud SQL, Spanner, AlloyDB, BigQuery editions, Bigtable, Dataflow… |
| Sustained use discount | Automatic | Up to 30% (N1), ~20% (N2/N2D/C2) | Not E2/N4/C3/A-series; no commitment |
| Spot VMs | None; reclaimable with 30 s notice | 60–91% | No SLA, no live migration; batch, CI, stateless workers |
| BigQuery editions slot commitments | Slot-hours | 1-/3-year rates | Standard/Enterprise/Enterprise Plus |
| Free tier | Per month | e.g., 1 TiB BigQuery queries, 10 GiB BQ storage, 5 GB Standard GCS in US regions, e2-micro | Good for PoCs |

## GKE Autopilot vs Standard

| Aspect | Autopilot | Standard |
|---|---|---|
| Node management | Google-managed, no node pools visible | You manage node pools, sizes, upgrades |
| Billing | Per pod vCPU/memory/ephemeral storage requested | Per node VM |
| Security posture | Hardened defaults enforced (Workload Identity Federation for GKE, Shielded nodes, no privileged pods except allow-listed) | Configurable |
| SLA | Control plane 99.95%; pods 99.9% multi-zone | Regional control plane 99.95%; zonal 99.5% |
| Customization | Limited (no DaemonSet-heavy node tweaks, some host access blocked) | Full: GPUs/TPUs, custom kernels, node affinity |
| Best for | Default choice; teams wanting Kubernetes without node ops | Special hardware, cost tuning, legacy needs |

## Cloud Run limits and defaults

| Item | Value |
|---|---|
| Request timeout | Default 5 min, max 60 min (services); jobs task timeout up to 24 h |
| Concurrency | Default 80, max 1000 requests per instance |
| Memory / CPU | Up to 32 GiB and 8 vCPU (GPU options such as NVIDIA L4 available) |
| Scaling | Scale to zero; min instances to avoid cold starts; max instances setting |
| Networking | Direct VPC egress or Serverless VPC Access connector; ingress internal / internal+LB / all |
| Cloud Run functions | Event-driven timeout 9 min; HTTP up to 60 min (2nd gen on Cloud Run) |
| Traffic | Revisions immutable; split by %; tags for URLs; `--no-traffic` |

## Pub/Sub, BigQuery and other quick numbers

| Service | Fact |
|---|---|
| Pub/Sub | Retention default 7 days, max 31 days; ack deadline default 10 s, max 600 s; max message 10 MB; dead-letter after 5–100 attempts; snapshots expire in 7 days; exactly-once and ordering keys available; BigQuery/Cloud Storage export subscriptions |
| BigQuery | Long-term storage price after 90 days without modification; on-demand billed per TiB scanned (first 1 TiB/month free); time travel 2–7 days (default 7) + 7-day fail-safe; max query runtime 6 h; up to 10,000 partitions per table; dataset location immutable |
| Spanner | 99.999% multi-region; nodes or processing units (1,000 PU = 1 node); ~10 TiB per node guidance; online schema changes |
| Bigtable | 99.999% multi-cluster; design row keys to avoid hotspots; SSD vs HDD clusters; autoscaling |
| Cloud SQL | Up to 64 TiB storage; HA = synchronous regional PD failover; PITR from binary logs/WAL; Enterprise Plus 99.99% and near-zero-downtime maintenance |
| Compute Engine | Spot 30-second preemption notice; custom machine types; sole-tenant nodes for licensing; live migration default |
| Cloud Logging | `_Default` 30 days, configurable 1–3650 days; `_Required` 400 days; log entry max 256 KB |
| Cloud Monitoring | Metrics retained 24 months; uptime checks from ≥3 locations at 1–15 min intervals |
| Cloud KMS | Key rotation schedules; HSM (FIPS 140-2 Level 3) and EKM for external keys; keys are regional/multi-regional/global |
| Secret Manager | Versioned secrets, automatic replication or user-managed regions, rotation notifications via Pub/Sub |

## VPC facts and limits

| Item | Value |
|---|---|
| VPC networks per project | Default quota 5 (raisable) |
| Subnet primary range | Regional; minimum /29; 4 addresses reserved per primary range (network, gateway, second-to-last, broadcast) |
| MTU | Default 1460; 1500 supported; up to 8896 (jumbo) |
| Peering | Non-transitive; no overlapping CIDRs; exchange subnet routes, optional custom routes; ~15,000 VM instances per peering group |
| Shared VPC | One host project per service project; host can serve many service projects; `compute.networkUser` on subnets |
| Firewall | Priority 0–65535 (lower wins); implied allow egress + deny ingress; hierarchical (org/folder) and network firewall policies; Cloud NGFW adds IPS and FQDN/geo objects |
| Private Google Access | Per subnet; lets VMs without external IP reach Google APIs |
| Cloud NAT | Regional, per-subnet, no inbound; logs available |
| Dynamic routing mode | Regional (default) or global for Cloud Router advertisements |
| Alias IP / secondary ranges | Needed for GKE (VPC-native) pods and services |

## Mnemonics

- **Storage class minimums**: "Some Nerds Can Archive — 0 / 30 / 90 / 365."
- **Golden signals**: **LETS** — Latency, Errors, Traffic, Saturation.
- **DORA four keys**: "**F**ast **L**eads **F**ail **R**arely" — Frequency, Lead time, Failure rate, Restore time.
- **Adoption Framework**: themes **L-L-S-S** (Learn, Lead, Scale, Secure); phases **T-S-T** (Tactical, Strategic, Transformational).
- **DR tiers**: "**B**ackup, **P**ilot, **W**arm, **H**ot" — cost and readiness rise together.
- **ADC lookup**: "**E**nv → **F**ile → **M**etadata" (GOOGLE_APPLICATION_CREDENTIALS → gcloud ADC file → attached SA).
- **Audit log retention**: "Admins and Systems keep 400; Data and Denied keep 30."
- **Cloud Run**: "5-60-80-1000" — default timeout 5 min, max 60, concurrency default 80, max 1000.
- **Pub/Sub**: "7-31-10-600" — retention 7 d default, 31 d max, ack 10 s default, 600 s max.
- **Error budget per 30 days**: 3 nines ≈ 43 min, 4 nines ≈ 4.3 min, 5 nines ≈ 26 s.
- **Interconnect SLA**: "2 in 1 metro = 99.9; 4 in 2 metros = 99.99."
- **Burn-rate windows**: "14.4 / 6 / 1 over 1 h / 6 h / 3 d."
- **Five-nines trio**: Spanner multi-region, Bigtable multi-cluster, Firestore multi-region.

## Service → one-line purpose glossary

### Compute
- **Compute Engine** — VMs with custom machine types, live migration, sole-tenant nodes.
- **Managed instance groups (MIG)** — autoscaled, autohealed VM fleets with rolling updates.
- **Spot VMs** — deeply discounted, preemptible-at-any-time capacity.
- **Sole-tenant nodes** — dedicated hosts for licensing/compliance.
- **Google Kubernetes Engine (GKE)** — managed Kubernetes; Standard and Autopilot modes.
- **GKE Enterprise** — multi-cluster fleets, Config Sync, Policy Controller, service mesh (formerly Anthos).
- **Cloud Run** — serverless containers (services and jobs) with revisions and traffic splitting.
- **Cloud Run functions** — event-driven/HTTP functions running on Cloud Run.
- **App Engine** — legacy PaaS (Standard/Flexible) with traffic-split versions.
- **Batch** — managed batch job scheduling on Compute Engine.
- **Google Cloud VMware Engine** — native vSphere SDDC in Google Cloud.
- **Bare Metal Solution** — dedicated hardware adjacent to Google Cloud for Oracle-type workloads.
- **Cloud Workstations** — managed, secure developer environments.
- **Cloud Shell / Cloud Shell Editor / Cloud Code** — browser terminal, IDE, and IDE plugins for Google Cloud.

### Storage and transfer
- **Cloud Storage** — object storage with Standard/Nearline/Coldline/Archive/Autoclass.
- **Persistent Disk / Hyperdisk** — network block storage; Hyperdisk decouples IOPS/throughput.
- **Local SSD** — ephemeral host-attached NVMe.
- **Filestore** — managed NFS (Basic, Zonal, Regional/Enterprise).
- **Google Cloud NetApp Volumes** — managed NetApp NFS/SMB with snapshots and replication.
- **Parallelstore** — high-performance parallel file system for AI/HPC.
- **Backup and DR Service** — centralized backup for VMs, databases, GKE with vaults.
- **Storage Transfer Service** — managed online transfer from S3/Azure/HTTP/on-prem.
- **Transfer Appliance** — shipped device for offline bulk transfer.

### Databases
- **Cloud SQL** — managed MySQL, PostgreSQL, SQL Server.
- **AlloyDB** — high-performance PostgreSQL-compatible with columnar engine; **AlloyDB Omni** runs anywhere.
- **Spanner** — globally distributed relational DB with 99.999% SLA.
- **Bigtable** — wide-column NoSQL for petabyte, low-latency workloads.
- **Firestore** — serverless document DB (Native and Datastore modes).
- **Memorystore** — managed Redis, Redis Cluster, Valkey, Memcached.
- **Database Migration Service** — minimal-downtime homogeneous/heterogeneous migrations.
- **Datastream** — serverless change data capture into BigQuery/Cloud Storage.

### Data analytics
- **BigQuery** — serverless data warehouse; **BigQuery ML**, **BI Engine**, **BigQuery Omni** (multicloud), **Analytics Hub** (data sharing), **BigQuery Data Transfer Service**.
- **Dataflow** — managed Apache Beam for batch and streaming.
- **Dataproc** — managed Spark/Hadoop (clusters and Serverless).
- **Pub/Sub** — global messaging and event ingestion.
- **Cloud Composer** — managed Apache Airflow orchestration.
- **Cloud Data Fusion** — visual, code-free ETL (CDAP).
- **Dataform** — SQL-based ELT pipelines in BigQuery.
- **Dataplex Universal Catalog** — data governance, lineage, quality, discovery (absorbed Data Catalog).
- **Looker / Looker Studio** — enterprise BI semantic layer / free dashboards.
- **Dataprep** — third-party (Trifacta) data wrangling.

### AI and ML
- **Vertex AI** — unified ML platform: training, Pipelines, Feature Store, Model Registry, endpoints, Workbench, Colab Enterprise, experiments.
- **Gemini models** — Google's multimodal foundation models served via Vertex AI.
- **Model Garden** — catalog of Google, open-source and partner models to deploy or tune.
- **Vertex AI Agent Builder** — build search and conversational/agent applications on enterprise data.
- **Gemini Enterprise / NotebookLM Enterprise** — enterprise agent platform and grounded research assistant.
- **AI Hypercomputer** — integrated TPU/GPU supercomputing stack for large-scale training/serving.
- **Cloud TPU / GPUs** — accelerators for training and inference.
- **Vertex AI Search / Conversational Agents (Dialogflow CX)** — enterprise search and chatbots.
- **Vision AI, Video Intelligence, Speech-to-Text, Text-to-Speech, Translation, Natural Language, Document AI** — pretrained perception and language APIs.
- **Contact Center AI** — virtual agents and agent assist for call centers.
- **Model Armor** — prompt/response screening for LLM apps (injection, jailbreak, sensitive data).
- **Gemini Cloud Assist** — AI assistant for design, troubleshooting, cost and operations in the console.
- **Gemini Code Assist** — AI coding assistant in IDEs and Google Cloud tools.

### Networking
- **VPC / Shared VPC / VPC Network Peering** — global software-defined networks, centralized host networking, private RFC 1918 connectivity.
- **Cloud Load Balancing** — global and regional L4/L7 load balancers.
- **Cloud CDN / Media CDN** — edge caching for web and large-scale media.
- **Cloud DNS** — managed public/private zones with routing policies (100% SLA).
- **Cloud NAT** — managed outbound NAT for private instances.
- **Cloud Router** — BGP for dynamic routes over VPN/Interconnect.
- **Cloud VPN (HA VPN)** — IPsec tunnels, 99.99% with HA.
- **Cloud Interconnect / Partner Interconnect / Cross-Cloud Interconnect** — private high-bandwidth links to on-prem or other clouds.
- **Network Connectivity Center** — hub-and-spoke connectivity management.
- **Private Service Connect** — private endpoints for Google APIs and producer services.
- **Private Google Access** — reach Google APIs from private IPs.
- **Cloud Armor** — WAF, DDoS protection, rate limiting, adaptive protection at the edge.
- **Cloud NGFW** — next-generation firewall with IPS, FQDN/geo objects, threat intelligence.
- **Cloud IDS** — managed intrusion detection (Palo Alto engines) via packet mirroring.
- **Network Intelligence Center** — topology, Connectivity Tests, Performance Dashboard, Firewall Insights, Network Analyzer.
- **Packet Mirroring** — clone traffic for inspection.
- **Service Directory** — service registry and private DNS integration.
- **Cloud Service Mesh** — managed Istio/Envoy mesh for mTLS, traffic control, telemetry.
- **Certificate Manager** — managed TLS certificates for load balancers.
- **Apigee / API Gateway / Cloud Endpoints** — full API management / serverless gateway / self-run ESPv2 proxy.

### Security and identity
- **Cloud IAM** — roles, policies, conditions, deny policies, PAM.
- **Cloud Identity** — identity provider and device management; Google Workspace-compatible.
- **Identity Platform** — CIAM for customer-facing apps.
- **Identity-Aware Proxy** — context-aware access to web apps and TCP forwarding without VPN.
- **Chrome Enterprise Premium** — zero-trust access platform (formerly BeyondCorp Enterprise).
- **Workload Identity Federation** — keyless access for external workloads and GKE pods.
- **Resource Manager / Organization Policy Service** — hierarchy and preventive guardrails.
- **Cloud KMS / Cloud HSM / Cloud EKM** — key management: software, FIPS 140-2 L3 HSM, external keys.
- **Secret Manager** — versioned secrets with IAM and rotation hooks.
- **Certificate Authority Service** — private CA hierarchy.
- **Sensitive Data Protection** — discover, classify, de-identify PII (formerly Cloud DLP).
- **Security Command Center** — posture, vulnerability, threat detection and compliance (Standard/Premium/Enterprise).
- **Assured Workloads** — compliance-controlled folders (FedRAMP, IL4, sovereignty).
- **VPC Service Controls** — service perimeters against data exfiltration.
- **Access Transparency / Access Approval** — visibility and approval of Google staff access.
- **Binary Authorization** — deploy-time image attestation enforcement.
- **Artifact Analysis** — vulnerability scanning and metadata for artifacts.
- **Web Security Scanner** — DAST for App Engine/GKE/Compute web apps.
- **reCAPTCHA** — bot and fraud protection.
- **Google Security Operations (Chronicle) / Mandiant** — SIEM/SOAR and threat intelligence/incident response.
- **Cloud Asset Inventory** — resource and policy inventory with feeds and search.
- **Policy Intelligence** — IAM recommender, policy analyzer, troubleshooter.
- **Confidential Computing / Shielded VMs** — encrypted-in-use VMs and verified boot.
- **OS Login / VM Manager** — IAM-based SSH and patch/config management.

### Operations, developer tools and management
- **Cloud Logging / Cloud Monitoring / Cloud Trace / Cloud Profiler / Error Reporting** — the Cloud Observability suite.
- **Managed Service for Prometheus** — Google-scale Prometheus backend with PromQL.
- **Personalized Service Health** — Google incidents relevant to your projects.
- **Cloud Build** — serverless CI with private pools and SLSA provenance.
- **Cloud Deploy** — managed continuous delivery with canary, approvals, rollback.
- **Artifact Registry** — containers and language packages (replaces Container Registry).
- **Developer Connect / Cloud Source Repositories** — Git integrations (CSR is legacy).
- **Terraform / Infrastructure Manager** — IaC and Google-managed Terraform runs.
- **Config Connector / Config Sync / Policy Controller** — Kubernetes-style resource management, GitOps, policy.
- **Service Catalog** — curated self-service solutions for developers.
- **Cloud Scheduler / Cloud Tasks / Workflows / Eventarc / Application Integration** — cron, task queues, serverless orchestration, event routing, iPaaS.
- **Cloud Billing / FinOps hub / Budgets** — cost visibility, savings, alerts.
- **Active Assist (Recommender)** — cost, security, performance, reliability recommendations.
- **Migration Center / Migrate to Virtual Machines / Migrate to Containers** — assess, lift-and-shift, containerize.
- **Cloud Quotas** — view, request and override quotas.
- **Firebase** — mobile/web app platform integrating Firestore, Auth, Hosting.

## Key takeaways

- Five-nines SLAs exist only for multi-region Spanner, multi-cluster Bigtable and multi-region Firestore; Cloud DNS is the sole 100%.
- Storage minimums 0/30/90/365 days for Standard/Nearline/Coldline/Archive; Autoclass when access is unknown.
- PD max 64 TiB; pd-ssd 30 IOPS/GiB; Local SSD 375 GiB ephemeral; regional PD for synchronous two-zone HA.
- Global external Application LB for worldwide HTTP(S) with Cloud Armor/CDN; passthrough NLBs preserve client IP; internal passthrough NLB is the next hop for NVAs.
- Interconnect 10/100 Gbps circuits, Partner 50 Mbps–50 Gbps, HA VPN 99.99% at ~3 Gbps per tunnel; SLA depends on redundancy topology.
- Admin Activity/System Event logs 400 days free; Data Access/Policy Denied 30 days and billable; `_Default` retention configurable to 3650 days.
- Know the top org policies (domain restriction, no SA keys, no external IPs, resource locations, uniform bucket access, public access prevention).
- Role pairs to remember: `serviceAccountUser` (act as) vs `serviceAccountTokenCreator` (impersonate); `bigquery.dataViewer` + `jobUser` for analysts; `compute.networkUser` for Shared VPC.
- Cloud Run: 5 min default/60 min max timeout, concurrency 80 default/1000 max, up to 32 GiB and 8 vCPU.
- Pub/Sub: 7-day default/31-day max retention, 10 s default/600 s max ack deadline, 10 MB messages.
- BigQuery long-term storage after 90 days; first 1 TiB of queries per month free; time travel up to 7 days.
- Resource CUDs for fixed shapes, spend-based CUDs for flexibility, SUD automatic, Spot 60–91% off with 30-second notice.
- DR tiers scale from backup/restore to active-active as RTO/RPO fall and cost rises.

## Quick self-check

- Q: Which Cloud Storage class has a 90-day minimum storage duration? — **A:** Coldline.
- Q: What Interconnect topology is required for the 99.99% SLA? — **A:** Four connections across two metros and two regions with global dynamic routing.
- Q: Which load balancer preserves the client source IP without a proxy protocol? — **A:** External or internal passthrough Network LB.
- Q: How long are Data Access audit logs kept by default and are they free? — **A:** 30 days; they are billed and off by default (except BigQuery).
- Q: Which org policy prevents sharing resources with identities outside your organization? — **A:** `iam.allowedPolicyMemberDomains` (domain restricted sharing).
- Q: Maximum request timeout for a Cloud Run service? — **A:** 60 minutes (default 5).
- Q: What is the maximum Pub/Sub message retention? — **A:** 31 days.
- Q: Which role lets a principal generate tokens as a service account (impersonate it)? — **A:** `roles/iam.serviceAccountTokenCreator`.
