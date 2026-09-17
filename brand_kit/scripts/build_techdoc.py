#!/usr/bin/env python3
"""
build_techdoc.py — Convert a branded Markdown manuscript into a print-quality
A4 PDF via headless Chrome, using the approved AI Tech GTM techdoc stylesheet.

Usage:
  python3 build_techdoc.py \
      --md fms_techdoc.md \
      --css /path/to/techdoc.css \
      --figures /path/to/diagrams \
      --out-html fms_techdoc.html \
      --out-pdf  fms_techdoc.pdf

Stdlib only. The Markdown parser is hand-written and supports:
  - YAML front matter (simple key: "value" form).
  - h1 / h2 / h3, paragraphs, **bold**, *italic*, `code`, links.
  - Fenced code blocks (```lang ... ```).
  - Nested ordered / unordered lists (indentation-based).
  - GitHub-style tables (with header separator line).
  - Blockquotes.
  - Standalone `---` horizontal rules (used as section dividers).
  - Custom markers:
        [[FIGURE: filename.png | Caption text]]
        [[CALLOUT:note|Title|Body]] / warn / tip
        [[STATS: v1 :: l1 || v2 :: l2 || v3 :: l3]]

Missing figures do not crash — a clearly-visible placeholder box is emitted
in their place, with the filename and caption preserved.
"""
from __future__ import annotations

import argparse
import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# Front matter
# =============================================================================

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    """Extract a tiny YAML-ish front-matter block. Only flat key: value pairs
    are supported. Values may be quoted."""
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    fm: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            v = v[1:-1]
        fm[k.strip()] = v
    return fm, body


# =============================================================================
# Inline rendering (bold/italic/code/links)
# =============================================================================

_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE = re.compile(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|mailto):[^>\s]+)>")


def render_inline(s: str) -> str:
    """Render inline Markdown to HTML. Code spans are protected from other
    substitutions via placeholders."""
    if s is None:
        return ""
    placeholders: List[str] = []

    def _stash_code(m: re.Match) -> str:
        placeholders.append(m.group(1))
        return f"\0CODE{len(placeholders) - 1}\0"

    s = _INLINE_CODE_RE.sub(_stash_code, s)
    # Escape after stashing code (code content is escaped separately later).
    s = html.escape(s, quote=False)
    # Bold / italic.
    s = _STRONG_RE.sub(r"<strong>\1</strong>", s)
    s = _EM_RE.sub(r"<em>\1</em>", s)
    # Links.
    s = _LINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">'
        f"{m.group(1)}</a>",
        s,
    )
    s = _AUTOLINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(1), quote=True)}">'
        f"{html.escape(m.group(1))}</a>",
        s,
    )
    # Restore code spans.
    def _pop_code(m: re.Match) -> str:
        idx = int(m.group(1))
        return f"<code>{html.escape(placeholders[idx])}</code>"

    s = re.sub(r"\0CODE(\d+)\0", _pop_code, s)
    return s


# =============================================================================
# Block parsing
# =============================================================================

# Custom markers.
_FIGURE_RE = re.compile(r"^\[\[FIGURE:\s*([^|]+?)\s*\|\s*(.+?)\s*\]\]\s*$")
_CALLOUT_RE = re.compile(
    r"^\[\[CALLOUT:(note|warn|tip)\|([^|]*)\|(.*)\]\]\s*$", re.DOTALL
)
_STATS_RE = re.compile(r"^\[\[STATS:\s*(.+?)\s*\]\]\s*$")

# Headings, lists, table separator.
_H_RE = re.compile(r"^(#{1,4})\s+(.*)$")
_UL_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
_OL_RE = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
_HR_RE = re.compile(r"^-{3,}\s*$")
_BLOCKQUOTE_RE = re.compile(r"^>\s?(.*)$")
_FENCE_RE = re.compile(r"^```(\w*)\s*$")


