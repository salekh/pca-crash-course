# Authoring contract — `ai-tech-gtm-collateral`

> **Status:** normative. Both the Google Slides deck compiler
> (`build_deck.py`) and the headless-Chrome PDF renderer (`build_techdoc.py`)
> consume this grammar. **One Markdown source → two artefacts.**

---

## 1. Purpose & audience

This skill produces AI/GTM collateral — pitch decks, executive
briefings, workshop material, deep tech guides, one-pagers — from a
single Markdown source of truth. The same file compiles to a
Google Slides deck **and** to a Chrome-rendered PDF without author edits.
That is only possible if the grammar is small, unambiguous, and
prescriptive.

Three readers of this document:

| Reader | Uses this doc to… |
| --- | --- |
| **Skill router** (the caller that picks `ai-tech-gtm-collateral` for a task) | Decide whether an incoming brief maps to a supported `collateral_type` and what front-matter to prefill. |
| **Deck compiler** (`build_deck.py`, other track) | Turn each directive block into the named Slides layout listed in §4, and honour the speaker-notes and cover-content rules in §5–§6. |
| **Chrome PDF renderer** (`build_techdoc.py`, this track) | Emit the print equivalent for each directive per §4/§7, and degrade unsupported constructs cleanly. |

If a change to one path (deck **or** print) forces a change to source
syntax, this file is updated first and **both** compilers are updated
to match. Source files never fork.

---

## 2. File format overview

- File extension: **`.md`**. UTF-8, LF line endings, no BOM.
- **Front-matter** is YAML between two `---` lines at the very top of
  the file (§3). If the first line is not `---`, front-matter is
  considered empty and every field falls back to its default.
- **Body** is CommonMark, plus a fixed catalogue of **fenced
  directives** (§4) using the `:::name` / `:::` fenced-directive syntax
  with an optional `{key="value"}` attribute list.
- Headings act as **structural cues**:
  - `#` — section (deck: no slide of its own; groups the following
    slides under a section index).
  - `##` — new slide with that title (deck path) / subsection heading
    (print path).
  - `###` — subsection within the current slide / sub-subsection in
    print.
- **Blockquotes** starting with `> notes:` are speaker notes bound to
  the current slide (§6).
- **Nested directives are not supported.** Directive blocks are flat
  and cannot contain other `:::` blocks. Regular CommonMark (lists,
  emphasis, links, inline code) inside a directive body is fine
  wherever the directive spec allows a body.

### 2.1 Minimal parseable example

```markdown
---
title: "Agentic SDLC in 20 minutes"
collateral_type: exec-briefing
customer: "Acme Corp"
---

::: stat {value="87" unit="%" label="of dev teams pilot agents in 2026"}
:::

## Why now

Three forces converge: models, tools, and org readiness.

> notes: Anchor on the readiness gap — that's the real story.
```

This file parses, compiles to a 2-slide deck (cover + "Why now"), and
renders to a one-page PDF.

---

## 3. YAML front-matter schema

All keys are lowercase. Unknown keys are preserved and passed through
to both compilers as opaque metadata (see §10).

| Field | Type | Required | Default | Allowed values | Notes |
| --- | --- | --- | --- | --- | --- |
| `title` | str | **yes** | — | any | Cover title. Sentence case recommended; ≤ 60 chars renders best on 16:9. |
| `subtitle` | str | no | *(none)* | any | Cover subtitle / dek. |
| `collateral_type` | enum | **yes** | — | `pitch-deck`, `exec-briefing`, `workshop-deck`, `tech-guide`, `one-pager` | Selects the master template on both paths. See §3.1. |
| `author` | str | no | `"Sanchit Alekh"` | any | Byline on cover and footer. |
| `customer` | str | no | *(none)* | any | Customer name. **Triggers the customer-safe footer swap** — see `confidentiality` below. |
| `date` | ISO 8601 date | no | *build date* | `YYYY-MM-DD` | Appears on cover and PDF title page. |
| `confidentiality` | enum | no | `internal` | `internal`, `proprietary`, `customer-shared`, `public` | Drives footer text. See §3.2. |
| `theme` | enum | no | `light` | `light`, `dark`, `auto` | `auto` = per-slide via a `theme=` attribute on the directive. |
| `abstract` | str | no | *(none)* | any (multiline `>` OK) | Print: rendered on the PDF title page under the title. Deck: rendered on an auto-inserted “About this briefing” slide **only** if `collateral_type ∈ {exec-briefing, tech-guide}`. |
| `tags` | list[str] | no | `[]` | free-form | Passed through; used by the skill router and filed as PDF keywords. |
| `logo_variant` | enum | no | *(auto)* | `google-cloud`, `google-cloud-mono`, `none` | Overrides the logo picked from `collateral_type` × `theme`. |
| `output_basename` | str | no | *slugified `title`* | `[a-z0-9-]+` | Sets the filename stem for `<basename>.pdf` and the deck name. |

