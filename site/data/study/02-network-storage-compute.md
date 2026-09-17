## How to use this module

Exam objective 1.3 ("Designing network, storage, and compute resources") is where most of the *product-knowledge* questions live. Nearly every question is a "which service?" question with two plausible distractors. The tables below are organised so you can memorise the **one or two discriminating facts** per service — the thing that makes it right or wrong for a scenario.

## Compute

### Platform comparison

| Platform | Use when | Avoid when | Scaling | Pricing model |
|---|---|---|---|---|
| **Compute Engine** | Lift-and-shift, specific OS/kernel, licensed software, GPUs/TPUs at VM level, stateful servers, anything not container-friendly | You want zero server management; bursty traffic that drops to zero | MIGs autoscale on CPU/LB/metrics/schedules; regional MIGs across zones; max 2,000 VMs per MIG (zonal/regional limits) | Per-second billing (1-min minimum), sustained-use discounts on some families, CUDs (1/3 yr), Spot |
| **GKE Standard** | Kubernetes with node-level control: custom node images, DaemonSets, local SSD, GPU time-slicing, Windows nodes, very large clusters | Small team that does not want to manage node pools/upgrades | Horizontal Pod Autoscaler, Vertical Pod Autoscaler, Cluster Autoscaler, Node Auto-Provisioning; up to 15,000 nodes (65,000 with recent limits) | Pay per node VM + cluster fee ($0.10/h per cluster, one zonal cluster free per account); CUDs |
| **GKE Autopilot** | Kubernetes API without managing nodes; Google enforces best practices; pay only for pod requests | Need privileged DaemonSets, custom kernels, or unsupported node customisation | Google scales nodes automatically; HPA/VPA for pods | Per-pod vCPU/memory/ephemeral storage per second; Spot pods; CUDs |
| **Cloud Run (services & jobs)** | Stateless HTTP/gRPC/WebSocket/event-driven containers; batch jobs to completion; scale to zero; any language via container | Long-lived stateful connections beyond 60 min, need for local persistent disk (use volumes/GCS FUSE/NFS mounts instead), licensed per-host software | 0→N instances (default max 100 per revision, raisable), up to 1,000 concurrent requests per instance, CPU always-allocated option, GPUs (L4) available | Per-100 ms CPU/memory while serving (request-based) or per-instance (instance-based); free tier; CUDs |
| **Cloud Run functions** (2nd gen, built on Cloud Run) | Single-purpose functions triggered by HTTP, Pub/Sub, Cloud Storage, Eventarc (90+ sources), Firestore | Complex apps with many endpoints; long-running workers (max 60 min HTTP / 9 min event-driven) | Per-request automatic, concurrency configurable | Invocations + compute time; same billing as Cloud Run |
| **App Engine** (Standard / Flexible) | Existing App Engine apps; simple web apps with traffic splitting and versions built in | New designs (Cloud Run is the successor) | Standard scales to zero, very fast; Flexible runs containers on VMs (min 1 instance) | Instance hours |
| **Batch** | HPC/batch jobs described as scripts or containers with dependencies, arrays, retries; runs on Compute Engine incl. Spot and GPUs | Latency-sensitive services | Managed job queue provisions/destroys VMs | Underlying VM pricing, no extra fee |
| **Google Cloud VMware Engine** | Move vSphere/vSAN/NSX estates unchanged; keep VMware tooling; then modernise gradually | Greenfield; small footprints (min 3 nodes per private cloud in production) | Add nodes to private cloud; autoscale policies | Per node (bare-metal ve1/ve2 nodes) incl. VMware licences; CUDs |
| **Bare Metal Solution** | Oracle RAC and other software that forbids virtualisation or needs specialised hardware; < 2 ms latency to Google Cloud region | Anything that runs fine in a VM | Manual | Monthly hardware subscription |

> **Exam tip:** "Minimise operational overhead" with a containerised web service → Cloud Run. Same but they explicitly need Kubernetes features (custom operators, service mesh, StatefulSets) → GKE Autopilot. Need to control node hardware → GKE Standard. Legacy binary with OS dependencies → Compute Engine MIG. Whole vSphere farm in 6 months → VMware Engine.

> **Trap:** Cloud Run **jobs** and **Batch** both run to completion. Cloud Run jobs = containerised tasks, up to 24 h per task, up to 10,000 tasks parallelisable; Batch = VM-level scheduling with GPUs, MPI, Spot, and shell scripts. HPC with tightly coupled nodes → Batch (or GKE), not Cloud Run.

### Machine families

| Family | Series | Optimised for | Typical exam use |
|---|---|---|---|
| **General purpose (cost)** | **E2** (shared-core e2-micro/small/medium up to 32 vCPU) | Lowest cost, dynamic CPU platform | Dev/test, small web/apps, "cheapest that works"; no sustained-use discounts on E2 (but cheapest baseline), supports custom types |
| **General purpose (balanced)** | **N2** (Intel), **N2D** (AMD), **N4** (Intel Emerald Rapids, Hyperdisk only, custom shapes, Titanium) , N1 (legacy, GPU-capable) | Balanced price/performance, largest variety of shapes, custom machine types, sole-tenant | Enterprise apps, medium DBs, most MIG workloads |
| **Compute-optimised** | **C3** (Intel Sapphire Rapids), **C3D** (AMD Genoa), **C4/C4A** (Intel Granite Rapids / Google Axion Arm), **H3** (HPC, 200 Gbps networking, no Spot), C2/C2D (older) | Highest per-core performance, consistent frequency, high network bandwidth | Game servers, HPC, ad serving, CI, high-traffic web tier, latency-sensitive services |
| **Memory-optimised** | **M1** (up to 4 TB), **M2** (up to 12 TB), **M3** (up to 4 TB, Ice Lake), **M4** (up to ~6 TB) | Large in-memory DBs; up to ~12 TB RAM | **SAP HANA**, in-memory analytics, large relational DBs; long CUD lock-in typical |
| **Accelerator-optimised** | **A2** (NVIDIA A100 40/80 GB), **A3** (H100/H200, up to 8 GPUs, 3.2 Tbps GPU networking; A3 Mega/Ultra), **A4** (B200/GB200), **G2** (NVIDIA L4 — inference, video transcoding, virtual workstations) | ML training and inference, HPC | Vertex AI custom training, LLM serving; G2/L4 is the "cost-effective inference" answer |
| **Arm** | **T2A** (Ampere Altra), **C4A** (Google Axion) | Arm-native, price-performance for scale-out | Web servers, containerised microservices, open-source DBs compiled for Arm |
| **Scale-out AMD** | **T2D** (AMD Milan, no SMT — each vCPU is a full core) | Scale-out workloads: web, containers, media transcoding | Best price-performance for throughput-oriented microservices |
| **Storage-optimised** | **Z3** (large Local SSD, up to 36 TiB) | High IOPS/throughput local storage | Scale-out databases, log analytics, flash-optimised DBs |

