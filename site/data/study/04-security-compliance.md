Section 3 is ~17.5% of the exam and maps directly to the **security pillar** of the Well-Architected Framework: implement security by design, zero trust, shift-left, defense in depth, least privilege, preemptive cyber defense, and use AI securely (and AI for security). Almost every question reduces to: *which control, at which level of the hierarchy, with the least privilege that still meets the requirement.*

## 3.1 Identity and Access Management

### Roles taxonomy

| Type | Examples | Guidance |
|---|---|---|
| **Basic (primitive)** | `roles/viewer`, `roles/editor`, `roles/owner` | Thousands of permissions across all services; **avoid in production**. Owner can also manage IAM and billing linkage; Editor cannot grant roles |
| **Predefined** | `roles/storage.objectViewer`, `roles/compute.instanceAdmin.v1` | Service-scoped, maintained by Google; default choice |
| **Custom** | `projects/p/roles/deployer` | Assemble permissions at org or project level (not folder); use when predefined roles are too broad; watch for `TESTING` permissions and role launch stages |

Policies are **allow policies** bound to a resource; a binding = role + principals (+ optional condition). Effective permissions are the **union** of policies inherited down the hierarchy (org → folder → project → resource) — you cannot remove an inherited grant at a lower level (use deny policies or restructure). A single allow policy holds up to 1,500 principals (groups count as one) — grant to **Google Groups**, not individuals.

### Predefined roles you must recognize

| Role | Grants | Typical exam context |
|---|---|---|
| `roles/resourcemanager.organizationAdmin` | Manage org IAM and hierarchy (does *not* grant billing or project data access) | Initial org setup; keep to a small break-glass group |
| `roles/resourcemanager.folderAdmin` / `projectCreator` | Manage folders / create projects | Landing zone automation SA |
| `roles/billing.admin` | Manage billing accounts, link projects (with `billing.projectManager`) | Separate finance role — separation of duties |
| `roles/iam.serviceAccountUser` | Act as / attach a service account to resources (VMs, Cloud Run, jobs) | Developer needs to deploy code running as SA |
| `roles/iam.serviceAccountTokenCreator` | Mint OAuth tokens / OIDC ID tokens / sign blobs as the SA (**impersonation**) | Short-lived credentials instead of keys |
| `roles/iam.serviceAccountAdmin` / `serviceAccountKeyAdmin` | Manage SAs / manage keys | Restrict key admin heavily |
| `roles/iam.workloadIdentityUser` | Allow external identity (KSA, WIF principal) to impersonate an SA | GKE Workload Identity, GitHub Actions |
| `roles/iam.securityReviewer` | Read all IAM policies | Auditors |
| `roles/compute.networkUser` | Use subnets in a Shared VPC host | Service project developers |
| `roles/compute.networkAdmin` / `securityAdmin` | Network resources / firewall & certs | Net team vs sec team split |
| `roles/compute.osLogin` / `osAdminLogin` | SSH via OS Login without / with sudo | Replace metadata SSH keys |
| `roles/storage.objectViewer` / `objectCreator` / `objectUser` / `objectAdmin` / `admin` | Read objects / write-only (no read) / read+write / all object ops / bucket + IAM | Least-privilege bucket access; `objectCreator` for drop-box uploads |
| `roles/bigquery.dataViewer` / `jobUser` / `dataEditor` | Read tables / run queries (needs both) / write | Analysts need dataViewer on dataset + jobUser on project |
| `roles/cloudkms.cryptoKeyEncrypterDecrypter` | Use key, not manage it | Grant to *service agents* for CMEK |
| `roles/cloudkms.admin` | Manage keys, cannot use them | Key custodians |
| `roles/secretmanager.secretAccessor` | Read secret payload | Application SA |
| `roles/iap.httpsResourceAccessor` / `iap.tunnelResourceAccessor` | Access IAP web app / IAP TCP forwarding | Zero-trust access |
| `roles/logging.viewer` vs `logging.privateLogViewer` | Logs / plus Data Access & Access Transparency logs | Security analysts |
| `roles/run.invoker` | Call a Cloud Run service | Service-to-service auth |
| `roles/browser` | See hierarchy without resource access | Navigation for auditors |

> **Trap:** `roles/viewer` at org level exposes data (e.g., can read Cloud Storage objects, BigQuery data) — it is not "read metadata only". For hierarchy browsing use `roles/browser`.

### IAM Conditions, deny policies, and Principal Access Boundaries

- **IAM Conditions** (CEL expressions on a binding): resource attributes (`resource.name.startsWith("projects/_/buckets/finance-")`, resource type, **tags** like `resource.matchTag("env", "prod")`), request attributes (`request.time < timestamp(...)` for time-boxed access, access levels for device/IP via `request.auth.access_levels`). Only on resources that support conditions and with uniform bucket-level access for Cloud Storage.
- **Deny policies**: evaluated **before** allow policies; if a deny matches, access is denied regardless of allow. Attach at org/folder/project; scope to principal sets (`principalSet://goog/public:all`, all in domain, all SAs in project) with exception principals; only permissions in the supported list (most Compute, Storage, IAM, BigQuery, KMS, Logging, etc.). Use case: "no one except the SRE break-glass group may delete Cloud SQL instances, even project owners".
- **Principal Access Boundary (PAB) policies**: bound to *principals* (a principal set, e.g., all users in your Workforce pool or org) and list which resources those principals are *eligible* to access; anything outside is denied even if an external project grants them a role. Solves data exfiltration by "insider granted a role in an attacker-controlled project". Enforced for supported services only (check enforcement version).
- **Domain restricted sharing** (org policy `iam.allowedPolicyMemberDomains`) blocks granting roles to identities outside listed Cloud Identity customer IDs (also blocks `allUsers`).