### 3.1 `collateral_type` → template mapping

| Value | Deck master | Print master |
| --- | --- | --- |
| `pitch-deck` | 16:9, dark cover + light body, dense visuals | not emitted (print path errors with a clear message) |
| `exec-briefing` | 16:9, light throughout, high-density | Chrome PDF (A4, 9.5 pt body, tight margins, high-density leave-behind layout) |
| `workshop-deck` | 16:9, alternating light/dark, section dividers between modules | Chrome PDF workbook (A4, agenda front-matter, module dividers) |
| `tech-guide` | 16:9, light, section dividers per `#` heading | Chrome PDF long-form (A4, ToC + running headers + section dividers) |
| `one-pager` | 1 title slide + 1 dense body slide max | Chrome PDF (single A4 portrait page, ultra-compressed) |

### 3.2 Confidentiality footer text

The footer string is deterministic. Both compilers emit it verbatim
in the bottom-left of every non-cover slide / every page footer.

| `confidentiality` | Footer text (no `customer:`) | Footer text (with `customer:` set) |
| --- | --- | --- |
| `internal` | `Google — Internal` | `Google & {customer} — Confidential` |
| `proprietary` | `Google Cloud  \|  Proprietary & Confidential` | `Google & {customer} — Proprietary & Confidential` |
| `customer-shared` | `Google Cloud  \|  Shared with customer` | `Google & {customer} — Confidential` |
| `public` | `Google Cloud` | `Google Cloud` *(customer swap is suppressed for public material)* |

**Customer-swap rule (normative):** if `customer:` is set **and**
`confidentiality ∈ {internal, proprietary, customer-shared}`, the
right column above wins. `public` never swaps. The swap happens at
compile time; author does not write footer text by hand.

---

## 4. Directive catalogue

All directives share the same block form. Attribute list is optional.

```
::: name {attr1="val" attr2="val"}
…body…
:::
```

Directive names are lowercase-with-dashes. Attribute values are
double-quoted strings, unquoted numbers, or unquoted `true`/`false`.
Every directive accepts an optional `theme="light|dark"` attribute
that overrides the file-level `theme` when `theme: auto`.

### 4.1 `:::stat` — hero big-number stat

**Syntax**

```
::: stat {value="87" unit="%" label="of dev teams pilot agents in 2026" caption="Google Cloud AI Adoption Survey, 2026"}
:::
```

**Fields**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `value` | str/num | **required** | Big number. Digits + optional decimal; use `unit` for the symbol. |
| `unit` | str | `""` | Suffix shown at ~40 % of `value` size. |
| `label` | str | **required** | One-line description under the number. |
| `caption` | str | `""` | Source / footnote, small type. |

**Slide mapping:** layout `stat-hero`.
**Print mapping:** `\fdestat{value}{unit}{label}{caption}` — a
bordered stat box; 92 mm wide, centred, source in `\footnotesize`.

### 4.2 `:::cards` — 2–4 small cards, one row

**Syntax** (body is a YAML list, one item per card):

```
::: cards
- icon: "shield-check"
  title: "Contained"
  body: "Sandboxed agents, non-human identity."
- icon: "cpu"
  title: "Capable"
  body: "Gemini 3 Pro planning, NB2 for visuals."
- icon: "gauge"
  title: "Observable"
  body: "Full trace of every tool call."
:::
```

**Fields per card**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `icon` | str | `""` | Icon slug (Google Material name, no prefix). |
| `title` | str | **required** | ≤ 24 chars renders best. |
| `body` | str | **required** | One line, ≤ 90 chars. |