def _split_table_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def parse_blocks(md: str) -> List[Dict[str, Any]]:
    """Parse the Markdown body into a list of block dicts."""
    lines = md.splitlines()
    i = 0
    n = len(lines)
    blocks: List[Dict[str, Any]] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Blank line
        if not stripped:
            i += 1
            continue

        # Fenced code block
        fence = _FENCE_RE.match(line)
        if fence:
            lang = fence.group(1)
            i += 1
            buf: List[str] = []
            while i < n and not _FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1  # skip closing fence
            blocks.append({"type": "code", "lang": lang, "text": "\n".join(buf)})
            continue

        # Custom markers (single line)
        m = _FIGURE_RE.match(line)
        if m:
            blocks.append(
                {
                    "type": "figure",
                    "filename": m.group(1).strip(),
                    "caption": m.group(2).strip(),
                }
            )
            i += 1
            continue

        m = _CALLOUT_RE.match(line)
        if m:
            blocks.append(
                {
                    "type": "callout",
                    "flavor": m.group(1),
                    "title": m.group(2).strip(),
                    "body": m.group(3).strip(),
                }
            )
            i += 1
            continue

        m = _STATS_RE.match(line)
        if m:
            raw = m.group(1)
            items = []
            for chunk in raw.split("||"):
                if "::" in chunk:
                    v, l = chunk.split("::", 1)
                    items.append((v.strip(), l.strip()))
            blocks.append({"type": "stats", "items": items})
            i += 1
            continue

        # Heading
        m = _H_RE.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            blocks.append({"type": "heading", "level": level, "text": text})
            i += 1
            continue

        # Horizontal rule (used as section divider in the manuscript;
        # section wrapping already forces page breaks, so we drop these).
        if _HR_RE.match(stripped):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Table: header row + separator + body rows.
        if "|" in stripped and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]):
            header = _split_table_row(lines[i])
            i += 2  # skip header and separator
            rows: List[List[str]] = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(_split_table_row(lines[i]))
                i += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue

        # Blockquote
        if _BLOCKQUOTE_RE.match(line):
            buf = []
            while i < n and _BLOCKQUOTE_RE.match(lines[i]):
                buf.append(_BLOCKQUOTE_RE.match(lines[i]).group(1))
                i += 1
            blocks.append({"type": "blockquote", "text": "\n".join(buf)})
            continue

        # List (ordered or unordered) — collect a contiguous list run and
        # parse indentation to build nesting.
        if _UL_RE.match(line) or _OL_RE.match(line):
            buf = []
            while i < n:
                cur = lines[i]
                if cur.strip() == "":
                    # A blank line ends the list only if the next non-blank
                    # line isn't a continuation / nested list item.
                    if (
                        i + 1 < n
                        and (_UL_RE.match(lines[i + 1]) or _OL_RE.match(lines[i + 1]))
                    ):
                        i += 1
                        continue
                    break
                if _UL_RE.match(cur) or _OL_RE.match(cur):
                    buf.append(cur)
                    i += 1
                elif cur.startswith(" ") or cur.startswith("\t"):
                    # Continuation of previous list item.
                    buf.append(cur)
                    i += 1
                else:
                    break
            blocks.append({"type": "list", "raw": buf})
            continue

        # Paragraph: consume lines until blank / structural marker.
        buf = [line]
        i += 1
        while i < n:
            nxt = lines[i]
            if (
                not nxt.strip()
                or _H_RE.match(nxt)
                or _FENCE_RE.match(nxt)
                or _FIGURE_RE.match(nxt)
                or _CALLOUT_RE.match(nxt)
                or _STATS_RE.match(nxt)
                or _HR_RE.match(nxt.strip())
                or _UL_RE.match(nxt)
                or _OL_RE.match(nxt)
                or _BLOCKQUOTE_RE.match(nxt)
                or ("|" in nxt and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]))
            ):
                break
            buf.append(nxt)
            i += 1
        blocks.append({"type": "para", "text": " ".join(b.strip() for b in buf)})

    return blocks


# =============================================================================
# List nesting
# =============================================================================


def _list_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def render_list(raw_lines: List[str]) -> str:
    """Turn a run of list-source lines into nested HTML lists."""
    items: List[Tuple[int, str, str, List[str]]] = []
    # (indent, kind, text, continuation_lines)
    for line in raw_lines:
        m = _UL_RE.match(line)
        if m:
            items.append((_list_indent(line), "ul", m.group(2), []))
            continue
        m = _OL_RE.match(line)
        if m:
            items.append((_list_indent(line), "ol", m.group(3), []))
            continue
        # Continuation
        if items:
            items[-1][3].append(line.strip())

    # Attach continuation text into item text (joined with a space so that
    # paragraph-like continuations flow naturally).
    normalised: List[Tuple[int, str, str]] = []
    for indent, kind, text, cont in items:
        if cont:
            text = text + " " + " ".join(cont).strip()
        normalised.append((indent, kind, text))

    if not normalised:
        return ""

    # Build a tree recursively.
    def build(idx: int, base_indent: int) -> Tuple[str, int]:
        out = []
        kind = normalised[idx][1]
        out.append(f"<{kind}>")
        while idx < len(normalised):
            indent, k, text = normalised[idx]
            if indent < base_indent:
                break
            if indent > base_indent:
                # nested — recurse
                sub, idx = build(idx, indent)
                # nest inside last <li>
                if out and out[-1].endswith("</li>"):
                    out[-1] = out[-1][: -len("</li>")] + sub + "</li>"
                else:
                    out.append("<li>" + sub + "</li>")
                continue
            if k != kind:
                # sibling list switches type at same indent — close and reopen
                out.append(f"</{kind}>")
                kind = k
                out.append(f"<{kind}>")
            out.append(f"<li>{render_inline(text)}</li>")
            idx += 1
        out.append(f"</{kind}>")
        return "".join(out), idx

    html_out, _ = build(0, normalised[0][0])
    return html_out


