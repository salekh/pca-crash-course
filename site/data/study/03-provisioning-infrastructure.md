Section 2 is ~17.5% of the exam. Section 1 asks *which* service; Section 2 asks *how you configure it* — which flag, which range, which topology, which limit. Questions are short scenario stems ("the team needs X with constraint Y; what should you configure?"). This module is organized by the five blueprint sub-objectives.

## 2.1 Configuring network topologies

### Hybrid connectivity: pick the pipe

| Option | Bandwidth | SLA | Use when | Avoid when |
|---|---|---|---|---|
| **Dedicated Interconnect** | 10 Gbps or 100 Gbps circuits (multiple per attachment) | 99.9% (2 links, 1 metro) / 99.99% (4 links, 2 metros, 2 regions) | High, steady throughput; you can reach a Google colocation facility | Small/bursty traffic; no colo presence |
| **Partner Interconnect** | 50 Mbps – 50 Gbps per VLAN attachment | Same 99.9/99.99% topologies (partner SLA separate) | Need private connectivity but no colo, or < 10 Gbps | You need > 50 Gbps per attachment |
| **Cross-Cloud Interconnect** | 10 or 100 Gbps | Same as Dedicated | Private L2/L3 link Google ↔ AWS/Azure/OCI/Alibaba | Only need occasional cloud-to-cloud transfer |
| **HA VPN** | ~3 Gbps per tunnel (sum of ingress + egress), add tunnels to scale | 99.99% with 2 tunnels to both interfaces | Encrypted traffic over the internet; Interconnect backup; quick start | Consistent multi-Gbps need |
| **Classic VPN** | ~3 Gbps per tunnel | 99.9% | Legacy only | Any new design (deprecated for dynamic routing) |