**Block-level attributes**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `columns` | int | `len(cards)` | Force column count; must be 2, 3, or 4. |
| `tint` | enum | `mixed` | `blue`, `red`, `yellow`, `green`, `mixed` (rotates the 4 brand colours). |

**Slide mapping:** layout `cards-row`.
**Print mapping:** a `tabularx` with `columns` equally-wide cells,
tinted header stripe per `tint`, icon rendered above title via
`\fdeicon{slug}`.

### 4.3 `:::figure` — image with caption

**Syntax**

```
::: figure {src="assets/agentic-topology.png" caption="Root-worker topology, ADK 2.0" alt="Diagram showing a root agent orchestrating four worker agents" credit="Google Cloud" width="0.66" aspect="16:9"}
:::
```

**Fields**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `src` | str | **required** | Path relative to the source file. |
| `caption` | str | `""` | Rendered under the image. |
| `alt` | str | *= caption* | Accessibility text; required if `caption` empty (parser warns). |
| `credit` | str | `""` | Small italic line right of caption. |
| `width` | float | `1.0` | Fraction of content width. Values ≤ `0.5` route to a half-slide layout. |
| `aspect` | enum | *(intrinsic)* | `16:9`, `3:2`, `4:3`. Forces a crop/pad frame. |

**Slide mapping:** `figure-full` when `width > 0.5`, otherwise
`figure-half` (image + adjacent text column absorbs any surrounding
prose until the next `##` or `:::`).
**Print mapping:** `\fdefigure[width]{src}{caption}{credit}`; PDF
alt-text is set from `alt` via `\pdftooltip`.

### 4.4 `:::quote` — pull quote

**Syntax**

```
::: quote {attribution="Jane Doe" role="Head of Platform, Acme" avatar="assets/jane.jpg"}
Agents changed how we ship — from six-week releases to daily drops.
:::
```

**Fields**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `attribution` | str | **required** | Name of speaker. |
| `role` | str | `""` | Title / organisation. |
| `avatar` | str | `""` | Optional headshot; rendered as a circular 64 pt crop. |

**Slide mapping:** layout `quote-hero`.
**Print mapping:** `\begin{fdequote}…\end{fdequote}` — indented,
oversized opening glyph, attribution right-aligned under the rule.

### 4.5 `:::agenda` — ordered agenda list

**Syntax** (body is a YAML list):

```
::: agenda
- title: "The agentic shift"
  duration: "10 min"
- title: "Reference topology"
  duration: "15 min"
- title: "Live build"
  duration: "25 min"
- title: "Q & A"
:::
```

**Fields per item**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `title` | str | **required** | Item name. |
| `duration` | str | `""` | Free-form; recommended `"N min"`. |
| `owner` | str | `""` | Optional presenter name for workshop decks. |

**Slide mapping:** layout `agenda`.
**Print mapping:** itemised list; `duration` right-aligned in a
`tabularx` `X r` layout with a hair-rule between rows.

### 4.6 `:::divider` — full-bleed rainbow gradient section divider

**Syntax**

```
::: divider {label="Reference topology" number="02"}
:::
```

**Fields**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `label` | str | **required** | Big word/phrase on the divider. |
| `number` | str | *(auto)* | Section counter, e.g. `"02"`. Auto-assigned by the compiler from the preceding `#` count if omitted. |

**Slide mapping:** layout `divider-gradient` (full-bleed rainbow
burst, label centred, number small top-right).
**Print mapping:** in `tech-guide` and `workshop`, a full-width
banner (`bg_gradient_divider.png`) spanning the text block, followed
by `\clearpage` so the next section starts on a fresh page. In
`one-pager`, a subtle 4-colour `\rule` and inline label (no page
break — one-pagers stay on one page by construction).

### 4.7 `:::callout` — coloured admonition

**Syntax**

```
::: callout {kind="warning" title="Cost trap"}
Cache invalidation on tool-heavy prompts wipes 70 % of the savings.
Pin your tool definitions.
:::
```

**Fields**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `kind` | enum | `note` | `note`, `warning`, `tip`, `insight`, `do`, `dont`. |
| `title` | str | *(= kind, title-cased)* | Header. |

