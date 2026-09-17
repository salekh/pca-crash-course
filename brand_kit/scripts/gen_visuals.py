#!/usr/bin/env python3
"""
gen_visuals.py — visual generation CLI for the ai-tech-gtm-collateral skill.

THIN WRAPPER over the `think-with-google-infographics` skill.

Every image produced by this file flows through one of three upstream scripts:

    * scripts/generate_architecture.py   (Nano Banana architecture diagrams)
    * scripts/generate_twg.py            (editorial hero illustrations)
    * scripts/render_graph.py            (Mermaid / Graphviz plain graphs)

This wrapper's ONLY job is to:
    1. Discover where the wrapped skill lives on disk.
    2. Export FONTCONFIG_FILE so render_graph.py finds Google Sans.
    3. Compose FDE / AI-Tech-Group GTM-flavoured prompts from preset stubs.
    4. Shell out to the correct upstream script with the correct argv.

It does NOT reimplement any generation, prompt-building, model call, or
font logic — all of that stays in the wrapped skill.

Branding rule (inherited): the literal string "Think with Google" must never
appear in generated OUTPUTS. It is fine in comments and docstrings here.
"""

from __future__ import annotations

import argparse
import os
import pwd
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Discovery of the wrapped skill
# ---------------------------------------------------------------------------

WRAPPED_SKILL_NAME = "think-with-google-infographics"
REQUIRED_SCRIPTS = ("generate_architecture.py", "generate_twg.py", "render_graph.py")
FALLBACK_ABS = Path(
    "/usr/local/google/home/sanchitalekh/cowork_workspace/skills/"
    + WRAPPED_SKILL_NAME
)