### Policy Intelligence tooling

| Tool | Answers |
|---|---|
| **IAM Recommender** | "This principal hasn't used 95% of Editor's permissions in 90 days — replace with these predefined roles" (insights + recommendations; auto-apply via API) |
| **Policy Analyzer** | "Who can access resource X / what can principal Y access?" (Cloud Asset Inventory analysis, incl. inherited & conditional bindings; also across org policies) |
| **Policy Troubleshooter** | "Why was principal Y denied permission P on resource X?" (checks allow, deny, PAB, org policy) |
| **Policy Simulator** | "If I replace this role binding, which recent access logs would have been denied?" (tests against 90 days of logs before you apply) |
| **Org Policy Simulator / dry-run** | Test org policy changes and custom constraints before enforcement |
| **Cloud Asset Inventory** | Point-in-time & historical resource/IAM snapshots, feed to Pub/Sub, export to BigQuery |
| **Security Health Analytics (SCC)** | Misconfiguration findings like public buckets, primitive roles, SA keys older than 90 days |

### Service account best practices

- Service accounts are both **principals** and **resources** (granting `serviceAccountUser` *on* the SA is what lets someone act as it). Prefer one SA per workload with minimal roles; never reuse the Compute Engine default SA (historically auto-granted Editor — disable with org policy `iam.automaticIamGrantsForDefaultServiceAccounts`).
- **Avoid user-managed keys**: enforce `iam.disableServiceAccountKeyCreation` and `iam.disableServiceAccountKeyUpload`; set `iam.serviceAccountKeyExpiryHours` if keys are unavoidable; rotate; monitor via `iam.serviceAccountKeys` audit logs and SCC. Use **attached SAs** (metadata server tokens) on GCE/GKE/Cloud Run, **impersonation** (`gcloud --impersonate-service-account`, `roles/iam.serviceAccountTokenCreator`) for humans and CI, and **federation** for external workloads.
- **Access scopes** on VMs are legacy; use `cloud-platform` scope and control with IAM roles.
- Distinguish **service agents** (Google-managed SAs like `service-PROJECT_NUMBER@gcp-sa-*.iam.gserviceaccount.com`) — you grant *them* CMEK or Shared VPC roles.
- Short-lived credentials: OAuth access tokens ≤ 1 h (extend to 12 h with org policy), ID tokens for Cloud Run/IAP, signed URLs via `signBlob`. Disable rather than delete SAs first (deletion can be restored within 30 days but bindings referencing it are dropped).

### Workload identity: on GKE and from outside

- **Workload Identity Federation for GKE**: the Pod's Kubernetes SA is a first-class IAM principal (`principal://iam.googleapis.com/projects/NUM/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NAMESPACE/sa/KSA`). Grant roles directly to that principal (preferred) or bind the KSA to a Google SA with `roles/iam.workloadIdentityUser` + annotation. Enabled per cluster and per node pool (GKE metadata server); Autopilot has it on by default.
- **Workload Identity Federation (WIF)**: external workloads (AWS, Azure, GitHub Actions, GitLab, any OIDC/SAML IdP, on-prem with certificates/X.509) exchange their native token for a Google short-lived token via a **workload identity pool** + **provider** (attribute mapping, attribute conditions, e.g., `assertion.repository == "org/repo"`). Two modes: direct resource access as the federated principal (`principal://` or `principalSet://`) or impersonate a Google SA. Eliminates downloaded keys for CI/CD and multicloud.
- **Workforce Identity Federation**: *human* users from an external IdP (Okta, Entra ID, ADFS) sign in to the console/gcloud via a **workforce pool** without provisioning them in Cloud Identity. Roles are granted to `principalSet://iam.googleapis.com/locations/global/workforcePools/POOL/group/GROUP`. Use when a subsidiary, partner, or acquisition must access your org without syncing users.

### Cloud Identity, SSO, and 2SV

- **Cloud Identity** (Free/Premium) is the identity backbone: users, groups, org units, device management; the org resource is created automatically when a Cloud Identity/Workspace domain is verified. Sync from Active Directory/LDAP with **Google Cloud Directory Sync (GCDS)** (one-way to Google), or provision via Entra ID/Okta SCIM.
- **SSO**: Google as SAML 2.0/OIDC service provider with a third-party IdP; authentication happens at the IdP, authorization in IAM; groups sync gives dynamic role membership. Google can also be the IdP for third-party SaaS.
- **2-Step Verification**: enforce per org unit; security keys (Titan/FIDO2) via **Advanced Protection Program** for admins; **context-aware access** adds device/IP/location checks. Minimum recommended: enforce 2SV for all, security keys for privileged roles, super admin accounts separate from daily accounts and no more than a few of them, with recovery options and monitoring.

## Resource hierarchy and organization policy

- **Organization → Folders (up to 10 levels) → Projects → Resources.** IAM and org policies inherit downward; folders model business units, environments (prod/non-prod), or compliance boundaries. Projects are the unit of billing, quotas, API enablement, and most IAM. Recommended landing-zone shape: `org/ → fldr-bootstrap, fldr-common (logging, networking hubs, security), fldr-production, fldr-non-production, fldr-development`, with a Shared VPC host project per environment.
- **Tags** (org-level key/values bound to resources) drive IAM conditions, org policy conditions, and firewall policy targeting; **labels** are metadata for billing/filters only.
- **Organization Policy Service** sets guardrails via **constraints**: *boolean* (enforce/not) or *list* (allow/deny values, supports `under:folders/123` and `in:` prefixes for locations). Policies inherit; a child can `inheritFromParent` and merge or **override** with `reset`; **custom constraints** (CEL on resource fields) for services that support them; **dry-run mode** and tag-conditional policies; **managed constraints** roll out by default for new orgs (secure-by-default).

