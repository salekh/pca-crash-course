---
title: Foundation Model Security for the Enterprise
subtitle: A grounded control map for CISOs deploying models and agents in production
collateral_type: pitch-deck
author: Sanchit Alekh
date: 2026-08-27
confidentiality: Google Cloud | Proprietary & Confidential
---

Foundation models are no longer a lab curiosity: they are inside customer-facing workflows, developer toolchains, and privileged agents. The security question has shifted from "can we experiment safely" to "what are the actual controls, evaluations, and containment tiers a regulated European enterprise needs before an agent is allowed to touch a production system." This deck maps that terrain — from what the frontier labs actually do, to the reality of prompt injection, to a concrete Google Cloud control set — without hype and without overclaim.

::: stat {value="14" unit="slides" label="Frameworks, threats, controls, and a 90-day plan — grounded in 2025-2026 public research"}
:::

> notes: Open by naming the audience shift. Two years ago, security teams debated whether generative AI was in scope at all. Today the question is which controls are load-bearing, and which are theatre. Set the expectation that this session is deliberately non-hype: it separates what is genuinely deployable now from what is still open research, and it names the parts of the field, especially indirect prompt injection, where no vendor has a complete answer.

## Agenda

::: agenda
- item: The threat surface — models, weights, agents
  duration: 8 min
- item: What the frontier labs actually do
  duration: 6 min
- item: Prompt injection & the agentic reality check
  duration: 10 min
- item: Defense-in-depth architecture on Google Cloud
  duration: 10 min
- item: Standards, regulation, maturity
  duration: 6 min
- item: A 90-day plan
  duration: 5 min
:::

> notes: Walk the room through the arc. The first three items build the honest threat picture — including the parts of it that no defender has fully solved. The middle two land the architecture: what does a defensible deployment look like on Google Cloud, mapped against SAIF, NIST, OWASP, and the EU AI Act. The last two are operational: how to measure maturity and where to start on Monday. Invite interrupt-style questions throughout; this material rewards debate.

# Why now

## Three shifts that turned foundation-model risk into a board-level issue

Models moved from chat to code execution, tool use, and multi-step autonomy in under 24 months. Regulation moved from principle to enforceable fines. Attack research moved from academic curiosity to published, reproducible exploit classes against production systems.

::: cards
- title: Capability shift
  body: Frontier labs now publish safety frameworks that explicitly track autonomous AI R&D, cyber uplift, and biological uplift as gated capability thresholds — a signal that in-model risk is treated as real by the developers themselves.
- title: Regulatory shift
  body: EU AI Act GPAI obligations apply from 2 August 2025; systemic-risk providers face enforceable fines up to €15M or 3 % of global turnover from 2 August 2026.
- title: Attacker shift
  body: MCP tool poisoning, indirect prompt injection, and agent confused-deputy attacks moved from proofs of concept to CVEs and named incidents in 2025 — including CVE-2025-6514 in the widely used mcp-remote OAuth client.
:::

> notes: Frame this as three converging forces, not one AI trend. The capability curve alone would not force security teams to act — but the arrival of enforceable GPAI obligations and a real, published exploit corpus does. Land the point that the enterprises that treat this as a 2026 regulatory deadline will already be behind, because attackers are shipping against production agents today. This slide is where the CISO decides whether to lean in.

## The threat surface has four distinct layers

Security teams often collapse "AI risk" into a single bucket. That is the wrong mental model. The threats, the controls, and the accountable owner differ at each layer.

::: cards
- title: Model layer
  body: Training-data poisoning, backdoors, weight exfiltration, jailbreaks against alignment, capability misuse (CBRN, cyber, autonomous R&D). Owner: model provider + security architect.
- title: Application layer
  body: OWASP LLM01-LLM10 — direct and indirect prompt injection, sensitive information disclosure, supply-chain risk, insecure output handling, system-prompt leakage, vector/embedding weaknesses. Owner: platform + app teams.
- title: Agentic layer
  body: Excessive agency, tool poisoning, confused deputy, non-human identity sprawl, MCP/A2A protocol abuse, prompt-based lateral movement across tools. Owner: platform security + IAM.
- title: Governance layer
  body: EU AI Act GPAI duties, NIST AI RMF alignment, ISO/IEC 42001 management system, red-team evidence, model cards, incident reporting. Owner: CISO + legal + risk.
