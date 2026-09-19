// Shared constants, data loading, persistent store, sampling and analytics engine.

export const DOMAINS = {
  1: { short: 'Designing & planning', title: 'Designing and planning a cloud solution architecture', weight: 0.25, modules: ['d1-design', 'd1-nsc'] },
  2: { short: 'Provisioning infrastructure', title: 'Managing and provisioning a cloud solution infrastructure', weight: 0.175, modules: ['d2-provision'] },
  3: { short: 'Security & compliance', title: 'Designing for security and compliance', weight: 0.175, modules: ['d3-security'] },
  4: { short: 'Technical & business processes', title: 'Analyzing and optimizing technical and business processes', weight: 0.15, modules: ['d4d5-processes'] },
  5: { short: 'Managing implementation', title: 'Managing implementation', weight: 0.125, modules: ['d4d5-processes'] },
  6: { short: 'Operations excellence', title: 'Ensuring solution and operations excellence', weight: 0.125, modules: ['d6-operations'] },
};

export const CASES = {
  ehr: {
    name: 'EHR Healthcare',
    file: 'case_study_ehr_healthcare.txt',
    industry: 'Healthcare SaaS',
    driver: 'Expiring colocation lease & rapid SaaS growth',
    sla: '99.9% availability · HIPAA BAA',
    blurb: 'Healthcare SaaS provider migrating from multiple colocation facilities to Google Cloud under HIPAA, with legacy on-prem insurance integrations.',
    arch: [
      { req: 'Expiring colocation lease + containerized web apps', services: ['GKE Regional Clusters', 'Migrate to Containers', 'Artifact Registry'], rationale: 'Run containerized web apps on regional multi-zone GKE for 99.9%+ availability and rapid cutover before lease expiration.', trap: 'Avoid zonal GKE clusters or manual VM lift-and-shift for already containerized apps.' },
      { req: 'Maintain legacy on-prem insurance file/API interfaces', services: ['Dedicated Interconnect', 'HA VPN', 'Apigee API Management'], rationale: 'Dedicated Interconnect (or Partner Interconnect) + HA VPN provides low-latency, encrypted hybrid connectivity; Apigee standardizes partner API onboarding.', trap: 'Do not force legacy insurance systems to migrate immediately when the case study states no plan to upgrade them now.' },
      { req: 'Relational & NoSQL databases (MySQL, MS SQL Server, Redis, MongoDB)', services: ['Cloud SQL for MySQL (HA)', 'Cloud SQL for SQL Server (HA)', 'Memorystore for Redis', 'MongoDB Atlas'], rationale: 'Managed database equivalents eliminate administration overhead while Regional HA satisfies the 99.9% uptime SLA.', trap: 'Do not rewrite MS SQL Server schemas to Spanner unless global multi-region active-active writes are required.' },
      { req: 'Centralized Active Directory user management', services: ['Google Cloud Directory Sync (GCDS)', 'Cloud Identity / Workspace SAML SSO', 'Managed Service for Microsoft AD'], rationale: 'Sync existing AD users/groups via GCDS and use AD FS/SAML for single sign-on without managing separate cloud identities.', trap: 'Avoid manually recreating user accounts in IAM or storing static credentials.' },
      { req: 'Ignored email alerts & fragmented open-source monitoring', services: ['Cloud Monitoring', 'Cloud Logging', 'Alerting Policies (PagerDuty/Slack/SMS)'], rationale: 'Consolidate observability into Google Cloud Observability and replace ignored email blasts with symptom-based SLO burn-rate alerts routed to on-call channels.', trap: 'Keeping self-managed Nagios/Prometheus without centralized alert routing violates operational excellence requirements.' },
      { req: 'Industry trend predictions & HIPAA regulatory compliance', services: ['BigQuery', 'Vertex AI', 'Sensitive Data Protection (DLP)', 'Assured Workloads / HIPAA BAA'], rationale: 'Ingest provider data into BigQuery for analytics/ML trend forecasting; de-identify PHI with Sensitive Data Protection under a signed HIPAA BAA.', trap: 'Never train ML models on raw unmasked PHI without de-identification or proper BAA boundaries.' }
    ]
  },
  cymbal: {
    name: 'Cymbal Retail',
    file: 'case_study_cymbal_retail.txt',
    industry: 'Omnichannel Digital Retail',
    driver: 'Generative AI catalog enrichment & conversational commerce',
    sla: 'High scalability · PCI DSS & PII compliance',
    blurb: 'Omnichannel retailer adopting generative AI for product attributes, imagery, and conversational commerce while modernizing legacy data pipelines.',
    arch: [
      { req: 'Automated product attribute, description & image generation', services: ['Vertex AI (Gemini 1.5 Pro/Flash)', 'Imagen on Vertex AI', 'Cloud Storage'], rationale: 'Gemini extracts structured attributes/descriptions from supplier docs/images; Imagen generates product color variations and background replacements.', trap: 'Avoid training custom vision/LLM models from scratch when pre-trained foundation models on Vertex AI solve catalog enrichment out of the box.' },
      { req: 'Human-in-the-Loop (HITL) review UI for associates', services: ['Cloud Run', 'Firestore / AlloyDB', 'Identity-Aware Proxy (IAP)'], rationale: 'Deploy a lightweight internal web UI on Cloud Run behind IAP where associates approve, edit, or reject GenAI suggestions before catalog publication.', trap: 'Never push unverified generative AI outputs directly into the production catalog when HITL review is explicitly required.' },
      { req: 'Conversational commerce & natural language product discovery', services: ['Vertex AI Search for Commerce', 'Conversational Agents (Dialogflow CX)'], rationale: 'Vertex AI Search for Commerce provides retail-tuned vector + keyword search with browse/recommendation capabilities integrated into Dialogflow CX virtual agents.', trap: 'Do not query operational SQL databases directly with LIKE queries for natural-language shopping discovery.' },
      { req: 'Reduce call center staffing costs & modernize legacy IVR', services: ['Customer Engagement Suite / Contact Center AI (CCAI)', 'Conversational Agents', 'Agent Assist'], rationale: 'Replace static IVR trees with AI virtual agents that resolve routine orders autonomously and assist human agents in real time.', trap: 'Retaining manual order entry by call center agents for standard transactions fails the cost-reduction business goal.' },
      { req: 'Replace legacy SFTP & batch ETL silos', services: ['Storage Transfer Service', 'Pub/Sub', 'Dataflow', 'BigQuery'], rationale: 'Ingest supplier files into Cloud Storage and stream events via Pub/Sub + Dataflow into BigQuery for a unified real-time customer and inventory view.', trap: 'Do not lift-and-shift fragile cron SFTP scripts onto Compute Engine VMs.' },
      { req: 'Customer data security, PCI DSS & AI safety guardrails', services: ['Model Armor', 'Sensitive Data Protection', 'Cloud Armor'], rationale: 'Model Armor protects virtual agents against prompt injection and PII leakage; Sensitive Data Protection redacts PII/PCI data across logs and warehouses.', trap: 'Relying solely on system prompt instructions without Model Armor or DLP leaves public-facing retail chatbots vulnerable to jailbreaks.' }
    ]
  },
  altostrat: {
    name: 'Altostrat Media',
    file: 'case_study_altostrat_media.txt',
    industry: 'Digital Media & Streaming',
    driver: 'Multimodal AI content discovery & hybrid Kubernetes governance',
    sla: '24/7 availability · Cost-optimized petabyte storage',
    blurb: 'Media platform standardizing Kubernetes across on-prem and cloud while deploying multimodal AI for summarization, moderation, and discovery.',
    arch: [
      { req: 'Consistent Kubernetes management across cloud & on-premises', services: ['GKE Enterprise (Fleets)', 'Config Sync', 'Policy Controller', 'Cloud Deploy'], rationale: 'GKE Enterprise unifies cluster fleet management across Google Cloud and on-prem ingestion nodes with GitOps policy enforcement via Config Sync.', trap: 'Managing standalone kubeconfigs and separate CI/CD scripts per environment violates the centralized platform requirement.' },
      { req: 'Optimize Cloud Storage costs for a growing petabyte media library', services: ['Cloud Storage Autoclass', 'Object Lifecycle Management', 'Cloud CDN'], rationale: 'Autoclass automatically transitions infrequently accessed audio/video masters to Nearline, Coldline, and Archive tiers without operational overhead.', trap: 'Keeping all historical media archives in Standard storage or manually scripting tier migrations increases storage TCO.' },
      { req: 'Multimodal metadata extraction & automated summarization', services: ['Gemini Multimodal on Vertex AI', 'Video Intelligence API', 'Speech-to-Text API'], rationale: 'Extract transcripts, scene labels, and concise episode summaries automatically from audio/video uploads triggered via Eventarc + Cloud Run functions.', trap: 'Do not build custom OCR/ASR pipelines when managed multimodal Vertex AI and pre-trained media APIs are available.' },
      { req: 'AI-powered detection of harmful & inappropriate content', services: ['Video Intelligence Explicit Content Detection', 'Vertex AI Safety Filters', 'Model Armor'], rationale: 'Combine automated visual/audio moderation on ingest with LLM safety filters and Model Armor for user-facing chat interactions.', trap: 'Manual human moderation alone cannot scale to 24/7 user uploads and real-time chat.' },
      { req: 'Auditable & explainable AI decisions for content & pricing', services: ['Vertex Explainable AI', 'Vertex AI Model Registry', 'Cloud Audit Logs'], rationale: 'Vertex Explainable AI surfaces feature attributions for recommendations/dynamic pricing; Model Registry and Audit Logs provide full lineage.', trap: 'Deploying black-box models without attribution tracking fails the explicit auditability technical requirement.' },
      { req: 'Hybrid cloud connectivity for legacy on-prem ingestion/archival', services: ['Dedicated / Partner Interconnect', 'Storage Transfer Service'], rationale: 'High-throughput Interconnect ensures deterministic bandwidth for large media file transfers between on-prem studios and Cloud Storage.', trap: 'Using public internet VPNs for high-volume broadcast video ingestion causes packet loss and unpredictable latency.' }
    ]
  },
  knightmotives: {
    name: 'KnightMotives Automotive',
    file: 'case_study_knightmotives_automotive.txt',
    industry: 'Automotive & Autonomous Vehicles',
    driver: '5-year fleet UX modernization, AV training & data monetization',
    sla: 'Global high reliability · EU Data Sovereignty (GDPR)',
    blurb: 'Global automaker modernizing mainframes, online build-to-order systems, dealer APIs, and autonomous driving AI across hybrid/multicloud environments.',
    arch: [
      { req: 'Re-architect unreliable online build-to-order vehicle configurator', services: ['Global External Application LB', 'Cloud Run / GKE', 'Cloud Spanner'], rationale: 'Cloud Spanner provides global strong consistency and 99.999% availability for real-time vehicle inventory and custom build-to-order transactions.', trap: 'Using single-region relational databases with asynchronous replication leads to stale dealer inventory and failed orders.' },
      { req: 'Autonomous vehicle (AV) model training & simulation at scale', services: ['Vertex AI Training', 'AI Hypercomputer (Cloud TPUs / A3 GPUs)', 'Google Cloud Batch / GKE'], rationale: 'AI Hypercomputer provides high-speed TPU/GPU pods with ultra-low-latency networking for massive distributed AV perception model training and simulation.', trap: 'Standard general-purpose VMs (E2/N2) cannot train foundation-scale autonomous driving models.' },
      { req: 'In-vehicle real-time AI & rural/edge connectivity challenges', services: ['LiteRT / Gemini Nano (On-Device)', 'Pub/Sub', 'Google Distributed Cloud Edge'], rationale: 'Run latency-critical inference directly on vehicle edge hardware with offline buffering, syncing telemetry via Pub/Sub when connectivity resumes.', trap: 'Requiring synchronous cloud round-trips for safety-critical in-vehicle driving decisions fails in rural dead zones.' },
      { req: 'EU data protection (GDPR) & strict data sovereignty compliance', services: ['Assured Workloads (EU Sovereign Controls)', 'Organization Policy (Resource Locations)', 'Cloud KMS (CMEK/EKM)'], rationale: 'Assured Workloads enforces EU data residency, personnel access controls, and cryptographic key sovereignty for European vehicle telemetry.', trap: 'Storing EU driver telemetry in multi-regional US buckets violates GDPR sovereignty constraints.' },
      { req: 'Corporate data monetization & breaking down data silos', services: ['BigQuery', 'Dataplex', 'Analytics Hub (Data Clean Rooms)', 'Looker'], rationale: 'Consolidate siloed telemetry and ERP data into BigQuery governed by Dataplex; share curated datasets securely with partners via Analytics Hub.', trap: 'Sharing raw unmasked customer driving logs via SFTP exports creates severe privacy and breach risks.' },
      { req: 'Mainframe/ERP modernization & hybrid/multicloud connectivity', services: ['Mainframe Assessment Tool / Dual Run', 'Cross-Cloud Interconnect', 'Apigee API Management'], rationale: 'Wrap legacy ERP/mainframe functions in modern REST APIs via Apigee for dealer tooling while migrating workloads incrementally via Dual Run.', trap: 'Attempting a "big bang" overnight mainframe rewrite risks halting global vehicle manufacturing supply chains.' }
    ]
  },
  mountkirk: {
    name: 'Mountkirk Games (Legacy)',
    file: 'case_study_mountkirk_games.txt',
    industry: 'Mobile Multiplayer Gaming',
    driver: 'Global game launch, real-time telemetry & leaderboards',
    sla: 'Global low latency · Strong consistency leaderboards',
    legacy: true,
    blurb: 'Multiplayer mobile gaming backend requiring global low-latency scaling, strongly consistent leaderboards, and streaming telemetry analytics.',
    arch: [
      { req: 'Global game backend scaling for millions of concurrent players', services: ['Global External Application LB', 'GKE Multi-cluster / Agones', 'Cloud CDN'], rationale: 'Distribute player traffic globally with anycast IP load balancing to regional GKE clusters running containerized game servers.', trap: 'Single-region Compute Engine VMs with manual scaling fail during viral launch spikes.' },
      { req: 'Real-time streaming telemetry ingestion & late-arriving data', services: ['Pub/Sub', 'Dataflow (Streaming)', 'BigQuery'], rationale: 'Pub/Sub buffers millions of events/sec; Dataflow handles windowing, watermarks, and late-arriving mobile telemetry before streaming into BigQuery.', trap: 'Using batch cron scripts or direct client writes to BigQuery causes data loss and high latency.' },
      { req: 'High-velocity time-series player state vs. global leaderboards', services: ['Cloud Bigtable', 'Cloud Spanner', 'Memorystore for Redis'], rationale: 'Use Spanner for globally consistent transactional state/leaderboards, Bigtable for high-write time-series telemetry, and Redis for sub-millisecond caching.', trap: 'Using BigQuery for sub-second transactional player profile lookups.' }
    ]
  },
  hrl: {
    name: 'Helicopter Racing League (Legacy)',
    file: 'case_study_hrl.txt',
    industry: 'Global Sports Streaming & Telemetry',
    driver: 'Low-latency video delivery, ML predictions & PCI tokenization',
    sla: 'Global edge delivery · PCI DSS scope reduction',
    legacy: true,
    blurb: 'Global sports league streaming live video and real-time race telemetry with explainable AI predictions and custom payment card tokenization.',
    arch: [
      { req: 'Real-time race telemetry ingestion & explainable AI predictions', services: ['Pub/Sub', 'Dataflow', 'BigQuery', 'Vertex AI Explainable AI'], rationale: 'Stream sensor telemetry via Pub/Sub + Dataflow into BigQuery; serve low-latency predictions with feature attributions via Vertex Explainable AI.', trap: 'Offline batch training without feature attributions fails commentator explainability requirements.' },
      { req: 'Secure viewer payment card tokenization with minimal PCI scope', services: ['Sensitive Data Protection (Deterministic Encryption)', 'Cloud KMS (Annual Rotation)', 'Cloud Run'], rationale: 'Tokenize PANs using deterministic encryption or Format-Preserving Encryption (FPE) in Sensitive Data Protection backed by Cloud KMS with 365-day rotation.', trap: 'Storing raw credit card numbers in standard relational databases expands PCI DSS audit scope across the entire environment.' },
      { req: 'Restrict origin load balancer ingress to authorized CDN partners', services: ['Cloud Armor Security Policies', 'Global External Application LB'], rationale: 'Attach a Cloud Armor security policy using preconfigured/named IP lists (e.g., Fastly CDN edge IPs) to block direct origin access.', trap: 'Using VPC firewall rules alone does not filter traffic at the Google Frontend (GFE) edge before reaching the External Application Load Balancer.' }
    ]
  },
  terramearth: {
    name: 'TerramEarth (Legacy)',
    file: 'case_study_terramearth.txt',
    industry: 'Heavy Equipment Manufacturing & IoT',
    driver: '20M vehicle fleet telemetry, predictive maintenance & dealer APIs',
    sla: 'Offline cellular buffering · Sub-second predictive alerts',
    legacy: true,
    blurb: 'Global manufacturer of 20 million mining and agricultural vehicles streaming 500+ sensor parameters for predictive maintenance and dealer parts optimization.',
    arch: [
      { req: 'High-throughput streaming telemetry (200K connected vehicles) & nightly batch uploads (20M vehicles)', services: ['Pub/Sub', 'Dataflow', 'Cloud Storage', 'BigQuery'], rationale: 'Pub/Sub ingests streaming MQTT/HTTP telemetry; Cloud Storage receives compressed nightly maintenance bay uploads; Dataflow unifies both into BigQuery.', trap: 'Streaming 20M vehicles directly into Cloud SQL or relational databases causes severe write bottlenecks.' },
      { req: 'Predictive maintenance ML models & automated parts ordering APIs for dealers', services: ['Vertex AI', 'BigQuery ML', 'Apigee API Management'], rationale: 'Train failure-prediction models on historical sensor time-series in BigQuery/Vertex AI and expose rate-limited REST APIs with OAuth/API keys to dealers via Apigee.', trap: 'Giving external dealerships direct IAM access to internal BigQuery tables violates least privilege.' },
      { req: 'Cost-optimized multi-petabyte sensor data lifecycle & analytics partitioning', services: ['BigQuery Partitioning & Clustering', 'Cloud Storage Lifecycle / Autoclass'], rationale: 'Partition BigQuery tables by ingestion/event timestamp and cluster by vehicle ID/model; transition raw archives in Cloud Storage to Coldline/Archive.', trap: 'Running unpartitioned SELECT * queries across petabytes of multi-year telemetry causes massive BigQuery scan costs.' }
    ]
  },
  jencomart: {
    name: 'JencoMart (Legacy)',
    file: 'case_study_jencomart.txt',
    industry: 'Global E-Commerce & Retail',
    driver: 'Global e-commerce migration, multi-region database & Asia latency',
    sla: '99.99% availability · Global strong consistency',
    legacy: true,
    blurb: 'Global retail conglomerate migrating e-commerce traffic from overloaded on-prem data centers to multi-region Google Cloud with low-latency edge delivery across Asia and Europe.',
    arch: [
      { req: 'Global low-latency web storefront & static media delivery for Asia/Europe expansion', services: ['Global External Application LB', 'Cloud CDN', 'Cloud Storage'], rationale: 'Terminate user traffic at the nearest Google PoP with Anycast IP and cache product images/assets at the edge via Cloud CDN.', trap: 'Serving static product images directly from a single-region US origin adds hundreds of milliseconds of RTT for Asian users.' },
      { req: 'Globally consistent transactional order database & high-scale user profile store', services: ['Cloud Spanner', 'Cloud Firestore / Bigtable', 'Memorystore for Redis'], rationale: 'Use Cloud Spanner for globally consistent financial/inventory transactions and Firestore or Bigtable for high-throughput session and user activity state.', trap: 'Relying on cross-region asynchronous read replicas for order inventory risks overselling during flash sales.' },
      { req: 'Zero-downtime database migration & automated CI/CD container deployments', services: ['Database Migration Service (DMS)', 'GKE / Cloud Run', 'Cloud Build & Cloud Deploy'], rationale: 'Use continuous DMS replication for minimal cutover downtime while deploying stateless microservices to GKE/Cloud Run via automated canary pipelines.', trap: 'Performing a weekend maintenance window dump-and-restore causes hours of global revenue loss.' }
    ]
  }
};