Other compute knobs:

- **Custom machine types** – choose exact vCPU/memory (N-series, E2, some others) to avoid paying for unused memory; **extended memory** beyond the default ratio. The answer when "the workload needs 6 vCPU and 40 GB and no predefined shape fits".
- **Spot VMs** (successor to preemptible) – 60–91% discount, can be reclaimed with 30 s notice, no SLA, no max runtime (preemptible had 24 h), not for stateful or must-finish work; ideal with MIGs, Batch, GKE node pools, Dataproc secondary workers, fault-tolerant HPC and CI.
- **Sole-tenant nodes** – physical host dedicated to you; needed for **per-core/per-socket BYOL** licences (Windows Server, SQL Server), compliance isolation, and *CPU overcommit* / *node affinity* control. Priced per node, not per VM.
- **Committed use discounts** – resource-based (specific machine family in region, 1 or 3 years, up to ~57% GP / ~70% memory-optimised) and **spend-based / flexible CUDs** (commit to $/hour across families and regions, also cover Cloud Run, GKE Autopilot, Cloud SQL, Spanner, etc.). **Sustained use discounts** apply automatically (N1/N2/N2D/C2/M1 etc., not E2/N4/C3) when a VM runs > 25% of the month.
- **Shielded VMs** (Secure Boot, vTPM, integrity monitoring) and **Confidential VMs** (AMD SEV / Intel TDX memory encryption in use) — pick for "data encrypted while processing".
- **Live migration** keeps VMs running through host maintenance (not available for GPU VMs and Spot; set `--maintenance-policy TERMINATE` instead).
- **Placement policies**: compact (low latency HPC) vs spread (availability across hosts).

## Storage

### Cloud Storage classes

| Class | Minimum storage duration | Retrieval fee | Storage price (relative) | Availability SLA (region / multi-region) | Use for |
|---|---|---|---|---|---|
| **Standard** | None | None | Highest | 99.9% / 99.95% | Hot data, websites, streaming, analytics staging, data accessed > once a month |
| **Nearline** | **30 days** | Yes (per GB) | ~½ Standard | 99.0% / 99.9% | Access ~once a month: backups, long-tail media |
| **Coldline** | **90 days** | Higher | ~¼ Standard | 99.0% / 99.9% | Access ~once a quarter: DR copies, older archives |
| **Archive** | **365 days** | Highest | Lowest (~1/20 Standard) | 99.0% / 99.9% | Access < once a year: compliance retention, cold archives — still millisecond access (no rehydration wait, unlike tape-style archives) |

Facts that show up in questions:

- All classes share the **same API, same millisecond latency, 11-nines designed durability**. Class changes cost: deleting/rewriting before the minimum duration is billed as if stored for the full minimum.
- **Autoclass** – bucket-level setting that automatically transitions objects between Standard → Nearline → Coldline → Archive based on access, with **no retrieval or early-deletion fees**; small management fee per 1,000 objects. Pick when access patterns are unknown or mixed.
- **Object Lifecycle Management** – rules by age, creation date, number of newer versions, storage class, `matchesPrefix`; actions **SetStorageClass** (only "colder") and **Delete**. Pick when access patterns are predictable ("after 30 days move to Nearline, delete after 7 years").
- **Location types**: **region** (lowest latency, cheapest), **dual-region** (two specific regions, e.g. `NAM4`; synchronous-ish replication, **Turbo replication** guarantees 15-minute RPO; 99.95% SLA), **multi-region** (`US`, `EU`, `ASIA`; geo-redundant, 99.95%). Data is always replicated across ≥2 zones within a region.
- **Object versioning** keeps noncurrent versions (combine with lifecycle to cap count). **Soft delete** (default 7 days) protects against deletion. **Retention policy** sets a minimum age before deletion; **Bucket Lock** makes it irreversible (WORM, regulatory e.g. SEC 17a-4). **Object holds** (event-based, temporary) freeze individual objects.
- Access control: **uniform bucket-level access** (IAM only, recommended) vs fine-grained ACLs; **signed URLs** (time-limited access without Google accounts); **public access prevention** org policy; **CMEK/CSEK** encryption; **VPC Service Controls** perimeter.
- Performance: parallel composite uploads, request rate ramp-up guidance (avoid sequential object names for hot writes), **Anywhere Cache** (zonal SSD cache in front of a bucket), **Cloud Storage FUSE** for mounting on GKE/Compute Engine (ML training data), **Storage Insights** for inventory.
- **Requester pays**, **Pub/Sub notifications**, static website hosting behind global external ALB + CDN.

### Block storage (Persistent Disk, Hyperdisk, Local SSD)