def _real_home() -> Path:
    """
    Return the real home dir even when $HOME is empty.

    Mirrors the fontconfig trick from render_graph.py in the wrapped skill:
    inside some sandboxes HOME is unset, so `~` expansion silently returns
    "/", which then breaks path resolution. `pwd.getpwuid` reads the real
    entry from /etc/passwd and always gives a usable answer.
    """
    home = os.environ.get("HOME")
    if home:
        return Path(home)
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def _candidate_skill_roots() -> List[Path]:
    """Ordered list of places we look for the wrapped skill."""
    candidates: List[Path] = []
    env_root = os.environ.get("TWG_SKILL_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    home = _real_home()
    candidates.append(home / "cowork_workspace" / "skills" / WRAPPED_SKILL_NAME)
    candidates.append(FALLBACK_ABS)
    # De-dupe while preserving order.
    seen: set = set()
    unique: List[Path] = []
    for c in candidates:
        key = str(c)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def resolve_skill_root() -> Path:
    """Return the wrapped skill's root dir; hard-fail with all paths tried."""
    checked: List[str] = []
    for root in _candidate_skill_roots():
        scripts_dir = root / "scripts"
        if all((scripts_dir / s).is_file() for s in REQUIRED_SCRIPTS):
            return root
        checked.append(str(root))
    print(
        "ERROR: could not locate the think-with-google-infographics skill.\n"
        "Checked these roots (none contained all three required scripts):\n"
        + "\n".join(f"  - {p}" for p in checked)
        + "\n\nSet TWG_SKILL_ROOT to point at the skill directory, or install it "
        "under ~/cowork_workspace/skills/",
        file=sys.stderr,
    )
    sys.exit(2)


def wrapped_scripts_dir() -> Path:
    return resolve_skill_root() / "scripts"


def wrapped_fontconfig() -> Optional[Path]:
    """Path to the wrapped skill's fonts.conf, or None if it moved."""
    fc = resolve_skill_root() / "assets" / "fontconfig" / "fonts.conf"
    return fc if fc.is_file() else None


def export_fontconfig(env: Dict[str, str]) -> None:
    """
    Export FONTCONFIG_FILE so the wrapped render_graph.py resolves Google Sans.

    render_graph.py materialises a fontconfig file with ABSOLUTE font paths to
    work around the sandbox where `~` and prefix="xdg" expand to nothing.
    Rather than duplicate that work here, we simply hand its file to every
    child process we launch.
    """
    fc = wrapped_fontconfig()
    if fc is not None:
        env["FONTCONFIG_FILE"] = str(fc)


# ---------------------------------------------------------------------------
# Preset registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArchPreset:
    id: str
    label: str
    notes: str
    spec_stub: str


@dataclass(frozen=True)
class IllustrationPreset:
    id: str
    label: str
    notes: str
    theme: str          # must be a valid --theme value for generate_twg.py
    prompt_stub: str


# Tuned for the FDE / AI Tech Group GTM domain. Every stub references
# current-generation building blocks (Vertex AI, ADK 2.0, Agent Gateway,
# Agent Retrieval, Gemini 3 Pro / 3.1 Flash, Nano Banana 2, MCP, A2A).
# No legacy models (no Imagen, Veo, Lyria, 1.5-series).

ARCHITECTURE_PRESETS: Dict[str, ArchPreset] = {
    "agentic-arch": ArchPreset(
        id="agentic-arch",
        label="Root-Worker agentic architecture on Vertex AI",
        notes="Default GTM shape. Root planner + parallel worker agents, ADK 2.0, Agent Retrieval, Agent Gateway.",
        spec_stub=(
            "A Root-Worker agentic architecture on Google Cloud Vertex AI. "
            "Left-to-right flow. User request enters a Root agent built with "
            "ADK 2.0 running on Cloud Run. The Root agent plans and dispatches "
            "to a fan-out of parallel Worker agents (also ADK 2.0), each "
            "specialised for a task. Workers reach tools and data via Agent "
            "Gateway (policy, quota, auth) and pull grounded context from "
            "Agent Retrieval (Vertex AI Vector Search 2.0) backed by Cloud "
            "Spanner and BigQuery. Long-horizon memory in Firestore. Model "
            "layer shows Gemini 3 Pro for planning / hard reasoning and "
            "Gemini 3.1 Flash for high-throughput worker calls. Optional MCP "
            "and A2A boundaries to external tools and partner agents. "
            "Observability plane on Cloud Logging + Cloud Trace."
        ),
    ),
    "model-plus-harness": ArchPreset(
        id="model-plus-harness",
        label="Model + Harness split diagram",
        notes="Separates raw model capability from the harness (tools, memory, orchestration) around it.",
        spec_stub=(
            "A two-layer diagram contrasting the MODEL layer and the HARNESS "
            "layer around it. Model layer: Gemini 3 Pro, Gemini 3.1 Flash, "
            "Nano Banana 2 for media, all served via Vertex AI. Harness layer "
            "wrapping the model: ADK 2.0 agent runtime, Agent Gateway for "
            "policy and identity, Agent Retrieval for grounding, tool "
            "registry with MCP + A2A adapters, memory store, evaluator loop, "
            "and safety filters. Show clearly that the harness is where "
            "enterprise value accrues, while the model is a swappable "
            "capability."
        ),
    ),
    "tokenomics": ArchPreset(
        id="tokenomics",
        label="Enterprise LLM tokenomics flow",
        notes="Prompt caching, output-token tax, thinking-token management, tool bloat. User fills in real numbers via --spec.",
        spec_stub=(
            "A tokenomics flow diagram for an enterprise LLM workload on "
            "Vertex AI. Show, left to right: (1) input tokens split into "
            "CACHED prefix (system prompt, tool schemas, few-shot) vs FRESH "
            "user turn, with a callout on prompt-caching hit rate and cost "
            "delta; (2) thinking / reasoning token budget for Gemini 3 Pro, "
            "with a control knob for thinking-token management; (3) tool-call "
            "expansion showing tool-schema bloat inflating every turn; "
            "(4) output tokens with the 'output-token tax' relative to input "
            "cost. End with a total-cost meter and a savings meter driven by "
            "cache hit rate + thinking control + tool pruning."
        ),
    ),
    "security-posture": ArchPreset(
        id="security-posture",
        label="Agentic security posture",
        notes="Sandboxing tiers, non-human identity, kill switches, prompt-injection defense, SecOps integration.",
        spec_stub=(
            "An agentic security posture diagram for a Vertex AI + ADK 2.0 "
            "deployment. Concentric containment tiers around the agent "
            "runtime: (1) sandboxed tool execution with per-tool "
            "capability grants; (2) non-human identity via Workload Identity "
            "Federation, with short-lived tokens minted through Agent "
            "Gateway; (3) prompt-injection defense on every ingested content "
            "boundary (web, docs, email, tool output); (4) kill switch and "
            "circuit breaker in the control plane; (5) audit and detection "
            "via Google SecOps interoperating with Microsoft Defender. Call "
            "out MCP and A2A boundaries as trust edges."
        ),
    ),
    "migration-journey": ArchPreset(
        id="migration-journey",
        label="Legacy stack to agentic stack migration journey",
        notes="Timeline / swim-lane migration from a legacy LLM stack to a Vertex AI + ADK 2.0 agentic stack.",
        spec_stub=(
            "A migration journey diagram, left-to-right timeline in swim "
            "lanes. Starting state: a monolithic RAG chatbot on a legacy "
            "stack (single model call, brittle retrieval, no tool use). "
            "Intermediate phases: (a) introduce Agent Retrieval on Vertex "
            "AI Vector Search 2.0; (b) replace the single call with an ADK "
            "2.0 Root agent + one Worker; (c) add Agent Gateway for policy "
            "and identity; (d) fan out to specialised Workers on Gemini 3.1 "
            "Flash; (e) add MCP tool servers and A2A partner agents. Target "
            "state: full Root-Worker agentic architecture with observability "
            "and evaluators. Mark each phase with concrete GTM value."
        ),
    ),
    "before-after": ArchPreset(
        id="before-after",
        label="Before / After architecture comparison",
        notes="Side-by-side legacy vs modern agentic stack — good for exec slides.",
        spec_stub=(
            "A side-by-side BEFORE / AFTER architecture comparison. LEFT "
            "(before): monolithic chatbot, single LLM call, hardcoded "
            "prompts, no retrieval grounding, no tool use, no policy plane. "
            "RIGHT (after): Root-Worker agentic architecture on Vertex AI, "
            "ADK 2.0 agents, Agent Gateway for policy and identity, Agent "
            "Retrieval for grounding, MCP tool registry, evaluator loop, "
            "Gemini 3 Pro + 3.1 Flash tiering. Use identical visual scale on "
            "both sides so the delta reads instantly."
        ),
    ),
    "maturity-curve": ArchPreset(
        id="maturity-curve",
        label="Agentic maturity curve",
        notes="Five-stage curve from scripted RAG to autonomous multi-agent operations.",
        spec_stub=(
            "An agentic maturity curve, five stages along an ascending "
            "arc. Stage 1: scripted RAG. Stage 2: single-agent tool use "
            "with ADK 2.0. Stage 3: Root-Worker topology with Agent "
            "Gateway. Stage 4: multi-agent collaboration over A2A with "
            "shared Agent Retrieval. Stage 5: autonomous long-horizon "
            "operations with evaluator loops, memory, and human-in-the-loop "
            "checkpoints. For each stage show the primary Google Cloud "
            "primitive that unlocks it."
        ),
    ),
    "agent-mesh": ArchPreset(
        id="agent-mesh",
        label="Multi-agent mesh over A2A",
        notes="Peer agents collaborating over A2A, each fronting its own tools and data via Agent Gateway.",
        spec_stub=(
            "A multi-agent mesh diagram. Several peer agents built with "
            "ADK 2.0 collaborate over the A2A protocol. Each agent fronts "
            "its own private tool set and data via Agent Gateway and pulls "
            "grounded context from Agent Retrieval. Show a shared identity "
            "and policy plane, plus a shared observability plane. Highlight "
            "which edges are internal (in-org A2A) vs partner (cross-org "
            "A2A with mutual attestation)."
        ),
    ),
    "cost-flow": ArchPreset(
        id="cost-flow",
        label="Per-request cost flow",
        notes="Sankey-style cost decomposition of a single agent request. User supplies rates via --spec.",
        spec_stub=(
            "A Sankey-style cost flow for a single end-to-end agent "
            "request on Vertex AI. Source node: user request. Downstream "
            "flows split into: cached input tokens, fresh input tokens, "
            "tool-call round trips, retrieval calls to Agent Retrieval, "
            "thinking tokens on Gemini 3 Pro, worker tokens on Gemini 3.1 "
            "Flash, and output tokens. Terminal nodes: unit cost per "
            "request, with a parallel 'savings if cached' shadow flow."
        ),
    ),
    "gateway-topology": ArchPreset(
        id="gateway-topology",
        label="Agent Gateway topology",
        notes="Zooms in on Agent Gateway — policy, identity, quota, routing, MCP/A2A adapters.",
        spec_stub=(
            "A zoomed-in topology of Agent Gateway sitting between ADK 2.0 "
            "agents and downstream resources. Show its internal planes: "
            "identity (Workload Identity Federation, short-lived tokens), "
            "policy (per-tool capability grants, egress rules), quota and "
            "rate limits, routing to MCP tool servers and A2A partner "
            "agents, observability tap, and prompt-injection filters at the "
            "content boundary. Upstream: multiple agents. Downstream: MCP "
            "tools, A2A partners, Agent Retrieval, private APIs."
        ),
    ),
    "evaluator-loop": ArchPreset(
        id="evaluator-loop",
        label="Evaluator + MUST-FIX loop",
        notes="Adds an independent evaluator agent that gates output and triggers MUST-FIX rounds.",
        spec_stub=(
            "An evaluator-loop diagram. A Root agent produces a candidate "
            "response. An INDEPENDENT evaluator agent (separate ADK 2.0 "
            "agent, separate prompt, no shared state) scores the response "
            "against a rubric and either PASSES it downstream or emits a "
            "MUST-FIX list back to the Root agent. Show the loop count "
            "guard, the human-in-the-loop escape hatch, and the audit trail "
            "in Cloud Logging."
        ),
    ),
    "sdlc-loop": ArchPreset(
        id="sdlc-loop",
        label="Agentic SDLC loop",
        notes="Spec-driven plan -> parallel worker implementation -> evaluator review -> merge.",
        spec_stub=(
            "An agentic Software Development Lifecycle loop. Phases in a "
            "circular flow: (1) spec-driven planning with a Root agent on "
            "Gemini 3 Pro; (2) explicit user approval gate; (3) parallel "
            "Worker agents implementing subtasks on Gemini 3.1 Flash; "
            "(4) independent evaluator/reviewer agent with MUST-FIX round; "
            "(5) hard-verification of claims against real artefacts; "
            "(6) merge and observability capture. Tools plane on MCP; "
            "identity via Agent Gateway."
        ),
    ),
}


ILLUSTRATION_PRESETS: Dict[str, IllustrationPreset] = {
    "agentic-workflow": IllustrationPreset(
        id="agentic-workflow",
        label="Agentic workflow hero",
        notes="Editorial illustration of a Root-Worker agentic workflow.",
        theme="ai_automation",
        prompt_stub=(
            "An editorial hero illustration of an agentic workflow. A "
            "central orchestrator figure dispatches tasks to a fan of "
            "specialised worker figures, each handling a distinct step. "
            "Convey coordination, parallelism, and grounded reasoning. "
            "Oversized abstract visual metaphors, no embedded text labels."
        ),
    ),
    "human-plus-agents": IllustrationPreset(
        id="human-plus-agents",
        label="Human + agents collaboration",
        notes="A human professional collaborating with a small team of agents, not replaced by them.",
        theme="ai_automation",
        prompt_stub=(
            "An editorial illustration of a human professional collaborating "
            "with a small team of AI agents as peers. The human is clearly "
            "in the loop, reviewing and steering, while the agents extend "
            "their reach. Warm, optimistic composition. No text labels."
        ),
    ),
    "cost-savings": IllustrationPreset(
        id="cost-savings",
        label="Tokenomics cost-savings hero",
        notes="Visual metaphor for cost reduction from prompt caching and thinking-token control.",
        theme="finance",
        prompt_stub=(
            "An editorial illustration for enterprise LLM cost savings. "
            "A large meter or scale tipping toward savings, with abstract "
            "flows representing cached context, controlled reasoning, and "
            "pruned tool schemas feeding the light side. No text labels."
        ),
    ),
    "secure-agents": IllustrationPreset(
        id="secure-agents",
        label="Secure agents hero",
        notes="Containment, identity, and kill-switch metaphors around an agent.",
        theme="security",
        prompt_stub=(
            "An editorial illustration of a secure AI agent. Concentric "
            "shields, a clear identity badge, and a visible control lever "
            "(kill switch) held by a human hand. Convey containment "
            "without menace. No text labels."
        ),
    ),
    "migration": IllustrationPreset(
        id="migration",
        label="Migration journey hero",
        notes="Bridge / path metaphor from a legacy stack to an agentic stack.",
        theme="growth",
        prompt_stub=(
            "An editorial illustration of a migration journey. A bridge or "
            "path leads from a dim, monolithic legacy structure on the left "
            "to a bright, modular agentic landscape on the right. Convey "
            "forward motion, safety, and the gain on the far side. No text "
            "labels."
        ),
    ),
    "evangelism": IllustrationPreset(
        id="evangelism",
        label="Evangelism / podcast hero",
        notes="For podcast episodes, keynote openers, and community talks.",
        theme="communication",
        prompt_stub=(
            "An editorial illustration for a technical evangelism moment. "
            "A speaker figure amplified by abstract sound waves reaching a "
            "diverse audience of practitioners. Warm, aspirational, "
            "not sales-y. No text labels."
        ),
    ),
    "developer-productivity": IllustrationPreset(
        id="developer-productivity",
        label="Developer productivity hero",
        notes="AI-assisted software engineering, vibe-coding, agentic SDLC.",
        theme="innovation",
        prompt_stub=(
            "An editorial illustration of AI-assisted software engineering. "
            "A developer at a workstation extended by ghost-like agent "
            "collaborators drafting, reviewing, and refactoring code in "
            "parallel. Convey flow, speed, and quality. No text labels."
        ),
    ),
    "data-to-insight": IllustrationPreset(
        id="data-to-insight",
        label="Data to insight hero",
        notes="Grounded reasoning: raw enterprise data being distilled into a decision.",
        theme="analytics",
        prompt_stub=(
            "An editorial illustration of the journey from raw enterprise "
            "data to a crisp business decision. Streams of abstract data "
            "converge into a lens or prism that emits a single clear "
            "insight beam. No text labels."
        ),
    ),
    "agent-mesh": IllustrationPreset(
        id="agent-mesh",
        label="Agent mesh / A2A hero",
        notes="Peer agents collaborating across organisational boundaries.",
        theme="omnichannel",
        prompt_stub=(
            "An editorial illustration of a mesh of AI agents collaborating "
            "as peers across organisational boundaries. Nodes of different "
            "shapes exchanging structured signals along glowing edges. "
            "Convey trust, protocol, and interoperability. No text labels."
        ),
    ),
    "supply-chain-agents": IllustrationPreset(
        id="supply-chain-agents",
        label="Supply-chain agents hero",
        notes="For retail / logistics customer material.",
        theme="supply_chain",
        prompt_stub=(
            "An editorial illustration of AI agents coordinating an "
            "end-to-end supply chain, from sourcing to last mile. Abstract "
            "conveyors, nodes, and route lines choreographed by unseen "
            "agent hands. No text labels."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Tier -> model / resolution mapping
# ---------------------------------------------------------------------------

# Architecture (generate_architecture.py uses --model {pro,nb2,lite}).
ARCH_TIER_MODEL = {"finished": "pro", "simple": "nb2", "pre-render": "lite"}

# Illustration (generate_twg.py accepts nano-banana-* aliases).
ILLUS_TIER_MODEL = {
    "finished": "nano-banana-pro",
    "simple": "nano-banana-2",
    "pre-render": "nano-banana-2-lite",
}

# Auto-resolution per tier (either script).
TIER_RESOLUTION = {"finished": "4K", "simple": "2K", "pre-render": "1K"}


# ---------------------------------------------------------------------------
# Output path resolution
# ---------------------------------------------------------------------------

def resolve_out_path(out: Optional[str], preset_id: str, count: int) -> Path:
    """
    Resolve the --out value into a concrete path we can hand downstream.

    Rules (documented in the task contract):
      - Default: ./assets/<preset-id>.png
      - If --out points at an existing directory (or ends in /), use it and
        put <preset-id>.png inside it.
      - Otherwise treat --out as a full filename.
      - Parent dirs are created.
      - When count > 1, the wrapped scripts append their own index suffix;
        we don't try to second-guess that here.

    The returned path is what we hand as --output to the wrapped script.
    """
    if out is None:
        target = Path("assets") / f"{preset_id}.png"
    else:
        p = Path(out)
        if p.is_dir() or out.endswith(os.sep):
            target = p / f"{preset_id}.png"
        else:
            target = p
    target.parent.mkdir(parents=True, exist_ok=True)
    return target.resolve()


# ---------------------------------------------------------------------------
# Subprocess plumbing
# ---------------------------------------------------------------------------

def _launch(argv: List[str], dry_run: bool) -> int:
    """Print + optionally exec. Returns child return code (0 on dry run)."""
    env = os.environ.copy()
    export_fontconfig(env)
    printable = " ".join(shlex.quote(a) for a in argv)
    if dry_run:
        print("DRY-RUN would exec:")
        print(f"  {printable}")
        if "FONTCONFIG_FILE" in env:
            print(f"  FONTCONFIG_FILE={env['FONTCONFIG_FILE']}")
        return 0
    print(f"exec: {printable}")
    return subprocess.call(argv, env=env)


# ---------------------------------------------------------------------------
# Subcommand: architecture
# ---------------------------------------------------------------------------

def cmd_architecture(args: argparse.Namespace) -> int:
    preset = ARCHITECTURE_PRESETS[args.preset]
    if args.spec:
        spec = preset.spec_stub + "\n\n" + args.spec
    else:
        spec = preset.spec_stub

    model = ARCH_TIER_MODEL[args.tier]
    resolution = args.resolution or TIER_RESOLUTION[args.tier]
    out_path = resolve_out_path(args.out, preset.id, args.count)

    script = wrapped_scripts_dir() / "generate_architecture.py"
    argv = [
        sys.executable, str(script),
        "--spec", spec,
        "--theme", args.theme,
        "--model", model,
        "--aspect-ratio", args.aspect,
        "--resolution", resolution,
        "--count", str(args.count),
        "--output", str(out_path),
    ]
    if args.title:
        argv += ["--title", args.title]
    if args.project:
        argv += ["--project", args.project]
    if args.location:
        argv += ["--location", args.location]
    if args.dry_run:
        # Push --dry-run through so the upstream also prints the composed
        # prompt from ITS side (useful when debugging prompt shaping).
        argv.append("--dry-run")

    rc = _launch(argv, dry_run=args.dry_run)
    print(f"resolved output: {out_path}")
    return rc


# ---------------------------------------------------------------------------
# Subcommand: illustration
# ---------------------------------------------------------------------------

def cmd_illustration(args: argparse.Namespace) -> int:
    preset = ILLUSTRATION_PRESETS[args.preset]
    if args.prompt:
        prompt = preset.prompt_stub + "\n\n" + args.prompt
    else:
        prompt = preset.prompt_stub

    model = ILLUS_TIER_MODEL[args.tier]
    resolution = args.resolution or TIER_RESOLUTION[args.tier]
    # nano-banana-2-lite is 1K-only; be defensive.
    if model == "nano-banana-2-lite" and resolution != "1K":
        print(
            f"note: nano-banana-2-lite only supports 1K; downgrading "
            f"{resolution} -> 1K",
            file=sys.stderr,
        )
        resolution = "1K"

    out_path = resolve_out_path(args.out, preset.id, args.count)

    script = wrapped_scripts_dir() / "generate_twg.py"
    argv = [
        sys.executable, str(script),
        "--prompt", prompt,
        "--theme", preset.theme,
        "--model", model,
        "--resolution", resolution,
        "--aspect-ratio", args.aspect,
        "--count", str(args.count),
        "--output", str(out_path),
    ]
    if args.project:
        argv += ["--project", args.project]
    if args.location:
        argv += ["--location", args.location]

    # generate_twg.py has no --dry-run flag, so we handle it locally by
    # short-circuiting the launch when dry_run is set.
    rc = _launch(argv, dry_run=args.dry_run)
    print(f"resolved output: {out_path}")
    return rc


# ---------------------------------------------------------------------------
# Subcommand: graph  (pass-through to render_graph.py)
# ---------------------------------------------------------------------------

def cmd_graph(args: argparse.Namespace) -> int:
    script = wrapped_scripts_dir() / "render_graph.py"
    argv = [sys.executable, str(script)]

    if args.check_fonts:
        argv.append("--check-fonts")
    if args.mermaid:
        argv += ["--mermaid", args.mermaid]
    if args.mermaid_src:
        argv += ["--mermaid-src", args.mermaid_src]
    if args.dot:
        argv += ["--dot", args.dot]
    if args.dot_src:
        argv += ["--dot-src", args.dot_src]
    if args.out:
        argv += ["--out", args.out]
    if args.scale is not None:
        argv += ["--scale", str(args.scale)]
    if args.width is not None:
        argv += ["--width", str(args.width)]
    if args.bg:
        argv += ["--bg", args.bg]
    if args.dpi is not None:
        argv += ["--dpi", str(args.dpi)]
    if args.engine:
        argv += ["--engine", args.engine]

    rc = _launch(argv, dry_run=False)
    if args.out:
        print(f"resolved output: {Path(args.out).resolve()}")
    return rc


# ---------------------------------------------------------------------------
# Subcommand: presets  (informational, no side effects)
# ---------------------------------------------------------------------------

def cmd_presets(_args: argparse.Namespace) -> int:
    print("ARCHITECTURE PRESETS")
    print("-" * 72)
    width = max(len(p.id) for p in ARCHITECTURE_PRESETS.values())
    for p in ARCHITECTURE_PRESETS.values():
        print(f"  {p.id:<{width}}  {p.label}")
        print(f"  {'':<{width}}    {p.notes}")
    print()
    print("ILLUSTRATION PRESETS")
    print("-" * 72)
    width = max(len(p.id) for p in ILLUSTRATION_PRESETS.values())
    for p in ILLUSTRATION_PRESETS.values():
        print(f"  {p.id:<{width}}  {p.label}  [theme={p.theme}]")
        print(f"  {'':<{width}}    {p.notes}")
    return 0


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gen_visuals.py",
        description=(
            "Thin wrapper over the think-with-google-infographics skill for "
            "AI Tech GTM collateral. Every visual flows through the wrapped "
            "skill's three scripts; this CLI only composes prompts and shells "
            "out."
        ),
    )
    subs = parser.add_subparsers(dest="cmd", required=True)

    # -- architecture --------------------------------------------------------
    a = subs.add_parser(
        "architecture",
        help="Generate GTM architecture diagrams via generate_architecture.py.",
    )
    a.add_argument(
        "--preset", required=True, choices=sorted(ARCHITECTURE_PRESETS.keys()),
        help="Preset spec stub to compose the diagram around.",
    )
    a.add_argument("--spec", default=None, help="Extra free-text spec appended to the preset stub.")
    a.add_argument("--title", default=None, help="Optional title rendered on the canvas.")
    a.add_argument("--aspect", default="16:9", choices=["16:9", "3:2", "4:3"],
                   help="Aspect ratio (default 16:9).")
    a.add_argument("--tier", default="finished", choices=["finished", "simple", "pre-render"],
                   help="finished=Nano Banana Pro @ 4K, simple=NB2 @ 2K, pre-render=NB2 Lite @ 1K.")
    a.add_argument("--resolution", default=None, choices=["1K", "2K", "4K"],
                   help="Override the tier-default resolution.")
    a.add_argument("--theme", default="new", choices=["new", "old"],
                   help="Visual theme for the wrapped script (default: new).")
    a.add_argument("--count", type=int, default=1, help="Number of variants.")
    a.add_argument("--out", default=None,
                   help="Output file or directory. Default: ./assets/<preset-id>.png.")
    a.add_argument("--project", default=None, help="GCP project id (passthrough).")
    a.add_argument("--location", default=None, help="GCP region (passthrough).")
    a.add_argument("--dry-run", action="store_true",
                   help="Print the composed subprocess argv (and pass --dry-run downstream) instead of running.")
    a.set_defaults(func=cmd_architecture)

    # -- illustration --------------------------------------------------------
    i = subs.add_parser(
        "illustration",
        help="Generate editorial hero illustrations via generate_twg.py.",
    )
    i.add_argument(
        "--preset", required=True, choices=sorted(ILLUSTRATION_PRESETS.keys()),
        help="Preset prompt stub + wrapped-script theme.",
    )
    i.add_argument("--prompt", default=None, help="Extra free-text prompt appended to the preset stub.")
    i.add_argument("--aspect", default="3:2",
                   choices=["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                   help="Aspect ratio (default 3:2).")
    i.add_argument("--tier", default="finished", choices=["finished", "simple", "pre-render"],
                   help="finished=Nano Banana Pro @ 4K, simple=Nano Banana 2 @ 2K, "
                        "pre-render=Nano Banana 2 Lite @ 1K.")
    i.add_argument("--resolution", default=None, choices=["1K", "2K", "4K"],
                   help="Override the tier-default resolution.")
    i.add_argument("--count", type=int, default=1, help="Number of variants.")
    i.add_argument("--out", default=None,
                   help="Output file or directory. Default: ./assets/<preset-id>.png.")
    i.add_argument("--project", default=None, help="GCP project id (passthrough).")
    i.add_argument("--location", default=None, help="GCP region (passthrough).")
    i.add_argument("--dry-run", action="store_true",
                   help="Print the composed subprocess argv instead of running. "
                        "(generate_twg.py has no --dry-run of its own.)")
    i.set_defaults(func=cmd_illustration)

    # -- graph ---------------------------------------------------------------
    g = subs.add_parser(
        "graph",
        help="Render plain Mermaid / Graphviz diagrams via render_graph.py.",
    )
    g.add_argument("--check-fonts", action="store_true",
                   help="Verify Google Sans resolves (passthrough).")
    src = g.add_mutually_exclusive_group()
    src.add_argument("--mermaid", default=None, help="Path to a .mmd source file.")
    src.add_argument("--mermaid-src", default=None, help="Inline Mermaid source.")
    src.add_argument("--dot", default=None, help="Path to a .dot / Graphviz source file.")
    src.add_argument("--dot-src", default=None, help="Inline Graphviz source.")
    g.add_argument("--out", default=None, help="Output path; extension picks the format.")
    g.add_argument("--scale", type=float, default=None, help="Mermaid raster scale factor.")
    g.add_argument("--width", type=int, default=None, help="Mermaid render width in px.")
    g.add_argument("--bg", default=None, help="Mermaid background colour.")
    g.add_argument("--dpi", type=int, default=None, help="Graphviz raster DPI.")
    g.add_argument("--engine", default=None,
                   choices=["dot", "neato", "fdp", "sfdp", "circo", "twopi"],
                   help="Graphviz layout engine.")
    g.set_defaults(func=cmd_graph)

    # -- presets -------------------------------------------------------------
    p = subs.add_parser("presets", help="List all available presets and exit.")
    p.set_defaults(func=cmd_presets)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