| Constraint | Effect / when the exam wants it |
|---|---|
| `iam.allowedPolicyMemberDomains` | Domain restricted sharing — prevents external principals and `allUsers` |
| `iam.disableServiceAccountKeyCreation` / `KeyUpload` | No long-lived SA keys |
| `iam.automaticIamGrantsForDefaultServiceAccounts` | Stop Editor on default SAs |
| `iam.serviceAccountKeyExpiryHours` / `allowServiceAccountCredentialLifetimeExtension` | Key/token lifetimes |
| `compute.vmExternalIpAccess` | Deny public IPs on VMs (list of exceptions) |
| `compute.requireShieldedVm` / `compute.restrictNonConfidentialComputing` | Force Shielded / Confidential |
| `compute.requireOsLogin` | OS Login everywhere |
| `compute.skipDefaultNetworkCreation` | No default VPC in new projects |
| `compute.restrictVpcPeering`, `compute.restrictSharedVpcHostProjects` / `SubnetworkProjects` | Control network topology |
| `compute.restrictCloudNATUsage`, `compute.disableSerialPortAccess`, `compute.disableNestedVirtualization`, `compute.storageResourceUseRestrictions` | Hardening |
| `compute.trustedImageProjects` | Only approved golden images |
| `gcp.resourceLocations` | **Data residency** — restrict where resources can be created (e.g., `in:eu-locations`) |
| `gcp.restrictServiceUsage` | Allow-list which APIs/services may be used |
| `gcp.restrictCmekCryptoKeyProjects` / `gcp.restrictNonCmekServices` | Require CMEK from approved key projects |
| `gcp.restrictTLSVersion` | Block TLS 1.0/1.1 |
| `storage.uniformBucketLevelAccess`, `storage.publicAccessPrevention`, `storage.retentionPolicySeconds`, `storage.softDeletePolicySeconds` | Bucket hardening |
| `sql.restrictPublicIp`, `sql.restrictAuthorizedNetworks` | No public Cloud SQL |
| `run.allowedIngress`, `run.allowedVPCEgress` | Cloud Run exposure |
| `cloudkms.allowedProtectionLevels`, `cloudkms.minimumDestroyScheduledDuration` | HSM/EKM only, destroy delay |
| `essentialcontacts.allowedContactDomains` | Notifications go to corporate domains |
| `ainotebooks.*`, `vertexai` model access restrictions | Notebook hardening; limit which Model Garden models can be used |

> **Exam tip:** IAM answers "*who* can do *what*"; org policy answers "*what is allowed at all*, regardless of who". "Even project owners must not be able to create external IPs" → org policy, not IAM.

## Data security: encryption, keys, and secrets

### Encryption layers

- **At rest**: everything is encrypted by default with AES-256 using **envelope encryption** — data chunks encrypted by DEKs, DEKs wrapped by KEKs in Google's internal Keystore, rotated automatically. **In transit**: TLS from clients to Google Front Ends, ALTS (mutual authentication) between Google services; traffic between data centers is encrypted at the physical layer. **In use**: Confidential Computing.

| Key option | Who holds key material | Rotation / control | Use when | Caveats |
|---|---|---|---|---|
| **Google-managed (default)** | Google | Automatic, no config | No specific regulatory control requirement | No customer-visible key lifecycle |
| **CMEK (Cloud KMS)** | Google's KMS, but *you* create, rotate, disable, destroy the key and control IAM on it | Automatic rotation schedule (symmetric), manual for asymmetric | "Customer must control/revoke encryption key", audit key usage, crypto-shredding | Key location must match resource location (or global/multi-region rules); disabled key → data unavailable; grant service agent `cryptoKeyEncrypterDecrypter` |
| **CMEK with Cloud HSM** | FIPS 140-2 **Level 3** HSMs managed by Google | Same API as KMS, `--protection-level=hsm` | Regulatory requirement for HSM-backed keys (PCI, banking) | Higher cost; HSM regions |
| **Cloud EKM** | Key material outside Google in a partner HSM/KMS (Thales, Fortanix, Entrust, Futurex, Virtru) via `--protection-level=external` / `external-vpc` | You control at the external provider; **Key Access Justifications** show *why* Google needs the key and let you deny | Sovereignty: "Google must never hold the key" | Availability depends on external KMS; latency; limited services |
| **CSEK** | You supply the raw AES-256 key on every API call; Google keeps it only in memory | Fully your problem | Legacy requirement; only **Cloud Storage** and **Compute Engine disks** | Lose the key = lose the data; not supported by most services — usually a distractor |
| **Client-side encryption** | Encrypt before sending (e.g., Tink, Cloud KMS-wrapped) | Yours | Zero-trust in the provider | Kills server-side features like BigQuery queries (except AEAD functions) |

### Cloud KMS details

- Hierarchy: **project → location → key ring → key → key version**. Key rings and keys cannot be deleted (only key versions destroyed); keys are regional, multi-regional, or global — pick the location of the data.
- **Purposes**: symmetric encrypt/decrypt, asymmetric sign/encrypt, MAC, raw. **Rotation**: `--rotation-period` (e.g., 90d) creates new primary versions; old versions remain for decryption; re-encryption is not automatic for stored data (use `ReEncrypt`/rewrite where needed). **Destroy**: scheduled with a delay (default 30 days, configurable 24 h–120 days) after which material is unrecoverable → *crypto-shredding*.
- **Separation**: keep keys in a dedicated **key project** owned by the security team; grant `roles/cloudkms.cryptoKeyEncrypterDecrypter` on specific keys to service agents of consuming projects; `cloudkms.admin` cannot decrypt.
- **Cloud KMS Autokey** creates keys/key rings on demand per resource according to policy (removes manual CMEK toil). **Key import** for BYOK; **Key Access Justifications**; Cloud KMS audit logs (Data Access) for every use.
- Supported CMEK surfaces: Compute Engine disks/images/snapshots, Cloud Storage, BigQuery, Cloud SQL, Spanner, Bigtable, Pub/Sub, Dataflow, GKE (etcd application-layer secrets, node boot disks), Vertex AI, Secret Manager, Logging buckets, Artifact Registry, Dataproc, Composer, etc.