| Disk type | Backing | Max size / IOPS class | Use when |
|---|---|---|---|
| **pd-standard** | HDD | 64 TB; low IOPS (0.75 read IOPS/GB) | Cold, sequential, cheap: batch scratch, backups |
| **pd-balanced** | SSD | 64 TB; 6 IOPS/GB, up to 80k | Default boot & general-purpose disk |
| **pd-ssd** | SSD | 64 TB; 30 IOPS/GB, up to 100k | Databases, latency-sensitive |
| **pd-extreme** | SSD | provisioned IOPS up to 120k; only on select large machines | Legacy high-IOPS DBs; largely superseded by Hyperdisk |
| **Hyperdisk Balanced / Throughput / Extreme / ML** | Next-gen block, decoupled provisioning of size, IOPS and throughput; required on C3/C4/N4/M3+; **Hyperdisk Balanced High Availability** = synchronous cross-zone replication; **Hyperdisk ML** = read-only multi-attach for model weights; **storage pools** for thin provisioning | Up to 350k IOPS (Extreme), 2,400 MB/s+ (Throughput) | Any new high-performance workload; SAP HANA, Hadoop/Kafka (Throughput), model serving (ML) |
| **Regional PD / Hyperdisk Balanced HA** | Synchronous replication across two zones in a region | Same as underlying type, higher price | HA for stateful VMs with manual/automated failover (`force-attach`) |
| **Local SSD** | NVMe/SCSI physically attached, 375 GB each (up to 12 TiB per VM on Z3) | Millions of IOPS, ~sub-100 µs | Scratch, caches, flash DBs — **data lost on stop/host error**; not snapshot-able |

Snapshots are incremental and can be scheduled; **instant snapshots** for fast in-zone restore; **standard snapshots** stored in Cloud Storage (regional or multi-regional location); **archive snapshots** for long-term retention. Disks can be attached read-only to many VMs (multi-reader) or read-write multi-writer for clustered file systems.

### File storage

| Service | Tiers / facts | Use when |
|---|---|---|
| **Filestore** | **Basic HDD / Basic SSD** (1–63.9 TiB, zonal), **Zonal** (1–100 TiB, high IOPS), **Regional** (1–100 TiB, synchronous 3-zone replication, 99.99%), **Enterprise** (legacy regional tier). NFSv3 (NFSv4.1 on newer tiers); backups; snapshots; Backup for GKE integration | Lift-and-shift apps needing POSIX shared file system, GKE ReadWriteMany PVs, media rendering, home directories |
| **Google Cloud NetApp Volumes** | Managed NetApp ONTAP: NFS & **SMB** (multi-protocol), snapshots, cross-region replication, Flex/Standard/Premium/Extreme service levels, up to PiB | Windows file shares (SMB with Active Directory), enterprise NAS features, SAP shared files, VMware Engine datastores |
| **Parallelstore / Managed Lustre** | Parallel file systems (DAOS / Lustre) with TB/s throughput | HPC and AI training data staging |
| **Cloud Storage FUSE** | Mount buckets as a file system (not POSIX-complete) | ML datasets, read-mostly access to objects |

> **Trap:** Filestore does **not** speak SMB; Windows shared drives → NetApp Volumes (or a Windows file server VM). Filestore Basic is **zonal** — for regional HA pick Filestore Regional.

### Database comparison

| Database | Model | Consistency | Scale | Latency | Topology | Typical use | Key limits / facts |
|---|---|---|---|---|---|---|---|
| **Cloud SQL** (MySQL, PostgreSQL, SQL Server) | Relational | Strong (single primary) | Vertical (up to 96–128 vCPU, 64 TB storage; Enterprise Plus larger), read replicas (async) for reads | ms | Zonal or regional HA (sync standby); cross-region replicas | Lift-and-shift OLTP, CMS, ERP back-ends | Writes do not scale horizontally; HA failover ~60 s (Enterprise Plus < 1 s-ish with data cache); automatic backups + PITR; Private IP via Private Service Access or PSC; Cloud SQL Auth Proxy; IAM DB auth |
| **AlloyDB for PostgreSQL** | Relational (PostgreSQL-compatible) | Strong | Vertical primary + up to 20 read-pool nodes; columnar engine accelerates analytics; storage scales to 128 TiB | Sub-ms cache-friendly, 4× faster than standard PG for OLTP, up to 100× for analytical queries (Google claims) | Regional HA by default, cross-region secondary clusters, AlloyDB Omni for anywhere | Demanding PostgreSQL OLTP + HTAP, migrate off Oracle | 99.99% SLA incl. maintenance; continuous backup + PITR; AlloyDB AI (vector search, model endpoint integration) |
| **Spanner** | Relational (GoogleSQL & PostgreSQL dialects) + Graph, key-value, vector search | **Strong, externally consistent** globally | **Horizontal** read & write; add nodes/processing units online; petabytes | ms (regional single-digit; multi-region writes pay cross-region commit latency) | Regional (99.99%) / dual-region / multi-region (99.999%) | Global OLTP: finance, gaming, retail inventory, ledgers | 1 node = 1,000 processing units (≈10 TB storage per node with newer limits); schema design (avoid hotspotting monotonic keys — use UUIDs/bit-reversed sequences); interleaved tables; no downtime maintenance; Data Boost for analytics |
| **Bigtable** | Wide-column NoSQL (HBase API, also SQL/GoogleSQL subset) | Strong within a cluster; **eventual** across replicated clusters (can request single-cluster routing for strong) | **Horizontal**, linear with nodes; petabytes; millions of QPS | **Single-digit ms** at p99 | Zonal clusters; replicate up to 8 clusters across zones/regions (multi-primary) | Time series, IoT telemetry, ad-tech, fraud detection features, personalisation, MapReduce/Dataflow sinks | No joins, no multi-row ACID (single-row atomic only); row-key design is everything (avoid sequential keys); min 1 node (HDD or SSD); ≥ 1 TB or high QPS to be cost-effective; autoscaling by CPU/storage; 99.999% with multi-cluster routing |
| **Firestore** (Native / Datastore mode / Enterprise-MongoDB compatible) | Document NoSQL | Strong; ACID transactions | Automatic horizontal; no capacity planning | ms; real-time listeners | Regional (99.99%) / multi-region (99.999%) | Mobile/web app back-ends, user profiles, real-time sync, offline-first, serverless apps | 1 MiB document limit; sustained write throughput per document ~1/s; index every query; Datastore mode = no real-time/offline but higher write throughput for server apps |
| **Memorystore** (Redis, Redis Cluster, Valkey, Memcached) | In-memory key-value | N/A (cache) | Redis: up to 300 GB per instance (Standard); Redis Cluster/Valkey: shards to TBs, zero-downtime scaling | **Sub-ms** | Basic (zonal) / Standard (cross-zone replica, 99.9%) / Cluster (multi-zone, 99.99%) | Session store, caching, leaderboards, rate limiting, pub/sub | Persistence (RDB/AOF) available on Cluster; not a system of record |
| **BigQuery** | Columnar analytical warehouse (SQL) | Strong (ACID DML, snapshot isolation) | Serverless; petabytes; slots | Seconds for scans; BI Engine sub-second for dashboards | Regional or multi-region (US/EU) datasets | Data warehouse, BI, log analytics, ML (BigQuery ML), lakehouse via BigLake, streaming analytics via Storage Write API | Pricing: on-demand per TB scanned or capacity (editions/slots); partition + cluster tables to cut cost; **not** for OLTP or high-QPS point lookups |