// Area → recommended study module(s) (module ids from data/study front matter).
export const AREA_MODULES = {
  'Gen AI, agents & AI safety': ['d2-provision', 'd1-nsc'],
  'AI/ML platform (Vertex AI, APIs, accelerators)': ['d2-provision', 'd1-nsc'],
  'API management (Apigee, API Gateway)': ['d4d5-processes'],
  'Migration & data transfer': ['d1-design', 'd4d5-processes'],
  'Business processes, stakeholders & adoption': ['d4d5-processes', 'd1-design'],
  'Cost optimization & billing': ['d4d5-processes', 'cheat-sheets'],
  'DR, backup & high availability': ['d1-design', 'd2-provision'],
  'Monitoring, SLOs & alerting': ['d6-operations'],
  'Logging & audit logs': ['d6-operations', 'd3-security'],
  'CI/CD & release management': ['d4d5-processes', 'd6-operations'],
  'Security posture & supply chain': ['d3-security'],
  'Compliance & governance': ['d3-security'],
  'IAM, identity & access': ['d3-security'],
  'Encryption & key management': ['d3-security'],
  'Network security (Armor, NGFW, IDS, VPC-SC)': ['d3-security', 'd2-provision'],
  'Load balancing, CDN & DNS': ['d1-nsc', 'd2-provision'],
  'VPC design & hybrid connectivity': ['d1-nsc', 'd2-provision'],
  'BigQuery & analytics': ['d1-nsc'],
  'Data pipelines & messaging': ['d1-nsc'],
  'Relational databases (Cloud SQL, AlloyDB, Spanner)': ['d1-nsc', 'd2-provision'],
  'NoSQL & caching (Bigtable, Firestore, Memorystore)': ['d1-nsc'],
  'Cloud Storage (objects)': ['d1-nsc', 'd2-provision'],
  'Block & file storage': ['d1-nsc', 'd2-provision'],
  'GKE & Kubernetes': ['d2-provision', 'd1-nsc'],
  'Serverless (Cloud Run, functions, App Engine)': ['d2-provision', 'd1-nsc'],
  'Compute Engine & VMs': ['d2-provision', 'd1-nsc'],
  'IaC & developer tooling (Terraform, gcloud, SDKs)': ['d4d5-processes'],
  'Architecture principles & Well-Architected Framework': ['d1-design', 'exam-overview'],
};

