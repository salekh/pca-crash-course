---
name: ai-tech-gtm-collateral
description: Produce on-brand, publication-grade GTM collateral for the Google Cloud FDE / AI Tech Group — pitch decks, exec briefings, workshop decks, tech guides / whitepapers, and one-page solution briefs. Long-form PDF output is rendered with headless Chrome from HTML + CSS Paged Media (LaTeX was evaluated head-to-head and rejected). Slide output goes through the Google Slides API. Uses the FDE brand identity (near-black + Grey-50 canvases, rainbow gradient divider, aurora bleeds, oversized cropped mark motif, Google Sans typography, static-instanced TTFs to defeat Chrome's variable-font Type 3 rasterisation). Diagrams and infographics flow exclusively through the think-with-google-infographics skill — Nano Banana Pro @ 4K for finished visuals, Nano Banana 2 for simple ones, Nano Banana 2 Lite for pre-renders. Author defaults to "Sanchit Alekh"; the footer auto-swaps to a customer-safe form when a customer name is supplied. Outputs are only .gslides and PDF (never pptx).
---

# AI Tech Group — GTM Collateral

Produce on-brand, publication-grade GTM collateral for the Google Cloud
**FDE / AI Tech Group** from Markdown source.

Two independent tracks share the same brand identity, palette and
copy conventions:

* **Long-form PDF track** — Markdown → HTML → headless Chrome → A4 PDF.
  Used for whitepapers, technical guides, exec briefings, one-pagers.
* **Slides track** — Markdown → gslides MCP batch ops → Google Slides
  (`.gslides`) + PDF export. Used for pitch decks, workshop decks,
  exec briefing decks.

Only **`.gslides` and PDF** are produced. Never `.pptx`, never `.odp`,
no `python-pptx` dependency.

The brand spec is `references/brand.md`. The authoring grammar shared
by both tracks is `references/authoring.md`. A real end-to-end worked
example lives at `references/examples/fms_techdoc.md` (a 32-page
foundation-model-security whitepaper) with the pre-rendered PDF and
its eight diagrams next to it. The 13-layout template inventory used
by the Slides track lives at `references/layout_catalogue.md`, and
three real batch-op files (`dup.json`, `fill.json`, `fix.json`) live
in `references/slides-batch-specs/`.

---

## 0. Non-negotiable rules — read first

1. **PDF output is HTML + CSS Paged Media rendered by headless Chrome.
   LaTeX is not used.** See §2A below for why. Never re-introduce a
   LaTeX / LuaLaTeX / fontspec / pandoc-as-renderer path — that
   pipeline was evaluated against Chrome on identical one-page content
   and lost (overflowed onto page 2, clipped the CTA block, broke the
   callout, hyphenated badly). Chrome matched the brand on the first
   attempt.
2. **`fvar` MUST be absent from every referenced font, and every
   Google face in the output PDF MUST read `CID TrueType` (never
   `Type 3`).** See §2B. This is enforced as a pre-flight gate on
   every render — a PDF with even one `Type 3` glyph program is a
   failed build, not a warning.
3. **All diagrams, infographics and illustrations MUST be produced via
   the `think-with-google-infographics` skill.** Never hand-roll a
   diagram. Never emit an ASCII / line diagram. `scripts/gen_visuals.py`
   is a thin wrapper that delegates to that skill's
   `generate_architecture.py`, `generate_twg.py` and `render_graph.py`
   — call it, don't reimplement it.
4. **Generative-media tier defaults**:
   * **Nano Banana Pro @ 4K** — finished / complex visuals shipped in
     a deliverable.
   * **Nano Banana 2** — simple visuals.
   * **Nano Banana 2 Lite** — pre-renders and experimentation only
     (1K max).
   * Model IDs (no `-preview` suffix): pro = `gemini-3-pro-image`,
     nb2 = `gemini-3.1-flash-image`, lite = `gemini-3.1-flash-lite-image`.
   * Do NOT reference legacy models (Imagen, Veo, Lyria) or the
     Gemini 1.5 series.
5. **The words "Think with Google" MUST NEVER appear in any generated
   output** — no watermarks, footers, headers, captions,
   illustrations, nothing. Referenced internally to steer the model;
   never visible.
6. **Deck fidelity is inherited from the template, not recreated.**
   Do not paint flat backgrounds and reimplement compositions
   programmatically. Copy the brand template deck, `duplicate-slide`
   the real layout pages, overwrite placeholder text, `reorder-slide`
   into narrative order. See §2D.
7. **Author defaults to `Sanchit Alekh`**. Override via the
   front-matter `author:` field.
8. **Footer auto-swap** — when `customer:` is set in front-matter, the
   default `Google Cloud  |  Proprietary & Confidential` footer is
   replaced with `Prepared for <customer> · Confidential`.
   `confidentiality: public` with no customer collapses it to
   `Google Cloud`. Full matrix in `references/brand.md`.
9. **Speaker notes on every deck slide.** If the author omits
   `> notes:` the deck compiler MUST auto-draft speaker notes from
   the slide body.
10. **Save the final artifact to a dated Google Drive folder using
    the `beautiful-drive` numeric-prefix convention** — additive,
    next free numeric prefix (`01-`, `02-`, `03-`, …), never move
    or disturb existing files.

---

## 1. Inputs to ask the user for, up front

Before generating anything, resolve these:

| Input | Required | Notes |
| :--- | :--- | :--- |
| `collateral_type` | yes | One of `pitch-deck`, `exec-briefing`, `workshop-deck`, `tech-guide`, `one-pager`. See §5. |
| Working title | yes | The manuscript's `title`. |
| Subtitle / one-liner | yes for cover-bearing formats | Shown under the title on the cover / hero slide. |
| Audience | yes | Drives tone and copy budget (see §2D). |
| Customer name | if customer-facing | Triggers footer auto-swap; also decides confidentiality wording. |
| Confidentiality | yes | `internal` (default), `customer`, `public`. |
| Key numbers / stats | for pitch/exec | The stat strip and any headline metric. |
| Diagrams needed | yes | List of diagram intents — each becomes a `gen_visuals.py` job. |
| Source facts to cite | yes | Every version number, framework name, CCL/ASL/tier name MUST be traceable to a source — see §2F. |
| Drive destination | yes | Parent folder; the skill creates the next-numeric subfolder. |

Ask these once, up front. Do not begin generation with partial inputs.

---

## 2. The nine production lessons (read before touching a build)

Every item below was learned the hard way in production. Symptoms and
fixes are stated plainly.

### 2A. Rendering engine — headless Chrome, not LaTeX

* PDF output is HTML/CSS + headless Chrome at
  `/opt/google/chrome/chrome`.
* **Chrome flags** (all required together):

  ```
  --headless --disable-gpu --no-sandbox
  --print-to-pdf=<absolute path>
  --no-pdf-header-footer
  --run-all-compositor-stages-before-draw
  --virtual-time-budget=30000
  --user-data-dir=<fresh temp dir per invocation>
  ```

  The virtual-time budget is what gives web fonts and background
  images enough clock to load; the fresh user-data-dir avoids
  cross-invocation profile races.
* **Why Chrome, not LaTeX.** On identical one-page content, the
  LuaLaTeX pipeline overflowed onto 2 pages, clipped the CTA block,
  broke the callout box, and hyphenated badly. Chrome matched the
  brand on the first attempt because the brand language (gradients,
  full-bleed plates, card shadows, grid) is natively CSS. LaTeX kept
  fighting the design; Chrome cooperated with it.
* **Proven at scale.** A 32-page A4 whitepaper with cover, table of
  contents, running headers, folios, 8 full-width figures, 15 tables,
  callouts and a stat strip renders reliably in this pipeline. The
  worked example is `references/examples/fms_techdoc.md` and its
  companion PDF.

### 2B. Fonts — the silent Type 3 killer

* Chrome **rasterises variable fonts into Type 3 glyph programs**.
  Type 3 fonts are non-scalable bitmap-ish programs — they degrade in
  print, break text selection, and get flagged by pre-press. **They
  look perfectly fine on screen**, so a broken PDF ships unnoticed
  unless you explicitly gate on it.
* **Fix:** pre-instance static TTFs with `fontTools` and reference
  ONLY those in `@font-face`. After instancing, **delete the tables
  `fvar, gvar, HVAR, VVAR, MVAR, STAT, avar, cvar`** — leaving even
  `STAT` behind can still trigger Type 3 in some Chrome builds.
* The bundled `assets/fonts/` set has already been instanced and
  scrubbed. Do not swap in a variable-font file. If you must add a
  new face:

  ```python
  from fontTools import ttLib
  DROP = {"fvar","gvar","HVAR","VVAR","MVAR","STAT","avar","cvar"}
  f = ttLib.TTFont("Face-Regular.ttf")
  for t in [t for t in f.keys() if t in DROP]:
      del f[t]
  f.save("Face-Regular.ttf")
  ```
* **Mandatory gate on every PDF:**

  ```
  pdffonts out.pdf | grep -c "Type 3"      # MUST return 0
  pdffonts out.pdf | grep "Google Sans"    # every row MUST read CID TrueType
  ```

  A PDF that fails this gate is a **failed build**, not a warning.

### 2C. Slides API gotchas — each cost real debugging time

* **`lineSpacing` is a percentage where `100` = single.** Passing
  `1.35` collapses every line on top of the next. Always use
  `100`–`150`.
* **`list_elements` `slide_index` is 0-based.** An earlier
  off-by-one assumption was wrong — verify before trusting.
* **Shapes report a bogus intrinsic size of `3000000 × 3000000`; the
  real geometry lives in a separate transform.** Never hand-reconstruct
  layout geometry from the API. Always mutate placeholders in place.
* **`update-text` fails on an empty placeholder shape** with:
  `The startIndex 0 must be less than the endIndex 0`. Template
  decks are full of empty placeholders. Two fixes: (1) detect
  empties first and skip / insert-text instead of update-text; or
  (2) split the ops into small per-slide chunks so one failure
  isolates instead of aborting the whole batch.
* **Some template elements are WordArt, not `SHAPE`.** `update-text`
  returns `is not of type SHAPE` and they CANNOT be edited via the
  API at all (e.g. the big `00%` stat numerals on the stat-hero
  layout). Options: edit them by hand in the Slides UI, or design
  around them (choose a different layout).
* **Theme layouts ARE inherited when a presentation is copied.**
  `add-slide` against an inherited layout yields the canvas, logo
  mark and footer for free — you do not have to repaint them.

### 2D. Deck design — the single biggest quality lesson

* **Do NOT synthesise layouts programmatically.** Painting flat
  backgrounds and re-implementing the compositions from scratch
  produces visibly mediocre output — it discards the aurora bleeds,
  the oversized cropped mark motif, and the decorated card / stat /
  chart / device compositions the template is built around.
* **Export-size tell:** the template-fidelity deck for the FMS
  briefing weighed ~3.1 MB. The synthesised-from-scratch variant of
  the same content weighed ~191 KB. The 16× gap is the fidelity you
  are throwing away.
* **Correct method:**
  1. Copy the brand template deck into your working folder.
  2. Enumerate the real layout pages you need for this narrative
     (see `references/layout_catalogue.md` for the 13-layout
     inventory and which source page carries which design).
  3. `duplicate-slide` each one — see
     `references/slides-batch-specs/dup.json` for the exact op shape.
  4. Overwrite ONLY the placeholder text via `update-text` (see
     `fill.json`; fixes go through `fix.json`).
  5. `reorder-slide` into narrative order.
* **The template is designed for SHORT COPY.** Placeholder slots are
  sized for one or two lines. Paragraph-length strings overflow their
  frames. Respect the **copy budget** — this matters more than any
  layout code. If the copy does not fit, cut it, don't resize the
  frame.

### 2E. Images in Google Slides — a hard organisational constraint

* The Slides API fetches images **server-side, with no credentials**,
  so it can only embed publicly-reachable URLs.
* **This Google Workspace domain blocks public link-sharing**
  (`publishOutNotPermitted`). Do not waste time retrying a signed
  or shared link, and do not attempt Drive workarounds — the
  policy is enforced at the domain level.
* **Consequence: figures cannot be auto-embedded into a `.gslides`
  via the API in this org.**
* **Workarounds, in order of preference:**
  1. Route figure-bearing collateral through the **Chrome PDF path**,
     where local image files work perfectly.
  2. Insert manually in the Slides UI via **Replace image** on an
     existing template image — this inherits the template's crop
     and position and takes seconds per slide.
  3. (Last resort) Publish the figure via an approved external CDN
     the org allows, then embed by URL. This has never worked for
     internal deliverables so far — assume it won't.

### 2F. Generated-diagram QA — fail mode is invention, not typos

**The failure mode is invention, and agent self-reported QA is not
sufficient.** A recent generation pass self-reported *"all six accepted
on first pass, every label read correctly"* — and shipped a figure that
had **fabricated a "CCL-1 to CCL-4" tier ladder that does not exist in
Google DeepMind's Frontier Safety Framework**, invented purely to make
its column look symmetrical with the two neighbouring framework columns.
Every label was spelled correctly, so a spelling-only check passed it.
Every figure MUST be **viewed and factually checked by the caller** —
not just by the generating agent.

**What the QA gate checks (in order):**

1. **Factual correctness of every taxonomy, tier name, version number,
   framework name, product name and date**, verified against the
   original source. This is the check that would have caught the
   fabricated CCL ladder.
2. Label spelling.
3. Tier / step ordering.
4. No duplicated labels or badges on one card.
5. No semantically misleading connectors (e.g. arrows between
   parallel columns that imply a progression that does not exist).
6. The literal string `"Think with Google"` appears nowhere.

**Remediation rule — regenerate, don't drop or patch.** A figure that
fails QA is:

* **NOT** dropped from the deliverable,
* **NOT** shipped with a caveat,
* **NOT** patched by hand in an image editor,
* → but **REGENERATED with a corrected, more explicit prompt, then
  re-QA'd**. Repeat until it passes. Every subsequent redraw
  compounds the earlier fixes into the same spec — do not drop
  earlier corrections when adding new ones.

**Prompt-repair tactics, keyed to the failure mode:**

| Failure mode | Symptom | Prompt repair |
| :--- | :--- | :--- |
| **Fabricated taxonomy** *(most dangerous)* | Model invents tiers / levels / versions to make a layout look symmetrical (e.g. "CCL-1…CCL-4" that does not exist in the FSF). | Name the real taxonomy explicitly. Enumerate the **exact** labels to render. Add a negative instruction: *"This column must NOT use numbered tiers"* and *"Do not invent labels; render only the labels listed here."* State plainly: *"Asymmetry between columns is correct — the real frameworks are not symmetric. Do not force symmetry."* |
| **Duplicated label or badge** | The same phrase appears twice on one card — e.g. a badge and a subtitle both reading "Currently deployed". | Add: *"Every text label must appear exactly once. Do not duplicate any label or badge."* Specify the badge as *"a single small badge reading 'X'; do not repeat that phrase anywhere else on the card."* |
| **Misspelling** | Any label deviates from the intended string. | Quote the exact string in the spec: *"labelled exactly: '<verbatim string>'"*. Do this for every label that must be typographically precise (product names, framework names, version numbers). |
| **Wrong order or missing tier** | Cards / tiers appear in the wrong order, or one is omitted. | Enumerate order explicitly, bottom-to-top or left-to-right: *"from bottom to top the cards are labelled exactly: 'A', 'B', 'C', 'D'"*. Do not rely on the model to infer order from prose. |
| **Semantically misleading connectors** | Arrows drawn between parallel columns implying a progression that does not exist. | State: *"These three columns are parallel and independent. Do not draw arrows or connectors between them."* Specify where connectors ARE allowed, if any. |
| **"Think with Google" leaks into the image** | The style-reference string appears in a caption, watermark or footer. | Remove the phrase from any user-visible field of the spec. Add: *"The literal string 'Think with Google' must not appear anywhere in the rendered image — no watermark, footer, caption, or label."* |

Compose these tactics as needed — a figure that failed on both a
fabricated tier ladder and a duplicated badge gets both repairs in the
same regenerated spec.

### 2G. Generative media config (verified working)

* **Project:** `sa-nexus-gcp-4-sandbox-183936` (aka `nexus`),
  location `global`.
* `sa-learning-1` (aka `argolis`) returns **403 on
  `aiplatform.endpoints.predict`** — do not target it for
  Nano Banana calls.
* **Required env for Nano Banana Pro** — without these, NB Pro
  fails with `Cert provider command returns non-zero status
  code -11`:

  ```
  export GOOGLE_API_USE_CLIENT_CERTIFICATE=false
  export GOOGLE_API_USE_MTLS_ENDPOINT=never
  ```
* **Model IDs (exact, no `-preview` suffix):**

  | Tier | Model ID | Use |
  | :--- | :--- | :--- |
  | NB Pro | `gemini-3-pro-image` | Finished / complex, 4K. |
  | NB 2 | `gemini-3.1-flash-image` | Simple diagrams. |
  | NB 2 Lite | `gemini-3.1-flash-lite-image` | Pre-render / experimentation, 1K. |

* `generate_architecture.py` takes `--spec` (or `--spec-file`),
  **not `--prompt`**. Passing `--prompt` silently produces the
  wrong output.

### 2H. Output formats

* Only `.gslides` and PDF. Never `.pptx`, never `.odp`, no
  `python-pptx` dependency.

### 2I. Defaults & filing

* Author `Sanchit Alekh` unless overridden.
* Footer `Google Cloud  |  Proprietary & Confidential`, auto-swapped
  to `Prepared for <customer> · Confidential` when `customer:` is
  set. `confidentiality: public` with no customer collapses to
  `Google Cloud`.
* Speaker notes auto-drafted on every deck slide.
* Deliverables filed to Google Drive under the `beautiful-drive`
  numeric-prefix convention (additive, next free `NN-` prefix,
  never disturb existing contents).

---

### 2J. Bundled worked examples are the quality bar

**Output that does not look at least this good is not finished.** The
files under `references/examples/` are the reference deliverables — not
demos. Consult them before authoring, and re-consult them when review
raises a "does this look right?" question.

| Bundled artefact | What it demonstrates | When to consult |
| :--- | :--- | :--- |
| `references/examples/fms_techdoc.md` | Full ~10k-word worked manuscript exercising every `[[FIGURE]]`, `[[CALLOUT]]`, `[[STATS]]` marker in anger; the copy budget, front-matter, section rhythm and citation pattern the Chrome PDF path is tuned for. | Before authoring any `tech-guide` or `exec-briefing`. Copy its structure — don't invent your own marker grammar. |
| `references/examples/fms_techdoc_rendered.pdf` | The **32-page A4 rendered output** that manuscript produces: cover, TOC, running headers, folios, 8 full-width figures, 15 tables, callouts, stat strip. Passes the Type 3 gate; every Google face is `CID TrueType`. ~1.75 MB. | The visual bar. New whitepapers that don't look like this at a glance (cover treatment, running header rhythm, figure density, callout styling) are not shipping. |
| `references/examples/diagrams/*.png` (8 files) | NB Pro @ 4K figures — each ≥ 1.7 MB, 2048 px on the long edge, "Think with Google" aesthetic. Includes `fig_frontier_frameworks.png`, the regenerated FSF figure after the fabricated-CCL-ladder failure (§2F). | The visual bar for any new diagram. If a generated figure looks smaller, flatter, softer or less densely-labelled than these, redraw (§2F). |
| `references/layout_catalogue.md` | The 13-layout template inventory: which source-deck page carries which composition (hero, stat-hero, three-card, agenda, quote, closing, etc.) and which `collateral_type` uses which layouts. | Before emitting any `duplicate-slide` op in a Slides build (§2D). |
| `references/slides-batch-specs/{dup,fill,fix}.json` | Real batch-op files from the FMS briefing deck: `dup.json` for `duplicate-slide` + `reorder-slide`, `fill.json` for per-slide `update-text` (chunked), `fix.json` for the second-pass repair of empties and WordArt swaps. | As templates for your own batch payloads — start from these, don't hand-roll the op shape. |
| `assets/html/techdoc.css` | The approved Chrome / CSS Paged Media stylesheet that produced the 32-page rendered PDF above. Handles cover, `@page` folios, running headers, break control, repeating table headers, callouts, stat strip. | Reuse verbatim. Do not fork per-deliverable — extend via a per-manuscript override sheet if truly necessary. |
| `scripts/build_techdoc.py` | Working Markdown → HTML → headless-Chrome PDF converter. Stdlib-only. Produced the verified 32-page whitepaper. | Every `tech-guide` and `one-pager` build. |
| `scripts/build_deck.py` | Markdown → gslides MCP batch-ops compiler. | Every Slides build. |

Additional quantitative bars:

* Chrome PDF path — `pdffonts` reports `Type 3` count `0`; every
  Google face reads `CID TrueType`.
* Every one of the eight figures survived the QA loop in §2F
  (including the regenerated Frontier Safety Framework figure that
  originally fabricated a "CCL-1…CCL-4" ladder).
* Slides path — the template-fidelity FMS briefing deck exports at
  ~3.1 MB. A synthesised-from-scratch equivalent exported at ~191 KB.
  The 16× gap is the fidelity you must not lose. If your export is
  under ~1 MB you are almost certainly repainting rather than
  duplicating template layouts (§2D).

If a new whitepaper does not visually look like the bundled rendered
PDF at a glance (cover treatment, running-header rhythm, figure
density, callout styling), the render is wrong — do not ship it.

---

## 3. Bundled assets & scripts

```
ai-tech-gtm-collateral/
├── SKILL.md
├── assets/
│   ├── html/
│   │   └── techdoc.css                Approved Chrome/CSS Paged Media stylesheet
│   ├── fonts/                         Static-instanced TTFs (fvar absent, STAT stripped)
│   │   ├── GoogleSans-Regular.ttf
│   │   ├── GoogleSans-Medium.ttf
│   │   ├── GoogleSans-Bold.ttf
│   │   ├── GoogleSansText-Regular.ttf
│   │   ├── GoogleSansText-Medium.ttf
│   │   ├── GoogleSansText-Bold.ttf
│   │   ├── GoogleSansText-Italic.ttf
│   │   ├── GoogleSansCode-Regular.ttf
│   │   └── fontconfig/fonts.conf      For headless diagram rendering (Graphviz etc.)
│   └── brand/                         Logos, gradient plate, aurora backgrounds, lockups
│       ├── logo_mark_color.png
│       ├── logo_mark_white.png
│       ├── logo_mark_mono_dark.png
│       ├── logo_motif_crop.png        Oversized cropped mark motif
│       ├── bg_gradient_divider.png    Rainbow diagonal
│       ├── bg_light_aurora.png
│       ├── bg_dark_aurora.png
│       ├── gcloud_lockup_color.{png,svg}
│       ├── gcloud_lockup_white.{png,svg}
│       └── palette.json               Sampled brand palette (source of truth)
├── scripts/
│   ├── build_techdoc.py               Markdown → HTML → headless-Chrome PDF (Chrome path)
│   ├── build_deck.py                  Markdown → gslides MCP batch ops (Slides path)
│   └── gen_visuals.py                 Thin wrapper over think-with-google-infographics
└── references/
    ├── brand.md                       Palette, type scale, footer matrix (normative)
    ├── authoring.md                   Shared Markdown grammar
    ├── layout_catalogue.md            The 13-layout template inventory
    ├── slides-batch-specs/
    │   ├── dup.json                   Real duplicate-slide + reorder ops
    │   ├── fill.json                  Real per-slide update-text ops
    │   └── fix.json                   Real post-hoc fix ops (empties, WordArt swaps)
    └── examples/
        ├── fms_techdoc.md             Full-length worked whitepaper
        ├── fms_techdoc_rendered.pdf   Its rendered output (Type 3 count = 0)
        └── diagrams/                  Eight NB-Pro figures embedded in it
```

---

## 4. Pipelines

### 4.1 Long-form PDF (Chrome path)

```
python3 scripts/build_techdoc.py \
    --md      <manuscript.md> \
    --css     assets/html/techdoc.css \
    --figures <diagrams_dir> \
    --out-html <out.html> \
    --out-pdf  <out.pdf>
```

The converter is stdlib-only. It parses the front-matter, a
Markdown subset (headings, lists, tables, blockquotes, code fences,
horizontal rules), plus three custom markers:

* `[[FIGURE: filename.png | Caption text]]`
* `[[CALLOUT:note|Title|Body]]` — also `warn`, `tip`
* `[[STATS: v1 :: l1 || v2 :: l2 || v3 :: l3]]`

Missing figures do not crash — a visible placeholder box is emitted
in their place with filename + caption preserved. Chrome is invoked
with the flag set in §2A. The stylesheet handles cover, TOC,
running headers, folios, break control, repeating table headers,
and figure layout.

### 4.2 Google Slides (Slides path)

```
python3 scripts/build_deck.py <manuscript.md>    # writes batch.json
```

`batch.json` is then fed to the `gslides` MCP `batch` tool. For
template-fidelity decks (the recommended path — see §2D), the
authoring flow is:

1. Copy the brand template deck to the working folder.
2. Use `duplicate-slide` (see `references/slides-batch-specs/dup.json`
   for the op shape) to clone the real layout pages you need.
3. Overwrite placeholder text via `update-text`
   (`fill.json`). Split into small per-slide chunks so one bad
   placeholder doesn't kill the whole batch (§2C).
4. `reorder-slide` into narrative order.
5. Insert figures manually via **Replace image** in the UI (§2E).
6. Export PDF; ship alongside `.gslides`.

### 4.3 Diagrams

```
python3 scripts/gen_visuals.py <intent-name> \
    --spec <spec-file>            # NOT --prompt
    --tier {pro,nb2,lite}         # default nb2; use pro for finished
    --out  <path>
```

Delegates to `think-with-google-infographics`. See §2F for the QA gate
and §2G for env vars and model IDs. Always render at NB2 Lite first
for layout / composition validation, then re-render finalists at
NB Pro @ 4K.

---

## 5. Collateral types

| `collateral_type` | Track | Purpose | Typical length | Cover treatment |
| :--- | :--- | :--- | :--- | :--- |
| `pitch-deck` | Slides | External customer pitch. | 10–18 slides | Hero title + subtitle over light aurora, oversized cropped mark. |
| `exec-briefing` | Slides + PDF | 20-minute exec conversation, leave-behind PDF. | 6–12 slides, 4–6 PDF pages | Dark cover, one headline stat. |
| `workshop-deck` | Slides | Day-long workshop with exercises + notes. | 30–60 slides | Light cover, module counter. |
| `tech-guide` | PDF | Long-form technical guide / whitepaper. | 15–40 A4 pages | Cover + TOC + section chapters, running headers, folios. |
| `one-pager` | PDF | Solution brief. | 1 A4 page | Full-bleed brand plate, single stat strip, single CTA. |

Copy-budget guidance per type is in `references/authoring.md`.

---

## 6. End-to-end workflow per type

### Pitch-deck / exec-briefing / workshop-deck (Slides path)

1. Collect the §1 inputs.
2. Draft the manuscript in Markdown using the `authoring.md` grammar.
   Respect the per-slot copy budget (§2D).
3. Copy the brand template deck to Drive under the next `NN-` folder.
4. Emit `dup.json` — one `duplicate-slide` per layout you need,
   plus `reorder-slide` ops (see `references/slides-batch-specs/dup.json`).
   Run via `gslides.batch`.
5. Emit `fill.json` — per-slide `update-text` ops. Split into
   small chunks (per-slide or per-block). Run via `gslides.batch`.
6. Run the fix pass (`fix.json`): re-issue any `update-text` that
   hit an empty placeholder (add insert-text instead), design
   around WordArt shapes that refused to update (§2C).
7. Insert diagrams manually via **Replace image** on template
   images (§2E).
8. Auto-draft speaker notes for every slide that lacks them.
9. Export PDF; verify the Type 3 gate on the exported PDF (§2B).
10. File both `.gslides` and PDF in the dated Drive folder; return links.

### Tech-guide / one-pager (Chrome PDF path)

1. Collect the §1 inputs. Every version number, framework name,
   tier name and product name goes in a "sources" annex the QA pass
   will check against (§2F).
2. Draft the manuscript in Markdown using the `authoring.md` grammar,
   including `[[FIGURE]]`, `[[CALLOUT]]`, `[[STATS]]` markers.
3. Generate figures with `gen_visuals.py` — NB Pro @ 4K for finished,
   NB2 for simple. Fact-check every label against sources (§2F).
4. `python3 scripts/build_techdoc.py --md … --css … --figures … --out-pdf …`.
5. **Run the Type 3 gate** (§2B). If it fails, do not ship.
6. Rasterise the first, a middle, and the last page (`pdftoppm` at
   200 dpi) and eyeball them for overflow / clipping / broken tables.
7. File the PDF (and its source `.md`, `.html` and figures) in the
   dated Drive folder under the next `NN-` prefix. Return links.

---

## 7. Pre-flight quality checklist

Every deliverable must pass all of these before shipping.

**Rendering / typography**

* [ ] `pdffonts <out.pdf> | grep -c "Type 3"` returns `0`.
* [ ] Every Google face in `pdffonts` output reads `CID TrueType`.
* [ ] No `fvar` table on any referenced font
      (`python3 -c "from fontTools import ttLib; print('fvar' in ttLib.TTFont('<f>.ttf'))"`
      → `False`).
* [ ] Page count > 1 for anything except a one-pager; page count == 1 for a one-pager.
* [ ] Rasterise 3 sample pages at 200 dpi and look at them.

**Content**

* [ ] Every framework name, tier name, version number, product name and
      date in figures verified against the original source. **No
      fabricated taxonomies.** (§2F)
* [ ] The literal string "Think with Google" appears nowhere in the
      output.
* [ ] No ASCII / line diagrams. Every diagram came from
      `think-with-google-infographics`.
* [ ] Footer matches the confidentiality × customer matrix (§2I).
* [ ] Author line correct.

**Slides-only**

* [ ] Every slide has speaker notes.
* [ ] No slot overflows its frame. Copy budget respected (§2D).
* [ ] Exported PDF passes the Type 3 gate.
* [ ] Deck file size is comparable to the brand template
      (fidelity indicator — synthesised decks are ~1/10 the size).

**Filing**

* [ ] Deliverable(s) placed under the next `NN-` prefix in the
      dated Drive folder.
* [ ] Existing folder contents untouched.
* [ ] Drive link(s) returned to the user.

---

## 8. See also

* `think-with-google-infographics` — the ONLY diagram / infographic
  engine this skill uses. Read its SKILL.md before authoring visuals.
* `beautiful-drive` — numeric-prefix folder convention for multi-file
  deliverables landing in Drive.
* `gdocs`, `gslides`, `gdrive` — Workspace MCP servers used by the
  Slides track for the actual API calls and Drive placement.

---

## 9. Historical note

An earlier version of this skill shipped a LuaLaTeX / fontspec PDF
pipeline (`assets/techdoc/fde-techdoc.cls`, a pandoc-driven
`build_techdoc.py`). It was evaluated head-to-head against the
Chrome path on identical content and lost on every dimension: layout
fidelity, break control, callout rendering, hyphenation, and iteration
speed. It has been removed. If you find LaTeX references anywhere in
a downstream file, they are stale — the Chrome path is authoritative.
