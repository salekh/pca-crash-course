#!/bin/bash
export GOOGLE_CLOUD_PROJECT=sa-nexus-gcp-4-sandbox-183936
export GOOGLE_API_USE_CLIENT_CERTIFICATE=false
export GOOGLE_API_USE_MTLS_ENDPOINT=never
S=/usr/local/google/home/sanchitalekh/cowork_workspace/skills/think-with-google-infographics/scripts
python3 $S/generate_architecture.py --model pro --resolution 4K --theme new --aspect-ratio 16:9 \
  --project sa-nexus-gcp-4-sandbox-183936 --location global \
  --title "The Agentic Attack Surface" \
  --spec "A central LLM agent runtime node labelled 'LLM Agent (probabilistic core)'. On the LEFT, three UNTRUSTED input sources feeding into it: 'Ingested Documents / RAG', 'External Web Content', and 'Third-party MCP Servers'. On the RIGHT, four PRIVILEGED action sinks the agent can invoke: 'Email / Messaging', 'Code Execution', 'Databases and CRM', and 'Cloud APIs'. A red dashed trust boundary separates the untrusted inputs from the agent runtime. Four small hazard badges sit on the untrusted inputs, labelled 'Indirect Prompt Injection', 'Tool Poisoning', 'Rug Pull', and 'Tool Shadowing'. A footer band across the bottom reads 'Lethal trifecta: private data access + untrusted content + external communication'." \
  --output figures/fig_attack_surface.png > f1.log 2>&1
echo "fig1 exit=$?"
python3 $S/generate_architecture.py --model pro --resolution 4K --theme new --aspect-ratio 16:9 \
  --project sa-nexus-gcp-4-sandbox-183936 --location global \
  --title "Defence in Depth for Foundation Models" \
  --spec "A six-tier horizontal layered stack diagram, stacked top to bottom, each tier a full-width rounded card with a title and a short descriptor. Tier 1 (top): 'User and Data Plane'. Tier 2: 'Prompt and Response Boundary' with descriptor 'Model Armor, injection screening, DLP'. Tier 3: 'Model Runtime' with descriptor 'Safety filters, guardrail classifiers'. Tier 4: 'Agent Runtime' with descriptor 'Capability-scoped tools, non-human identity, kill switch'. Tier 5: 'Infrastructure' with descriptor 'VPC Service Controls, CMEK, Private Service Connect, sandboxing'. Tier 6 (bottom): 'Governance and Telemetry' with descriptor 'Security Command Center, audit logging, red teaming, EU AI Act evidence'. A tall vertical arrow runs up the right-hand side labelled 'Detect and respond across all tiers'. A second tall vertical arrow runs up the left-hand side labelled 'SAIF principles applied end to end'." \
  --output figures/fig_defense_depth.png > f2.log 2>&1
echo "fig2 exit=$?"