Quick discriminators:

- **Cloud SQL vs Spanner**: regional vs global; vertical vs horizontal; wire-compatible with MySQL/PG vs not (Spanner PG dialect is *compatible-ish*, not drop-in).
- **AlloyDB vs Cloud SQL for PostgreSQL**: AlloyDB when you need more performance, HTAP, 99.99% with maintenance included, or Oracle-migration target; Cloud SQL for simplicity/cost or MySQL/SQL Server.
- **Bigtable vs Firestore**: Bigtable = massive throughput/analytics-adjacent with simple access patterns; Firestore = app developer ergonomics, transactions, mobile SDKs.
- **Bigtable vs BigQuery**: Bigtable = operational low-latency key lookups; BigQuery = analytical SQL scans.
- **Memorystore vs Firestore for sessions**: Memorystore when sub-ms and ephemeral; Firestore when durable.

### Data processing services

| Service | What it is | Use when | Avoid when |
|---|---|---|---|
| **Dataflow** | Managed Apache Beam; unified **batch + streaming**; autoscaling, exactly-once, windowing, watermarks; templates (e.g., Pub/Sub → BigQuery); Dataflow Prime; Streaming Engine | New pipelines, streaming analytics, ETL/ELT at scale, CDC processing, "serverless" and "no cluster management" | Team has heavy Spark/Hadoop investment and wants to reuse jobs unchanged |
| **Dataproc** | Managed Hadoop/Spark/Flink/Trino clusters (90-second spin-up); **Dataproc Serverless for Spark**; ephemeral clusters with Cloud Storage connector instead of HDFS | Migrating existing Spark/Hive/Pig jobs; ML with Spark; cost control via Spot secondary workers and autoscaling | Greenfield streaming (prefer Dataflow) |
| **BigQuery** | Serverless SQL warehouse; ELT with SQL, scheduled queries, **Dataform** for SQL workflows, BigQuery ML, remote functions, BigLake | Analytics, ELT inside the warehouse, ML on tabular data | Row-level OLTP |
| **Cloud Data Fusion** | Managed CDAP: **visual, code-free ETL/ELT** with 150+ connectors, lineage, runs on Dataproc | Business analysts / low-code integration, enterprise connectors (SAP, Salesforce) | Simple pipelines where Dataflow templates suffice; cost sensitive (instance runs 24×7) |
| **Cloud Composer** | Managed **Apache Airflow** – DAG orchestration across services/clouds | Scheduling and dependency management of multi-step pipelines | Event-driven microservice chaining (use Workflows/Eventarc); simple cron (use Cloud Scheduler) |
| **Pub/Sub** | Global messaging: topics/subscriptions, push/pull/BigQuery & Cloud Storage subscriptions, ordering keys, dead-letter topics, filtering, schemas, seek/replay, 31-day max retention | Ingestion buffer, event fan-out, decoupling | Ordered global queue with strict FIFO across all messages; task rate control (Cloud Tasks) |
| **Datastream** | Serverless CDC (Oracle, MySQL, PostgreSQL, SQL Server, AlloyDB) → BigQuery / Cloud Storage / Spanner (via Dataflow) | Near-real-time replication for analytics; low-downtime migration | Full database lift (DMS) |
| **Eventarc** | Routes CloudEvents from Google services (via Audit Logs), Pub/Sub, and third-party sources to Cloud Run, Cloud Run functions, GKE, Workflows | Event-driven architectures on serverless | High-throughput streaming (Pub/Sub + Dataflow) |
| **Workflows** | Serverless orchestration of HTTP calls with state, retries, callbacks | Service chaining, long-running business flows | Data-heavy transformations |
| **Dataplex Universal Catalog / BigLake** | Data governance, discovery, lineage, quality, lakehouse tables over Cloud Storage | Governance requirements, data mesh | — |
| **Looker / Looker Studio** | BI semantic layer / free dashboards | Reporting layer on BigQuery | — |

Reference streaming architecture: **Pub/Sub → Dataflow → BigQuery (analytics) + Bigtable (serving)**, optionally Cloud Storage as raw archive. Reference batch: **Cloud Storage → Dataflow/Dataproc → BigQuery**, orchestrated by Composer.

> **Exam tip:** "Existing Spark jobs, minimal change, reduce cost" → Dataproc with ephemeral clusters, Cloud Storage instead of HDFS, Spot secondary workers, or Dataproc Serverless. "Handle late-arriving data with windowing" → Dataflow. "Non-programmers need to build pipelines" → Data Fusion. "Orchestrate a nightly chain of jobs with dependencies" → Composer.

## Networking

### VPC fundamentals

