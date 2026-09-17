# Layout catalogue — AI Tech GTM collateral

Derived from the master template `Branding development for FDE Group`.
Source pages 1–7 are **brand-guide explainer content** and are NOT layouts.
Pages 8–19 are the reusable layout library.

> [!IMPORTANT]
> Two mechanisms produce a branded slide, and they are not interchangeable.
>
> | Mechanism | What you get | Use for |
> | :--- | :--- | :--- |
> | **Theme layout** (`add-slide` + `layout`) | Canvas colour, footer bar, logo mark bottom-left — **inherited automatically**, no elements to place | Any slide whose design is "branded canvas + text" |
> | **Decorated page** (`duplicate-slide` of a library page) | The full composition: cards, stat blocks, chart frames, device mocks | Layouts marked ✦ below |
>
> Verified: a slide created against the inherited theme layout renders the
> `#F8F9FA` canvas, the logo mark and the `Google Cloud | Proprietary &
> Confidential` footer with **no elements supplied by the caller**.

## Canvas

- Aspect: 16:9.
- Never hand-compute geometry from `list_elements` — every shape reports a
  bogus intrinsic `3000000×3000000`; the real transform is separate.
- `list_elements` `slide_index` is **off-by-one** against `list_slides`.

## The library

| # | Layout id | Source pg | Theme | Composition | Directive |
| :-- | :--- | :--: | :--- | :--- | :--- |
| 1 | `title-dark` | 8 | dark | Oversized cropped motif bleeding off-canvas, display title, date line | front-matter |
| 2 | `divider-gradient` | 2, 7 | gradient | Full-bleed rainbow gradient, white knockout mark, short white title | `:::divider` |
| 3 | `statement-light` | 9 | light | Large logo motif left, 2–3 line sentence-case headline right | `:::quote` |
| 4 | ✦ `cards-4-light` | 10 | light | Headline left, 2×2 icon medallion cards right, caption under each | `:::cards` |
| 5 | ✦ `cards-4-dark` | 11 | dark | Same as above on near-black | `:::cards theme=dark` |
| 6 | `image-right-dark` | 12 | dark | Header + sub-body left, full-bleed image right | `:::figure half` |
| 7 | `image-right-light` | 13 | light | Same on `#F8F9FA` | `:::figure half` |
| 8 | `statement-center-dark` | 14 | dark | Centred sparkle icon above a centred 3-line statement | `:::quote theme=dark` |
| 9 | ✦ `device-mock-light` | 15 | light | Label + 24pt headline + body left, laptop frame right | `:::figure device` |
| 10 | ✦ `chart-light` | 16 | light | White chart card left, label + headline + body right | `:::figure chart` |
| 11 | ✦ `stats-3up-light` | 17 | light | Section header, three columns each with icon, header, `00%` stat, description | `:::stat` |
| 12 | `agenda-light` | 18 | light | Motif left, numbered `01…04` rows with rules right | `:::agenda` |
| 13 | `closing-light` | 19 | light | Full-bleed soft rainbow, oversized display "Thank You" | auto-appended |

✦ = decorated page; must be duplicated from the library, not synthesised from
the theme layout alone.

## Mapping collateral type → slide order

| Collateral type | Layout sequence |
| :--- | :--- |
| **pitch-deck** | `title-dark` → `agenda-light` → `statement-light` → `cards-4-*` → `image-right-*` → `stats-3up-light` → `chart-light` → `divider-gradient` → `closing-light` |
| **exec-briefing** | `title-dark` → `statement-center-dark` → `stats-3up-light` → `cards-4-dark` → `closing-light` |
| **workshop-deck** | `title-dark` → `agenda-light` → (`divider-gradient` → `cards-4-light` → `device-mock-light`)×modules → `closing-light` |
| **tech-guide** | Chrome PDF path only — no slide layouts |
| **one-pager** | Chrome PDF path only — no slide layouts |

## Brand-guide pages (do not use as layouts)

| Pg | Content |
| :-- | :--- |
| 1 | "Group Identity" cover — collaborator credits, deck-specific |
| 3 | "Icon Mark" — mark rationale + logo download link |
| 4 | "Usage" — do/don't lockup rules |
| 5 | "Backgrounds" — do/don't placement on photography and gradients |
| 6 | "Beyond the Slides" — environmental/merch applications |

These encode the **rules** captured in `brand.md`; they are reference, not
output. Page 1's dark-hero treatment is superseded by `title-dark` (pg 8),
which is the parameterised version.