**Kind → colour** (both paths):

| `kind` | Accent | Icon |
| --- | --- | --- |
| `note` | Google Blue 600 | `info` |
| `warning` | Google Yellow 700 | `warning` |
| `tip` | Google Green 600 | `lightbulb` |
| `insight` | Google Blue 900 | `insights` |
| `do` | Google Green 700 | `check-circle` |
| `dont` | Google Red 600 | `cancel` |

**Slide mapping:** layout `callout` (single slide; oversized icon at
left, title + body at right).
**Print mapping:** `\begin{fdecallout}{kind}{title}…\end{fdecallout}`
— tinted left rule, icon in the margin.

### 4.8 `:::table` — semantic table

**Syntax**

```
::: table {caption="Deployment tiers" columns=[{name="Tier", align="left", type="text"}, {name="Latency (ms)", align="right", type="num"}, {name="Cost ($/mo)", align="right", type="money"}, {name="GA?", align="center", type="bool"}]}
Tier,Latency (ms),Cost ($/mo),GA?
Edge,45,120,true
Regional,110,60,true
Multi-region,180,240,false
:::
```

**Block attributes**

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `caption` | str | `""` | Rendered above the table. |
| `columns` | list[obj] | **required** | Ordered column specs. |

**Column object**

| Key | Type | Allowed | Notes |
| --- | --- | --- | --- |
| `name` | str | any | Header text. |
| `align` | enum | `left`, `right`, `center` | Cell + header alignment. |
| `type` | enum | `text`, `num`, `money`, `pct`, `bool`, `date` | Drives formatting: `num` right-aligns and thousands-groups, `money` prefixes currency, `pct` appends `%`, `bool` renders check/cross glyphs, `date` normalises to ISO. |

**Body:** a CSV block. First row is the header (must match `columns`
`name` order). Values are parsed per column `type`.

**Slide mapping:** layout `table`.
**Print mapping:** `tabularx` with a tinted (Google Blue 50) header
row, hair-rules between rows, alignment per column spec.

---

## 5. Slide-title cues in decks

| Markdown | Deck compiler behaviour | Print renderer behaviour |
| --- | --- | --- |
| `# Heading` | Registers a new **section**. Emits a divider slide (`divider-gradient`) with the heading as `label` and auto `number`, **unless** the very next block is an explicit `:::divider` (author-controlled). | `\section{Heading}` — with a full-width banner in `tech-guide`. |
| `## Heading` | **Starts a new slide.** Heading becomes the slide title. Any prose or directives until the next `##` (or `#`) belong to that slide. | `\subsection{Heading}`. |
| `### Heading` | Sub-heading **within** the current slide (rendered as a light-weight lozenge or sub-title, layout-dependent). | `\subsubsection{Heading}`. |

**Cover / hero rule:** every heading, paragraph, and directive that
appears **before the first `##`** (and after the front-matter) is
treated as **cover content** by the deck compiler. Typical use: a
short hook paragraph plus a `:::stat` or `:::cards` that renders on a
custom cover layout. The print renderer places this content on the
PDF title page (below the title/abstract).

---

## 6. Speaker notes

Speaker notes are captured with a blockquote whose first line is
`notes:` (case-insensitive, trailing colon required):

```
## Why now

Three forces converge: models, tools, and org readiness.

> notes: Anchor on the readiness gap — it is the real story.
> Mention the Acme pilot as the proof point.
```

- Notes attach to the **current slide** (the most recent `##`).
- On the cover slide, notes attach if they appear before the first
  `##`.
- Multiple `> notes:` blocks on the same slide are concatenated in
  order, separated by a blank line.

### 6.1 Auto-drafting rule (deck compiler MUST honour)

> **Normative.** If a slide has **no** explicit `> notes:` block, the
> deck compiler **must auto-draft** a speaker-notes paragraph from
> the slide body — 40–80 words, plain prose, second-person voice,
> written to be *spoken* not read. It should paraphrase the slide's
> directives (stat, cards, quote, table headers) rather than
> transcribe them. Auto-drafted notes are marked with a leading
> `[auto] ` tag in the Slides notes pane so authors can distinguish
> them and promote them to explicit blocks when reviewing.

