# Brand — `ai-tech-gtm-collateral`

> **Status:** normative. The Google Slides deck compiler (`build_deck.py`)
> and the headless-Chrome techdoc renderer (`build_techdoc.py`) both
> consume this specification. Every colour, mark, and background referenced here is
> vendored under `assets/brand/`; every claim is grounded in
> `template_source.pdf` (the AI Tech Group template) or
> `assets/brand/palette.json` (sampled from that same PDF).

---

## 1. Purpose

This document is the written brand specification for the Google Cloud
AI Tech Group's GTM collateral system. It defines the palette,
typography, grid, dark/light rules, footer contract, logo and
co-branding usage, background/motif rules, and per-collateral defaults
that both the Slides and print paths must render identically. All
colours, marks, and background plates are sampled or extracted from
`template_source.pdf` and vendored under `assets/brand/`; nothing here
is invented, and no palette value outside `palette.json` may be
introduced without re-sampling the template.

---

## 2. Palette

Every hex below is a verbatim key from `assets/brand/palette.json`.
Do not introduce new tokens without re-sampling the template and
updating `palette.json` first.

| Role | Token | Hex | Sample | Where used |
| --- | --- | --- | --- | --- |
| Canvas — dark | `canvas.dark` | `#202124` | <span style="background:#202124;color:#fff;padding:0 8px">202124</span> | Dark-theme slide/page background; body text on light. |
| Canvas — light | `canvas.light` | `#F8F9FA` | <span style="background:#F8F9FA;color:#202124;padding:0 8px">F8F9FA</span> | Light-theme slide/page background. |
| Accent — blue | `accent.blue` | `#4471ED` | <span style="background:#4471ED;color:#fff;padding:0 8px">4471ED</span> | Interactive/link accent, key-figure highlights, sparkle at mark centre. |
| Text on dark — primary | `text_on_dark.primary` | `#FFFFFF` | <span style="background:#FFFFFF;color:#202124;padding:0 8px;border:1px solid #ccc">FFFFFF</span> | H1–H3 and body on dark canvas. |
| Text on dark — secondary | `text_on_dark.secondary` | `#BABBBC` | <span style="background:#BABBBC;color:#202124;padding:0 8px">BABBBC</span> | Captions, footer text, secondary labels on dark. |
| Text on light — primary | `text_on_light.primary` | `#000000` | <span style="background:#000000;color:#fff;padding:0 8px">000000</span> | H1–H3 and body on light canvas. |
| Text on light — secondary | `text_on_light.secondary` | `#5F6368` | <span style="background:#5F6368;color:#fff;padding:0 8px">5F6368</span> | Captions, footer text, secondary labels on light (Google Grey-600). |
| Gradient stop 1 (red) | `gradient_stops[0]` | `#EC4032` | <span style="background:#EC4032;color:#fff;padding:0 8px">EC4032</span> | Divider gradient — top-left. |
| Gradient stop 2 (orange) | `gradient_stops[1]` | `#FF9302` | <span style="background:#FF9302;color:#202124;padding:0 8px">FF9302</span> | Divider gradient — early diagonal. |
| Gradient stop 3 (yellow) | `gradient_stops[2]` | `#FABF03` | <span style="background:#FABF03;color:#202124;padding:0 8px">FABF03</span> | Divider gradient — mid diagonal. |
| Gradient stop 4 (green) | `gradient_stops[3]` | `#42AB42` | <span style="background:#42AB42;color:#fff;padding:0 8px">42AB42</span> | Divider gradient — late diagonal. |
| Gradient stop 5 (blue) | `gradient_stops[4]` | `#0764FF` | <span style="background:#0764FF;color:#fff;padding:0 8px">0764FF</span> | Divider gradient — bottom-right. |
| Google brand — blue | `google_brand.blue` | `#4285F4` | <span style="background:#4285F4;color:#fff;padding:0 8px">4285F4</span> | Google-quad chart series, Google Cloud lockup wordmark. |
| Google brand — red | `google_brand.red` | `#EA4335` | <span style="background:#EA4335;color:#fff;padding:0 8px">EA4335</span> | Google-quad chart series. |
| Google brand — yellow | `google_brand.yellow` | `#FBBC04` | <span style="background:#FBBC04;color:#202124;padding:0 8px">FBBC04</span> | Google-quad chart series. |
| Google brand — green | `google_brand.green` | `#34A853` | <span style="background:#34A853;color:#fff;padding:0 8px">34A853</span> | Google-quad chart series. |