export const EXAM = { questions: 50, minutes: 120, caseStudies: 2, perCase: 6 };

// ---------- data ----------
const cache = {};
export async function loadJSON(path) {
  if (!cache[path]) cache[path] = fetch(path).then(r => { if (!r.ok) throw new Error(path + ' ' + r.status); return r.json(); });
  return cache[path];
}
export async function loadText(path) {
  if (!cache[path]) cache[path] = fetch(path).then(r => { if (!r.ok) throw new Error(path + ' ' + r.status); return r.text(); });
  return cache[path];
}
let bank = null, bankById = null;
export async function getBank() {
  if (!bank) {
    bank = await loadJSON('data/questions.json');
    bankById = new Map(bank.map(q => [q.id, q]));
  }
  return bank;
}
export function q(id) { return bankById ? bankById.get(id) : null; }
export const getStudyIndex = () => loadJSON('data/study/index.json');
export const getMeta = () => loadJSON('data/meta.json');

// ---------- store (localStorage) ----------
const KEY = 'pca-crash-course.v1';
const defaults = () => ({ attempts: [], qstats: {}, study: {}, bookmarks: [], session: null });
let state = null;
export function store() {
  if (!state) {
    try { state = Object.assign(defaults(), JSON.parse(localStorage.getItem(KEY) || '{}')); }
    catch { state = defaults(); }
  }
  return state;
}
export function save() { try { localStorage.setItem(KEY, JSON.stringify(store())); } catch (e) { console.warn('save failed', e); } }
export function resetStore() { state = defaults(); save(); }
export function recordAnswer(qid, correct) {
  const s = store().qstats[qid] || { seen: 0, correct: 0, wrong: 0, last: 0 };
  s.seen++; correct ? s.correct++ : s.wrong++; s.last = Date.now(); s.lastCorrect = correct;
  store().qstats[qid] = s; save();
}
export function toggleBookmark(qid) {
  const b = store().bookmarks; const i = b.indexOf(qid);
  i >= 0 ? b.splice(i, 1) : b.push(qid); save(); return i < 0;
}
export const isBookmarked = (qid) => store().bookmarks.includes(qid);