The print renderer ignores speaker notes entirely.

---

## 7. Degrade rules for the Chrome PDF path

Both `build_deck.py` and `build_techdoc.py` see the same AST. The
table below is the print-side contract: what each directive turns
into in each print `collateral_type`. `pitch-deck` never reaches the
print path.

| Directive | `exec-briefing` | `tech-guide` | `workshop` | `one-pager` |
| --- | --- | --- | --- | --- |
| `:::stat` | `\fdestat` box, inline. | `\fdestat` box, floats to top of column. | `\fdestat`, boxed in agenda header. | Inline bold `value unit` + label; box suppressed. |
| `:::cards` | `tabularx` row, tinted cells. | Same, plus subtle drop-shadow rule. | Same as briefing. | **Collapses to a compact table** — 2-column `key: body` list, no icons. |
| `:::figure` | `\fdefigure`, `width` respected, floats. | `\fdefigure` with numbered caption `Figure N`. | Same as guide. | Fixed to 45 % width; caption inline right. |
| `:::quote` | `fdequote` env. | `fdequote` env, larger opening glyph. | Same. | Italic inline sentence, attribution in parentheses. |
| `:::agenda` | `tabularx` `X r`. | Same, plus per-item `\subsection*`. | Same as guide, front-matter of the workbook. | Not expected; if present, becomes an inline `1. …; 2. …` list. |
| `:::divider` | Full-width rainbow banner, no `\clearpage`. | **Full-width banner + `\clearpage`**, new section counter. | Same as guide. | **Subtle 4-colour `\rule` + inline label**, no page break. |
| `:::callout` | `fdecallout`, tinted rule. | Same. | Same. | Same, but body clipped to 3 lines max. |
| `:::table` | `tabularx`, tinted header. | Same, plus `\caption` under. | Same. | `\small` `tabular*`, no caption; overflow columns hidden with an ellipsis warning in the build log. |

Unknown directives (§10) render as a grey passthrough box titled
`[unhandled directive: name]` in every print class so the omission is
visible during proofing.

---

## 8. Parser contract

The parser is a **line-oriented state machine**. No lookahead beyond
the current line except to close a directive on `^:::\s*$`. It has
five states: `START`, `FRONTMATTER`, `BODY`, `DIRECTIVE`,
`NOTES_BLOCK`.

**Front-matter.** If line 1 matches `^---\s*$`, everything up to the
next `^---\s*$` is fed to `yaml.safe_load`. If the closing `---` is
missing, the parser errors with `E001: unterminated front-matter`.

**Directive open.**

```
^:::\s*(?P<name>[a-z][a-z0-9-]*)(?:\s+\{(?P<attrs>[^}]*)\})?\s*$
```

**Directive close.**

```
^:::\s*$
```

**Attribute mini-grammar.** Space-separated `key=value` pairs, where
`value` is either a double-quoted string, an unquoted number
(`-?\d+(\.\d+)?`), or an unquoted boolean (`true`/`false`). Complex
values (lists, nested objects) live in the directive **body** as
YAML, not in the attribute list.

```
attrs   := pair (WS pair)*
pair    := key "=" value
key     := [a-z][a-z0-9_-]*
value   := DQ_STRING | NUMBER | BOOL
```

**Body content per directive.**

| Directive | Body content type |
| --- | --- |
| `stat`, `divider`, `figure` | *empty* (all data in attributes). Parser warns on non-empty body. |
| `quote`, `callout` | CommonMark inline. |
| `cards`, `agenda`, `table` (`columns` list) | YAML list / object. |
| `table` | Line 1 = CSV header, lines 2..n = CSV rows. |

**Speaker notes.** Any blockquote whose first non-`>` line matches
`^\s*notes:\s*(.*)$` enters `NOTES_BLOCK`; all subsequent quoted
lines are concatenated as note content, until a blank line or a
non-blockquote line ends the block.

**Headings.** Standard ATX (`#`, `##`, `###`). Setext underlines are
not supported (parser warns).

**Nesting.** Directive blocks are **flat**. A `:::` open inside a
directive body triggers `E010: nested directives not supported`.

