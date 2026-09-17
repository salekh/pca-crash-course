# ai-tech-gtm-collateral — brand asset kit

Vendored assets for the offline track of the Google Cloud FDE / AI Tech Group
collateral system. All files are self-contained: no network fetch is required
at render time.

## `assets/brand/`

### Logo mark variants (transparent PNG, RGBA)

| File | Size (px) | Purpose |
| --- | --- | --- |
| `logo_mark_color.png`      | 4096×3251 | Full-colour mark, white background knocked out with a soft distance-to-white ramp. Use as the primary mark. |
| `logo_mark_white.png`      | 4096×3251 | Pure-white knockout preserving the mark's anti-aliased alpha. Use on dark or gradient surfaces. |
| `logo_mark_mono_dark.png`  | 4096×3251 | Google Grey-900 (`#202124`) knockout preserving the mark's alpha. Use on light surfaces. |
| `logo_motif_crop.png`      | 4096×3836 | ~55 %×65 % top-left crop of the colour mark, alpha dialled to 85 %. Bleeds off a corner as an oversized background motif in the same style as the template PDF. |

All four PNGs are RGBA with alpha extrema `(0, 255)` — no white halo when
composited over black, magenta, or the aurora plates.

### Background plates (RGB PNG, 3840×2160, 16:9)

| File | Purpose |
| --- | --- |
| `bg_gradient_divider.png` | Full-bleed diagonal divider gradient reconstructed from the five per-hue extrema (`#EC4032`, `#FF9302`, `#FABF03`, `#42AB42`, `#0764FF`) sampled off page 02 of the source template. Runs red top-left → orange → yellow → green → blue bottom-right. |
| `bg_light_aurora.png`     | Light content-slide background: Google Grey-50 (`#F8F9FA`) canvas with faint red/orange top-right bloom and yellow/orange bottom-left bloom. Procedural — corner blobs were tuned to match template pages 03/04/10. |
| `bg_dark_aurora.png`      | Dark content-slide background: Google Grey-900 (`#202124`) canvas with yellow top-right, green bottom-left, red left, and blue bottom-right corner blooms. Procedural — matches template pages 11/12/14/15. |

### Palette

`palette.json` — dark canvas (`#202124`) and light canvas (`#F8F9FA`) confirmed
against the template's actual pixel medians; gradient stops sampled from page 02
per-hue extrema; accent blue sampled from the central Gemini sparkle in the
source logo; secondary greys reflect the template body copy.

### Google Cloud lockup

| File | Provenance |
| --- | --- |
| `gcloud_lockup_color.png` | **Official Google-produced asset.** 2900×512 PNG from Wikimedia Commons: `Lockup_GoogleCloud_FullColor_rgb_2900x512px.png`. The filename matches Google's internal brand-kit naming convention. Source: <https://commons.wikimedia.org/wiki/File:Lockup_GoogleCloud_FullColor_rgb_2900x512px.png> |
| `gcloud_lockup_white.png` | **Derived from the official OneColor lockup.** Alpha channel is preserved from `Lockup_GoogleCloud_OneColor_rgb_2900x512px.png` (Wikimedia Commons); RGB recoloured to pure white. This is the standard brand-approved "reversed on dark" treatment. Source: <https://commons.wikimedia.org/wiki/File:Lockup_GoogleCloud_OneColor_rgb_2900x512px.png> |
| `gcloud_lockup_color.svg` | **PLACEHOLDER.** No modern (post-2022) Google Cloud lockup SVG is available from an unambiguously first-party public source. Replace with the official SVG from the Partner Marketing Hub (<https://partnermarketinghub.withgoogle.com/brands/google-cloud/>) or `go/cloudbrand` (Googler-internal). |
| `gcloud_lockup_white.svg` | **PLACEHOLDER.** Same story — replace once the official SVG is obtained; recolour the strokes/fills to `#FFFFFF` if the source is dark-on-transparent. |

## `assets/fonts/`

Vendored copies of every Google Sans family the skill needs, preserving the
original filenames from the user's font cache:

- `GoogleSans-VariableFont_GRAD,opsz,wght.ttf` + `GoogleSans-Italic-VariableFont_GRAD,opsz,wght.ttf` — display Google Sans (variable axes).
- `GoogleSansText-{Regular,Italic,Medium,MediumItalic,Bold,BoldItalic}.ttf` — body Google Sans Text (six static cuts).
- `GoogleSansMono-VariableFont_wght.ttf` + `GoogleSansMono-Italic-VariableFont_wght.ttf` — Google Sans Mono for code / tabular data.
- `GoogleSansCode-VariableFont_wght.ttf` + `GoogleSansCode-Italic-VariableFont_wght.ttf` — Google Sans Code (developer-oriented mono).
- `GoogleSansFlex-VariableFont_GRAD,ROND,opsz,slnt,wdth,wght.ttf` — Google Sans Flex (full six-axis variable font).

### `assets/fonts/fontconfig/fonts.conf`

Copy of the `think-with-google-infographics` fontconfig, with the `<dir>` line
rewritten to the final install path
(`/usr/local/google/home/sanchitalekh/cowork_workspace/skills/ai-tech-gtm-collateral/assets/fonts`).
The system fontset include, cachedir, and the sans-serif / Helvetica / Arial /
Roboto / monospace remap rules are kept unchanged so any legacy default resolves
to a Google Sans family.

## Verification

```bash
FONTCONFIG_FILE=<skill>/assets/fonts/fontconfig/fonts.conf fc-match "Google Sans"
# → GoogleSans-VariableFont_GRAD,opsz,wght.ttf: "Google Sans" "Regular"
```

Any resolution to `Noto Sans` (or similar) means the `<dir>` path in
`fontconfig/fonts.conf` no longer matches where the fonts landed on this
machine — fix the path first.