### Secret Manager

- Central store for API keys, passwords, certificates; **secret** (metadata, IAM, replication policy: automatic or user-managed regions, CMEK) with **versions** (enable/disable/destroy); IAM `roles/secretmanager.secretAccessor` on the secret; versions referenced as `latest` or pinned; **rotation** via schedule that publishes to Pub/Sub for a Cloud Run function to rotate; **expiration** and annotations; regional secrets for residency; access logged in Data Access audit logs. Integrations: Cloud Run/functions mount secrets as env vars or files; GKE Secret Manager add-on / CSI driver; Cloud Build `availableSecrets`.
- Never store secrets in code, images, metadata, or environment variables committed to repos; use the Secret Manager API at runtime.

### Confidential Computing and Sensitive Data Protection

- **Confidential VMs / GKE Nodes / Dataproc / Space**: hardware-based memory encryption (AMD SEV, SEV-SNP, Intel TDX), remote **attestation** via vTPM tokens; Confidential Space lets multiple parties run agreed workloads on pooled data (clean rooms) without any party seeing raw data.
- **Sensitive Data Protection (formerly Cloud DLP)**: 150+ **infoTypes** (credit cards, SSNs, names, custom dictionaries/regex), **inspection** (BigQuery, Cloud Storage, Datastore, streams, hybrid), **de-identification** transformations: **masking**, **redaction**, **tokenization / pseudonymization** with **format-preserving encryption (FPE-FFX)** or deterministic encryption (reversible with the KMS-wrapped key), crypto-hashing, **bucketing**, **date shifting**, generalization; **re-identification risk analysis** (k-anonymity, l-diversity); **Discovery service** automatically profiles data across the org to find sensitive tables/buckets and feeds SCC and Dataplex. Use SDP templates and Dataflow templates for large-scale pipelines; Cloud Run function trigger for uploads to quarantine buckets.

> **Remember:** "Analysts need to join on customer IDs but must never see PII" → deterministic or FPE tokenization (reversible, join-preserving). "Must be irreversible" → crypto-hashing or masking.

## Separation of duties patterns

- **Environment separation** by folders/projects with distinct IAM; developers have no roles in prod projects; deployments go through CI/CD service accounts.
- **Billing**: `roles/billing.admin` on the billing account to finance; project owners get `billing.projectManager` to link, not to see invoices.
- **Keys**: KMS admins in a security project cannot decrypt; data owners use keys but cannot manage them; EKM/KAJ for external approval.
- **Network vs security**: `compute.networkAdmin` (subnets/routes) vs `compute.securityAdmin` (firewalls, SSL policies) in the Shared VPC host; app teams only `networkUser`.
- **Org admin vs super admin**: Cloud Identity super admins can grant themselves org admin — restrict, monitor, and use dedicated accounts. Org admin ≠ project data access.
- **Logging**: aggregated log sink to a **central logging project** that application teams can't modify; Bucket Lock / log bucket **retention lock** for immutability.
- **Deployments**: Binary Authorization attestors owned by security; developers can't sign; break-glass requires justification and generates alerts.
- **Approval workflows**: IAM **Privileged Access Manager (PAM)** for just-in-time, time-bound role grants with approvals and justification; Access Approval for Google-side access.

## Security controls

### Cloud Audit Logs

| Log type | Default | Retention in `_Required` / `_Default` | Records | Cost |
|---|---|---|---|---|
| **Admin Activity** | Always on, cannot disable | **400 days** (`_Required`, not configurable) | Create/modify/delete configs, IAM changes | Free |
| **System Event** | Always on | 400 days | Google-initiated actions (live migration, autoscaler) | Free |
| **Policy Denied** | On by default (can exclude) | **30 days** in `_Default` | VPC-SC and org policy denials | Chargeable ingestion |
| **Data Access** | **Off by default** (except BigQuery) | 30 days in `_Default` (configurable 1–3650 days) | Read/write of user data (ADMIN_READ, DATA_READ, DATA_WRITE) | Chargeable; can be large |
| **Access Transparency** | Enable at org (requires eligible support tier) | 400 days in `_Required` | Google personnel access with justification | Free |
| **Access Approval** | Opt-in per project/folder/org | — | Approve/deny Google access requests before they happen (with KMS/EKM signing) | Feature of Assured Workloads / add-on |

- Enable Data Access logs at the **org level** for critical services (Cloud Storage, KMS, Secret Manager, BigQuery is already on) with exemptions for noisy identities. `roles/logging.privateLogViewer` is needed to read Data Access logs.
- **Log Router sinks**: destinations Cloud Logging buckets (with **Log Analytics** SQL), **BigQuery** (analysis), **Cloud Storage** (cheap long-term, Bucket Lock for WORM), **Pub/Sub** (SIEM export — Splunk, Google SecOps), or another project. **Aggregated sinks** at org/folder with `--include-children` capture everything below; **intercepting sinks** stop child projects from also receiving; exclusion filters cut volume. Grant the sink's writer identity permission on the destination.
- Log buckets: set retention 1–3650 days, **lock** to prevent shortening, CMEK, regional placement for residency. Cloud Logging isn't a SIEM: stream to **Google Security Operations (Chronicle)** or a third party.
- Other evidence logs: VPC Flow Logs, Firewall Rules Logging, Cloud NAT logs, LB request logs, DNS query logs, Cloud Armor logs, IAP access logs, Data Access on KMS for key usage.