:::

> notes: Insist on the layer separation. A control that stops jailbreaks does not stop indirect prompt injection through a poisoned document, and neither addresses the fact that an agent's service account may have IAM roles far exceeding its business function. Ask the audience which layer their current governance actually covers — most will admit governance and model layers, with the application and agentic layers still unowned. That gap is where breaches happen.

## What the frontier labs actually do — and where the frameworks converge

All three leading labs publish a capability-gated safety framework updated in 2025. The naming differs, but the "bones" are the same: define capability thresholds, evaluate before deployment, apply proportionate mitigations, and disclose. For an enterprise buyer this convergence is useful — it means model choice is no longer a bet on whether the provider has a safety programme, only on how it is implemented.

::: table {caption="Frontier lab safety frameworks — current public versions" columns=[{name="Provider", align="left", type="text"}, {name="Framework", align="left", type="text"}, {name="Capability construct", align="left", type="text"}, {name="Tracked risk domains", align="left", type="text"}]}
Provider,Framework,Capability construct,Tracked risk domains
Anthropic,Responsible Scaling Policy (RSP),AI Safety Levels (ASL-2 → ASL-3 → ASL-4),CBRN uplift; autonomous AI R&D; cyber
OpenAI,Preparedness Framework v2 (Apr 2025),High / Critical thresholds in Tracked Categories,Biological & Chemical; Cybersecurity; AI Self-improvement
Google DeepMind,Frontier Safety Framework v3 (Sept 2025),Critical Capability Levels (CCLs) + Tracked Capability Levels (TCLs),CBRN; cyber; ML R&D uplift; harmful manipulation; misalignment
Industry,Frontier Model Forum,Shared safety research & evaluations,Members: Amazon, Anthropic, Google, Meta, Microsoft, OpenAI
:::

> notes: The important shift in 2025 is that Anthropic deployed Claude Opus 4 under its ASL-3 security and deployment standard — the first frontier model to ship under an elevated tier — and Google DeepMind's September 2025 FSF update added a Critical Capability Level for harmful manipulation and formalised misalignment mitigations. Read this as evidence that the labs' own risk models now match, rather than dismiss, enterprise concerns. Note also that the UK AI Safety Institute was renamed the AI Security Institute in February 2025, and the US counterpart is now CAISI — the state-backed evaluation ecosystem is real and growing.

## Model weight security: the RAND framework the industry now benchmarks against

RAND's 2024 report Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models is the canonical reference for model-artefact protection. It defines five graded security levels and enumerates the actual attack vectors — most of which have already been used in the wild against other high-value targets.

::: stat {value="SL1 → SL5" unit="tiers" label="RAND security levels — 38 catalogued attack vectors, 167 recommended controls, ranging from opportunistic amateurs (SL1) to top-priority nation-state operations (SL5)"}
:::

> notes: The three numbers to remember are five levels, thirty-eight attack vectors, and one hundred and sixty-seven controls. SL5, resistant to top-priority nation-state operations, is not something any frontier lab or hyperscaler claims to have fully achieved today — the non-profit Security Level 5 was formed specifically to make that tier reachable. For an enterprise, the pragmatic target is closer to SL3 for internally fine-tuned or proprietary models: hardened supply chain, personnel vetting proportional to access, and hardware-rooted key isolation. Mention that Vertex AI's CMEK plus VPC-SC posture supports the deployment-side controls, but weight protection begins at the training environment.

## The agentic attack surface is a new class of exposure

Agents combine three ingredients that traditional application security has never had to reason about together: a probabilistic core that treats all incoming tokens as potentially instructive, a set of privileged tools it can invoke, and content ingested at runtime from sources the developer does not control. Stanford, DeepMind, and independent researchers have converged on the observation that this combination is inherently a confused-deputy problem.