**Errors are numbered and terminal** — the build fails on any `E***`.
Warnings (`W***`) log but do not fail.

---

## 9. Worked example

Save as `example.md`. Runs on both compilers:

```markdown
---
title: "Agentic SDLC — a working reference for Acme"
subtitle: "From pilot to platform in one quarter"
collateral_type: tech-guide
customer: "Acme Corp"
confidentiality: proprietary
author: "Sanchit Alekh"
date: 2026-08-27
theme: light
abstract: >
  A reference architecture and rollout plan for adopting agentic
  software development inside Acme's platform engineering group.
tags: [agentic, sdlc, adk, gemini-3]
output_basename: acme-agentic-sdlc-ref
---

::: stat {value="6.4" unit="×" label="dev velocity uplift in the Acme pilot" caption="Acme × Google Cloud, Q2 2026"}
:::

::: cards {columns=3 tint="mixed"}
- icon: "shield-check"
  title: "Contained"
  body: "Sandboxed agents, non-human identity, kill switches."
- icon: "cpu"
  title: "Capable"
  body: "Gemini 3 Pro planning, NB2 Lite for pre-renders."
- icon: "gauge"
  title: "Observable"
  body: "Every tool call traced and cost-attributed."
:::

# The agentic shift

## Why the pilot worked

Three forces landed at the same time: capable planning models, a
mature tool protocol (MCP/A2A), and Acme's readiness to rewire
change-management around shorter release cycles.

::: figure {src="assets/topology-root-worker.png" caption="Root-worker topology as deployed for Acme" alt="A root agent orchestrating four specialised worker agents across build, test, review, and deploy" credit="Google Cloud" width="0.7" aspect="16:9"}
:::

> notes: Open on the velocity number, not the topology. The topology
> is proof, not story. If asked about safety, jump to the callout on
> the next slide before returning here.

## What the team said

::: quote {attribution="Priya Rao" role="Principal Engineer, Acme Platform"}
We stopped shipping features and started shipping *decisions*. The
agents handle the mechanical parts.
:::

# Reference topology

::: divider {label="Reference topology" number="02"}
:::

## Tiering the deployment

::: table {caption="Deployment tiers considered for Acme" columns=[{name="Tier", align="left", type="text"}, {name="Latency (ms)", align="right", type="num"}, {name="Cost ($/mo)", align="right", type="money"}, {name="GA?", align="center", type="bool"}]}
Tier,Latency (ms),Cost ($/mo),GA?
Edge,45,120,true
Regional,110,60,true
Multi-region,180,240,false
:::

::: callout {kind="warning" title="Cost trap"}
Cache invalidation on tool-heavy prompts wipes 70 % of the savings.
Pin your tool definitions and version them in source control.
:::

# Rollout

## Next 90 days

::: agenda
- title: "Harden the containment tier"
  duration: "Weeks 1–3"
  owner: "Platform Security"
- title: "Port two internal apps to the root-worker pattern"
  duration: "Weeks 4–8"
  owner: "Platform Eng"
- title: "Open the harness to two product teams"
  duration: "Weeks 9–12"
  owner: "DevEx"
:::
```

**How this file renders on each path**

| Element | Deck (`build_deck.py`) | PDF (`build_techdoc.py`, `tech-guide` class) |
| --- | --- | --- |
| Front-matter | Cover slide: dark, "Acme Corp" locked-in the footer as `Google & Acme Corp — Proprietary & Confidential`. | Title page with abstract and same footer on every subsequent page. |
| Pre-`##` stat + cards | Cover + a hero "opening" slide with the 6.4× stat and 3 cards. | Both rendered on the title page below the abstract. |
| `# The agentic shift` | Auto section-divider slide (rainbow gradient, label = heading, number = `01`). | `\section{The agentic shift}` with full-width rainbow banner + `\clearpage`. |
| `## Why the pilot worked` | New slide, prose + figure. Notes block attaches. | `\subsection{…}`; figure floats to top. |
| `## What the team said` | New slide, `quote-hero` layout. Auto-drafted `[auto]` notes since none were provided. | `\subsection{…}`; `fdequote` environment. |
| `# Reference topology` + explicit `:::divider` | Explicit divider **wins**; no duplicate auto-divider is emitted. | Explicit banner replaces the auto one. |
| `:::table` | `table` layout slide. | `tabularx` with Blue-50 header, numbered caption. |
| `:::callout {kind="warning"}` | `callout` slide, yellow accent, large warning icon. | `fdecallout` with yellow rule. |
| `:::agenda` | `agenda` slide with duration column. | Itemised list with right-aligned duration column and per-item `\subsection*`. |

