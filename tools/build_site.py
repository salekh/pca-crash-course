#!/usr/bin/env python3
"""Build step for the PCA crash-course static site.

- Validates + merges question files into site/data/questions.json (via validate_questions).
- Copies study modules (data/study/*.md) into site/data/study/ and writes an index.json
  with the parsed front matter, a heading outline and a word count.
- Writes site/data/meta.json with bank statistics used by the landing page.

Usage: python3 tools/build_site.py
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDY_SRC = os.path.join(ROOT, "data", "study")
SITE = os.path.join(ROOT, "site")
STUDY_DST = os.path.join(SITE, "data", "study")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        if re.fullmatch(r"-?\d+", v):
            v = int(v)
        meta[k.strip()] = v
    return meta, text[m.end():]


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)


def outline(body):
    out = []
    in_code = False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{2,3})\s+(.*)", line)
        if m:
            out.append({"level": len(m.group(1)), "text": m.group(2).strip(), "id": slugify(m.group(2))})
    return out


def build_study():
    os.makedirs(STUDY_DST, exist_ok=True)
    index = []
    for fn in sorted(os.listdir(STUDY_SRC)):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(STUDY_SRC, fn), encoding="utf-8") as f:
            text = f.read()
        meta, body = parse_front_matter(text)
        if "id" not in meta:
            print(f"WARN {fn}: missing front matter id", file=sys.stderr)
            continue
        words = len(re.findall(r"\w+", re.sub(r"\|", " ", body)))
        entry = {
            "id": meta["id"],
            "file": fn,
            "title": meta.get("title", fn),
            "domain": int(meta.get("domain", 0)),
            "order": int(meta.get("order", 99)),
            "minutes": int(meta.get("minutes", max(10, round(words / 220)))),
            "summary": meta.get("summary", ""),
            "words": words,
            "outline": outline(body),
        }
        index.append(entry)
        with open(os.path.join(STUDY_DST, fn), "w", encoding="utf-8") as f:
            f.write(body)
    index.sort(key=lambda e: e["order"])
    with open(os.path.join(STUDY_DST, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)
    print(f"study modules: {len(index)}  total words: {sum(e['words'] for e in index)}")
    return index


# Coarse topic areas used by the analytics views. First matching rule wins; rules are
# matched against the fine-grained topic first, then topic + stem.
AREA_RULES = [
    ("Gen AI, agents & AI safety", r"gemini|gen ?ai|generative|llm|rag\b|grounding|agent builder|agent engine|adk\b|model armor|imagen|vector search|prompt|tuning|model garden|notebooklm|synthid|conversational agents|dialogflow|context caching|provisioned throughput"),
    ("AI/ML platform (Vertex AI, APIs, accelerators)", r"vertex|ml\b|machine learning|tpu|gpu|hypercomputer|bigquery ml|bqml|document ai|vision api|speech|translation|video intelligence|natural language|feature store|model monitoring|training|inference|recommendations ai|search for commerce|dynamic workload"),
    ("API management (Apigee, API Gateway)", r"apigee|api gateway|cloud endpoints|api product|api management|api key"),
    ("Migration & data transfer", r"migrat|transfer appliance|storage transfer|datastream|database migration|dms\b|rehost|replatform|refactor|6 rs|lift-and-shift|cutover|vmware engine|mainframe|bare metal"),
    ("Business processes, stakeholders & adoption", r"stakeholder|change management|adoption framework|raci|kpi|roi|tco|capex|opex|build vs buy|build-vs-buy|skills|training plan|center of excellence|ccoe|decision|adr\b|proof of concept|poc\b|support plan|customer success|business continuity|bia\b|bcp"),
    ("Cost optimization & billing", r"cost|billing|cud|committed use|sustained use|spot vm|preemptible|budget|finops|pricing|rightsiz|right-siz|discount|egress charge|chargeback|showback"),
    ("DR, backup & high availability", r"disaster recovery|\bdr\b|rpo|rto|backup|snapshot|failover|high availability|\bha\b|multi-region|regional pd|warm standby|pilot light|hot standby|point-in-time|pitr|resilien"),
    ("Monitoring, SLOs & alerting", r"slo|sli\b|sla\b|error budget|burn rate|monitoring|alert|uptime check|dashboard|prometheus|ops agent|golden signals|profiler|trace|error reporting|observab|synthetic|incident|postmortem|toil|on-call|sre\b"),
    ("Logging & audit logs", r"logging|log sink|log bucket|log router|audit log|data access log|log analytics|log-based|log retention|vpc flow log|firewall log"),
    ("CI/CD & release management", r"ci/cd|cicd|cloud build|cloud deploy|artifact registry|canary|blue[- /]green|rolling update|rollout|release channel|deployment strateg|gitops|config sync|skaffold|feature flag|traffic split|revision|pipeline trigger|dora"),
    ("Security posture & supply chain", r"binary authorization|artifact analysis|vulnerabilit|slsa|assured oss|supply chain|security command center|scc\b|web security scanner|shielded|confidential vm|container-optimized|posture|event threat|pen test|penetration"),
    ("Compliance & governance", r"hipaa|gdpr|pci|coppa|fedramp|compliance|assured workloads|sovereign|residency|data governance|dataplex|policy tag|column-level|row-level|masking|sensitive data protection|dlp|de-identif|access transparency|access approval|retention polic|bucket lock|regulat"),
    ("IAM, identity & access", r"iam\b|role|service account|workload identity|workforce identity|federation|cloud identity|sso|saml|oidc|2sv|mfa|least privilege|impersonat|org polic|organization polic|resource hierarchy|folder|deny polic|principal access|privileged access|iap\b|identity-aware|os login|permission"),
    ("Encryption & key management", r"cmek|csek|kms|hsm|ekm|encryption|key rotation|secret manager|key access justification|confidential computing"),
    ("Network security (Armor, NGFW, IDS, VPC-SC)", r"cloud armor|waf|ddos|firewall|ngfw|cloud ids|intrusion|vpc service controls|vpc-sc|perimeter|access context|zero trust|beyondcorp|chrome enterprise premium|rate limit"),
    ("Load balancing, CDN & DNS", r"load balanc|\balb\b|\bnlb\b|cloud cdn|cdn\b|cloud dns|dns\b|neg\b|network endpoint group|health check|ssl polic|certificate manager|global access|anycast"),
    ("VPC design & hybrid connectivity", r"vpc|subnet|interconnect|vpn|cloud router|bgp|peering|shared vpc|network connectivity center|ncc\b|private google access|private service connect|psc\b|private services access|cloud nat|\bnat\b|cidr|ip address|routing|route\b|hybrid connect"),
    ("BigQuery & analytics", r"bigquery|bq\b|looker|analytics hub|bi engine|data warehouse|slot|partition|clustering|materialized view|data mart"),
    ("Data pipelines & messaging", r"dataflow|dataproc|pub/sub|pubsub|data fusion|composer|airflow|beam|spark|hadoop|kafka|eventarc|workflows|cloud tasks|scheduler|etl|elt|streaming|event-driven|batch processing|cdc\b"),
    ("Relational databases (Cloud SQL, AlloyDB, Spanner)", r"cloud sql|alloydb|spanner|postgres|mysql|sql server|relational|oracle|read replica"),
    ("NoSQL & caching (Bigtable, Firestore, Memorystore)", r"bigtable|firestore|datastore|memorystore|redis|valkey|memcache|nosql|wide-column|document database|key-value|cache"),
    ("Cloud Storage (objects)", r"cloud storage|gcs\b|bucket|object|storage class|nearline|coldline|archive|autoclass|lifecycle|signed url|turbo replication|soft delete|versioning"),
    ("Block & file storage", r"persistent disk|hyperdisk|local ssd|filestore|netapp|nfs|block storage|file storage|parallelstore|lustre|disk"),
    ("GKE & Kubernetes", r"gke|kubernetes|k8s|autopilot|node pool|pod|cluster|helm|kustomize|gateway api|service mesh|istio|anthos|fleet|policy controller|workload|hpa|vpa"),
    ("Serverless (Cloud Run, functions, App Engine)", r"cloud run|cloud functions|run functions|app engine|serverless|function|concurrency|min instances|cold start"),
    ("Compute Engine & VMs", r"compute engine|\bvm\b|vms\b|instance|machine type|machine famil|managed instance group|mig\b|autoscal|sole-tenant|sole tenant|reservation|custom machine|startup script|image famil|golden image|os config|vm manager|patch|live migration|spot"),
    ("IaC & developer tooling (Terraform, gcloud, SDKs)", r"terraform|infrastructure as code|iac\b|infrastructure manager|config connector|deployment manager|gcloud|gsutil|cloud shell|cloud code|workstation|emulator|client librar|sdk|api access|application default|adc\b|exponential backoff|quota|rest api|grpc"),
    ("Architecture principles & Well-Architected Framework", r"well-architected|pillar|requirement|trade-off|tradeoff|architecture|design|scalab|performance|latency|sustainab|operational excellence|reliability|caching strategy|microservice|monolith|integration pattern|coupling"),
]
AREA_RULES_C = [(name, re.compile(rx, re.I)) for name, rx in AREA_RULES]
AREA_DOMAIN_FALLBACK = {
    1: "Architecture principles & Well-Architected Framework",
    2: "Compute Engine & VMs",
    3: "IAM, identity & access",
    4: "Business processes, stakeholders & adoption",
    5: "IaC & developer tooling (Terraform, gcloud, SDKs)",
    6: "Monitoring, SLOs & alerting",
}


def classify_area(q):
    topic = q.get("topic", "")
    for name, rx in AREA_RULES_C:
        if rx.search(topic):
            return name
    blob = topic + " " + q.get("question", "") + " " + " ".join(q.get("options", []))
    # Score by number of distinct matches on the full text; ties -> earlier rule.
    best, best_n = None, 0
    for name, rx in AREA_RULES_C:
        n = len(rx.findall(blob))
        if n > best_n:
            best, best_n = name, n
    return best or AREA_DOMAIN_FALLBACK.get(q.get("domain"), "Other")


def build_questions():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "validate_questions.py"), "--build"],
                       capture_output=True, text=True)
    tail = "\n".join(r.stdout.strip().splitlines()[-9:])
    print(tail)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit("question validation failed")
    path = os.path.join(SITE, "data", "questions.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    qs = data if isinstance(data, list) else data.get("questions", [])
    for q in qs:
        q["area"] = classify_area(q)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, separators=(",", ":"))
    areas = Counter(q["area"] for q in qs)
    print("areas:", len(areas))
    for a, n in areas.most_common():
        print(f"  {n:4d}  {a}")
    return qs


def build_meta(questions, study):
    qs = questions
    topics = Counter((q["domain"], q["topic"]) for q in qs)
    meta = {
        "questionCount": len(qs),
        "officialSampleCount": sum(1 for q in qs if q.get("officialSample")),
        "byDomain": dict(Counter(q["domain"] for q in qs)),
        "byDifficulty": dict(Counter(q["difficulty"] for q in qs)),
        "byCaseStudy": dict(Counter(q["caseStudy"] or "none" for q in qs)),
        "topicCount": len(topics),
        "areaCount": len(set(q["area"] for q in qs)),
        "studyModules": len(study),
        "studyWords": sum(e["words"] for e in study),
    }
    with open(os.path.join(SITE, "data", "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print("meta:", json.dumps(meta))


if __name__ == "__main__":
    study = build_study()
    questions = build_questions()
    build_meta(questions, study)