::: figure {kind="architecture" src="figures/agentic-attack-surface.png" prompt="Widescreen 16:9 architecture diagram, Google brand pastel palette on white background, Google Sans typography. Center: a single AI Agent node depicted as a rounded card labelled 'LLM Agent (probabilistic core)'. Left side: three untrusted input sources feeding into the agent — a document icon labelled 'Ingested documents / RAG corpus', a globe icon labelled 'External web content', and a plug icon labelled 'Third-party MCP servers / tools'. Right side: four privileged action sinks the agent can call — 'Email / messaging', 'Code execution & shell', 'Databases & CRM', 'Cloud APIs (IAM, storage)'. Above the agent, a red dashed 'Trust boundary' line separates the agent runtime from the LLM itself, with a caption 'The LLM lives outside the trust boundary'. Below the agent, a labelled arrow 'Prompt-derived tool call' points from center to right. Overlay four small red hazard badges near the untrusted inputs: 'Indirect prompt injection', 'Tool poisoning', 'Rug pull / silent redefinition', 'Cross-server tool shadowing'. Bottom banner reads 'Lethal trifecta: private data access + untrusted content + external communication'. Clean flat vector style, no photorealism, no embedded stock imagery."}
:::

> notes: Walk the diagram left to right. The agent's natural-language interface carries no notion of who authorised what — a sentence from a poisoned document arrives at the LLM with the same weight as a system message. The agent then translates that sentence into a tool call, and the tool executes under the agent's own service-account identity, not the requester's. That is the confused deputy, restated for the AI era. Palo Alto Unit 42's March 2026 Double Agents research showed this concretely against Vertex AI Agent Engine's default OAuth scoping, and Anthropic and Google DeepMind now cite this class as their primary near-term deployment concern.

## Prompt injection: the honest reality check

Indirect prompt injection — malicious instructions smuggled into content the model ingests — has no complete defense today. Every published mitigation is a probabilistic reduction, not a hard boundary. A credible security programme names this openly and compensates with containment, not with a promise of a filter that will catch everything.

::: quote {attribution="Simon Willison — the 'lethal trifecta' formulation, widely adopted in 2025"}
An agent that combines access to private data, exposure to untrusted content, and the ability to communicate externally can be induced to exfiltrate that data — and the attacker only needs one of the three to be under their influence.
:::

::: callout {kind="warning" title="No vendor has solved indirect prompt injection"}
Anthropic's Constitutional Classifiers reduced jailbreak success on Claude 3.5 Sonnet from 86 % to 4.4 % in automated evaluation (Feb 2025), and the January 2026 next-generation version withstood 1,700+ cumulative hours of red-teaming with one high-risk vulnerability found. These are strong results — but the labs themselves position them as defense-in-depth layers, not as a complete fix for adversarial input.
:::

> notes: This is the slide where the deck earns its credibility. If a vendor tells the CISO they have "solved" prompt injection, they should be shown the door. What is real is a layered stack: instruction hierarchy in training (OpenAI 2024), classifier-based screening at the boundary (Anthropic's Constitutional Classifiers, Google Cloud's Model Armor), and capability-based runtime containment such as Google DeepMind's CaMeL approach that treats tool calls as capability-gated rather than trusting the LLM's intent. State plainly that the current best answer is architectural — minimise the lethal trifecta at design time — not a magic filter.

## Defense in depth: what a defensible foundation-model deployment looks like

The controls that work today are not novel — they are the same layered posture enterprise security has always used, adapted to the model and the agent. Boundary screening, identity, containment, evaluation, monitoring, and governance, applied at every layer of the stack.

::: figure {kind="architecture" src="figures/defense-in-depth.png" prompt="Widescreen 16:9 layered architecture diagram, Google brand pastel palette on white background, Google Sans typography. Six horizontal stacked tiers, each a rounded card with clear label and 3-5 icon-plus-text control examples inside. Top tier (Google Blue 100): 'User & data plane — Identity, DLP, sensitive-data classification'. Second tier (Google Green 100): 'Prompt & response boundary — Model Armor, prompt injection screening, output filtering, PII redaction'. Third tier (Google Yellow 100): 'Model runtime — Vertex AI safety filters, instruction hierarchy, constitutional classifiers, output constraints'. Fourth tier (Google Red 100): 'Agent runtime — capability-scoped tools, human-in-the-loop for high-risk actions, kill switch, session isolation'. Fifth tier (Google Blue 50): 'Infrastructure — VPC-SC perimeter, CMEK, Private Service Connect, sandboxed execution'. Bottom tier (Google Grey 100): 'Governance & telemetry — SCC AI Protection, audit logs, red-team evals, incident response, EU AI Act evidence'. On the right, a vertical arrow labelled 'Detect + respond across all tiers' with 'Security Command Center' badge. On the left, a vertical arrow labelled 'SAIF principles applied end-to-end'. Clean flat vector style, no photorealism."}
:::