// ---------- helpers ----------
export const shuffle = (a) => { const r = a.slice(); for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[r[i], r[j]] = [r[j], r[i]]; } return r; };
export const pct = (n, d) => d ? Math.round(100 * n / d) : 0;
export const fmtTime = (s) => { s = Math.max(0, Math.round(s)); const m = Math.floor(s / 60), r = s % 60; return `${m}:${String(r).padStart(2, '0')}`; };
export const fmtClock = (s) => { s = Math.max(0, Math.round(s)); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60; return h ? `${h}:${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}` : `${m}:${String(r).padStart(2, '0')}`; };
export const fmtDate = (t) => new Date(t).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
export const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
export const sameSet = (a, b) => { const sa = new Set(a), sb = new Set(b); return sa.size === sb.size && [...sa].every(x => sb.has(x)); };

// ---------- sampling ----------
export function filterBank(all, f = {}) {
  return all.filter(qq => {
    if (f.domains && f.domains.length && !f.domains.includes(qq.domain)) return false;
    if (f.areas && f.areas.length && !f.areas.includes(qq.area)) return false;
    if (f.difficulty && f.difficulty !== 'all' && qq.difficulty !== f.difficulty) return false;
    if (f.caseStudy && f.caseStudy !== 'all') { if (f.caseStudy === 'none' ? qq.caseStudy : f.caseStudy === 'any' ? !qq.caseStudy : qq.caseStudy !== f.caseStudy) return false; }
    if (f.type && f.type !== 'all' && qq.type !== f.type) return false;
    if (f.source === 'official' && !qq.officialSample) return false;
    if (f.source === 'unseen' && store().qstats[qq.id]) return false;
    if (f.source === 'wrong' && !(store().qstats[qq.id] && store().qstats[qq.id].lastCorrect === false)) return false;
    if (f.source === 'bookmarked' && !isBookmarked(qq.id)) return false;
    if (f.search) { const s = f.search.toLowerCase(); if (!(qq.question + ' ' + qq.topic + ' ' + qq.options.join(' ')).toLowerCase().includes(s)) return false; }
    return true;
  });
}