### 2.1 Sampling provenance

The `sample_notes` string in `assets/brand/palette.json` reads,
verbatim:

> Dark = modal dark pixel of page 15 (matches Google Grey-900 #202124). Light = modal off-white pixel of page 04 (matches Google Grey-50 #F8F9FA). Gradient stops = five per-hue extrema sampled across page 02 (the full-bleed divider page).

The accent blue `#4471ED` was sampled from the Gemini-style sparkle at
the centre of the AI Tech chevron-diamond mark in the same source PDF.
The Google brand quad (`#4285F4 / #EA4335 / #FBBC04 / #34A853`) is the
canonical Google identity palette and is retained as-is for chart
series and for the Google Cloud lockup — it is not re-sampled from the
template.

---

## 3. Type scale

Family stack (all four are Google-owned; substitution is disallowed):

| Family | Role | Notes |
| --- | --- | --- |
| **Google Sans** | Display, H1, H2, H3, cover headline | Geometric sans; use for anything ≥ 14 pt print / ≥ 24 pt slide. |
| **Google Sans Text** | Body, lists, tables, captions, labels | Text-optimised cut; use for anything < 14 pt print / < 24 pt slide. |
| **Google Sans Mono** | Inline code, tabular numerals, CLI snippets | Prefer for narrow inline monospace runs. |
| **Google Sans Code** | Block code, syntax-highlighted listings | Ligature-aware cut for `code` fences and print listings. |
| **Google Sans Flex** | *(reserved)* | Variable-axis master; **explicitly excluded** from the shipping stack. Chrome rasterises variable fonts into Type 3 glyph programs (non-scalable, breaks selection, degrades in print) — the deck compiler and Chrome PDF renderer reference only pre-instanced static TTFs. |

> Roboto is **not** permitted. Neither is any Noto or DejaVu fallback:
> if `fc-match "Google Sans"` returns anything else, the render is
> broken (see §10).

The two tables below are house choices for this skill. Print sizes
follow the user's dense-doc preference (9.5 pt body / 1.5 line-height);
slide sizes are calibrated for 1920×1080 at typical exec-briefing
viewing distance.

### 3.1 Print scale (Chrome PDF; A4)

| Role | Family | Weight | Size (pt) | Line-height | Tracking |
| --- | --- | --- | --- | --- | --- |
| H1 (chapter) | Google Sans | 700 | 22 | 1.15 | 0 |
| H2 (section) | Google Sans | 600 | 15 | 1.25 | 0 |
| H3 (subsection) | Google Sans | 600 | 12 | 1.30 | 0 |
| Body | Google Sans Text | 400 | 9.5 | 1.50 | 0 |
| Caption | Google Sans Text | 400 (italic) | 8.5 | 1.35 | 0 |
| ALL-CAPS label | Google Sans Text | 600 | 8 | 1.20 | +40 (1/1000 em) |
| Inline code | Google Sans Mono | 400 | 9 | 1.50 | 0 |
| Block code | Google Sans Code | 400 | 8.5 | 1.35 | 0 |

### 3.2 Slide scale (Google Slides; 1920×1080)

| Role | Family | Weight | Size (pt) | Line-height | Tracking |
| --- | --- | --- | --- | --- | --- |
| Display (cover) | Google Sans | 700 | 60 | 1.05 | 0 |
| H1 (slide title) | Google Sans | 600 | 44 | 1.10 | 0 |
| H2 (subhead) | Google Sans | 600 | 30 | 1.15 | 0 |
| Body | Google Sans Text | 400 | 18 | 1.35 | 0 |
| Caption | Google Sans Text | 400 | 12 | 1.30 | 0 |
| ALL-CAPS accent | Google Sans Text | 700 | 12 | 1.20 | +80 (1/1000 em) |
| Inline code | Google Sans Mono | 400 | 16 | 1.35 | 0 |
| Block code | Google Sans Code | 400 | 14 | 1.30 | 0 |

### 3.3 Numerals

Use **tabular** (fixed-width) figures for all stat callouts, table
columns, KPI dashboards, and footer page numbers. Use proportional
(default) figures only inside running prose. In Chrome/CSS this
is `font-feature-settings: "tnum" 1;` on the affected selector; in
Slides, apply the "Tabular figures" OpenType feature via the theme.

---

## 4. Baseline grid & safe margins

Both canvases are laid out on a 12-column grid. The numbers in the
tables below are the values the compilers use to place text frames;
authors do not set them by hand.

### 4.1 Slides — 16:9 at 1920×1080

| Zone | Value |
| --- | --- |
| Canvas | 1920 × 1080 px |
| Safe outer margin | 72 px (top / left / right / bottom-of-content) |
| Column grid | 12 columns |
| Gutter | 40 px |
| Column width (derived) | ≈ 118 px |
| Footer strip (reserved) | 60 px, bottom of canvas |
| Title baseline | 128 px from top (H1 sits inside the safe area) |

### 4.2 Print — A4 (Chrome PDF)

| Zone | Value |
| --- | --- |
| Trim size | 210 × 297 mm (A4) |
| Body block | ≈ 178 × 263 mm |
| Outer margin | 16 mm |
| Inner (spine) margin | 16 mm |
| Top margin | 18 mm |
| Bottom margin | 16 mm (accommodates footer + page number) |
| Column grid | 12 columns (used mainly by figure floats) |
| Gutter | 12 pt |
| Page number | Bottom-right, Google Sans Text 8.5 pt |

---

## 5. Dark vs light slide rules

| Situation | Canvas | Background plate | Logo variant | Primary text | Secondary text |
| --- | --- | --- | --- | --- | --- |
| Standard content (default) | Light | `bg_light_aurora.png` | `logo_mark_mono_dark.png` (footer, 24 px) | `#000000` | `#5F6368` |
| Dark content (deep-dive, product screens, hero stat) | Dark | `bg_dark_aurora.png` | `logo_mark_white.png` (footer, 24 px) | `#FFFFFF` | `#BABBBC` |
| Cover — light theme | Light | `bg_light_aurora.png` | `logo_mark_color.png` (upper-left) + `gcloud_lockup_color.png` (upper-right) | `#000000` | `#5F6368` |
| Cover — dark theme | Dark | `bg_dark_aurora.png` | `logo_mark_color.png` (upper-left) + `gcloud_lockup_white.png` (upper-right) | `#FFFFFF` | `#BABBBC` |
| **Divider slide (always full-bleed)** | Gradient | `bg_gradient_divider.png` | *(mark suppressed)* | `#FFFFFF` (title only) | *(not used)* |
| Motif slot | inherit from theme | as above **plus** `logo_motif_crop.png` in the top-left or bottom-right ~35% of the slide, 40–70% opacity | as above | as above | as above |

Divider slides always carry the full-bleed gradient
(`bg_gradient_divider.png`), the section title set in white Google Sans
60 pt, and no footer.

---

## 6. Footer & confidentiality rules

### 6.1 Default footer construction

Every non-cover slide and every non-cover print page carries a footer
with two elements:

| Element | Position | Asset / string | Theme = light | Theme = dark |
| --- | --- | --- | --- | --- |
| Small mono mark | Bottom-left | `logo_mark_mono_dark.png` on light, `logo_mark_white.png` on dark | 24 px tall | 24 px tall |
| Footer string | Bottom-right | see §6.2 | Google Sans Text 8.5 pt, `#5F6368` | Google Sans Text 8.5 pt, `#BABBBC` |
| Page number (print only) | Bottom-right, after the footer string | tabular figure | Google Sans Text 8.5 pt, `#5F6368` | — |

The default footer string is **`Google Cloud  |  Proprietary &
Confidential`** — this is what appears when `confidentiality:
proprietary` (or the compiler's fallback default) is in effect and no
`customer:` is set.

### 6.2 Confidentiality mapping (mirrors `authoring.md` §3.2)

Both the deck compiler and the Chrome PDF renderer resolve the footer
string from `confidentiality` × `customer:` at compile time. Authors
never type footer text by hand.

| `confidentiality` | No `customer:` | With `customer:` set |
| --- | --- | --- |
| `internal` | `Google — Internal` | `Google & {customer} — Confidential` |
| `proprietary` *(default)* | `Google Cloud  \|  Proprietary & Confidential` | `Google & {customer} — Proprietary & Confidential` |
| `customer-shared` | `Google Cloud  \|  Shared with customer` | `Google & {customer} — Confidential` |
| `public` | `Google Cloud` | `Google Cloud` *(customer swap suppressed on public material)* |

Two derived rules called out by name:

1. **Customer-swap rule.** If `customer:` is set **and**
   `confidentiality ∈ {internal, proprietary, customer-shared}`, the
   footer string switches to the "With `customer:` set" column above.
   For `proprietary` this yields `Prepared for {customer} ·
   Confidential` semantically — the exact rendered string is
   `Google & {customer} — Proprietary & Confidential` per the table
   (authoring.md §3.2 is the source of truth).
2. **Public-suppression rule.** When `confidentiality: public` is set
   the footer collapses to `Google Cloud` regardless of `customer:`.

---

## 7. Logo usage & co-branding

### 7.1 Primary mark — AI Tech chevron-diamond

| Surface | File | When |
| --- | --- | --- |
| Colour, light or gradient background | `logo_mark_color.png` | Covers, marketing hero, executive summary slide. |
| White knockout, dark background | `logo_mark_white.png` | Dark-theme covers, dark-theme footers. |
| Mono knockout, light background | `logo_mark_mono_dark.png` | Light-theme interior footers (24 px slide / 0.30 in print). |
| Oversized motif | `logo_motif_crop.png` | Explicit motif slot only (§8), 40–70 % opacity, max **one** per deck. |

### 7.2 Google Cloud lockup

| Surface | File | Format | Notes |
| --- | --- | --- | --- |
| Cover, light | `gcloud_lockup_color.png` | 2900 × 512 raster | OFFICIAL colour lockup, sourced from Wikimedia's Google-brand-kit filename. |
| Cover, dark | `gcloud_lockup_white.png` | 2900 × 512 raster | Derived from the OneColor lockup with white RGB + preserved alpha. |
| Any surface | `gcloud_lockup_color.svg` / `gcloud_lockup_white.svg` | **PLACEHOLDER text files** | These SVGs are *not* real vectors. Do not ship them. Fetch the production SVG from **Partner Marketing Hub** (Google internal) and drop it in with the same basename before releasing any customer-shared deliverable. |

### 7.3 Placement matrix

| Slide / page | AI Tech mark | Google Cloud lockup |
| --- | --- | --- |
| Cover — layout A (chevron hero) | Upper-left, colour, ≈ 96 px tall (slide) / 0.75 in (print) | Upper-right, colour or white per theme, ≈ 48 px tall (slide) / 0.40 in (print) |
| Cover — layout B (centre-hero) | Centre, colour, ≈ 240 px tall (slide) / 1.5 in (print) | Bottom-right cluster with byline, ≈ 40 px tall (slide) / 0.35 in (print) |
| Interior slide | Bottom-left footer, mono, 24 px | *(omitted)* |
| Interior page (print) | Bottom-left footer, mono, 0.30 in | *(omitted)* |
| Exec-briefing back page | Bottom-right, mono, 0.35 in | Bottom-right, colour, 0.40 in (colophon) |
| Divider slide | *(suppressed)* | *(suppressed)* |

### 7.4 Clear space & minimum size

| Rule | Value |
| --- | --- |
| Minimum clear space around either mark | ≥ height of the letter "G" in the wordmark |
| GCloud lockup — minimum on-screen height | 32 px |
| GCloud lockup — minimum print height | 0.35 in |
| AI Tech mark — minimum on-screen height | 24 px (footer size floor) |
| AI Tech mark — minimum print height | 0.30 in |

### 7.5 Do-not list

- Do not recolour the AI Tech mark (no theme tints, no gradient fills).
- Do not skew, rotate, or apply perspective to either mark.
- Do not add drop-shadows, outer glows, or bevels.
- Do not crop either mark. The **only** permitted crop is
  `logo_motif_crop.png`, used exclusively in the motif slot defined in
  §8.
- Do not ship the placeholder SVG lockups (`gcloud_lockup_*.svg`) —
  replace them with the Partner Marketing Hub vector before release.
- Do not swap in a legacy Google Cloud rainbow lockup or a legacy AI
  mark.

---

## 8. Backgrounds & motifs

| Asset | Role | Rules |
| --- | --- | --- |
| `bg_gradient_divider.png` | Full-bleed section-divider background | Divider slides only. Title in white Google Sans 60 pt, centre-aligned. **Never** place body copy over it. |
| `bg_light_aurora.png` | Standard light-theme canvas | Default backdrop for light content slides and light print pages. Do **not** increase opacity or re-tint — the plate is already tuned to sit behind long-form body copy without hurting contrast. |
| `bg_dark_aurora.png` | Standard dark-theme canvas | Default backdrop for dark content slides. Same rule: do not re-tint or overlay additional colour washes. |
| `logo_motif_crop.png` | Oversized cropped mark used as an editorial motif | Place in the top-left **or** bottom-right ~35 % of the slide, at **40–70 % opacity**. **Maximum one motif slot per deck.** Never behind body copy — reserve for section-opener or single-quote slides. |

---

## 9. Application to collateral types

The `collateral_type` values below come from `authoring.md` §3.1.
Each row is the brand default; a front-matter `theme:` value overrides
the canvas column, and a `logo_variant:` value overrides the lockup
column.

| `collateral_type` | Canvas default | Cover treatment | GCloud lockup on cover? | Footer default | Motif usage |
| --- | --- | --- | --- | --- | --- |
| `pitch-deck` | Dark | Layout B (centre-hero mark, subtitle + date) | Yes (bottom-right cluster) | `Google Cloud  \|  Proprietary & Confidential` (swap to customer if `customer:` set) | Up to one motif slot on a section opener. |
| `exec-briefing` | Light | Layout A (upper-left mark, upper-right lockup, dense TOC on cover) | Yes (upper-right) **and** on the back-page colophon | `Google & {customer} — Proprietary & Confidential` when `customer:` set, else `Google Cloud  \|  Proprietary & Confidential` | Optional motif on the executive-summary slide only. |
| `workshop-deck` | Light | Layout A with agenda strip under the title | Yes (upper-right) | `Google Cloud  \|  Proprietary & Confidential` | Motif reserved for module dividers (still ≤ 1 per deck). |
| `tech-guide` | Light (print) / auto (deck) | Print title page with abstract; deck cover Layout A | Yes on print title page; deck cover only | `Google Cloud  \|  Proprietary & Confidential` (+ page number, print) | Motif discouraged — technical density leaves no room. |
| `one-pager` | Light | Compact header band (mark left, lockup right, title below) | Yes (right of header band) | `Google Cloud  \|  Proprietary & Confidential` | No motif. |

---

## 10. Verification checklist

Run this list before any deliverable leaves the desk. Each row must
pass; a single failure blocks release.

| # | Check | How |
| --- | --- | --- |
| 1 | Google Sans is installed and resolves without fallback. | `fc-match "Google Sans"` must return a Google Sans face, **not** Noto, DejaVu, or Roboto. Repeat for `"Google Sans Text"`, `"Google Sans Mono"`, `"Google Sans Code"`. |
| 2 | Palette is intact in the rendered artefact. | Sample the exported PDF/PNG with a colour picker at three points (canvas, accent, footer text) and confirm the hex matches `assets/brand/palette.json`. |
| 3 | Footer string matches the intended audience. | Cross-check `confidentiality` × `customer:` against §6.2. `public` never carries a customer name; `internal` never uses the "Google Cloud" prefix. |
| 4 | Logo clear-space respected. | Around every AI Tech mark and every Google Cloud lockup, the empty margin is ≥ the height of the letter "G" in the wordmark. |
| 5 | Minimum sizes respected. | GCloud lockup ≥ 32 px on screen / ≥ 0.35 in on print; AI Tech mark ≥ 24 px / ≥ 0.30 in. |
| 6 | No legacy imagery. | No old Google Cloud rainbow lockup; no Roboto; no legacy AI mark; no non-Google-Sans headline face; placeholder SVG lockups replaced with the Partner Marketing Hub vector. |
| 7 | Motif budget respected. | At most one slide/page uses `logo_motif_crop.png`; it is not behind body copy. |
| 8 | Divider slides are full-bleed gradient only. | Every divider uses `bg_gradient_divider.png` full-bleed, title in white, no footer, no body copy. |
| 9 | Backgrounds are the vendored plates, unmodified. | `bg_light_aurora.png` / `bg_dark_aurora.png` opacity, tint, and blur are all at defaults. |
| 10 | Confidentiality footer is present on **every** non-cover surface. | Spot-check first, middle, and last non-cover slide/page. |