- **Interconnect + VPN backup** is the canonical exam pattern: same Cloud Router, BGP on both; set the VPN route advertisement with a *worse* MED (higher value = lower priority) so the Interconnect path is preferred, and the VPN takes over automatically when BGP on the Interconnect drops.
- **HA VPN topologies**: HA VPN gateway has two interfaces. For 99.99% you need tunnels from *both* interfaces to peer devices (2 tunnels to a single peer with two IPs, or 4 tunnels to two peers). HA VPN to HA VPN between two VPCs (e.g., two Google Cloud orgs, or overlapping-CIDR workarounds) is supported.
- **Cloud Router** does BGP; without it you have static routes only (Classic VPN). Key knobs:
  - **Custom route advertisements** — advertise only specific subnets, or add the `199.36.153.4/30` restricted VIP so on-prem can reach Google APIs via Interconnect.
  - **Dynamic routing mode** on the VPC: *regional* (routes learned only in the Cloud Router's region) vs **global** (all regions learn on-prem routes and vice versa). Global mode is what you set to let a single Interconnect serve multi-region VPC subnets.
  - **BGP MED / base priority** to prefer one link; **BFD** for sub-second failure detection.
  - Partner Interconnect always uses Google ASN **16550**.
- **Interconnect for API access**: Interconnect does not carry public internet traffic. To reach Google APIs on-prem, resolve `*.googleapis.com` to `private.googleapis.com` (199.36.153.8/30) or `restricted.googleapis.com` (199.36.153.4/30) and advertise that range via Cloud Router.

> **Exam tip:** "Encrypt traffic over Interconnect" → **HA VPN over Cloud Interconnect** (tunnels ride the VLAN attachment) or **MACsec for Cloud Interconnect** on 10/100 Gbps Dedicated links.

### Network Connectivity Center (NCC)

NCC is a **hub-and-spoke** model. Spokes can be VLAN attachments, HA VPN tunnels, Router appliances (third-party SD-WAN VMs), or **VPC spokes**. Two exam uses:

1. **Site-to-site data transfer**: use Google's backbone to route between two on-prem sites (branch A ↔ branch B through Google).
2. **VPC spokes**: full-mesh connectivity between many VPCs *without* the non-transitivity problems of peering. This is the modern answer for "dozens of VPCs need to talk to each other and on-prem".

### VPC design fundamentals

- VPCs are **global**; subnets are **regional**; a subnet can span all zones in its region. Firewall rules and routes are VPC-wide.
- **CIDR planning**: primary ranges from RFC 1918 (also 100.64.0.0/10 and privately-used public ranges are allowed); subnets cannot overlap within a VPC or with peered VPCs. Reserve four addresses per subnet (network, gateway, second-to-last, broadcast). Subnets can be **expanded** (never shrunk) without downtime.
- **Secondary ranges** are for **alias IPs** — required for VPC-native GKE: one range for **Pods** (default gives each node a /24 = up to 110 Pods), one for **Services**. Size Pod ranges for the *maximum* node count; you can add additional Pod ranges to an existing cluster but not resize.
- **Shared VPC**: host project owns the network; service projects attach.

| Role | Granted at | Lets you |
|---|---|---|
| `roles/compute.xpnAdmin` (Shared VPC Admin) | Org or folder | Enable host projects, attach service projects |
| `roles/compute.networkAdmin` | Host project | Create/modify subnets, routes, firewall rules |
| `roles/compute.securityAdmin` | Host project | Firewall rules & SSL certs |
| `roles/compute.networkUser` | Host project or **individual subnet** | Service-project developers create resources in that subnet |
| Service Project Admin (e.g., `roles/compute.instanceAdmin`) | Service project | Create VMs that use shared subnets (still needs networkUser) |

> **Remember:** Grant `compute.networkUser` at the *subnet* level to give team A only subnet A. GKE in a service project also needs the **GKE service agent** of the service project granted `roles/container.hostServiceAgentUser` and `networkUser` in the host project.

- **VPC Network Peering**: private RFC 1918 connectivity between two VPCs (same or different orgs), no single point of failure, no bandwidth bottleneck. Constraints: **non-transitive** (A↔B and B↔C does *not* give A↔C), no overlapping CIDRs, a per-network limit on the number of peerings (default ~25, increasable) and on total subnet/route counts in the peering group. Custom route exchange (import/export) must be enabled explicitly; on-prem routes learned via Cloud Router *can* be exported to peers if you export custom routes.
- **Private services access** is VPC peering with a Google-managed producer VPC (Cloud SQL, Memorystore, Filestore, Vertex AI legacy private endpoints). It needs an **allocated IP range** (recommend at least /16 for Cloud SQL) and inherits peering non-transitivity — on-prem can reach Cloud SQL only if you export custom routes and advertise the allocated range.
- **Private Service Connect (PSC)** replaces peering for producer/consumer patterns:
  - **PSC endpoints** (consumer side): an internal IP in *your* subnet forwarding to a published service or to Google APIs (`all-apis` or `vpc-sc` bundle). No route exchange, no CIDR overlap issue, transitive from on-prem.
  - **PSC backends**: a PSC **NEG** behind *your own* load balancer, so you can front a producer service with Cloud Armor, your own certificates, and URL maps.
  - **Published services** (producer side): expose an internal load balancer through a **service attachment** with consumer accept lists; NAT subnet on the producer side.
  - Managed services increasingly default to PSC: Cloud SQL, AlloyDB, Memorystore, Vertex AI online prediction, Apigee.
- **Private Google Access** (subnet flag) lets VMs *without* external IPs reach Google APIs. `private.googleapis.com` = all APIs; `restricted.googleapis.com` = only APIs that support **VPC Service Controls** (used inside perimeters).
- **Cloud NAT**: regional, managed egress-only NAT for VMs/GKE without external IPs; configure per subnet or per-cluster; **static NAT IPs** for allow-listing by partners; **Private NAT** for NCC/inter-VPC overlapping ranges. Watch port allocation (default 64 ports/VM; enable dynamic port allocation).

### Security protection at the network layer

**Firewall constructs and evaluation order** (default enforcement order):

1. **Hierarchical firewall policies** — org and folder level; rules can `allow`, `deny`, or `goto_next` (delegate); attached to org/folders; stateful.
2. **Global network firewall policies** (VPC level, global rules).
3. **Regional network firewall policies**.
4. **VPC firewall rules** (legacy per-rule model).
5. Implied rules: allow all egress, **deny all ingress** at priority 65535.

Within each level, lower priority number wins (0–65535). Network policies vs VPC rules order can be swapped with `--network-firewall-policy-enforcement-order`. Target by **network tags**, **service accounts** (preferred — tags are editable by instance admins), or **secure tags** (IAM-governed, work across hierarchy and Shared VPC).

| Cloud NGFW tier | Adds | Typical exam trigger |
|---|---|---|
| **Essentials** | Firewall policies, secure tags, address groups, firewall rules logging | Baseline segmentation |
| **Standard** | FQDN objects, geolocation objects, Google Threat Intelligence lists | "Block traffic from country X" / "allow only to specific domains" |
| **Enterprise** | **Intrusion prevention (IPS)** with Palo Alto signatures, **TLS inspection**, firewall endpoints per zone | "Inspect and *block* malware/exploits inline" |

- **Firewall Rules Logging** must be enabled per rule/policy; logs go to Cloud Logging (not enabled by default, costs money). **VPC Flow Logs** are per-subnet samples of flows (5-second aggregation default), used for forensics, cost analysis, and network topology.
- **Cloud IDS**: managed **detection-only** IDS (Palo Alto threat signatures) using **Packet Mirroring** to an IDS endpoint per zone/region. It alerts to Cloud Logging/SCC but does not block. For blocking → Cloud NGFW Enterprise.
- **Cloud Armor**: attaches **security policies** to *backend services* of global external Application LBs, classic ALB, external proxy NLBs, and regional external ALBs. Features: IP/CIDR allow-deny, geo rules, custom rules in CEL, **preconfigured WAF rules** (ModSecurity CRS 3.3 signatures: `sqli`, `xss`, `lfi`, `rfi`, `rce`, `scannerdetection`, `protocolattack`, `sessionfixation`, `cve-canary` for Log4j), **rate limiting** (`throttle` and `rate-based-ban` keyed on IP, header, cookie, region), **Adaptive Protection** (ML detection of L7 DDoS with suggested rules — Enterprise tier), **bot management** with reCAPTCHA tokens, and **edge security policies** for Cloud CDN/backend buckets. Cloud Armor Enterprise adds DDoS response support and bill protection.
- **DDoS**: L3/L4 volumetric protection is *always on* for Google front ends (passthrough NLBs get basic protection too). L7 protection requires a proxy LB + Cloud Armor. Preview mode lets you log what a rule *would* do.

> **Trap:** Cloud Armor cannot attach to an internal load balancer or a passthrough network LB. If the stem says "internal service, needs WAF" the answer is usually an internal ALB with a third-party WAF, or re-architecting behind a global external ALB with IAP.

### Load balancer selection and configuration

| LB | Layer | Scope | Tier | Backends | Key facts |
|---|---|---|---|---|---|
| Global external ALB | L7 HTTP(S) | Global anycast IP | Premium | MIGs, zonal/serverless/hybrid/internet/PSC NEGs, buckets | Cloud Armor, CDN, IAP, URL maps, Google-managed certs |
| Regional external ALB | L7 | Regional | Standard OK | Same (regional) | Data residency; Cloud Armor supported |
| Internal ALB (regional / cross-region) | L7 | Internal, proxy-only subnet needed | n/a | MIGs, NEGs | Cross-region ILB = global internal access with failover |
| External proxy NLB (global/regional) | L4 TCP/SSL | Global or regional | Premium/Standard | MIGs, NEGs | Terminates TCP/SSL at proxy; client IP via PROXY protocol |
| Internal proxy NLB | L4 TCP | Regional / cross-region | n/a | MIGs, hybrid NEGs | TCP to on-prem via hybrid NEG |
| External passthrough NLB | L4 TCP/UDP/ESP/ICMP | Regional | Standard/Premium | MIGs, zonal NEGs | Preserves client IP; no proxy; backend service or target pool |
| Internal passthrough NLB | L4 | Regional | n/a | MIGs, zonal NEGs | Next-hop for routes (NVA HA), global access flag |

- **Proxy-based** LBs require a **proxy-only subnet** (internal ALB/proxy NLB, regional external ALB) and source traffic from health-check + proxy ranges; **passthrough** LBs deliver the original client IP to the backend.
- **Health checks** originate from **35.191.0.0/16** and **130.211.0.0/22**; your firewall must allow these to backends (for internal passthrough NLB also 209.85.152.0/22 and 209.85.204.0/22 for legacy checks). Health check protocol, port, interval, healthy/unhealthy thresholds are on the health check object; MIG **autohealing** can reuse the same health check object with a different threshold.
- **Backend service** holds: balancing mode (UTILIZATION, RATE, CONNECTION), capacity scaler, **session affinity** (client IP, generated cookie, header, HTTP cookie, stateful cookie), connection draining timeout, timeouts, Cloud CDN, IAP, Cloud Armor policy, logging sample rate, **outlier detection**, locality LB policy.
- **NEG types**: **zonal** (`GCE_VM_IP_PORT` for container-native LB — traffic straight to Pod IPs, or `GCE_VM_IP` for passthrough), **serverless** (Cloud Run / functions / App Engine; per region), **internet** (external FQDN/IP origin, e.g., on-prem public endpoint or third-party API behind the ALB), **hybrid** (`NON_GCP_PRIVATE_IP_PORT` — on-prem IPs reachable via Interconnect/VPN), **PSC** (a published service or Google API as backend), and **Private Service Connect NEG** for regional producers.
- **URL maps**: host and path rules, route rules (header/query match), URL rewrites, redirects, traffic splitting by weight (canary), default service. Backend buckets serve static content from Cloud Storage.
- **Certificates**: classic **Google-managed SSL certs** (up to 100 domains each, ~15 per target proxy, no wildcards, require load-balancer authorization) vs **Certificate Manager** (wildcards via DNS authorization, certificate maps at scale, self-managed uploads, CA Service integration, regional certs). SSL policies set minimum TLS version and cipher profile. Backend can use HTTP/2, gRPC, or HTTP; frontends support QUIC/HTTP/3 on global external ALB.
- **Network Service Tiers**: Premium = global anycast, cold-potato routing, required for global LBs; Standard = regional egress via ISPs, cheaper.

### Cloud DNS

| Zone type | Purpose |
|---|---|
| Public zone | Internet-facing authoritative DNS (100% SLA), DNSSEC support |
| Private zone | Names visible only to authorized VPCs |
| **Forwarding zone** | Send queries for a domain to on-prem DNS servers (queries originate from **35.199.192.0/19** — allow it on-prem and return via same path) |
| **Peering zone** | Let VPC A resolve using VPC B's private zones/forwarding (transitive-ish DNS without network peering) |
| Managed reverse lookup | PTR for non-RFC1918 |

- **Inbound server policy**: on-prem resolves Google Cloud private names via an inbound forwarder IP in each subnet region. **Outbound server policy**: send *all* VPC queries to alternative name servers.
- **Routing policies**: **weighted round robin** (canary), **geolocation** (nearest region), **failover** (primary/backup; primary health is derived from internal passthrough NLB / internal ALB health checks). DNS failover is the standard "active/passive across regions for internal apps" answer when a cross-region internal ALB isn't in play.
- Cloud Domains for registration; DNS peering to a hub VPC is a common Shared VPC pattern.

> **Exam tip:** "Zonal outage should not take down the app" → regional MIG behind an LB; "regional outage" → multi-region backends behind a **global** external ALB (single anycast IP, automatic failover based on capacity/health) or cross-region internal ALB for internal traffic.

## 2.2 Configuring individual storage systems

### Block storage allocation and sizing

- **Persistent Disk** types: `pd-standard` (HDD), `pd-balanced`, `pd-ssd`, `pd-extreme` (provisioned IOPS). **IOPS/throughput scale with disk size** and, for smaller VMs, with vCPU count — an under-performing 100 GB pd-standard is fixed by making it bigger or switching type, not by adding VMs. Max 64 TB per disk; disks can be resized *up* online.
- **Hyperdisk** (newer machine series: C3, N4, M3, A3, etc.): performance **decoupled from capacity** — provision IOPS/throughput independently. Variants: **Balanced** (general), **Extreme** (max IOPS, databases), **Throughput** (HDD-priced streaming/Hadoop), **ML** (read-only shared across many VMs for model weights), **Balanced High Availability** (synchronous cross-zone). Storage pools let you thin-provision capacity/performance across disks.
- **Regional PD / Hyperdisk Balanced HA**: synchronous replication across two zones in one region; on zone failure **force-attach** to a VM in the other zone (RPO 0, RTO minutes). Used for HA databases on VMs (e.g., SQL Server FCI, SAP).
- **Local SSD**: 375 GB units (or 3 TB on newer series), NVMe, highest IOPS, **ephemeral** — data lost on stop/host error; use for scratch/cache only.
- **Snapshots**: incremental, globally usable, stored in multi-regional or regional locations; **snapshot schedules** (resource policy attached to disks: hourly/daily/weekly, retention days, delete behavior). **Instant snapshots** for fast in-zone recovery; **archive snapshots** for cheap long-term retention. Machine images capture full VM (all disks + metadata); custom images from disks/snapshots for golden images, with image families and deprecation states.
- **Filestore** tiers: Basic HDD/SSD (zonal, 1–63.9 TB), **Zonal** (high performance), **Regional** (99.99%, synchronous across zones), **Enterprise**. NFSv3/v4.1; use for lift-and-shift shared POSIX file systems and GKE `ReadWriteMany`. For HPC/AI: **Parallelstore** / **Managed Lustre**.

### Cloud Storage configuration

| Setting | What to know |
|---|---|
| Storage classes | Standard (no minimum), **Nearline 30 days**, **Coldline 90 days**, **Archive 365 days** minimum storage duration; retrieval fees rise as class gets colder; all classes have millisecond access |
| **Autoclass** | Bucket-level automatic transitions based on access; no retrieval or early-deletion fees; ideal when access pattern is unknown |
| Location | Region, dual-region (predefined pairs or custom), multi-region; dual-region gives 99.95% availability SLA with RPO ≈ 15 min via **turbo replication** (otherwise "typically within an hour", no SLA) |
| **Uniform bucket-level access** | Disables object ACLs; IAM only; required for IAM conditions and recommended everywhere. Becomes permanent after 90 days |
| **Public access prevention** | Bucket or org policy (`storage.publicAccessPrevention`) |
| **Signed URLs** | Time-limited access without a Google identity; V4 signing max **7 days**; signed by a service account key or via `iam.serviceAccounts.signBlob` (no key download). **Signed policy documents** for browser uploads |
| **CORS** | JSON config on bucket for browser-side cross-origin GET/PUT |
| **Object versioning** | Keeps noncurrent versions; combine with lifecycle `numNewerVersions`/`daysSinceNoncurrentTime` |
| **Soft delete** | Default 7-day retention of deleted objects (configurable 0–90 days); restores via `gcloud storage restore` |
| **Retention policy / Bucket Lock** | Retention period up to 100 years; **locking is irreversible**; objects can't be deleted/overwritten until age ≥ period; WORM for SEC 17a-4/FINRA. **Object holds** (event-based/temporary) for legal holds; **object retention lock** for per-object retention |
| Lifecycle rules | Actions: `Delete`, `SetStorageClass`, `AbortIncompleteMultipartUpload`. Conditions: `age`, `createdBefore`, `isLive`, `numNewerVersions`, `matchesStorageClass`, `daysSinceCustomTime`, `matchesPrefix/Suffix`. Evaluated roughly daily; rules are OR'd, conditions within a rule AND'd |
| Encryption | Google-managed default; CMEK (default key per bucket); CSEK per object |
| Access logs | Cloud Audit Logs data access (recommended) or legacy usage logs to a bucket |
| Requester pays | Consumer's project billed for egress/ops |

Example lifecycle JSON the exam may show:

```json
{"rule": [
  {"action": {"type": "SetStorageClass", "storageClass": "NEARLINE"}, "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}},
  {"action": {"type": "Delete"}, "condition": {"age": 365, "isLive": false}}
]}
```

> **Trap:** Moving objects to Coldline and deleting them 20 days later incurs the *90-day minimum* charge. Match the class to the *actual* retention window; when unsure, Autoclass.

### Data transfer and latency

| Tool | Use when |
|---|---|
| `gcloud storage cp/rsync` | Ad hoc; parallel by default; automatic parallel composite uploads for large files |
| **Storage Transfer Service** | Scheduled/recurring transfers from S3, Azure Blob, HTTP(S) lists, other buckets, or **on-prem POSIX file systems via transfer agents**; bandwidth limits; event-driven transfers; metadata preservation |
| **Transfer Appliance** | Physical device (TA7 ~7 TB, TA40 ~40 TB, TA300 ~300 TB usable); rule of thumb: > ~1 week of online transfer, or > 10s of TB on limited bandwidth |
| **BigQuery Data Transfer Service** | SaaS sources (Google Ads, YouTube), S3/Redshift/Teradata → BigQuery |
| **Database Migration Service** | Homogeneous and heterogeneous DB migrations (MySQL/PostgreSQL/SQL Server/Oracle → Cloud SQL/AlloyDB) with CDC |
| Datastream | CDC replication to BigQuery/Cloud Storage/AlloyDB |

Quick math: 1 Gbps ≈ 10 TB/day at ~100% utilization; 100 TB over 100 Mbps ≈ 3 months → appliance. Reduce latency for global readers with **Cloud CDN** (cache modes, signed cookies/URLs, cache keys) or multi-region buckets; for hot regional data, keep bucket and compute in the *same region* to avoid egress and add latency.

### Data growth planning by database

| Service | Scaling levers | Limits & numbers to remember |
|---|---|---|
| **Cloud SQL** | **Automatic storage increase** (grows, never shrinks), vertical resize (restart), up to ~8–10 **read replicas** (cross-region allowed, cascading), **Enterprise Plus** edition: 99.99% SLA, near-zero-downtime maintenance (< 1 s for planned ops), data cache (local SSD), 35-day PITR retention | 64 TB storage; single-writer; HA = synchronous regional standby (failover ~60 s) |
| **Spanner** | **Processing units** (100 PU granularity; 1,000 PU = 1 node), **managed autoscaler** on CPU/storage, horizontal splits; regional 99.99%, multi-region 99.999% | ~10 TB storage per node; keep CPU < 65% (regional) / 45% (multi-region); avoid hotspot keys (UUIDs not sequences) |
| **Bigtable** | Add nodes per cluster, **autoscaling** on CPU + storage utilization, up to 8 replicated clusters, app profiles for routing | SSD ~5 TB/node, HDD ~16 TB/node; keep below ~60% storage for latency; single-row transactions; multi-cluster routing = 99.999% |
| **BigQuery** | Storage is serverless; compute via **editions** (Standard/Enterprise/Enterprise Plus) with slot autoscaling and baseline slots, or **on-demand** ($/TB scanned, default 2,000-slot quota) | **Partitioning** (ingestion time, date/timestamp, integer range; up to 10,000 partitions; expiration per partition) + **clustering** (up to 4 columns) cut scan cost; **long-term storage** price (~50% off) after 90 days without modification; time travel 2–7 days + 7-day fail-safe; require partition filter |
| **AlloyDB** | Read pool instances, columnar engine, primary vertical scale; 99.99% SLA incl. maintenance | PostgreSQL-compatible; storage scales automatically |
| **Firestore** | Automatic; multi-region 99.999% | 1 write/sec per document guidance, 10 MiB doc limit |
| **Memorystore** | Redis Cluster horizontal scale, read replicas; Valkey/Redis/Memcached | Ephemeral: plan RDB snapshots/AOF for Redis if persistence matters |

### Data protection (backup & recovery)

| Service | Backup mechanism | PITR | Cross-region |
|---|---|---|---|
| Cloud SQL | Automated daily backups (retain 1–365, default 7) + on-demand; backups can be stored in a custom location | Yes, via binary logs/WAL: 7 days (Enterprise) / up to 35 days (Enterprise Plus) | Cross-region read replica; promote for DR; backups multi-regional by default |
| Spanner | Backups retained up to **1 year**, copyable to other regions/projects; scheduled backups | **Version retention up to 7 days** (`version_retention_period`, default 1 h) using stale reads/`RESTORE` | Multi-region configs already replicated |
| Bigtable | Table backups retained up to **90 days**; restore into any instance/project | No (use replication) | Copy backups across regions |
| Firestore | Scheduled daily/weekly backups (retain up to 14 weeks); export to GCS | **PITR 7 days** | Multi-region location |
| BigQuery | Time travel + snapshots + cross-region dataset replication; table clones | 2–7 days time travel | Dataset replicas |
| Compute Engine | Snapshot schedules, machine images; **Backup and DR Service** for application-consistent backups | Snapshot granularity | Snapshots multi-regional |
| GKE | **Backup for GKE**: backup plans per cluster, scoped by namespace/protected app, includes PVs; restore to other cluster/region | Schedule | Yes |
| Cloud Storage | Versioning, soft delete, dual/multi-region, Storage Transfer to second bucket | n/a | Turbo replication |

**Backup and DR Service** = Google's managed Actifio: agent-based, application-consistent backups for VMs, databases (SQL Server, Oracle, SAP HANA), VMware Engine and file systems; **backup vaults** provide immutable, indelible storage with minimum enforced retention (ransomware resilience); mount-and-migrate instant recovery. Tie RPO/RTO to mechanism: snapshots/hourly backups (RPO 1 h), replicas (RPO seconds), multi-region synchronous (RPO 0).

> **Exam tip:** "Restore the table to the state 3 hours ago after a bad UPDATE" → Spanner: stale read at timestamp within version retention; BigQuery: `FOR SYSTEM_TIME AS OF`; Cloud SQL: PITR clone to new instance; Firestore: PITR read/export.

## 2.3 Configuring compute systems

### Compute Engine provisioning

- **Machine families**: E2 (cost-optimized, shared-core options), N2/N2D/N4/C3/C3D/C4 (general/compute), M1/M2/M3 (memory-optimized up to ~12 TB for SAP HANA), H3 (HPC), A2/A3/A4 (GPU), Z3 (storage-optimized). **Custom machine types** for odd shapes; **extended memory** beyond ratio.
- **Instance templates** are immutable; **MIGs** create identical VMs from a template. **Regional MIGs** spread across ≥3 zones (recommended) for zonal-failure resilience; target distribution shape EVEN/BALANCED/ANY.
- **Autoscaling policies**: CPU utilization, LB serving capacity (utilization or RPS), Cloud Monitoring metrics (per-instance or per-group, e.g., Pub/Sub backlog), **schedules**, **predictive autoscaling** (CPU history). Knobs: min/max replicas, **initialization (cool-down) period** (default 60 s), 10-minute **stabilization window** for scale-in, scale-in controls (max instances removed per window).
- **Autohealing**: application health check + initial delay; recreates VMs that fail (different from LB health check removing traffic).
- **Update policies** (rolling updates): `--type=proactive|opportunistic`, `--max-surge` (extra VMs, cost), `--max-unavailable` (capacity dip), `--minimal-action=refresh|restart|replace`, `--replacement-method=substitute|recreate` (recreate preserves names/stateful). **Canary**: set a second template with a fixed `--canary-version` target size (e.g., 10%), then promote. **Stateful MIGs** preserve disks/IPs/metadata per instance (databases, Kafka, ZooKeeper).
- **Spot VMs**: 60–91% discount, no SLA, can be preempted any time (no 24-hour cap unlike legacy preemptible), **30-second** ACPI shutdown notice → run a shutdown script to checkpoint; excluded from live migration; use for batch, CI, fault-tolerant workers, GKE spot node pools (with taints/tolerations) and Dataproc secondary workers. Handle preemption with checkpointing, idempotent tasks, MIG auto-recreate, and mixing Spot with on-demand.
- **Sole-tenant nodes**: dedicated hosts for BYOL per-core licensing (Windows Server, SQL Server), compliance isolation; support node affinity and CPU overcommit.
- **Reservations**: zonal capacity guarantees (on-demand price; combine with CUDs), shared reservations across projects, **future reservations** for planned large launches or GPU/TPU capacity; **Dynamic Workload Scheduler** for accelerators (below).
- **Committed use discounts**: resource-based (vCPU/memory per region, 1 or 3 years) and **flexible spend-based CUDs** (dollar/hour across families, Cloud Run, GKE Autopilot, Cloud SQL, etc.). Sustained-use discounts apply automatically to N1/N2 style families but not to E2 or newer series.
- **VM Manager (OS Config)**: OS inventory, **patch management** (patch jobs and scheduled patch deployments with maintenance windows, pre/post scripts, reboot config), **OS policies** for desired-state config (packages, repos, files). Requires OS Config agent + metadata `enable-osconfig=TRUE` + service account.
- **Shielded VMs**: Secure Boot, vTPM, measured boot integrity monitoring (org policy `compute.requireShieldedVm`). **Confidential VMs**: memory encryption in use via AMD SEV/SEV-SNP (N2D, C2D, C3D) or Intel TDX (C3); Confidential GKE Nodes; **Confidential Space** for multi-party computation with attestation. Live migration supported for SEV.
- **Startup/shutdown scripts and metadata**; **OS Login** for IAM-managed SSH; **guest attributes** for status.
- **Google Cloud VMware Engine**: fully managed vSphere/vSAN/NSX-T private clouds (3-node minimum production, single-node pilot), stretched clusters, connected to VPC via private services access — lift-and-shift VMware estates without refactoring, then modernize.

### GKE configuration

| Aspect | **Autopilot** | **Standard** |
|---|---|---|
| Node management | Google provisions/scales/patches nodes; you pay per Pod requests (vCPU/memory/ephemeral) | You manage node pools; pay per node |
| Defaults | VPC-native, Workload Identity, Shielded + Secure Boot, hardened, regional only | You choose; zonal or regional |
| Constraints | No privileged Pods (limited), no SSH to nodes, curated DaemonSets, compute classes (Balanced, Scale-Out, Performance, Accelerator) | Full flexibility, custom node images, local SSD, sole-tenant |
| Autoscaling | Automatic (Pod-driven) | Cluster Autoscaler + **Node Auto-Provisioning (NAP)** creates pools by shape |
| SLA | 99.95% control plane; 99.9% Pods across zones | 99.95% regional / 99.5% zonal control plane |

- **Networking**: VPC-native (alias IP) is required; **container-native load balancing** with `GCE_VM_IP_PORT` NEGs (annotation `cloud.google.com/neg: '{"ingress": true}'`), **Dataplane V2** (Cilium/eBPF) for network policy and observability, **Gateway API** (`gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, `gke-l7-rilb`, `gke-l7-cross-regional-internal-managed`) replacing Ingress for L7; multi-cluster Gateway via fleets.
- **Private clusters**: nodes without external IPs, control plane private endpoint (optionally public endpoint with **authorized networks**); Cloud NAT for egress; Private Google Access. Newer clusters use **Private Service Connect** for control plane connectivity and "private nodes" per node pool.
- **Release channels**: Rapid, Regular (default), Stable, **Extended** (longer support, older minors); enroll for automatic upgrades; **maintenance windows** and **maintenance exclusions** (up to 30 days no minor upgrades, or longer with scope limits); node pool **surge upgrades** (`max-surge-upgrade`, `max-unavailable-upgrade`) or **blue-green** node upgrades; PodDisruptionBudgets protect availability.
- **Workload Identity Federation for GKE**: Kubernetes ServiceAccount authenticates as IAM principal (`principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NS/sa/KSA`) — no service account keys; legacy approach binds KSA to a Google service account via `roles/iam.workloadIdentityUser`.
- **Security hardening**: Shielded nodes, Binary Authorization, GKE Sandbox (gVisor), Container-Optimized OS, Secret Manager CSI/Kubernetes secrets encrypted with Cloud KMS (application-layer secrets encryption), network policy, Pod Security Admission, security posture dashboard.
- **Storage**: PD CSI (ReadWriteOnce), Filestore CSI (ReadWriteMany), GCS FUSE CSI, Hyperdisk; regional PD for zonal-failure tolerance of stateful sets.
- **GKE Enterprise** (formerly Anthos): **fleets** group clusters across GCP, on-prem (bare metal/VMware), AWS/Azure, and attached clusters; **Config Sync** (GitOps from a repo to many clusters), **Policy Controller** (OPA Gatekeeper constraint templates, e.g., disallow privileged containers), **Cloud Service Mesh** (managed Istio: mTLS, traffic splitting, observability), **Connect gateway** (kubectl to any fleet cluster via Google identity), multi-cluster Ingress/Gateway and Services, fleet-level Workload Identity, **Cloud Run for Anthos** retired in favor of Knative/Cloud Run.

> **Exam tip:** "Enforce that every cluster in every environment has the same namespaces/RBAC/policies" → Config Sync + Policy Controller in a fleet, not manual `kubectl`.

### Cloud Run and serverless

- **Services** (request-driven, HTTP/gRPC/WebSockets, request timeout up to 60 min) vs **Jobs** (run-to-completion tasks, up to 24 h per task, parallel tasks, scheduled via Cloud Scheduler) vs **Cloud Run functions** (event/HTTP functions built on Cloud Run; formerly Cloud Functions 2nd gen).
- **Concurrency**: default 80 requests per instance, max 1,000; set 1 for non-thread-safe code. **min instances** (keep warm, avoid cold starts; billed) and **max instances** (protect downstream DBs). **CPU allocation**: *request-based* (CPU only during requests; scale-to-zero pricing) vs *instance-based / always allocated* (background work, cheaper for steady high traffic, required for some sidecars). Up to 8 vCPU / 32 GiB (more on larger configs), **GPUs (NVIDIA L4)** for inference, startup CPU boost, health probes, sidecar containers, volume mounts (GCS, NFS, in-memory).
- **Revisions & traffic splitting**: immutable revisions, tag-based URLs, gradual rollout percentages, instant rollback.
- **Ingress settings**: `all`, `internal` (VPC + VPC-SC perimeter sources only), `internal-and-cloud-load-balancing`. Put a global external ALB with a **serverless NEG** in front for custom domains, Cloud Armor, CDN, IAP, and multi-region deployments; `run.googleapis.com/ingress` internal + ALB = no direct `*.run.app` exposure.
- **Egress to VPC**: **Direct VPC egress** (preferred: no connector, higher throughput, Pod-like IP in subnet, network tags) or **Serverless VPC Access connector** (legacy, connector instances). VPC egress setting: `private-ranges-only` vs `all-traffic` (route all egress through VPC → Cloud NAT static IP for allow-listing).
- **Invocation IAM**: `roles/run.invoker`; `allUsers` invoker = public (may be blocked by org policy `run.allowedIngress` / `iam.allowedPolicyMemberDomains`). Service-to-service: caller uses its service account identity token (audience = target URL). `roles/run.developer` deploys; `roles/run.admin` manages IAM.
- **Eventarc**: triggers Cloud Run/functions/GKE/Workflows from Pub/Sub, **Cloud Audit Logs** events (e.g., object finalized via `storage.objects.create` or direct GCS events), and 130+ direct Google sources plus third-party; delivered as CloudEvents. Eventarc Advanced adds a message bus with enrollment/filters.
- **App Engine**: **Standard** (sandboxed runtimes, scale to zero, sub-second startup, free tier, no custom binaries beyond runtime, 60-second-ish request limits on automatic scaling) vs **Flexible** (Docker on VMs, min 1 instance, no scale-to-zero, slower deploys, SSH to instances, any language). One App Engine app per project, region immutable; traffic splitting by IP/cookie/random; new designs → Cloud Run.
- **Orchestration glue**: **Workflows** (serverless YAML/JSON step orchestration of APIs, up to 1 year per execution, retries/callbacks, cheap per step) vs **Cloud Tasks** (asynchronous HTTP task queues with rate limits, retries, de-dup, scheduled delivery — *targeted* dispatch) vs **Pub/Sub** (fan-out, streaming, at-least-once, 7-day retention default up to 31 days) vs **Cloud Scheduler** (cron → HTTP/Pub/Sub/App Engine) vs **Cloud Composer** (managed Airflow for data pipelines with dependencies; always-on cost) vs **Cloud Batch** (managed batch jobs on VMs incl. Spot and GPUs).

### Infrastructure as Code

| Tool | Model | Use when |
|---|---|---|
| **Terraform** (google / google-beta providers) | HCL, state file (store in a GCS backend with versioning and locking) | Default answer for reproducible, multi-env infra; modules, `terraform plan` in CI |
| **Infrastructure Manager** | Managed Terraform executor in Google Cloud; deployments and revisions tracked, state managed by Google | Terraform without self-hosting runners; Cloud Build-based |
| **Config Connector** / **Config Controller** | Kubernetes CRDs (KRM) for Google Cloud resources; Config Controller = hosted Config Connector + Config Sync + Policy Controller | Teams standardized on GitOps/kubectl; policy-guarded platform |
| Deployment Manager | Legacy YAML/Jinja | Avoid for new work (deprecated path) |
| Service Catalog / Cloud Foundation Fabric & Toolkit | Curated Terraform blueprints, org bootstrap ("fabric FAST") | Landing zones, enterprise foundations |

Pair IaC with **Cloud Build** triggers (plan on PR, apply on merge), `gcloud` for imperative tasks, and **Gemini Cloud Assist** for generating/diagnosing configs. Golden images via **Packer** on Cloud Build; OS drift managed by VM Manager.

## 2.4 Vertex AI (Gemini Enterprise Agent Platform) for end-to-end ML

The blueprint now calls this **Gemini Enterprise Agent Platform**; the console and most questions still use **Vertex AI** names. Know the lifecycle components:

| Stage | Component | Key facts |
|---|---|---|
| Ingest / prepare | **Vertex AI Datasets** (managed image/text/tabular/video), BigQuery, Cloud Storage, Dataflow/Dataproc for feature engineering, **Dataplex** for governance | Keep data in BigQuery for tabular; GCS for unstructured |
| Features | **Vertex AI Feature Store** (BigQuery-backed offline store; online store = Bigtable-backed or Optimized online serving with embeddings) | Solves training/serving skew; point-in-time lookups |
| Experiment | Colab Enterprise, **Vertex AI Workbench** instances, Experiments, TensorBoard | Managed notebooks with IAM & VPC-SC |
| Train | **AutoML**, **custom training** (prebuilt or custom containers, CustomJob / HyperparameterTuningJob, distributed with Reduction Server, GPUs/TPUs, Spot), **Ray on Vertex AI**, tuning of Gemini (supervised fine-tuning, distillation, RLHF) | Choose AutoML for speed with no ML team; custom when you own code |
| Orchestrate | **Vertex AI Pipelines** (Kubeflow Pipelines v2 or TFX DSL, serverless execution, artifact lineage via ML Metadata, scheduled runs, compiled to YAML) | The "automate retrain when new data arrives" answer, triggered by Cloud Run functions / Eventarc / Scheduler |
| Register | **Model Registry** (versions, aliases like `default`/`champion`, evaluation results, deploy to endpoint) | Governance checkpoint before deploy |
| Serve | **Online prediction endpoints** (dedicated machine types, autoscaling replicas, traffic split between models, **private endpoints via Private Service Connect**, dedicated endpoints for large payloads) and **batch prediction** (BigQuery/GCS in → out, no endpoint) | Batch = cheapest for nightly scoring; online = low latency |
| Monitor | **Model Monitoring** (training-serving skew and prediction drift, feature attribution drift, alerts), Vertex AI Evaluation (gen-AI eval service), Cloud Monitoring metrics | Monitoring triggers pipeline re-run |
| SQL-native | **BigQuery ML**: `CREATE MODEL` (linear/logistic, boosted trees, DNN, k-means, ARIMA_PLUS forecasting, matrix factorization, AutoML, imported TF/ONNX/XGBoost), **remote models** calling Gemini or Vertex endpoints, `ML.GENERATE_TEXT`, `ML.GENERATE_EMBEDDING`, vector search in BigQuery | Analysts without Python; data never leaves BigQuery |

**Gen-AI specifics**: Gemini models (Pro/Flash/Flash-Lite families) via the Vertex AI API; **context caching** for repeated large prompts; **Provisioned Throughput** for guaranteed capacity; **batch prediction for Gemini** at discount; **Vertex AI RAG Engine** and **Vector Search** (ScaNN-based ANN) for retrieval; **Gen AI evaluation service**; safety filters and system instructions; **Model Armor** in front of prompts/responses.

### AI Hypercomputer

Integrated stack of hardware + open software + flexible consumption for large-scale training/serving.

- **GPUs**: A2 (A100 40/80 GB), **A3** (8× H100 80 GB; A3 Mega adds GPUDirect-TCPXO ~1.8 Tbps inter-node), A3 Ultra (H200), **A4** (B200) and A4X (GB200 NVL72 rack scale). G2 (L4) for cost-efficient inference and graphics.
- **TPUs**: **v5e** (best price-performance for inference and medium training, up to 256 chips per pod), **v5p** (large-scale training, up to 8,960 chips per pod, 3D torus ICI), **Trillium (v6e)** (~4.7× v5e per-chip compute), **Ironwood (v7)** (inference-optimized, largest pods). Multislice spans multiple pods over the DCN. Frameworks: JAX, PyTorch/XLA, TensorFlow; MaxText/MaxDiffusion reference implementations.
- **Schedulers**: GKE (with **Cluster Director**, Kueue, JobSet, TPU/GPU node pools, compact placement), Slurm on Compute Engine, Vertex AI training/serving, Ray.
- **Storage/network** for training: Hyperdisk ML (read-only model weights fan-out), **Parallelstore** / **Managed Lustre** (parallel file systems), GCS with Anywhere Cache and FUSE, Jupiter fabric and RDMA networking.
- **Dynamic Workload Scheduler (DWS)**: **Flex Start** mode (queue a request for GPUs/TPUs for up to 7 days at discount; obtains capacity all-at-once) and **Calendar** mode (reserve future capacity blocks of 7 or 14 days, up to 8 weeks ahead). Exposed through GKE, Compute Engine MIGs (resize requests), Batch, and Vertex AI training.

| Consumption model | Best for |
|---|---|
| On-demand | Short experiments, unpredictable |
| **Spot** | Fault-tolerant training with checkpointing, batch inference; can be preempted |
| **Reservations / future reservations** | Guaranteed capacity for production serving or planned training; combine with CUDs |
| **DWS Flex Start** | "Need 64 H100s sometime this week, cheapest possible" |
| **DWS Calendar** | "Training run starts on the 15th for 14 days" |
| **Committed use discounts (accelerators)** | Steady 1–3 year usage |
| Vertex AI **Provisioned Throughput** | Guaranteed tokens/sec for Gemini serving |

Cloud Run functions and Workflows are the glue: trigger pipeline runs on new data, post-process predictions, fan out inference requests; Cloud Run with GPUs handles bursty small-model serving that scales to zero.

> **Exam tip:** Map the requirement: "largest foundation-model pretraining" → TPU v5p/Trillium pods or A3/A4 clusters with GKE + DWS/reservations; "serve LLM at low cost with variable traffic" → TPU v5e / L4 GPUs on GKE or Cloud Run GPU; "no ML team, tabular churn model" → BigQuery ML or AutoML; "repeatable retraining with lineage" → Vertex AI Pipelines + Model Registry.

## 2.5 Prebuilt AI APIs, Agent Builder, and Model Garden

### Google AI APIs — pick the managed model

| Need | API / product | Notes |
|---|---|---|
| Enterprise search over docs, websites, structured data; RAG out of the box | **Vertex AI Search** (AI Applications / Agent Builder) | Data stores (GCS, BigQuery, websites, Confluence/SharePoint connectors), grounding source for Gemini, answers with citations |
| Chat/voice agents with deterministic flows | **Conversational Agents** (Dialogflow CX) + **Agent Assist** / **Contact Center AI Platform** | Playbooks (LLM) + flows (state machine); telephony integration |
| Image labels, OCR, faces, logos, SafeSearch | **Cloud Vision API** | Batch and online; AutoML Vision retired into Vertex |
| Document extraction (invoices, W-2s, IDs) | **Document AI** | Pretrained processors + custom extractor; human-in-the-loop |
| Video labels, shot change, explicit content, transcription | **Video Intelligence API** | Also Vertex video models |
| Speech-to-text (Chirp models), text-to-speech (WaveNet/Neural2/Studio voices) | **Speech-to-Text v2**, **Text-to-Speech** | Streaming, diarization, 125+ languages |
| Translation | **Cloud Translation** (basic, advanced with glossaries, adaptive/LLM), AutoML translation | Real-time and batch |
| Entities, sentiment, classification | **Natural Language API** (or Gemini directly) | Legacy for many use cases |
| Image generation/editing | **Imagen** on Vertex AI | Watermarking with SynthID |
| Video generation | **Veo**; music **Lyria**; speech **Chirp 3** | Model Garden |
| Multimodal reasoning, code, long context | **Gemini** models | Choose Flash for cost/latency, Pro for quality |
| Data loss / PII detection | **Sensitive Data Protection** | Security, not "AI API", but shows up in the same stems |

Rule: if a **pretrained API** satisfies accuracy needs → use it (zero training, per-call pricing). If domain-specific accuracy is required → **custom training** or tuning in Vertex AI; if data is tabular in BigQuery → BigQuery ML.

### Gemini Enterprise, NotebookLM Enterprise, and agents

- **Gemini Enterprise** (evolution of Agentspace): company-wide agentic search and assistant that connects to Google Workspace, Microsoft 365, Salesforce, ServiceNow, Jira, etc., with enterprise-grade IAM/ACL enforcement and prebuilt/custom agents (Deep Research, Idea Generation, data agents). Use for "let employees query all corporate knowledge with citations and take actions".
- **NotebookLM Enterprise**: source-grounded notebooks (upload docs, generate summaries, audio overviews) governed by IAM, VPC-SC, CMEK, data residency — no training on customer data.
- **Agent Development Kit (ADK)**: open-source framework (Python/Java) for multi-agent systems with tools, sessions, memory; deploy to **Vertex AI Agent Engine** (managed runtime with sessions, memory bank, evaluation, tracing) or Cloud Run/GKE. **Agent Garden** offers samples; **Agent2Agent (A2A)** protocol for inter-agent interoperability; **MCP** for tool integration (e.g., MCP Toolbox for Databases).
- **Gemini Code Assist** (developer coding assistant; Enterprise tier customizes on private repos) and **Gemini Cloud Assist** (operations: design, troubleshoot, cost insights inside the console) are the Gemini "assistants" the exam names — distinguish them from building your own agents.

### Model Garden

| Category | Examples | How you consume |
|---|---|---|
| Google first-party | Gemini, Imagen, Veo, Chirp, Gemma (open weights), MedLM, embeddings | Serverless API (pay per token/char) or tune |
| **Open models** | Llama, Mistral/Mixtral, Qwen, DeepSeek, Gemma, Stable Diffusion, Hugging Face catalog | **Self-deploy** to a Vertex AI endpoint on your GPUs/TPUs (you pay for infra; full control, VPC-SC/CMEK) — or several as **Model-as-a-Service** serverless APIs |
| **Partner models** | Anthropic Claude, Mistral (MaaS), AI21, others | MaaS pay-as-you-go through Vertex AI billing, same IAM/monitoring, no separate contract |

Governance: org policy constraint to restrict which Model Garden models a project may use; models run in Google's boundary with **no training on your data**; Access Transparency, data residency for many models (ML processing region), zero-data-retention options.

### Grounding — reduce hallucination

| Source | Use case |
|---|---|
| **Grounding with Google Search** | Fresh public facts, entity info; returns citations and search suggestions (display obligations) |
| **Grounding with Vertex AI Search data store** | Your enterprise docs; simplest managed RAG |
| **Grounding with Google Maps** | Location-aware responses |
| **RAG Engine** / Vector Search / AlloyDB & Cloud SQL `pgvector` / BigQuery vector search | Custom RAG when you control chunking, embeddings, and retrieval |
| Function calling / tools | Live system data (inventory, orders) |

Design pattern: documents → chunk/embed → store → retrieve top-k → prompt Gemini with context → Model Armor screening → return with citations; evaluate with the Gen AI evaluation service; log prompts/responses to BigQuery for audits.

> **Trap:** "Model must answer only from our policy documents and cite them" is a grounding/RAG question (Vertex AI Search or RAG Engine), **not** a fine-tuning question. Fine-tuning changes style/format/task behavior; it does not reliably inject facts or keep them current.

## Key takeaways

- Dedicated Interconnect = 10/100 Gbps, Partner = 50 Mbps–50 Gbps, HA VPN = 99.99% with two tunnels; back an Interconnect with HA VPN on the same Cloud Router using MED priorities; global dynamic routing lets one link serve all regions.
- VPC peering is non-transitive and needs non-overlapping CIDRs; NCC VPC spokes or PSC are the modern answers for many-to-many and producer/consumer connectivity.
- Shared VPC: `xpnAdmin` at org/folder, `networkUser` at subnet granularity, GKE also needs `container.hostServiceAgentUser`.
- Firewall evaluation: hierarchical → global network → regional network → VPC rules → implied deny ingress; Cloud NGFW Enterprise = IPS + TLS inspection; Cloud IDS detects only.
- Cloud Armor attaches to backend services of proxy-based external LBs: WAF preconfigured rules, rate limiting, Adaptive Protection, bot management.
- Health checks come from 35.191.0.0/16 and 130.211.0.0/22; global external ALB needs Premium Tier; proxy LBs need proxy-only subnets; passthrough LBs preserve client IP.
- Cloud Storage minimums: Nearline 30, Coldline 90, Archive 365 days; signed URLs ≤ 7 days; Bucket Lock is irreversible; soft delete default 7 days; turbo replication ≈ 15-minute RPO.
- PD performance scales with size; Hyperdisk decouples IOPS from capacity; regional PD gives RPO 0 within a region; snapshots are incremental and global.
- Cloud SQL: auto storage increase, replicas, Enterprise Plus 99.99% and 35-day PITR; Spanner 100 PU granularity with 7-day version retention and 1-year backups; Bigtable backups 90 days; BigQuery partition + cluster + long-term storage after 90 days.
- MIGs: regional across zones, autohealing with health checks, rolling updates via max surge/unavailable, canary via second template; Spot = 30-second notice, no SLA.
- GKE Autopilot bills per Pod and manages nodes; Standard gives node control; use Workload Identity Federation, release channels, maintenance windows, Gateway API, Config Sync + Policy Controller across fleets.
- Cloud Run: concurrency 80 default, min instances kill cold starts, Direct VPC egress for private access, `roles/run.invoker` for auth, ingress internal + ALB for enterprise exposure, Eventarc for events.
- Vertex AI lifecycle = Datasets/Feature Store → Training → Pipelines → Model Registry → Endpoints/Batch → Model Monitoring; BigQuery ML for SQL-first teams.
- AI Hypercomputer = A3/A4 GPUs and TPU v5e/v5p/Trillium with GKE/Slurm/Vertex, obtained via reservations, Spot, or Dynamic Workload Scheduler Flex Start/Calendar.
- Prefer pretrained APIs and Model Garden MaaS before custom training; ground Gemini with Vertex AI Search or RAG Engine rather than fine-tuning to inject facts.

## Quick self-check

- Q: You need 99.99% availability for on-prem connectivity with 40 Gbps steady throughput and no colo footprint. What do you provision? — **A:** Partner Interconnect with four VLAN attachments across two metros/two regions (two Cloud Routers), global dynamic routing; HA VPN as encrypted fallback if required.
- Q: Which IP ranges must your firewall allow for Google Cloud load balancer health checks? — **A:** 35.191.0.0/16 and 130.211.0.0/22.
- Q: A team in a service project must create VMs only in subnet `web-us` of the host project. Which role, where? — **A:** `roles/compute.networkUser` on that specific subnet in the host project (plus instance admin in their own project).
- Q: Objects must be immutable for 7 years to satisfy regulators. Configure? — **A:** Bucket retention policy of 7 years and **lock** it (Bucket Lock); optionally object holds for legal cases.
- Q: A Cloud Run service must call a Cloud SQL private IP and present a fixed egress IP to a partner. How? — **A:** Direct VPC egress (or connector) with `all-traffic` egress, route through Cloud NAT with a static IP; Cloud SQL via private IP/PSC.
- Q: Rolling out a new instance template to a MIG must never reduce serving capacity. Which flags? — **A:** `--max-unavailable=0` with `--max-surge` > 0 (proactive rolling update), optionally a canary target size first.
- Q: Restore a Spanner database to its state 2 hours ago after bad writes. Requirement beforehand? — **A:** `version_retention_period` set to at least 2 hours (up to 7 days) so you can stale-read/backup-and-restore at that timestamp.
- Q: Data scientists want retraining triggered when a new file lands in a bucket, with lineage and approvals before deployment. Which services? — **A:** Eventarc/Cloud Run function → Vertex AI Pipelines run → Model Registry (evaluation + alias) → endpoint deploy; Model Monitoring feeds back.
- Q: Cheapest way to get 64 H100 GPUs for a 3-day training job that can start any time this week? — **A:** Dynamic Workload Scheduler Flex Start on GKE or a MIG resize request (with checkpointing to GCS).