// Weighted exam sample mimicking the real blueprint: ~2 case studies, remaining by domain weight.
export function sampleExam(all, n = EXAM.questions) {
  const targets = {};
  let acc = 0;
  for (const d of [1, 2, 3, 4, 5, 6]) { targets[d] = Math.round(DOMAINS[d].weight * n); acc += targets[d]; }
  targets[1] += n - acc; // fix rounding on the largest domain
  const picked = [], used = new Set();
  const activeCases = Object.keys(CASES).filter(k => !CASES[k].legacy);
  const cases = shuffle(activeCases).slice(0, EXAM.caseStudies);
  for (const c of cases) {
    const pool = shuffle(all.filter(x => x.caseStudy === c));
    for (const x of pool.slice(0, EXAM.perCase)) { picked.push(x); used.add(x.id); targets[x.domain]--; }
  }
  // prefer questions never seen, then least recently seen
  const st = store().qstats;
  const rank = (x) => (st[x.id] ? 1 + (st[x.id].last / 1e13) : 0) + Math.random() * 0.5;
  for (const d of [1, 2, 3, 4, 5, 6]) {
    const pool = all.filter(x => !x.caseStudy && x.domain === d && !used.has(x.id)).sort((a, b) => rank(a) - rank(b));
    for (const x of pool.slice(0, Math.max(0, targets[d]))) { picked.push(x); used.add(x.id); }
  }
  while (picked.length < n) { const rest = all.filter(x => !used.has(x.id)); if (!rest.length) break; const x = rest[Math.floor(Math.random() * rest.length)]; picked.push(x); used.add(x.id); }
  return { questions: shuffle(picked).slice(0, n), cases };
}