# =============================================================================
# Block rendering
# =============================================================================


def _figure_html(
    filename: str, caption: str, figures_dir: Path
) -> str:
    src = figures_dir / filename
    caption_html = render_inline(caption)
    if src.exists():
        # Use file:// URL so Chrome resolves the image irrespective of the
        # HTML file's own location.
        href = "file://" + str(src.resolve())
        return (
            f'<figure><img src="{html.escape(href, quote=True)}" '
            f'alt="{html.escape(filename)}"/>'
            f"<figcaption>{caption_html}</figcaption></figure>"
        )
    # Placeholder — clearly visible, filename baked in, caption preserved.
    return (
        f'<figure class="ph"><div class="ph-box">'
        f'<div class="ph-tag">FIGURE PLACEHOLDER</div>'
        f'<div class="ph-file">{html.escape(filename)}</div>'
        f'<div class="ph-note">Image not yet available — this box will be '
        f"replaced when the figure lands in the diagrams directory.</div>"
        f"</div>"
        f"<figcaption>{caption_html}</figcaption></figure>"
    )


def _callout_html(flavor: str, title: str, body: str) -> str:
    cls = "callout" if flavor == "note" else f"callout {flavor}"
    return (
        f'<div class="{cls}"><div class="t">{render_inline(title)}</div>'
        f"<p>{render_inline(body)}</p></div>"
    )