> notes: Emphasise that no single tier is load-bearing on its own. The Model Armor boundary catches direct prompt injection and obvious data exfiltration attempts, but a determined indirect-injection attack will pass through — which is why the agent tier below it enforces capability scoping, and the infrastructure tier below that enforces VPC-SC and CMEK so exfiltration cannot leave the perimeter even if the agent is compromised. This is the diagram to leave on screen while walking through the control mapping later. It is also the diagram to hand to platform teams as a target architecture.

## Identity, containment, and kill switches for agents

The single most impactful control most enterprises are missing is treating the agent as a non-human identity with least-privileged, capability-scoped access — not as an extension of the user who invoked it. Palo Alto Unit 42's March 2026 Vertex AI research demonstrated privilege escalation via default service-agent OAuth scoping; every hyperscaler platform has an equivalent risk pattern.

::: cards
- title: Non-human identity
  body: Each agent runs under its own workload identity with narrowly scoped IAM roles. No shared service accounts. OAuth scopes restricted to the tools the agent actually needs. Rotate credentials, audit like human identities.
- title: Capability-scoped tools
  body: Tools declare what data they can read and what actions they can commit. High-impact tools (payments, code execution, external send) require human-in-the-loop approval or a second-agent verifier, not model self-consent.
- title: Sandboxed execution
  body: Code interpreters and shells run in ephemeral, network-egress-restricted sandboxes. VPC Service Controls contain the blast radius. Data plane isolated from control plane.
- title: Kill switch & session isolation
  body: A single operator action must be able to disable the agent globally. Sessions are isolated so a poisoned context in one tenant cannot cross-contaminate another. Every tool invocation is logged and reversible where possible.
:::

> notes: These four controls are the practical answer to the confused-deputy problem. Land the point that Google Cloud's Vertex AI Agent Engine supports the underlying primitives today — CMEK, Private Service Connect interface, VPC-SC integration, and per-agent service identities were shipped in the September 2025 release notes — but the security posture is only as good as the IAM discipline the platform team enforces on top. If the audience takes one control home from this deck, it should be per-agent service accounts with least-privilege scopes.

## Evaluation & red-teaming: what "we tested it" should actually mean

Vendor claims of safety must be backed by evaluations the buyer can inspect. The evaluation ecosystem matured significantly in 2025 with the UK AI Security Institute's open Inspect framework, MITRE ATLAS as the reference threat taxonomy, and standardised prompt-injection benchmarks.

::: table {caption="Evaluation building blocks — what to require in vendor and internal assessments" columns=[{name="Layer", align="left", type="text"}, {name="What to measure", align="left", type="text"}, {name="Reference source", align="left", type="text"}]}
Layer,What to measure,Reference source
Capability,CBRN / cyber / autonomy uplift vs. baseline,Provider RSP / FSF / Preparedness reports
Jailbreak robustness,Universal & targeted jailbreak success rate,Anthropic Constitutional Classifiers methodology
Prompt injection,Direct + indirect injection catch rate + false-positive rate,OWASP LLM01; academic benchmarks
Agentic misuse,Confused-deputy / tool-poisoning success across a tool suite,MITRE ATLAS; Invariant Labs MCP research
Data protection,PII leakage rate; membership inference; system-prompt extraction,OWASP LLM02 / LLM07
Red-team hours,Documented human red-team effort + independent bounty results,AISI / third-party red teams
:::

> notes: The right question to ask a vendor is not "is it safe" but "show me the evaluation harness, the sample size, the false-positive rate, and the residual risk". Anthropic publishes numbers — 1,700 hours of red-teaming, 198,000 attempts, one high-risk finding for the next-generation classifiers. That is the level of transparency an enterprise security team should expect and should replicate internally against its own tools and data. Internal red-teaming against a realistic agent tool suite, not a chatbot, is where most programmes are underweight today.

# Standards, regulation, controls

## The compliance surface converges — but obligations bite on different clocks

Four instruments will define what a European enterprise must be able to evidence. They are complementary, not overlapping — and the EU AI Act GPAI clock is the one already running.