// ---------- analytics ----------
export function analyze(attempt) {
  const items = attempt.items.map(it => ({ ...it, q: q(it.id) })).filter(it => it.q);
  const total = items.length;
  const correct = items.filter(it => it.correct).length;
  const answered = items.filter(it => it.chosen && it.chosen.length).length;
  const groupBy = (keyFn, labelFn) => {
    const m = {};
    for (const it of items) {
      const k = keyFn(it.q); if (k == null) continue;
      m[k] = m[k] || { key: k, label: labelFn ? labelFn(k) : k, total: 0, correct: 0, time: 0 };
      m[k].total++; if (it.correct) m[k].correct++; m[k].time += it.time || 0;
    }
    return Object.values(m).map(g => ({ ...g, pct: pct(g.correct, g.total), avgTime: g.total ? g.time / g.total : 0 }));
  };
  const byDomain = [1, 2, 3, 4, 5, 6].map(d => {
    const g = groupBy(x => x.domain === d ? d : null)[0] || { key: d, total: 0, correct: 0, pct: 0, time: 0, avgTime: 0 };
    return { ...g, label: DOMAINS[d].short, weight: DOMAINS[d].weight };
  });
  const byArea = groupBy(x => x.area).sort((a, b) => a.pct - b.pct || b.total - a.total);
  const byDifficulty = ['easy', 'medium', 'hard'].map(k => groupBy(x => x.difficulty === k ? k : null)[0] || { key: k, label: k, total: 0, correct: 0, pct: 0 });
  const byType = ['single', 'multi'].map(k => groupBy(x => x.type === k ? k : null)[0] || { key: k, label: k, total: 0, correct: 0, pct: 0 });
  const byCase = groupBy(x => x.caseStudy, k => CASES[k] ? CASES[k].name : k);
  const times = items.map(it => it.time || 0);
  const totalTime = times.reduce((a, b) => a + b, 0);
  const slowest = items.slice().sort((a, b) => (b.time || 0) - (a.time || 0)).slice(0, 5);
  const flagged = items.filter(it => it.flagged);
  const wrong = items.filter(it => !it.correct);
  // Weighted score: each domain's accuracy weighted by exam blueprint weight (only domains present).
  let wsum = 0, wtot = 0;
  for (const d of byDomain) if (d.total) { wsum += d.pct * d.weight; wtot += d.weight; }
  const weighted = wtot ? Math.round(wsum / wtot) : pct(correct, total);
  const score = pct(correct, total);
  const verdict = score >= 80 ? 'ready' : score >= 70 ? 'border' : 'notyet';
  // Weak areas: at least 2 questions and < 70% (or any wrong if few questions), sorted by impact = wrong count × domain weight.
  const weak = byArea.filter(a => a.total >= 2 && a.pct < 70 || a.total === 1 && a.pct === 0)
    .map(a => ({ ...a, impact: (a.total - a.correct) })).sort((a, b) => b.impact - a.impact || a.pct - b.pct).slice(0, 6);
  const strong = byArea.filter(a => a.total >= 2 && a.pct >= 85).sort((a, b) => b.total - a.total).slice(0, 5);
  const changed = items.filter(it => it.changes && it.changes > 0).length;
  return { items, total, correct, answered, score, weighted, verdict, byDomain, byArea, byDifficulty, byType, byCase, totalTime, avgTime: total ? totalTime / total : 0, slowest, flagged, wrong, weak, strong, changed };
}

export function isCorrect(qq, chosen) { return sameSet(qq.answer, chosen || []); }