def _stats_html(items: List[Tuple[str, str]]) -> str:
    parts = ['<div class="stats">']
    for v, l in items:
        parts.append(
            f'<div class="stat"><div class="n">{render_inline(v)}</div>'
            f'<div class="l">{render_inline(l)}</div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def _table_html(header: List[str], rows: List[List[str]]) -> str:
    out = ["<table><thead><tr>"]
    for cell in header:
        out.append(f"<th>{render_inline(cell)}</th>")
    out.append("</tr></thead><tbody>")
    for row in rows:
        # Pad short rows so column count matches header.
        while len(row) < len(header):
            row.append("")
        out.append("<tr>")
        for cell in row:
            out.append(f"<td>{render_inline(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _code_html(text: str) -> str:
    return f"<pre><code>{html.escape(text)}</code></pre>"


def _blockquote_html(text: str) -> str:
    return f"<blockquote>{render_inline(text)}</blockquote>"


# =============================================================================
# Section assembly
# =============================================================================

_H1_NUM_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def _strip_h1_number(text: str) -> Tuple[str, Optional[str]]:
    """Strip a leading 'N. ' from an H1 so the CSS counter does not
    double-number it. Returns (title, original_number_or_None)."""
    m = _H1_NUM_RE.match(text.strip())
    if m:
        return m.group(2).strip(), m.group(1)
    return text.strip(), None


def render_body(blocks: List[Dict[str, Any]], figures_dir: Path) -> Tuple[str, List[str]]:
    """Render body HTML. Returns (body_html, section_titles)."""
    out: List[str] = []
    section_titles: List[str] = []
    open_section = False

    def close_section():
        nonlocal open_section
        if open_section:
            out.append("</section>")
            open_section = False

    for b in blocks:
        t = b["type"]
        if t == "heading" and b["level"] == 1:
            close_section()
            title, _ = _strip_h1_number(b["text"])
            section_titles.append(title)
            out.append('<section>')
            out.append(f'<h2 class="sec">{render_inline(title)}</h2>')
            open_section = True
            continue

        if t == "heading" and b["level"] == 2:
            out.append(f"<h3>{render_inline(b['text'])}</h3>")
            continue

        if t == "heading" and b["level"] >= 3:
            out.append(f"<h4>{render_inline(b['text'])}</h4>")
            continue

        if t == "para":
            out.append(f"<p>{render_inline(b['text'])}</p>")
            continue

        if t == "list":
            out.append(render_list(b["raw"]))
            continue

        if t == "table":
            out.append(_table_html(b["header"], b["rows"]))
            continue

        if t == "code":
            out.append(_code_html(b["text"]))
            continue

        if t == "blockquote":
            out.append(_blockquote_html(b["text"]))
            continue

        if t == "figure":
            out.append(_figure_html(b["filename"], b["caption"], figures_dir))
            continue

        if t == "callout":
            out.append(_callout_html(b["flavor"], b["title"], b["body"]))
            continue

        if t == "stats":
            out.append(_stats_html(b["items"]))
            continue

        if t == "hr":
            # Section divider in the manuscript — sections already page-break.
            continue

    close_section()
    return "\n".join(out), section_titles


# =============================================================================
# Cover / TOC / additional CSS
# =============================================================================


def render_cover(fm: Dict[str, str], assets_dir: Path) -> str:
    """Cover page modelled on the `.cover` block already in the CSS."""
    brand = assets_dir / "brand"
    logo_mark = (brand / "logo_mark_color.png").resolve()
    motif = (brand / "logo_motif_crop.png").resolve()
    gcloud_lockup = (brand / "gcloud_lockup_color.png").resolve()

    title = fm.get("title", "Untitled")
    subtitle = fm.get("subtitle", "")
    author = fm.get("author", "")
    date = fm.get("date", "")
    confidentiality = fm.get(
        "confidentiality", "Google Cloud | Proprietary & Confidential"
    )

    return f"""
<section class="cover">
  <div class="grad"></div>
  <img class="motif" src="file://{motif}" alt=""/>
  <div class="body">
    <img class="mark" src="file://{logo_mark}" alt="AI Tech logo"/>
    <div class="eyebrow">AI Tech GTM · Reference Whitepaper</div>
    <h1 class="cover-title">{html.escape(title)}</h1>
    <p class="sub">{html.escape(subtitle)}</p>
  </div>
  <div class="rule"></div>
  <div class="meta">
    <b>Author</b>&nbsp;&nbsp;{html.escape(author)}
    &nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;
    <b>Published</b>&nbsp;&nbsp;{html.escape(date)}
    &nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;
    <b>Classification</b>&nbsp;&nbsp;{html.escape(confidentiality)}
  </div>
  <div class="lockups">
    <img class="g" src="file://{gcloud_lockup}" alt="Google Cloud"/>
  </div>
</section>
"""


def render_toc(section_titles: List[str]) -> str:
    lis = "".join(
        f'<li><span class="ti">{html.escape(t)}</span>'
        f'<span class="dots"></span></li>'
        for t in section_titles
    )
    return f"""
<section class="toc">
  <h2>Contents</h2>
  <ol>{lis}</ol>
</section>
"""


# Additional CSS on top of the branded stylesheet. Only ADDS behaviour the
# manuscript needs that the stylesheet lacks — never restyles what already
# works.
_EXTRA_CSS = r"""
/* --- string(doctitle) source: cover title carries the running header.
   NOTE: headless Chrome resolves string-set less reliably across named
   @page contexts (the cover uses `@page cover`), so build_techdoc.py
   also injects the doctitle as a literal string into the @page rule
   at build time as a belt-and-braces measure. --- */
.cover-title{ string-set: doctitle content(); }

/* --- avoid orphaned headings; keep first paragraph with heading --- */
h2.sec{ break-after: avoid-page; }
h3, h4{ break-after: avoid-page; break-inside: avoid; }
h3 + p, h3 + ul, h3 + ol, h3 + table, h3 + figure, h3 + pre,
h3 + .callout, h3 + .stats { break-before: avoid; }

/* --- keep tables and figures whole where possible --- */
table{ page-break-inside: auto; }
tr, thead{ page-break-inside: avoid; }
figure{ page-break-inside: avoid; }
pre{ page-break-inside: avoid; }

/* --- placeholder figure box, used when a diagram file is not yet
       generated. Clearly visible; caption remains numbered. --- */
figure.ph .ph-box{
  border: 1.2pt dashed var(--gred);
  background: repeating-linear-gradient(
    45deg, #FDECEA 0 6mm, #FEF6F5 6mm 12mm);
  padding: 14mm 10mm; text-align: center; border-radius: 1.5mm;
}
figure.ph .ph-tag{
  font-family:'Google Sans'; font-weight:700; font-size:8pt;
  letter-spacing:.14em; text-transform:uppercase; color:var(--gred);
  margin-bottom: 2mm;
}
figure.ph .ph-file{
  font-family:'Google Sans Mono'; font-size:10pt; color:var(--ink);
  margin-bottom: 2mm;
}
figure.ph .ph-note{
  font-size: 8.4pt; color: var(--ink2); max-width: 120mm;
  margin: 0 auto; line-height: 1.4;
}

/* --- blockquotes (rarely used but needed for completeness) --- */
blockquote{
  border-left: 3pt solid var(--rule);
  padding: 1mm 4mm; margin: 0 0 4mm; color: var(--ink2); font-style: italic;
}

/* --- TOC row layout with title + dots --- */
.toc li .ti{ font-family:'Google Sans Text'; color:var(--ink); }

/* --- References: tighter list spacing, code-font-friendly links --- */
section:last-of-type ul li{ margin-bottom: 1.2mm; font-size: 8.8pt; }
section a{ color: var(--accent); text-decoration: none; word-break: break-word; }
section a:hover{ text-decoration: underline; }

/* --- pretty ordered/unordered numbering that survives nesting --- */
li li::before{ opacity:.75; }

/* --- avoid content pressing against the folio; keep last line breathable --- */
section > *:last-child{ margin-bottom: 6mm; }

/* --- ensure the section-number badge and title stay together --- */
h2.sec{ page-break-after: avoid; }

/* --- widow / orphan control on prose and lists ---
   Chrome's paged-media widow / orphan support is partial but honoured
   inside block containers; combined with per-item break-inside it
   materially reduces stray single lines at page bottoms/tops. */
p{ orphans: 3; widows: 3; }
ul, ol{ orphans: 2; widows: 2; }
ul > li, ol > li{ break-inside: avoid; page-break-inside: avoid; }
/* Keep the LAST item of a short list glued to its predecessor so a
   1-line trailing item cannot be stranded on the next page. */
ol > li:last-child, ul > li:last-child{
  break-before: avoid; page-break-before: avoid;
}
/* Keep short lists whole where they fit; long lists (e.g. references)
   fall back to normal flow because they cannot fit on one page. */
ol, ul{ break-inside: auto; }
"""


# =============================================================================
# HTML assembly
# =============================================================================


def rewrite_css_paths(css_text: str, css_dir: Path) -> str:
    """Rewrite url('assets/...') references in the CSS to absolute file://
    URLs so the HTML file can live outside the toolkit directory."""

    def _sub(m: re.Match) -> str:
        raw = m.group(1).strip().strip("'\"")
        if raw.startswith(("http://", "https://", "data:", "file://", "/")):
            return m.group(0)
        abs_path = (css_dir / raw).resolve()
        return f"url('file://{abs_path}')"

    return re.sub(r"url\(([^)]+)\)", _sub, css_text)


def build_html(
    md_path: Path,
    css_path: Path,
    figures_dir: Path,
    out_html: Path,
) -> Tuple[str, List[str], List[str]]:
    """Render the full HTML document. Returns (html_string, present_figs,
    missing_figs) for reporting."""
    md_text = md_path.read_text(encoding="utf-8")
    fm, body_md = parse_front_matter(md_text)

    blocks = parse_blocks(body_md)

    # Track figure presence for the build report.
    present: List[str] = []
    missing: List[str] = []
    for b in blocks:
        if b["type"] == "figure":
            f = figures_dir / b["filename"]
            (present if f.exists() else missing).append(b["filename"])

    body_html, section_titles = render_body(blocks, figures_dir)

    css_text = css_path.read_text(encoding="utf-8")
    css_text = rewrite_css_paths(css_text, css_path.parent)

    # Belt-and-braces: inject the doctitle as a literal string into the
    # @top-left rule so Chrome renders the running header even when
    # `string(doctitle)` fails to propagate across the named `@page cover`
    # context. We keep the string(section) reference intact so section
    # titles still update per-section on the top-right.
    # Headless Chrome does not reliably resolve `string(section)` in
    # @top-right, and `string(doctitle)` set on the cover does not carry
    # into subsequent named-page contexts. We override both margin boxes
    # with literal strings derived from front-matter so the running header
    # never comes out blank in the PDF.
    def _esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    doctitle_literal = _esc(fm.get("title", ""))
    # Prefer an explicit `header_right` if the author provided one;
    # otherwise fall back to the date, then to the confidentiality string.
    header_right = fm.get("header_right") or fm.get("date") or fm.get(
        "confidentiality", ""
    )
    header_right_literal = _esc(header_right)
    header_override_css = (
        "@page{"
        "@top-left{"
        f'content:"{doctitle_literal}";'
        "font-family:'Google Sans Text';font-size:7.5pt;color:#5F6368;}"
        "@top-right{"
        f'content:"{header_right_literal}";'
        "font-family:'Google Sans Text';font-size:7.5pt;color:#5F6368;}"
        "}"
    )
    css_text = css_text + "\n" + header_override_css

    # Locate the bundled brand assets. In the shipped skill layout
    # (assets/html/techdoc.css + assets/brand/, assets/fonts/), the assets
    # root is the CSS file's grandparent. Fall back to sibling `assets/`
    # for standalone toolkit layouts where the CSS lives at the toolkit root.
    _css_parent = css_path.parent
    if (_css_parent.parent / "brand").is_dir():
        assets_root = _css_parent.parent
    elif (_css_parent / "assets").is_dir():
        assets_root = _css_parent / "assets"
    else:
        assets_root = _css_parent.parent
    cover_html = render_cover(fm, assets_root)
    toc_html = render_toc(section_titles)

    title = fm.get("title", "Untitled")

    html_out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<style>{css_text}
{_EXTRA_CSS}
</style>
</head>
<body>
{cover_html}
{toc_html}
{body_html}
</body>
</html>
"""
    out_html.write_text(html_out, encoding="utf-8")
    return html_out, present, missing


# =============================================================================
# Chrome invocation
# =============================================================================


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Invoke headless Chrome to print the HTML file to PDF."""
    chrome = "/opt/google/chrome/chrome"
    if not os.path.exists(chrome):
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        if chrome is None:
            raise RuntimeError("Cannot find a Chrome executable.")

    with tempfile.TemporaryDirectory(prefix="chrome-techdoc-") as udd:
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={pdf_path.resolve()}",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=30000",
            f"--user-data-dir={udd}",
            f"file://{html_path.resolve()}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            raise RuntimeError(f"Chrome exited with code {proc.returncode}")


def optimise_pdf(pdf_path: Path) -> Optional[int]:
    """Downsample embedded images with Ghostscript. Chrome embeds raster
    figures at their source resolution which can make the PDF hundreds of
    megabytes when the source PNGs are large — unacceptable for
    distribution. Ghostscript's /printer profile downsamples colour
    images to 200 dpi (well above print quality at A4 figure sizes)
    while preserving the CID TrueType font streams intact.

    Skipped silently if `gs` is not on PATH. Returns the new byte size,
    or None when the optimisation was skipped or failed."""
    gs = shutil.which("gs")
    if gs is None:
        return None
    tmp_out = pdf_path.with_suffix(".opt.pdf")
    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        "-dPDFSETTINGS=/printer",
        "-dDownsampleColorImages=true",
        "-dColorImageResolution=200",
        "-dDownsampleGrayImages=true",
        "-dGrayImageResolution=200",
        "-dDownsampleMonoImages=true",
        "-dMonoImageResolution=600",
        "-dEmbedAllFonts=true",
        "-dSubsetFonts=true",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={tmp_out}", str(pdf_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0 or not tmp_out.exists():
        return None
    # Atomic swap.
    tmp_out.replace(pdf_path)
    return pdf_path.stat().st_size


# =============================================================================
# Entry point
# =============================================================================


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md", required=True, type=Path)
    ap.add_argument("--css", required=True, type=Path)
    ap.add_argument("--figures", required=True, type=Path)
    ap.add_argument("--out-html", required=True, type=Path)
    ap.add_argument("--out-pdf", required=True, type=Path)
    args = ap.parse_args()

    _, present, missing = build_html(
        args.md, args.css, args.figures, args.out_html
    )
    render_pdf(args.out_html, args.out_pdf)
    raw_size = args.out_pdf.stat().st_size
    opt_size = optimise_pdf(args.out_pdf)

    print(f"Wrote {args.out_html}")
    print(f"Wrote {args.out_pdf}")
    print(f"Figures present ({len(present)}): {', '.join(present) or '—'}")
    print(f"Figures placeheld ({len(missing)}): {', '.join(missing) or '—'}")
    if opt_size is not None:
        print(
            f"Ghostscript optimisation: "
            f"{raw_size / 1024 / 1024:.1f} MB -> "
            f"{opt_size / 1024 / 1024:.1f} MB"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