### VPC Service Controls

- **Purpose**: mitigate **data exfiltration** from Google-managed services (Cloud Storage, BigQuery, Bigtable, Spanner, Pub/Sub, Vertex AI, Secret Manager, KMS, Logging, …) by creating a **service perimeter** around projects/VPC networks. IAM controls *who*; VPC-SC controls *from where* and *to where* API calls may flow.
- **Concepts**: perimeter (projects + VPC networks + **restricted services**), **access levels** from Access Context Manager (IP CIDR, device policy, user/SA identity, geography, or custom CEL), **ingress rules** (allow calls from outside identities/networks into the perimeter for specific services/methods), **egress rules** (allow calls from inside to specific external projects/resources), **perimeter bridges** (share resources between perimeters — legacy; prefer ingress/egress), **VPC accessible services** (limit which APIs VMs inside can call at all), **dry-run** mode (logs violations without enforcing).
- **Requirements**: use `restricted.googleapis.com` (199.36.153.4/30) or a PSC endpoint with the `vpc-sc` bundle so requests never reach unrestricted VIPs; private DNS zone overriding `*.googleapis.com`; block external egress otherwise.
- **Pitfalls** (classic exam wrong answers): a project belongs to only **one** perimeter; Shared VPC host and service projects should be in the **same** perimeter; console access from corporate laptops needs an access level; Cloud Build default pool, Dataflow workers, Cloud Run, Vertex AI notebooks, and third-party SaaS integrations need specific ingress/egress rules or private pools; VPC-SC does **not** protect Compute Engine VM-to-internet traffic (that's firewall/NAT); it does **not** replace IAM; BigQuery cross-project queries and Cloud Storage copies between perimeters fail without egress rules; enabling enforcement without dry-run breaks pipelines. Policy Denied audit logs show violations with a unique ID you paste into the troubleshooter.

### Access Context Manager and context-aware access

- **Access levels** are the shared vocabulary: basic (conditions on IP subnets, device policy from **Endpoint Verification** — OS, screen lock, encryption, corporate-owned, region, principals) or custom (CEL). Consumed by VPC-SC ingress, **IAP**, IAM conditions, Google Workspace, and **Chrome Enterprise Premium**.
- **Chrome Enterprise Premium** (formerly BeyondCorp Enterprise): zero-trust access to web apps, SSH/RDP (via IAP), SaaS, and on-prem apps (via **IAP connector / app connector**) based on identity + device posture + context, plus Chrome browser threat and data protection (DLP in browser, malware scanning, URL filtering). Answer for "remote workforce, no VPN, device trust required".

### Security Command Center

| Tier | Includes | When |
|---|---|---|
| **Standard** (free) | Security Health Analytics (basic misconfig findings), Web Security Scanner custom scans, anomaly detection, integrate with Cloud Armor/SDP findings | Every org baseline |
| **Premium** | Full SHA + compliance dashboards (CIS, PCI, NIST, ISO), **Event Threat Detection** (log-based: crypto-mining, brute force, malware, exfil), **Container Threat Detection**, **VM Threat Detection**, Web Security Scanner managed scans, **attack path simulation & attack exposure scores**, security posture management, Sensitive Data Protection discovery integration, Assured OSS; pay-as-you-go or subscription | Production orgs, regulated |
| **Enterprise** | Premium + multi-cloud (AWS/Azure) CNAPP, **Google SecOps SIEM/SOAR** case management, Mandiant threat intel & attack surface management, IaC scanning, toxic combinations | Central SOC, multicloud |

Findings can trigger notifications to Pub/Sub → Cloud Run function for auto-remediation (e.g., revoke public bucket), and **mute rules** for accepted risk. SCC works at org level (Premium) or project level (limited).

### Network defenses (recap from Section 2)

**Cloud Armor** (L7 WAF/DDoS on external proxy LBs), **Cloud IDS** (detection via packet mirroring), **Cloud NGFW Enterprise** (inline IPS/TLS inspection), hierarchical firewall policies with `goto_next` delegation, Private Google Access + restricted VIP, Cloud NAT instead of external IPs, Shared VPC with centralized firewall control, **Packet Mirroring** for third-party tooling, **Network Intelligence Center** (Connectivity Tests, Firewall Insights showing shadowed/unused rules).

## Secure remote access

- **Identity-Aware Proxy (IAP)**:
  - **Web (HTTPS)**: sits in front of ALB backends, App Engine, Cloud Run; users authenticate with Google identity (or Identity Platform for external users) and must hold `roles/iap.httpsResourceAccessor`; add access levels for device/IP; backends should verify the signed **JWT header** (`x-goog-iap-jwt-assertion`).
  - **TCP forwarding**: SSH/RDP to VMs **without external IPs** through the tunnel; allow ingress from **35.235.240.0/20** on port 22/3389; user needs `roles/iap.tunnelResourceAccessor`; `gcloud compute ssh --tunnel-through-iap`. Replaces bastion hosts and VPNs for admin access.
- **OS Login**: ties Linux accounts to Google identities via metadata `enable-oslogin=TRUE` (org policy `compute.requireOsLogin`), roles `roles/compute.osLogin` / `osAdminLogin`; supports 2SV (`enable-oslogin-2fa`), POSIX info from Cloud Identity, centralized key management, audit trail; can be used with Active Directory via managed AD for Windows.
- **Service account impersonation**: humans and pipelines use `gcloud auth ... --impersonate-service-account` or `gcloud config set auth/impersonate_service_account`; requires `roles/iam.serviceAccountTokenCreator` on the SA; every impersonated call is logged with both identities. Delegation chains allowed. Use instead of key files for admin automation and Terraform.
- **Cloud Workstations**: managed, browser/IDE-accessible dev environments inside your VPC with IAP, VPC-SC, and no source code on laptops.
- **Bastions** are last resort; if used: no external IP on targets, IAP to bastion, OS Login, Shielded VM, session recording.

## Securing the software supply chain

| Stage | Control | Facts |
|---|---|---|
| Source | Cloud Build triggers from GitHub/GitLab/Secure Source Manager; branch protection; signed commits | Software Delivery Shield umbrella |
| Dependencies | **Assured Open Source Software** (Google-built, scanned, signed Java/Python/JS packages with SLSA provenance), Artifact Registry **remote repositories** proxying public registries with caching and scanning, **virtual repositories** to prioritize private over public (defends against dependency confusion) | |
| Build | **Cloud Build** with private pools (VPC access, no public IP), per-trigger service accounts, `--no-source` for hermetic builds; generates **SLSA Build Level 3 provenance** (signed attestations of what built the artifact) | SLSA levels 0–3: L1 provenance exists, L2 hosted build signed, L3 hardened/isolated builders |
| Store | **Artifact Registry** (Docker/OCI, Maven, npm, Python, Go, apt/yum, generic; regional/multi-regional, CMEK, IAM per repo, immutable tags, cleanup policies) — Container Registry is shut down | |
| Scan | **Artifact Analysis** (formerly Container Analysis): automatic **vulnerability scanning** on push (OS packages + language packages), on-demand scanning API, continuous re-scan of recent images, SBOM generation (SPDX/CycloneDX), stores metadata as **notes/occurrences** (Grafeas) | Findings flow to SCC |
| Deploy gate | **Binary Authorization**: policy per project (default rule + cluster/Cloud Run service specific rules) requiring **attestations** signed by **attestors** (KMS/PGP keys) — e.g., "passed vuln scan", "QA approved"; **dry-run**, **breakglass** annotation (audit-logged), **continuous validation** logs running Pods that violate policy; supported on GKE, Cloud Run, GKE Enterprise (incl. on-prem, attached), Cloud Deploy integration; allow-list images by pattern (e.g., only from `us-docker.pkg.dev/my-proj/*`) | Answer to "only images built by our pipeline may run" |
| Delivery | **Cloud Deploy** pipelines with approvals, canary/blue-green; **Cloud Deploy + Binary Authorization + Artifact Registry** = attested promotion | |
| Runtime | GKE security posture, Container Threat Detection, Workload vulnerability scanning, Policy Controller constraints, GKE Sandbox, image signing with **Sigstore/cosign** in Artifact Registry | |

## Securing AI workloads

- **Model Armor**: model-agnostic screening of **prompts and responses** for prompt injection/jailbreak, sensitive data (SDP infoTypes), malicious URLs, harmful content categories, and PDF content; defined as **templates**; enforced via API, Vertex AI integration, **Apigee** policies, or as **service extensions** on the Application Load Balancer; findings in SCC.
- **Training data**: run **Sensitive Data Protection** de-identification before fine-tuning or building embeddings; restrict datasets with IAM/BigQuery column policies; use Dataplex lineage to prove which data trained which model.
- **Secure deployment**: **private endpoints via Private Service Connect** (no public prediction URLs), **VPC Service Controls** perimeters including `aiplatform.googleapis.com`, `notebooks.googleapis.com`, `bigquery.googleapis.com`; **CMEK** on datasets, models, endpoints, pipelines, Workbench and Feature Store; **Workload Identity / dedicated service accounts** for pipelines (`roles/aiplatform.user` scoped per project); Vertex AI Workbench with no external IP, idle shutdown, and Data Access logging; disable root; Colab Enterprise with restricted runtimes.
- **Governance**: Google does not use customer prompts/data to train foundation models; **zero data retention** configurations for Gemini (no caching / abuse-monitoring opt-out with approval); **Access Transparency** covers Vertex AI; **org policy** to restrict Model Garden models and to disallow public endpoints; **safety filters** (harm categories/thresholds) and system instructions; **SynthID** watermarking for generated media; **Gen AI evaluation** and red-teaming before launch; logging of prompts/responses to BigQuery with SDP masking for audit; SCC AI Protection (Enterprise) inventories AI assets and detects threats.
- **Agents/tools**: scope agent tool credentials with least privilege SAs; validate tool outputs; human-in-the-loop for actions with side effects; Apigee as the policy enforcement point for LLM APIs (quota, key management, Model Armor policies, token-based rate limits).

> **Exam tip:** "Chatbot must not leak customer PII from the knowledge base and must resist prompt injection" → Model Armor templates on prompts *and* responses plus SDP de-identification of source data; not just "add a system prompt".

## 3.2 Designing for compliance

### Regulations and what Google Cloud gives you

| Regime | Scope | Google Cloud approach |
|---|---|---|
| **HIPAA** (US health data / PHI) | Covered entities & business associates | Sign the **Business Associate Agreement (BAA)** via console; use only **HIPAA-covered services**; you are still responsible for configuration (IAM, encryption, audit logs, no PHI in log messages/labels); Assured Workloads HIPAA control package; Cloud Healthcare API for FHIR/DICOM/HL7v2 with de-identification |
| **GDPR** (EU personal data) | Controllers/processors handling EU residents' data | Cloud Data Processing Addendum, SCCs, **data residency** via `gcp.resourceLocations` + regional services, **EU Sovereign Controls** / Assured Workloads EU regions and support, data subject rights (deletion → crypto-shredding with CMEK, BigQuery `DELETE`, retention automation), SDP for discovery/minimization, Access Transparency/Approval |
| **PCI DSS** (cardholder data) | Merchants and processors | Google Cloud is a **PCI DSS Level 1 service provider**; your **CDE scope** is your responsibility — reduce scope with **tokenization** (SDP FPE/Payment provider tokens), network segmentation (separate projects/VPCs, firewall policies, VPC-SC), no cardholder data in logs, Cloud Armor WAF for public apps (Req. 6), quarterly scans, KMS/HSM key management with dual control |
| **COPPA** (children under 13, US) | Consumer apps aimed at children | Verifiable parental consent, data minimization, restricted profiling; on Google Cloud: SDP to detect child PII, retention lifecycle rules, Identity Platform for consent flows; it is a *design* obligation, not a service you turn on |
| **CCPA/CPRA, LGPD, PIPEDA** | Regional privacy | Same toolset: inventory (Dataplex/Data Catalog), residency, deletion, access logs |
| **FedRAMP** (US federal) Moderate/High, **DoD IL2/4/5**, **CJIS**, **ITAR**, **IRS 1075** | US public sector | **Assured Workloads** folders with the matching control package: restricts regions, personnel (US persons support), services, and enforces CMEK/EKM and Access Approval where required; FedRAMP High authorized regions |
| **Data sovereignty** (EU, Japan, Australia, Canada, KSA, etc.) | Government/critical infrastructure | Assured Workloads regional packages, **Sovereign Controls by partners** (T-Systems Sovereign Cloud, S3NS in France, Thales) with partner-held keys via EKM and partner-run support; **Google Distributed Cloud** air-gapped for disconnected requirements |
| **SOC 1/2/3, ISO/IEC 27001, 27017, 27018, 27701, CSA STAR** | Industry attestations of *Google's* controls | Download reports from **Compliance Reports Manager**; they cover the platform, not your workload — shared responsibility |

> **Trap:** "Google Cloud is HIPAA-certified so our app is compliant" — wrong. There is no HIPAA certification; you sign the BAA, restrict to covered services, and configure controls yourself.

### Assured Workloads and sovereign controls

- **Assured Workloads** = a *folder* with a **control package** (e.g., FedRAMP Moderate, FedRAMP High, IL4, CJIS, HIPAA, HITRUST, ITAR, EU Regions and Support with Sovereignty Controls, Japan Regions, Canada Protected B, Australia Regions, KSA). It auto-applies org policies (resource locations, service restrictions, CMEK requirements), scopes **support personnel** by location/citizenship, and offers **monitoring** of violations and **Key Access Justifications**. Create it up front — you cannot retrofit some restrictions onto existing projects.
- **Sovereignty stack**: data residency (`gcp.resourceLocations`) → operational sovereignty (Access Transparency + **Access Approval** so Google support cannot touch data without your approval; Key Access Justifications with EKM lets you deny decryption) → software sovereignty (open source, GKE Enterprise portability, Google Distributed Cloud).
- **Access Transparency** logs Google staff actions; **Access Approval** makes you approve them in advance (integrates with KMS/EKM to deny cryptographically). Both are expected answers for "prove/control that provider personnel can't access data".

### Data governance controls in BigQuery and Dataplex

- **Column-level security**: define a **policy tag taxonomy** (Dataplex/Data Catalog), attach tags to columns, grant `roles/datacatalog.categoryFineGrainedReader` on the tag to users who may read; others get denied or, with **data policies**, see **dynamic masking** (nullify, hash, default value, partial email/last four) via `roles/bigquerydatapolicy.maskedReader`. Enforce access control on the taxonomy.
- **Row-level security**: `CREATE ROW ACCESS POLICY ... GRANT TO ("group:emea@…") FILTER USING (region = "EMEA")`; combine with column policies. **Authorized views/datasets/routines** share query results without granting table access. **Dataset/table expiration** and **partition expiration** implement retention; **CMEK** per dataset; BigQuery Data Access logs are on by default.
- **Dataplex Universal Catalog**: discover and catalog assets across BigQuery, Cloud Storage, Spanner, Vertex; **data lineage** (which pipeline produced which table), **data profiling and data quality** scans, business glossary, **SDP discovery** attaches sensitivity aspects; lakes/zones with automatic policy propagation to underlying buckets/datasets — the "governance layer" answer.
- **Retention & lifecycle**: Cloud Storage retention policies + Bucket Lock (WORM), object holds; Cloud Logging bucket retention + lock; BigQuery time travel/snapshots; Spanner/Cloud SQL backup retention; SDP + lifecycle rules for minimization; **Cloud Storage Autoclass** and Archive for long retention at low cost.

### Audits and evidence

- Centralize logs (aggregated org sink) into a locked, CMEK-protected bucket or BigQuery dataset in a project only auditors and security can read; keep Admin Activity ≥ 400 days by default and extend Data Access retention per policy (e.g., 1 year for PCI, 6 years for HIPAA documentation retention).
- Use **SCC compliance dashboards** (CIS Google Cloud Benchmark, PCI DSS, NIST 800-53, ISO 27001) to export findings; **Audit Manager** (in SCC) generates control evidence reports mapped to frameworks; **Compliance Reports Manager** supplies Google's SOC/ISO/PCI AoC artifacts; **Cloud Asset Inventory** exports prove configuration at a point in time; Policy Analyzer answers "who had access on date X".
- Penetration testing on your own workloads needs no Google pre-approval (follow AUP); Web Security Scanner for OWASP checks; **Security Health Analytics** for continuous CIS drift; **Recommender** for over-privileged identities as periodic access reviews.
- Map each requirement to control + evidence: encryption (KMS key inventory + Data Access logs), access (IAM policy exports + Policy Analyzer), segregation (VPC-SC perimeters, org policies), incident response (SCC findings history, Pub/Sub → SOAR), change management (Admin Activity logs + Cloud Deploy approvals).

## Key takeaways

- Avoid basic roles; grant predefined roles to Google Groups at the lowest scope that works; IAM inherits downward as a union, so restrict via deny policies, PAB, or hierarchy design — not by hoping a child policy "removes" access.
- Memorize the SA role trio: `serviceAccountUser` (attach/act as), `serviceAccountTokenCreator` (impersonate/mint tokens), `workloadIdentityUser` (external/KSA identity may impersonate).
- Eliminate SA keys: attached SAs, impersonation, Workload Identity Federation for GKE and external CI/multicloud, Workforce Identity Federation for external humans; enforce with `iam.disableServiceAccountKeyCreation`.
- Org policy = guardrails that even owners can't bypass: `gcp.resourceLocations` (residency), `iam.allowedPolicyMemberDomains`, `compute.vmExternalIpAccess`, `storage.publicAccessPrevention`, `gcp.restrictNonCmekServices`.
- Encryption ladder: default → CMEK (customer control, key location = data location, service agent needs `cryptoKeyEncrypterDecrypter`) → Cloud HSM (FIPS 140-2 L3) → Cloud EKM with Key Access Justifications (Google never holds key) → CSEK (GCS/PD only, you supply key per call).
- KMS hierarchy project → location → key ring → key → version; automatic rotation for symmetric keys; scheduled destruction (default 30 days) enables crypto-shredding; keep keys in a separate security-owned project.
- Secret Manager for secrets with versions, IAM per secret, rotation via Pub/Sub; never bake secrets into images or metadata.
- Audit logs: Admin Activity and System Event always on with 400-day retention; Data Access off by default (except BigQuery) with 30 days; route via aggregated sinks to locked buckets/BigQuery/Pub/Sub (SIEM).
- VPC Service Controls stop exfiltration from Google APIs; require restricted VIP, access levels, ingress/egress rules; run dry-run first; one perimeter per project; not a substitute for IAM.
- IAP (web + TCP via 35.235.240.0/20) with OS Login and access levels replaces VPNs/bastions; Chrome Enterprise Premium adds device posture and browser protection for zero trust.
- Supply chain: Artifact Registry + Artifact Analysis scanning + Cloud Build SLSA L3 provenance + Binary Authorization attestations (with break-glass and continuous validation) + Assured OSS.
- Securing AI: Model Armor on prompts/responses, SDP on training data, PSC private endpoints, VPC-SC around Vertex AI, CMEK, no training on customer data, org policy on model access.
- Compliance is shared responsibility: sign the HIPAA BAA and use covered services; reduce PCI scope with tokenization and segmentation; use Assured Workloads folders for FedRAMP/IL/EU sovereignty; Access Transparency + Access Approval for provider-access control.
- BigQuery governance: policy tags for column-level security, dynamic masking with `maskedReader`, row access policies, authorized views; Dataplex for catalog, lineage, and quality; Compliance Reports Manager and Audit Manager for evidence.

## Quick self-check

- Q: A CI pipeline on GitHub Actions must deploy to Cloud Run without any stored credentials. Design? — **A:** Workload Identity Federation pool + OIDC provider for GitHub with an attribute condition on the repo, granting the federated principal (or an impersonated SA via `roles/iam.workloadIdentityUser`) `roles/run.developer` and `roles/iam.serviceAccountUser` on the runtime SA.
- Q: Regulators require that Google can never access encryption keys and every key use must be justified. Which option? — **A:** Cloud EKM (external key manager) with Key Access Justifications; pair with Access Approval and Assured Workloads if sovereignty is in scope.
- Q: Which audit logs are on by default, and for how long are they kept? — **A:** Admin Activity and System Event (400 days in `_Required`, not configurable); Policy Denied on by default (30 days in `_Default`); Data Access is off by default except BigQuery.
- Q: Analysts in project B keep failing to query a BigQuery dataset in perimeter-protected project A even with `bigquery.dataViewer`. Why and fix? — **A:** VPC Service Controls blocks the cross-perimeter call; add an ingress rule (or put project B in the same perimeter / an egress rule from A) rather than granting more IAM.
- Q: Admins need SSH to VMs that have no public IPs, with MFA and full audit. Configure? — **A:** IAP TCP forwarding (allow 35.235.240.0/20 to port 22), `roles/iap.tunnelResourceAccessor`, OS Login with 2FA enforced via `compute.requireOsLogin`, Admin Activity + Data Access logs on.
- Q: Only container images built by your pipeline and free of critical CVEs may run in prod GKE. Which controls? — **A:** Cloud Build produces provenance, Artifact Analysis scans in Artifact Registry, an attestor signs passing images, Binary Authorization policy requires that attestation (continuous validation on), Policy Controller optionally as a second gate.
- Q: A customer-support LLM app must not reveal PII from tickets and must resist jailbreaks. What do you add? — **A:** Model Armor templates screening prompts and responses (prompt injection, sensitive data with SDP infoTypes), SDP de-identification of the ticket corpus before indexing, private endpoint + VPC-SC, and response logging with masking.
- Q: Finance must see full credit card numbers, support only the last four, and everyone else nothing, from the same BigQuery table. How? — **A:** Policy tag on the column; grant `datacatalog.categoryFineGrainedReader` to finance, a masking data policy (last four) with `bigquerydatapolicy.maskedReader` to support; others are denied on that column.
- Q: What distinguishes Assured Workloads from simply setting `gcp.resourceLocations`? — **A:** Assured Workloads bundles residency with personnel/support restrictions, service allow-lists, CMEK/EKM and Access Approval requirements, and continuous compliance monitoring for a named regime (FedRAMP, IL4, EU sovereignty); the org policy alone controls only resource location.