- A **VPC is global**; **subnets are regional** (span all zones in the region). Resources in different regions in one VPC talk over internal IPs across Google's backbone without VPN.
- **Auto mode** VPC creates a /20 subnet in every region (fine for demos, not production — convert to custom mode). **Custom mode** for production; subnets can have secondary ranges (GKE pods/services, alias IPs), and can be expanded (not shrunk) without downtime.
- **Routes**: system-generated subnet routes, default route to internet gateway, custom static routes, dynamic routes learned by **Cloud Router (BGP)**; dynamic routing mode **regional** (only advertise/learn routes for the Cloud Router's region) vs **global** (all regions — required for hybrid access to a whole VPC via one interconnect region). **Policy-based routes** steer traffic to internal passthrough NLB (NVA insertion).
- **Firewall rules** (VPC-level, stateful, implied deny-ingress/allow-egress, priority 0–65535, targets by tag or service account) vs **firewall policies** (hierarchical at org/folder, global/regional network policies, rules evaluated before VPC rules, support FQDN/geo/Threat Intelligence objects, address groups). **Cloud NGFW** adds Essentials/Standard/Enterprise tiers: Enterprise = TLS inspection + intrusion prevention (Palo Alto-powered).
- **VPC Flow Logs** (5-second sampling intervals), **Firewall Rules Logging**, **Packet Mirroring**, **Network Intelligence Center** (Connectivity Tests, Network Analyzer, Performance Dashboard, Topology) for troubleshooting.
- **Container networking**: GKE **VPC-native** clusters use alias IP ranges for pods (secondary ranges); pod IPs are routable in the VPC; **GKE Dataplane V2** (eBPF/Cilium) enables network policy and observability; private clusters have private node IPs and optional private control-plane endpoint; **Gateway API** for Ingress; Cloud Service Mesh for mTLS/L7 policy.

### Shared VPC vs VPC Network Peering vs Network Connectivity Center

| | **Shared VPC** | **VPC Network Peering** | **Network Connectivity Center (NCC)** |
|---|---|---|---|
| What | One host project owns the VPC; service projects attach and deploy resources into its subnets | Private RFC 1918 connectivity between two VPCs (same or different orgs) | Hub-and-spoke: VPC spokes, hybrid spokes (VPN, Interconnect, router appliances), Private Service Connect propagation |
| Admin model | Centralised network team, subnet-level IAM (`compute.networkUser`) | Each side configures peering; both must accept | Central hub admin; spokes can be in other projects |
| Transitivity | N/A (single VPC) | **Not transitive** (A↔B, B↔C ≠ A↔C) | **Transitive** among VPC spokes (full mesh via hub) |
| Limits | One host per service project; many service projects | Peering group limits (VMs, routes, ~25–50 peers per VPC) | Scales to hundreds of VPCs |
| Routes exchanged | Same VPC | Subnet routes automatic; custom routes optional import/export | Subnet routes; dynamic routes from hybrid spokes |
| Overlapping IPs | Not allowed within VPC | Not allowed | Not allowed (use PSC/NAT for overlapping) |
| Pick when | Single org, central control, need shared internal LBs/firewalls | Two teams/orgs need private connectivity, few VPCs | Many VPCs or mixed VPC + on-prem + multicloud with transitive routing |

### Private access options

| Option | Solves | Direction | Notes |
|---|---|---|---|
| **Private Google Access** | VMs **without external IPs** reach Google APIs (Cloud Storage, BigQuery…) | VPC → Google APIs | Per-subnet setting; on-prem via Interconnect/VPN using `private.googleapis.com` (199.36.153.8/30) or `restricted.googleapis.com` (199.36.153.4/30, VPC-SC-enforced) and DNS overrides |
| **Private Service Connect (PSC)** | Private, consumer-chosen internal IP for Google APIs (endpoint/backend), for **published services** of another producer VPC (SaaS, partners, your own services across VPCs), and for managed services (Cloud SQL, AlloyDB, Memorystore, Vertex AI) | Consumer → producer, no peering, no IP overlap issues | The modern answer for cross-VPC / cross-org service access; also PSC *interfaces* for producer→consumer; works with internal ALB for L7 |
| **Private Service Access (PSA)** | Google-managed services (Cloud SQL private IP, Memorystore, Filestore, Vertex AI legacy) hosted in a Google-owned VPC **peered** to yours | Peering | Requires allocating an IP range (`servicenetworking.googleapis.com`); inherits peering non-transitivity (on-prem needs custom route export) |
| **Serverless VPC Access / Direct VPC egress** | Cloud Run / Cloud Run functions / App Engine reach internal IPs in a VPC | Serverless → VPC | Direct VPC egress (no connector) is preferred for Cloud Run |
| **Cloud NAT** | Outbound internet for private VMs/GKE nodes/serverless | VPC → internet (egress only) | Regional, per-VPC-network, software-defined (no choke point), static IPs for allowlisting, logging; also **Private NAT** for NCC/hybrid overlapping ranges |
| **Identity-Aware Proxy TCP forwarding** | SSH/RDP to VMs without external IPs or bastions | Admin → VM | Allow 35.235.240.0/20 in firewall |

> **Trap:** Cloud NAT does not accept inbound connections and cannot be used across VPCs. PSA (peering) vs PSC (endpoint) — new managed-service connections should prefer **PSC**; questions mentioning "IP range exhaustion" or "transitive access from on-prem to Cloud SQL private IP" hint at PSC.

### Cloud Load Balancing family

| Load balancer | Layer | Scope | Front-end IP | Backends | Use when |
|---|---|---|---|---|---|
| **Global external Application LB** | L7 HTTP(S), HTTP/2, gRPC, WebSocket | Global (Premium tier); anycast single IP | External, anycast IPv4/IPv6 | MIGs, zonal/serverless/hybrid/internet NEGs, Cloud Storage buckets, in any region | Internet-facing web/API with global users; needs Cloud CDN, Cloud Armor, URL maps, managed certs, IAP |
| **Regional external Application LB** | L7 | Regional (works in Standard tier) | External regional | Same in-region backends | Regional compliance, Standard tier, or features only in Envoy-based regional LB |
| **Internal Application LB** (regional or cross-region) | L7 | Regional or cross-region internal | Internal RFC 1918 (proxy subnet required) | MIGs, NEGs, Cloud Run/PSC NEGs, hybrid | Internal microservices with path routing, header rewrites, traffic splitting |
| **Global / regional external proxy Network LB** | L4 TCP/SSL proxy (terminates at Google edge) | Global or regional | External anycast | Any region | Non-HTTP TCP (e.g., SMTP, custom protocols) needing global anycast, SSL offload, or client IP hidden (proxy protocol optional) |
| **Regional internal proxy Network LB** (also cross-region) | L4 TCP proxy | Regional/cross-region internal | Internal | MIGs, hybrid NEGs | Internal TCP services with proxying (e.g., to on-prem via hybrid NEG) |
| **External passthrough Network LB** | L4 (TCP/UDP/ESP/GRE/ICMP, all ports) | Regional | External regional IP (packets forwarded unmodified; client IP preserved) | Backend service with MIGs/instance groups or target pools | UDP/gaming/VoIP, non-proxied protocols, preserve client IP, DSR-style |
| **Internal passthrough Network LB** | L4 TCP/UDP | Regional (global access option for clients in other regions) | Internal | MIGs, zonal NEGs | Internal L4 services, database front-ends, **next hop for NVA/firewall appliances** |

Supporting facts:

- Only **proxy LBs** (Application and proxy Network) terminate connections; **passthrough** LBs preserve source IP and require backends to handle the LB IP.
- **Cloud CDN** attaches to external Application LBs (global/regional) — caches at edge, supports cache keys, signed URLs, negative caching, invalidation.
- **Cloud Armor** attaches to external Application LBs and external proxy Network LBs: WAF preconfigured rules (OWASP top 10: SQLi, XSS…), IP/geo allow/deny, rate limiting, adaptive protection (ML DDoS), bot management (reCAPTCHA); **Cloud Armor Enterprise** adds DDoS response and bill protection. Layer 3/4 DDoS protection is always-on for Google front ends.
- **Health checks** come from 35.191.0.0/16 and 130.211.0.0/22 — firewall must allow them.
- **Serverless NEGs** front Cloud Run / Cloud Run functions / App Engine; **hybrid NEGs** route to on-prem IPs over Interconnect/VPN; **internet NEGs** to external origins; **PSC NEGs** to published services.
- **Cloud DNS**: 100% SLA; public and private zones, **DNS peering**, forwarding zones (to on-prem), **routing policies** (weighted round robin, geolocation, failover with health checks for internal LBs), DNSSEC, Cloud Domains for registration. **Service Directory** for service registry.

> **Exam tip:** "Single anycast IP, users worldwide, HTTPS, need WAF and CDN" → global external Application LB. "UDP game traffic, preserve client IP" → external passthrough Network LB. "Route internal traffic through a firewall appliance" → internal passthrough NLB as next hop. "Load balance internal microservices with header-based routing" → internal Application LB.

### Hybrid and multicloud connectivity

| Option | Bandwidth | SLA | Encryption | Needs | Pick when |
|---|---|---|---|---|---|
| **Dedicated Interconnect** | **10 Gbps or 100 Gbps** per circuit; up to 8×10G or 2×100G per attachment bundle (LACP); VLAN attachments up to 50 Gbps each | **99.9%**: 2 connections in the **same metro** (different edge availability domains), VLAN attachments to Cloud Router(s) in one region. **99.99%**: 4 connections across **2 metros**, attachments to Cloud Routers in **2 regions**, **global dynamic routing** | Not by default (private fibre) — add MACsec (on 10/100G) or HA VPN over Interconnect | Presence in a Google colocation facility | Sustained high bandwidth, low latency, predictable costs, large migrations |
| **Partner Interconnect** | **50 Mbps – 50 Gbps** per VLAN attachment | 99.9% / 99.99% (same topology rules, via partner) | Not by default | Connection to a supported partner | No colo presence, need < 10 Gbps, faster provisioning |
| **Cross-Cloud Interconnect** | 10 or 100 Gbps dedicated links to AWS, Azure, OCI, Alibaba | 99.9% / 99.99% | Optional MACsec | Google-provided connections in partner clouds' colo | Multicloud with predictable bandwidth |
| **HA VPN** | ~3 Gbps per tunnel (sum of ingress+egress); add tunnels/ECMP | **99.99%** when 2 interfaces / ≥ 2 tunnels per interface to appropriately redundant peer (4 tunnels for two on-prem devices) | IPsec | Public IPs, BGP (Cloud Router) required | Fast start, encryption, backup for Interconnect, low/medium bandwidth |
| **Classic VPN** | ~3 Gbps per tunnel | 99.9% | IPsec | Static or BGP routing | Legacy only; deprecated for dynamic routing to on-prem — don't pick for new designs |
| **Direct / Carrier Peering** | Varies | None | None | Google edge presence | Only for reaching Google public services (Workspace, YouTube) — **not** for VPC access; distractor |
| **Network Connectivity Center** | — | — | — | — | Hub for many sites/VPCs, site-to-site transit over Google's backbone |

**Cloud Router / BGP facts:** Cloud Router is regional, exchanges routes over BGP with on-prem routers, supports **custom route advertisements**, **MED/priority** for active/passive tunnels, BFD for fast failover, and global dynamic routing mode to advertise all regions. HA VPN gateways have two interfaces with two external IPs; each tunnel needs a BGP session. Interconnect VLAN attachments each attach to one Cloud Router. For 99.99%, place Cloud Routers in **two regions** and enable **global dynamic routing**.

> **Remember:** HA VPN = 99.99% only with **two tunnels on both interfaces to redundant peers**; a single tunnel gets no SLA. Interconnect 99.99% = **four** connections, **two metros**, two Cloud Router regions. Encryption over Interconnect = HA VPN over Cloud Interconnect or MACsec.

> **Trap:** Bandwidth-heavy, latency-sensitive, "connect our data centre to Google Cloud for the next 5 years at 20 Gbps" → Dedicated Interconnect (2×10G), not VPN. "Need connectivity within a week and we are not in a colo" → Partner Interconnect or HA VPN. "Traffic must be encrypted over the Interconnect" → HA VPN over Interconnect or MACsec.

## AI/ML design (Vertex AI and Gemini)

### Platform overview

| Building block | What it is | Use when |
|---|---|---|
| **Vertex AI** | Unified ML platform: Workbench/Colab Enterprise notebooks, datasets, AutoML, custom training (containers, distributed, GPUs/TPUs), Pipelines (Kubeflow/TFX), Model Registry, Feature Store, online/batch prediction endpoints, Model Monitoring, Experiments, Vertex AI Studio | Any custom ML or generative AI workload where you want managed MLOps |
| **Gemini models** (Gemini 2.x Pro/Flash/Flash-Lite, plus Imagen, Veo, Chirp, embeddings) | Google's multimodal foundation models served via Vertex AI API; long context (up to 1–2 M tokens), function calling, grounding, JSON mode, context caching, batch prediction, provisioned throughput | Text/vision/audio/video understanding and generation, agents, code |
| **Model Garden** | Catalogue of Google, open (Gemma, Llama, Mistral…) and partner (Anthropic Claude…) models — deploy to endpoints, tune, or call as APIs | Need a specific open model, self-hosted weights on Vertex endpoints/GKE, or third-party model with Google Cloud billing/governance |
| **Vertex AI Agent Builder** (Agent Development Kit, Agent Engine runtime, Vertex AI Search, Conversational Agents/Dialogflow CX) | Build, deploy and govern agents; out-of-box enterprise search and RAG over websites, Cloud Storage, BigQuery, connectors | Enterprise search, chatbots/agents grounded in company data with minimal ML work |
| **Gemini Enterprise** | Enterprise agent platform / front door (formerly Agentspace) that unifies search, NotebookLM, prebuilt and custom agents across corporate data | Employee productivity assistants, knowledge search |
| **Vertex AI Vector Search** | Managed ANN vector index (ScaNN) for embeddings; also vectors in AlloyDB (pgvector/ScaNN), Spanner, BigQuery, Firestore, Memorystore | Semantic search, recommendations, RAG retrieval at scale |
| **Grounding** | Ground Gemini responses in Google Search, Vertex AI Search datastores, or your own retrieval | Reduce hallucination, cite sources, freshness |
| **AI Hypercomputer** | Integrated stack for large-scale AI: TPUs (v5e, v5p, v6e Trillium, Ironwood) and NVIDIA GPU supercomputers (A3/A4), high-bandwidth networking, Hyperdisk ML/Parallelstore, GKE/Slurm orchestration, Dynamic Workload Scheduler (Flex Start / Calendar mode), open frameworks (JAX, PyTorch, MaxText), Cluster Director | Training or serving very large models where consumption model (on-demand, Spot, DWS, CUD/reservations) and hardware choice matter |
| **Model Armor / Sensitive Data Protection** | Prompt & response screening (prompt injection, jailbreak, harmful content, data loss, malicious URLs) / PII discovery and de-identification | Securing generative AI apps (Section 3) |
| **Gemini Code Assist / Gemini Cloud Assist** | Developer coding assistant / console & operations assistant | Productivity; not runtime components |

### GPUs vs TPUs

| | GPUs (NVIDIA L4, A100, H100/H200, B200) | TPUs (v5e, v5p, Trillium v6e, Ironwood) |
|---|---|---|
| Frameworks | PyTorch, TensorFlow, JAX, CUDA ecosystem; broadest compatibility | JAX, TensorFlow, PyTorch/XLA; best for large matrix ops and transformers |
| Best for | Mixed workloads, custom kernels, inference of many model types, graphics/video (L4) | Very large-scale training/serving of LLMs with high throughput per dollar; pods with ICI interconnect |
| Where | Compute Engine A2/A3/A4/G2, GKE, Vertex AI, Cloud Run (L4), Dataflow | Compute Engine TPU VMs, GKE, Vertex AI |
| Exam signal | "CUDA", "existing PyTorch code", "video transcoding", "cost-effective inference" (L4) | "TensorFlow/JAX", "massive training run", "best price-performance for LLM training" |

Consumption models: on-demand, **Spot** (fault-tolerant training with checkpoints), **reservations** and CUDs (guaranteed capacity), **Dynamic Workload Scheduler** (queue for scarce accelerators; Flex Start for short jobs, Calendar for reserved future windows).

### Pre-trained APIs

| API | Does | Choose over Gemini when |
|---|---|---|
| **Cloud Vision** | Labels, OCR, faces, landmarks, safe search | Simple, high-volume classic vision at low cost |
| **Document AI** | Structured extraction from invoices, IDs, forms, contracts; pre-trained and custom processors | Document parsing with layout awareness and human-in-the-loop |
| **Video Intelligence** | Shot detection, labels, OCR, object tracking in video | Batch video cataloguing |
| **Speech-to-Text (Chirp)** / **Text-to-Speech** | ASR, TTS in 100+ languages | Call centres, captions, IVR |
| **Cloud Natural Language** | Entities, sentiment, syntax, classification | Simple text analytics at scale |
| **Cloud Translation** | Text translation (NMT and LLM-based), glossaries, AutoML translation | Deterministic bulk translation |
| **Vertex AI Search** | Enterprise search/RAG over your data | Search-driven apps without building retrieval |
| **Conversational Agents (Dialogflow CX)** / **Contact Center AI** | Deterministic + generative chat/voice bots | Customer service automation |
| **Recommendations AI (Vertex AI Search for retail)** | Product recommendations | Retail personalisation |

### Prompting vs tuning vs training

- **Prompt engineering / in-context learning** (system instructions, few-shot examples, long context, context caching) → *first choice*; zero training cost, immediate iteration.
- **RAG / grounding** → when answers must reflect **private, changing, or citable** data; retrieval from Vertex AI Search or Vector Search injects facts at request time; cheaper and fresher than tuning; use AlloyDB/BigQuery vectors when data already lives there.
- **Supervised fine-tuning / LoRA (parameter-efficient tuning)** on Gemini or open models → when you need consistent **style, format, or domain behaviour** that prompting cannot achieve, or to shrink prompts for latency/cost; requires labelled examples (hundreds to thousands); distillation to smaller models for cost.
- **RLHF / preference tuning** → align outputs to human preferences when you have preference data.
- **Training from scratch or continued pre-training** → only for truly novel domains/languages with massive data and budget (AI Hypercomputer); almost never the exam answer for an enterprise app.
- **Classic ML (AutoML / BigQuery ML / custom training)** → tabular prediction, forecasting, classification where an LLM is overkill; BigQuery ML when data is already in BigQuery and the team knows SQL.

> **Exam tip:** "Chatbot must answer from internal policy documents that change weekly" → RAG with Vertex AI Search / Agent Builder grounding — **not** fine-tuning. "Reduce hallucinations about recent events" → grounding with Google Search. "Model must not leak PII and must resist prompt injection" → Model Armor + Sensitive Data Protection. "Run open-weight Llama privately" → Model Garden deploy to Vertex endpoint or GKE with GPUs.

## Key takeaways

- Compute ladder: Cloud Run functions (events) → Cloud Run (stateless containers, scale to zero) → GKE Autopilot (Kubernetes, no nodes) → GKE Standard (node control) → Compute Engine (VMs) → VMware Engine / Bare Metal (special cases). Batch for HPC/batch on VMs.
- Machine families: E2 cheapest, N2/N4 balanced + custom shapes, C3/C4 compute-bound, M-series for SAP HANA/in-memory (up to 12 TB), A2/A3/A4 GPUs for training, G2/L4 for inference, T2D/T2A/C4A for scale-out price-performance.
- Spot: 60–91% off, 30 s reclaim notice, no SLA; sole-tenant for per-core BYOL; CUDs after rightsizing; flexible CUDs span families and serverless.
- Cloud Storage min durations 0/30/90/365 days (Standard/Nearline/Coldline/Archive); all classes ms latency and 11 nines durability; Autoclass for unknown access patterns, lifecycle rules for known ones; bucket lock = WORM; dual-region turbo replication = 15-min RPO.
- Block: pd-balanced default, Hyperdisk for new high-performance/decoupled IOPS, regional PD/Hyperdisk HA for cross-zone sync, Local SSD is ephemeral. Filestore = NFS (Regional tier for 99.99%), NetApp Volumes = SMB + NFS.
- Databases: Cloud SQL (regional relational), AlloyDB (high-performance PostgreSQL), Spanner (global relational, 99.999%), Bigtable (wide-column, ms, PB, no joins), Firestore (documents, mobile, 99.999% multi-region), Memorystore (sub-ms cache), BigQuery (analytics).
- Data processing: Dataflow (Beam, batch+stream, serverless), Dataproc (Spark/Hadoop lift), Data Fusion (no-code ETL), Composer (Airflow orchestration), Pub/Sub (ingest/decouple), Datastream (CDC), Eventarc (event routing to serverless).
- VPC is global, subnets regional; firewall policies (hierarchical) evaluate before VPC rules; Cloud Router BGP with global dynamic routing for multi-region hybrid.
- Shared VPC = central control in one VPC; peering = non-transitive pairwise; NCC = transitive hub-and-spoke at scale. PSC is the modern private-connectivity answer; PSA is the peering-based legacy for Cloud SQL private IP; Private Google Access for API access from private VMs.
- Load balancers: global external ALB (L7, anycast, CDN, Armor), regional external/internal ALB (L7 Envoy), proxy NLBs (L4 TCP/SSL, terminate), passthrough NLBs (L4, preserve client IP, UDP, NVA next hop).
- Hybrid: Dedicated 10/100 Gbps, Partner 50 Mbps–50 Gbps, Cross-Cloud Interconnect to other clouds, HA VPN 99.99% (2 interfaces/4 tunnels), Classic VPN 99.9%; 99.99% Interconnect needs 4 links in 2 metros; encrypt with MACsec or HA VPN over Interconnect.
- AI: Gemini models via Vertex AI; Model Garden for open/partner models; Agent Builder + Vertex AI Search for RAG and agents; AI Hypercomputer (TPUs/GPUs + DWS) for large training; prefer prompting → RAG → tuning → training in that order; secure with Model Armor and Sensitive Data Protection.

## Quick self-check

- Q: A containerised REST API has unpredictable traffic that is zero at night; the team wants no infrastructure management. Which platform? — **A:** Cloud Run (scale to zero, per-request billing).
- Q: Which Cloud Storage class has a 90-day minimum storage duration? — **A:** Coldline (Nearline 30, Archive 365, Standard none).
- Q: Two VPCs are peered with a third; can VPC A reach VPC C through B? — **A:** No — peering is not transitive; use NCC (VPC spokes) or Shared VPC.
- Q: You need to load balance UDP traffic and preserve the client source IP. Which LB? — **A:** External passthrough Network Load Balancer.
- Q: Requirement: 99.99% SLA on a VPN to on-prem. Minimum topology? — **A:** HA VPN gateway with both interfaces used and two tunnels per interface (four tunnels) to redundant on-prem gateways, BGP via Cloud Router.
- Q: Which database for IoT telemetry at 1 million writes/second with single-digit-ms reads by device ID and time? — **A:** Bigtable (row key = device ID + reversed timestamp).
- Q: Which service turns a Spark job estate into a lower-cost managed deployment with minimal code changes? — **A:** Dataproc (ephemeral clusters, Cloud Storage connector, Spot secondary workers) or Dataproc Serverless.
- Q: Internal support bot must answer from documents updated daily and cite them. Fine-tune or RAG? — **A:** RAG/grounding with Vertex AI Search (Agent Builder); fine-tuning does not keep up with changing content and does not cite sources.