::: table {caption="Standards & regulatory instruments relevant to foundation-model deployment" columns=[{name="Instrument", align="left", type="text"}, {name="Scope", align="left", type="text"}, {name="Status / date", align="left", type="text"}, {name="Enterprise implication", align="left", type="text"}]}
Instrument,Scope,Status / date,Enterprise implication
EU AI Act — GPAI (Art. 53 / 55),General-purpose model providers; systemic risk >10²⁵ FLOPs,Obligations from 2 Aug 2025; fines from 2 Aug 2026,Provider due diligence; downstream deployers inherit transparency evidence
GPAI Code of Practice,Voluntary compliance route,Published 10 Jul 2025; endorsed Aug 2025,Signing creates presumption of compliance under AI Act
NIST AI RMF 1.0 + AI 600-1,Voluntary risk-management framework + GenAI profile,RMF Jan 2023; GenAI profile Jul 2024; 12 risk categories,Baseline for internal AI risk programme; maps to Govern / Map / Measure / Manage
ISO/IEC 42001:2023,AI Management System (AIMS) — auditable,Published Dec 2023; certifiable,Operating model for AI governance; harmonised with ISO 27001 structure
OWASP Top 10 for LLM Apps 2025 (v2.0),Application-security risk taxonomy,Published 18 Nov 2024,Baseline threat list for platform and app teams
MITRE ATLAS,Adversarial TTP knowledge base for AI,Continuously updated,Threat-modelling reference; complements ATT&CK for AI systems
:::

> notes: The critical dates for a European enterprise: 2 August 2025 — GPAI obligations apply, providers should be signing the Code of Practice; 2 August 2026 — enforcement of GPAI provisions begins, with fines up to fifteen million euros or three percent of global turnover. Downstream deployers do not carry the GPAI duties directly, but they will be asked by procurement and auditors to evidence which provider commitments they rely on. Land the recommendation to adopt ISO/IEC 42001 as the operating spine, NIST AI RMF as the risk vocabulary, and OWASP LLM Top 10 plus MITRE ATLAS as the threat inventory.

## Google Cloud control mapping — what maps to what, today

Every control in the defense-in-depth architecture has a Google Cloud counterpart that is generally available or in publicly documented preview. The table below is deliberately restricted to capabilities that have documented product surface — not roadmap slides.

::: table {caption="Google Cloud controls mapped to threat categories and standards" columns=[{name="Control", align="left", type="text"}, {name="What it does", align="left", type="text"}, {name="Addresses", align="left", type="text"}]}
Control,What it does,Addresses
Model Armor,Screens prompts, responses, and agent interactions for prompt injection, jailbreak, data-loss, malicious URLs, and offensive content; multi-cloud REST or in-line integration,OWASP LLM01 / LLM02 / LLM05; SAIF boundary
Security Command Center — AI Protection,Discovers AI assets (including shadow AI), maps AI-BOM, detects threats and posture risks alongside other cloud workloads,SAIF detection & response; ISO/IEC 42001 monitoring
Sensitive Data Protection (Cloud DLP),Classifies and redacts PII / secrets in prompts and responses; integrated with Model Armor,OWASP LLM02 / LLM07; GDPR
Vertex AI safety filters,Configurable harm-category thresholds on Gemini and served models,SAIF harmonised controls
Vertex AI Agent Engine,Managed agent runtime with CMEK, Private Service Connect interface, VPC-SC support, per-agent identity,Agentic containment; RAND SL3-class deployment posture
VPC Service Controls,Data-perimeter enforcement around Vertex AI, storage, and BigQuery,Weight & data exfiltration; agent blast-radius containment
CMEK / Cloud HSM,Customer-managed encryption keys for training data, weights, and agent state,Data confidentiality; regulatory data-residency
SAIF + CoSAI,Google's Secure AI Framework (six elements) and the industry-wide Coalition for Secure AI workstreams,Programme-level governance; ISO/IEC 42001 alignment
:::

> notes: The narrative is that Google Cloud publishes SAIF as the reference framework, contributes to CoSAI as the industry venue, and ships the primitives — Model Armor, SCC AI Protection, Sensitive Data Protection, Agent Engine with CMEK and PSC — that let a platform team implement it. Be honest about what is not on this slide: nothing here removes the enterprise's responsibility to enforce least-privileged IAM on agent service accounts, to red-team its own tool suite, or to sign off on residual risk. The Palo Alto Unit 42 Double Agents research is the caution that misconfiguration of these primitives is where risk actually lands.