---

## 10. Extension policy

The grammar is intentionally small. Additions follow these rules so
old sources keep compiling.

1. **Reserve unknown directives as opaque passthroughs.** If a
   compiler sees `:::foo` and does not recognise `foo`, it MUST NOT
   error. It stores the raw block in the AST as
   `{type: "unknown", name: "foo", attrs, body}`. The deck compiler
   renders it on a plain `content` layout with the raw body in a
   monospace text frame and a red header `[unhandled: foo]`. The
   print renderer emits the grey passthrough box from §7.
2. **No positional arguments, ever.** Every parameter is a named
   attribute. New parameters are new attribute keys with a default
   value that reproduces old behaviour.
3. **Names are lowercase-with-dashes.** New directive names use the
   same pattern and never collide with a CommonMark construct.
4. **Reserved namespace.** Directive names starting with `x-` are
   reserved for author-local experimentation and will always be
   treated as opaque passthroughs. Use them for one-off content that
   should not block the build.
5. **No breaking changes to existing directive attributes.** To
   change semantics, add a new attribute with an opt-in default and
   plan a deprecation window of at least one minor release.
6. **Front-matter unknown keys are preserved**, passed to both
   compilers as opaque metadata, and surfaced in the PDF's XMP
   metadata block.
7. **Version pin.** A future `authoring_version: 2` field in
   front-matter is reserved to switch grammars if a breaking change
   ever becomes unavoidable. Absent means version 1 (this document).

---

### Appendix A — layout name registry (shared with the Slides track)

| Directive / cue | Slides layout name |
| --- | --- |
| Cover (pre-first-`##` content) | `cover-dark` / `cover-light` (per `theme`) |
| `# Heading` (auto divider) | `divider-gradient` |
| `## Heading` (default body) | `content` |
| `:::stat` | `stat-hero` |
| `:::cards` | `cards-row` |
| `:::figure` (`width > 0.5`) | `figure-full` |
| `:::figure` (`width ≤ 0.5`) | `figure-half` |
| `:::quote` | `quote-hero` |
| `:::agenda` | `agenda` |
| `:::divider` | `divider-gradient` |
| `:::callout` | `callout` |
| `:::table` | `table` |
| unknown `:::foo` | `content` with `[unhandled: foo]` header |

### Appendix B — error and warning codes

| Code | Meaning |
| --- | --- |
| `E001` | Unterminated front-matter. |
| `E002` | Front-matter is not a mapping. |
| `E003` | `collateral_type` missing or not in the enum. |
| `E004` | `confidentiality` not in the enum. |
| `E010` | Nested directive detected. |
| `E011` | Unterminated directive block. |
| `E012` | Malformed attribute list. |
| `E020` | `:::table` header row does not match `columns`. |
| `W101` | `:::figure` has neither `caption` nor `alt`. |
| `W102` | Setext heading used; convert to ATX. |
| `W103` | Directive body present on a directive that expects none. |
| `W110` | Print path invoked for `collateral_type: pitch-deck` (deck-only). |

---

### Open design questions (non-blocking)

- **`theme: auto`** — should per-directive `theme=` override cascade
  onto the *next* directive as well, or reset every block? Current
  spec: resets every block (safer). Revisit after first workshop use.
- **`:::cards` on the one-pager path** — the compact-table degrade is
  readable but loses the icons; consider a `keep-icons` opt-in.
- **Auto-drafted speaker notes** — should the `[auto]` tag be
  configurable (e.g. suppressed on `pitch-deck` where the author
  always edits notes)? Currently always on.
- **`:::table` column typing** — no `enum` or `link` column types
  yet. Add on demand.
- **Localisation of footer strings** — footers are English-only; a
  `lang:` front-matter field would unlock EN/DE swaps for DACH work.
