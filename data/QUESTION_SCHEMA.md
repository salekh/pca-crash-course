# PCA Question Bank — Schema & Style Guide

Every question file is a JSON array of question objects stored under `data/questions/`.
File naming: `<batch-id>.json` (e.g. `d1-business-a.json`, `cs-ehr-a.json`).

## Object schema

```json
{
  "id": "d1-bus-001",
  "domain": 1,
  "topic": "Non-functional requirements",
  "difficulty": "medium",
  "type": "single",
  "caseStudy": null,
  "question": "Your company ... What should you do?",
  "options": [
    "Option A text",
    "Option B text",
    "Option C text",
    "Option D text"
  ],
  "answer": [2],
  "explanation": "Why the correct answer is correct AND why each distractor is wrong.",
  "refs": ["https://cloud.google.com/architecture/framework"]
}
```

| Field | Type | Rules |
|---|---|---|
| `id` | string | Globally unique. Prefix pattern `d<domain>-<slug>-<nnn>` or `cs-<case>-<nnn>`. |
| `domain` | int 1–6 | Exam section (see below). Case-study questions still carry the most relevant domain. |
| `topic` | string | Short topic label, e.g. "Cloud Interconnect", "IAM", "Spanner". Used for filtering & analytics. |
| `difficulty` | `easy` \| `medium` \| `hard` | Aim for ~20% easy, ~55% medium, ~25% hard. |
| `type` | `single` \| `multi` | `multi` questions MUST say "(Choose two.)" or "(Choose three.)" at the end of the stem. ~15% of questions should be `multi`. |
| `caseStudy` | `null` \| `"ehr"` \| `"cymbal"` \| `"altostrat"` \| `"knightmotives"` | Set only if the stem depends on the case study. Stem must start with e.g. "For this question, refer to the EHR Healthcare case study." |
| `question` | string | Scenario-based stem, 2–6 sentences. End with "What should you do?", "Which approach should you recommend?", "What should you do first?" etc. |
| `options` | string[] | Exactly 4 options for `single`; 4–6 for `multi`. Plausible distractors, similar length, no "all of the above". |
| `answer` | int[] | Zero-based indices into `options`. Length 1 for `single`; 2–3 for `multi`. Vary the correct position (do NOT always use index 0/1). |
| `explanation` | string | 3–8 sentences. State why the answer is correct and address each distractor briefly ("Option A is wrong because…"). |
| `refs` | string[] | 1–3 official Google Cloud documentation URLs (cloud.google.com). |

## Exam sections (domain numbers)

1. Designing and planning a cloud solution architecture (~25%)
2. Managing and provisioning a cloud solution infrastructure (~17.5%)
3. Designing for security and compliance (~17.5%)
4. Analyzing and optimizing technical and business processes (~15%)
5. Managing implementation (~12.5%)
6. Ensuring solution and operations excellence (~12.5%)

## Style rules — make it feel like the real exam

* Real PCA questions are **scenario-based**: a company, a constraint (cost, latency, compliance, minimal ops overhead, existing skill set), and a goal. Never ask trivia like "What does IAM stand for?".
* Use Google's exam phrasing: "You want to follow Google-recommended practices", "with the least amount of operational overhead", "while minimizing cost", "You need to ensure…", "What should you do?".
* Distractors must be **technically valid-sounding but violate a stated constraint** (wrong region strategy, more ops overhead, more cost, wrong consistency model, unnecessary service, anti-pattern such as service-account keys, etc.).
* Cover current products and names: Cloud Run (not Cloud Functions 1st gen — say "Cloud Run functions"), Vertex AI / Agent Builder / Model Garden / Gemini models, AI Hypercomputer, Gemini Cloud Assist, Migration Center, Private Service Connect, Cloud NGFW, Chrome Enterprise Premium (formerly BeyondCorp Enterprise), Model Armor, Sensitive Data Protection (formerly DLP), Cloud Logging/Monitoring (Observability), Cloud Deploy, Artifact Registry, Binary Authorization, Assured Workloads, Cloud KMS/HSM/EKM, Workload Identity Federation, Backup and DR Service, Spanner, AlloyDB, Bigtable, BigQuery, Dataflow, Dataproc, Pub/Sub, Memorystore, Filestore, Cloud Storage classes, Cloud Interconnect (Dedicated/Partner/Cross-Cloud), HA VPN, Cloud Router, Cloud Armor, Cloud CDN, Load balancer families (global external ALB, regional, internal, passthrough NLB, proxy NLB), GKE Autopilot/Standard/Enterprise, Anthos → "GKE Enterprise", Config Connector, Terraform, Cloud Build, Apigee, Cloud Workstations, Cloud Shell, gcloud/gsutil/bq, emulators.
* Explicitly apply the **Google Cloud Well-Architected Framework** pillars (operational excellence, security/privacy/compliance, reliability, cost optimization, performance optimization, sustainability) where relevant.
* Vary the correct option index uniformly across 0–3.
* No duplicate or near-duplicate stems within or across files. Vary company types (fintech, healthcare, retail, gaming, media, manufacturing, public sector, startups).
* Keep JSON strictly valid: escape quotes, no trailing commas, no comments.