## A maturity model for the foundation-model security programme

Most European enterprises today are between Level 1 and Level 2. The gap that matters is not model choice — it is whether the platform, IAM, and evaluation programme have caught up to what the models can already do.

::: cards
- title: L1 — Ad hoc
  body: Shadow AI tolerated. No inventory. No boundary controls. Agents deployed with default service-account scopes. Governance limited to acceptable-use policy.
- title: L2 — Foundational
  body: AI inventory in SCC or equivalent. Model Armor or comparable at the boundary. Vertex AI safety filters tuned. NIST AI RMF adopted as vocabulary. Basic red-team on chatbot surface.
- title: L3 — Managed
  body: Per-agent identities with least-privileged IAM. VPC-SC and CMEK on all AI workloads. ISO/IEC 42001 AIMS established. Internal prompt-injection benchmark against real tool suites. EU AI Act GPAI evidence collected from providers.
- title: L4 — Optimised
  body: Capability-scoped tool architecture (CaMeL-style). Continuous automated red-teaming. Third-party evaluation on production agents. Kill-switch drills executed. Attested weight-security posture aligned to RAND SL3+ where warranted.
:::

> notes: Use this as a self-scoring prompt in the room. Ask the CISO to place their programme on the ladder and to name the specific control that separates their current level from the next. In almost every case, the gap between Level 2 and Level 3 is IAM discipline on agents and evidence collection for the EU AI Act, not additional tooling. Level 4 is achievable today but requires organisational commitment to red-team as a discipline, not an event.

## A 90-day plan a platform team can actually execute

The programme below is deliberately narrow. It targets the highest-leverage controls first and leaves broader model-strategy questions for a follow-on cycle.

::: agenda
- item: Days 1-30 — Inventory & baseline
  duration: Discover all AI workloads (SCC AI Protection). Enumerate agents, tools, and non-human identities. Baseline against OWASP LLM Top 10 and MITRE ATLAS. Confirm which providers have signed the EU AI Act GPAI Code of Practice.
- item: Days 31-60 — Boundary & identity
  duration: Deploy Model Armor in front of all production model calls. Enforce per-agent service accounts with least-privileged IAM. Enable VPC-SC around Vertex AI, storage, and BigQuery. Turn on CMEK for agent state and any fine-tuned models.
- item: Days 61-90 — Evaluate & govern
  duration: Run an internal red-team against the top three production agents using an indirect-prompt-injection corpus. Stand up an ISO/IEC 42001-shaped AIMS with named owner. Execute one kill-switch drill. Publish a residual-risk register to the risk committee.
- item: Day 90 — Decision gate
  duration: Board-level readout on maturity movement, residual risk, and the investment case for Level 3 → Level 4.
:::

> notes: Sequence matters. Discovery has to come first because most organisations will find agents and tools they did not know were in production. Boundary and identity come next because they are the controls that reduce blast radius even before the evaluation programme is mature. Evaluation and governance close the loop and produce the evidence artefacts the audit function will ask for. Ninety days is realistic if the platform team owns the plan and the CISO clears the IAM changes on agent service accounts — that is usually the political blocker, not the technical one.

## What to take away

Foundation-model security is no longer a research topic; it is an operating discipline with a defined control map, a real regulatory clock, and a growing corpus of published incidents. The enterprises that will deploy agents safely are the ones that separate what is genuinely deployable now — boundary screening, per-agent identity, VPC-SC, CMEK, red-teaming — from what is still open research, and then execute the deployable set with the same rigour they apply to any other production system.

::: callout {kind="insight" title="Three principles to leave the room with"}
1. Assume indirect prompt injection will succeed sometimes — design containment so the blast radius is bounded when it does. 2. Treat every agent as a non-human identity with least-privileged, capability-scoped access — not as the user who invoked it. 3. Evidence beats assertion — require published evaluation numbers from providers, and reproduce them internally against your own tool suite.
:::

> notes: Close on the three principles. They are deliberately architectural rather than tool-specific because they will still be true in twelve months when the model landscape has shifted again. Offer the follow-on: a workshop to walk the platform team through the 90-day plan against the customer's actual Vertex AI, Agent Engine, and IAM posture, with a joint red-team exercise at the end. Thank the room and open for questions.

# Sources

## Sources cited in this deck

- Google DeepMind. *Strengthening our Frontier Safety Framework* (v3, 22 Sept 2025; updated 17 April 2026). https://deepmind.google/blog/strengthening-our-frontier-safety-framework/
- Google DeepMind. *Updating the Frontier Safety Framework* (4 Feb 2025). https://deepmind.google/blog/updating-the-frontier-safety-framework/
- OpenAI. *Our updated Preparedness Framework* (v2, 15 April 2025). https://openai.com/index/updating-our-preparedness-framework/
- Anthropic. *Constitutional Classifiers: Defending against universal jailbreaks* (3 Feb 2025). https://www.anthropic.com/research/constitutional-classifiers
- Anthropic. *Next-generation Constitutional Classifiers* (9 Jan 2026). https://www.anthropic.com/research
- Frontier Model Forum. *Membership*. https://www.frontiermodelforum.org/membership/
- RAND Corporation. *Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models* (2024). https://www.rand.org/pubs/research_reports/RRA2849-1.html
- Security Level 5. *SL5 standard for frontier AI weight security*. https://sl5.org/
- OWASP GenAI Security Project. *Top 10 for LLM Applications 2025 (v2.0)* (18 Nov 2024). https://genai.owasp.org/
- NIST. *AI Risk Management Framework 1.0* (Jan 2023) and *Generative AI Profile, NIST AI 600-1* (July 2024). https://www.nist.gov/itl/ai-risk-management-framework
- MITRE. *ATLAS — Adversarial Threat Landscape for Artificial-Intelligence Systems*. https://atlas.mitre.org/
- ISO/IEC 42001:2023. *Information technology — Artificial intelligence — Management system*. https://www.iso.org/standard/81230.html
- European Commission. *General-Purpose AI Code of Practice* (published 10 July 2025). https://digital-strategy.ec.europa.eu/en/policies/ai-code-practice
- Jones Day. *EU AI Act: European Commission Publishes General-Purpose AI Code of Practice* (2 Aug 2025). https://www.jonesday.com/en/insights/2025/08/eu-ai-act-european-commission-publishes-general-purpose-ai-code-of-practice
- Simon Willison. *The lethal trifecta for AI agents* (2025). https://simonwillison.net/
- Wallace, E. et al. *The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions* (arXiv:2404.13208, 2024).
- Invariant Labs. *MCP Tool Poisoning* (April 2025), summarised at https://www.mintmcp.com/ and CVE-2025-6514 (mcp-remote OAuth).
- Palo Alto Networks Unit 42. *Double Agents: Exposing Security Blind Spots in GCP Vertex AI* (31 March 2026). https://unit42.paloaltonetworks.com/double-agents-vertex-ai/
- Google Cloud. *Securing AI with Google Cloud*. https://cloud.google.com/security/securing-ai
- Google Cloud. *Model Armor product page*. https://cloud.google.com/security/products/model-armor
- Google Cloud. *Security Command Center — AI Protection overview*. https://cloud.google.com/security-command-center/docs/ai-protection-overview
- Google Cloud. *Vertex AI release notes* (Agent Engine CMEK, PSC interface, Sept 2025). https://docs.cloud.google.com/vertex-ai/docs/core-release-notes
- Google. *Secure AI Framework (SAIF) — six core elements*. https://safety.google/safety/saif/
- Coalition for Secure AI (CoSAI). https://www.coalitionforsecureai.org/
- UK AI Security Institute (renamed from AI Safety Institute, Feb 2025). https://www.aisi.gov.uk/
- Stack Overflow Blog. *AI agents are a confused deputy with the keys to your kingdom* (17 June 2026). https://stackoverflow.blog/2026/06/17/ai-agents-expose-the-security-checks-you-never-actually-wrote/

> notes: The Sources section is intentionally exhaustive so any claim on any slide can be traced back to its origin. When this deck is shared as a PDF, the appendix goes with it. In conversation, the two documents to point curious CISOs at first are the RAND weight-security report — because it establishes the vocabulary — and the OWASP LLM Top 10 2025 — because it is the shortest, sharpest introduction to the application-layer threat surface.
