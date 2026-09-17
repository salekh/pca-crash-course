#!/usr/bin/env python3
"""
build_deck.py — compile an authoring Markdown file into a branded
AI Tech GTM Google Slides deck (batch op list for the gslides MCP `batch` tool).

Outputs batch.json.  Canvas is 720x405 pt (16:9).
"""
import json, re, sys, pathlib

W, H = 720, 405
M = 46                      # side margin
FOOT_Y = 372

# ---- brand tokens (sampled from the template deck) -------------------------
LIGHT   = "#F8F9FA"
DARK    = "#202124"
ACCENT  = "#4471ED"
INK     = "#000000"
INK2    = "#5F6368"
ONDARK  = "#FFFFFF"
ONDARK2 = "#BABBBC"
GSANS   = "Google Sans"
GTEXT   = "Google Sans Text"

LOGO_URL = ("https://lh7-rt.googleusercontent.com/slidesz/AGV_vUdliC07B7nkkGK4s7Z2sWyRCGhvDRnu"
            "UUz4azLYpN1TkwpKcsB8K2kA_7sJ9otYmza5GsuCAW4oz5HVi8C6KJVAz-kkernga5m4rRZ8fzTfeqhuM5"
            "HPnoUAl6S1Wx8mhfT94KnB1vGGBRrynsrVphLaDXwDiY85N9ZJg1k19VWkRNbD8djF=s1024"
            "?key=InGD1-mP1xUXmMVM5NZrgQ")
GRAD_URL = ("https://lh7-rt.googleusercontent.com/slidesz/AGV_vUfpSSsHQK4mkxSPv8s3ORdBYxhl-x4v"
            "xliVPho1fhhWWOPzXa7XQha11ULjUE7TSqrw_144O6q7EjAd1gG2-fO3NVy0lsm9o8qWUDUPT4rNyh-MfG"
            "-vlzXgvHF-QiJy3e-cSntTMNB6kQ-L5_RakN4fOjavPhs9jNcW0tghl8ox7PH0k9Uw=s2048"
            "?key=InGD1-mP1xUXmMVM5NZrgQ")

ops = []
def slide(sid, bg=LIGHT):
    ops.append({"op": "add-slide", "id": sid})
    ops.append({"op": "set-background", "slide": sid, "color": bg})

def title_metrics(t, w=628):
    n = len(t or "")
    if n > 78:  return 15.5, 62
    if n > 56:  return 17.5, 52
    if n > 38:  return 19.0, 44
    return 21.0, 34

def tb(sid, text, x, y, w, h, size, color, font=GTEXT, bold=False,
       align="left", spacing=None):
    if text is None or not str(text).strip():
        return
    text = str(text)
    o = {"op": "add-textbox", "slide": sid, "text": text, "x": x, "y": y,
         "width": w, "height": h, "font_size": size, "color": color,
         "font_family": font, "alignment": align}
    if bold: o["bold"] = True
    if spacing: o["line_spacing"] = spacing*100 if spacing < 10 else spacing
    ops.append(o)

def shape(sid, x, y, w, h, fill, stype="RECTANGLE"):
    ops.append({"op": "add-shape", "slide": sid, "shape_type": stype,
                "x": x, "y": y, "width": w, "height": h, "background_color": fill})

def img(sid, url, x, y, w, h):
    ops.append({"op": "add-image", "slide": sid, "url": url,
                "x": x, "y": y, "width": w, "height": h})

def footer(sid, dark=False):
    img(sid, LOGO_URL, M, FOOT_Y, 20, 15)
    tb(sid, "Google Cloud  |  Proprietary & Confidential", W-300-M, FOOT_Y+3,
       300, 14, 7, ONDARK2 if dark else INK2, GTEXT, align="right")

def notes(sid, text):
    if text: ops.append({"op": "set-notes", "slide": sid, "text": text})

# ---------------------------------------------------------------- parsing --
def parse(md):
    fm = {}
    if md.startswith("---"):
        end = md.index("\n---", 3)
        for line in md[3:end].strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1); fm[k.strip()] = v.strip()
        md = md[end+4:]
    # split into blocks on headings
    slides, cur = [], None
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# ") and not ln.startswith("## "):
            if cur: slides.append(cur)
            cur = {"type": "divider", "title": ln[2:].strip(), "body": [], "notes": ""}
        elif ln.startswith("## "):
            if cur: slides.append(cur)
            cur = {"type": "content", "title": ln[3:].strip(), "body": [], "notes": ""}
        elif ln.startswith("> notes:"):
            if cur: cur["notes"] = ln[8:].strip()
        elif ln.startswith("::: ") or ln.startswith(":::"):
            name = ln[3:].strip().split()[0] if ln[3:].strip() else ""
            if name and name != "":
                blk, i = [], i+1
                while i < len(lines) and not lines[i].strip() == ":::":
                    blk.append(lines[i]); i += 1
                if cur is None:
                    cur = {"type": "content", "title": "", "body": [], "notes": ""}
                cur["body"].append({"directive": name, "raw": "\n".join(blk),
                                    "attrs": ln})
        elif ln.strip():
            if cur is None:
                cur = {"type": "lead", "title": "", "body": [], "notes": ""}
            cur["body"].append({"directive": "p", "raw": ln.strip()})
        i += 1
    if cur: slides.append(cur)
    return fm, slides

def attr(s, key):
    m = re.search(key + r'=["\']([^"\']*)["\']', s)
    return m.group(1) if m else ""

def wrap_est(text, chars):
    return max(1, -(-len(text)//chars))

# ------------------------------------------------------------------ build --
def build(fm, slides):
    n = 0
    # ---------- title ----------
    n += 1; sid = f"s{n}"
    slide(sid, DARK)
    img(sid, LOGO_URL, M, 52, 74, 56)
    tb(sid, fm.get("title",""), M, 138, 560, 96, 38, ONDARK, GSANS, bold=True, spacing=1.05)
    tb(sid, fm.get("subtitle",""), M, 246, 520, 46, 14, ONDARK2, GTEXT, spacing=1.35)
    tb(sid, f"{fm.get('author','')}  ·  Google Cloud", M, 306, 400, 16, 10, ONDARK, GTEXT)
    tb(sid, fm.get("date",""), M, 322, 400, 16, 9, ONDARK2, GTEXT)
    footer(sid, dark=True)

    for s in slides:
        title = s["title"]
        body  = s["body"]
        # ---------- divider ----------
        if s["type"] == "divider":
            n += 1; sid = f"s{n}"
            slide(sid, DARK)
            img(sid, LOGO_URL, W-210, 96, 168, 128)
            shape(sid, M, 150, 62, 4, ACCENT)
            tb(sid, title, M, 172, 420, 80, 34, ONDARK, GSANS, bold=True, spacing=1.08)
            notes(sid, s["notes"]); continue

        dirs = [b["directive"] for b in body]
        # ---------- agenda ----------
        if "agenda" in dirs:
            n += 1; sid = f"s{n}"; slide(sid)
            tb(sid, title or "Agenda", M, 46, 400, 34, 26, INK, GSANS, bold=True)
            items = re.findall(r'-\s*item:\s*(.+)', next(b["raw"] for b in body if b["directive"]=="agenda"))
            durs  = re.findall(r'duration:\s*(.+)', next(b["raw"] for b in body if b["directive"]=="agenda"))
            y = 100
            for k, it in enumerate(items):
                tb(sid, f"{k+1:02d}", M, y, 34, 20, 13, ACCENT, GSANS, bold=True)
                tb(sid, it.strip(), M+42, y, 430, 20, 12, INK, GTEXT)
                if k < len(durs):
                    tb(sid, durs[k].strip(), W-M-90, y+1, 90, 18, 9, INK2, GTEXT, align="right")
                shape(sid, M, y+24, W-2*M, 0.8, "#DADCE0")
                y += 40
            footer(sid); notes(sid, s["notes"]); continue

        # ---------- figure ----------
        if "figure" in dirs:
            b = next(x for x in body if x["directive"]=="figure")
            src = attr(b["attrs"], "src") or attr(b["raw"], "src")
            local = FIGMAP.get(pathlib.Path(src).name)
            n += 1; sid = f"s{n}"; slide(sid)
            ts, th_ = title_metrics(title)
            tb(sid, title, M, 30, W-2*M, th_, ts, INK, GSANS, bold=True, spacing=1.1)
            if local:
                iy = 30 + th_ + 8
                img(sid, local, M, iy, W-2*M, min(300, FOOT_Y-iy-10))
            lead = next((x["raw"] for x in body if x["directive"]=="p"), "")
            if lead and not local:
                tb(sid, lead, M, 90, W-2*M, 180, 12, INK2, GTEXT, spacing=1.4)
            footer(sid); notes(sid, s["notes"]); continue

        # ---------- cards ----------
        if "cards" in dirs:
            b = next(x for x in body if x["directive"]=="cards")
            titles = re.findall(r'-\s*title:\s*(.+)', b["raw"])
            bodies = re.findall(r'body:\s*(.+)', b["raw"])
            lead   = next((x["raw"] for x in body if x["directive"]=="p"), "")
            n += 1; sid = f"s{n}"; slide(sid)
            ts, th_ = title_metrics(title)
            tb(sid, title, M, 30, W-2*M, th_, ts, INK, GSANS, bold=True, spacing=1.1)
            ly = 30 + th_ + 6
            if lead:
                tb(sid, lead[:230], M, ly, W-2*M, 34, 9.5, INK2, GTEXT, spacing=1.35)
            k = len(titles) or 1
            gap, top = 12, ly + (40 if lead else 6)
            cw = (W-2*M-gap*(k-1))//k
            for j in range(k):
                x = M + j*(cw+gap)
                ch = FOOT_Y - top - 12
                shape(sid, x, top, cw, ch, "#FFFFFF")
                shape(sid, x, top, cw, 3, ACCENT)
                tb(sid, titles[j], x+12, top+14, cw-24, 34, 11.5, INK, GSANS, bold=True, spacing=1.15)
                if j < len(bodies):
                    tb(sid, bodies[j][:290], x+12, top+52, cw-24, ch-64, 8.5, INK2, GTEXT, spacing=1.35)
            footer(sid); notes(sid, s["notes"]); continue

        # ---------- stat ----------
        if "stat" in dirs:
            b = next(x for x in body if x["directive"]=="stat")
            val = attr(b["attrs"], "value"); unit = attr(b["attrs"], "unit")
            lab = attr(b["attrs"], "label")
            lead = next((x["raw"] for x in body if x["directive"]=="p"), "")
            n += 1; sid = f"s{n}"; slide(sid)
            ts, th_ = title_metrics(title)
            tb(sid, title, M, 34, W-2*M, th_, ts, INK, GSANS, bold=True, spacing=1.1)
            ly = 34 + th_ + 6
            if lead: tb(sid, lead[:260], M, ly, W-2*M, 42, 9.5, INK2, GTEXT, spacing=1.35)
            ry = ly + (50 if lead else 8)
            shape(sid, M, ry, W-2*M, 1.4, INK)
            vs = 42 if len(val) <= 4 else 28
            tb(sid, val, M, ry+16, 300, 56, vs, ACCENT, GSANS, bold=True)
            if unit: tb(sid, unit, M, ry+78, 300, 20, 10.5, INK2, GTEXT)
            tb(sid, lab, M+320, ry+18, W-2*M-320, FOOT_Y-ry-30, 10.5, INK, GTEXT, spacing=1.4)
            footer(sid); notes(sid, s["notes"]); continue

        # ---------- quote ----------
        if "quote" in dirs:
            b = next(x for x in body if x["directive"]=="quote")
            txt = b["raw"].strip()
            attrib = attr(b["attrs"], "attribution")
            n += 1; sid = f"s{n}"; slide(sid, DARK)
            tb(sid, txt[:300], M, 118, W-2*M-60, 130, 22, ONDARK, GSANS, bold=True, spacing=1.2)
            if attrib: tb(sid, attrib, M, 274, W-2*M, 20, 10, ONDARK2, GTEXT)
            footer(sid, dark=True); notes(sid, s["notes"]); continue

        # ---------- table ----------
        if "table" in dirs:
            b = next(x for x in body if x["directive"]=="table")
            rows = [r for r in b["raw"].splitlines() if r.strip() and not r.strip().startswith("columns")]
            rows = [r.split(",") for r in rows]
            rows = [r for r in rows if len(r) > 1][:8]
            lead = next((x["raw"] for x in body if x["directive"]=="p"), "")
            n += 1; sid = f"s{n}"; slide(sid)
            ts, th_ = title_metrics(title)
            ts = min(ts, 18)
            tb(sid, title, M, 26, W-2*M, th_, ts, INK, GSANS, bold=True, spacing=1.1)
            if lead: tb(sid, lead[:180], M, 26+th_+4, W-2*M, 26, 8.5, INK2, GTEXT, spacing=1.3)
            if rows:
                ncol = min(len(rows[0]), 4)
                tid = f"{sid}_t"
                ops.append({"op":"add-table","id":tid,"slide":sid,"rows":len(rows),"cols":ncol})
                for ri, r in enumerate(rows):
                    for ci in range(ncol):
                        val = r[ci].strip() if ci < len(r) else ""
                        ops.append({"op":"set-table-cell","table":tid,"row":ri,"col":ci,"text":(val[:150] or " ")})
                        ops.append({"op":"style-table-cell","table":tid,"row":ri,"col":ci,
                                    "font_size":7.5,"font_family":GTEXT,
                                    "background_color":"#E8F0FE" if ri==0 else "#FFFFFF",
                                    "bold": ri==0})
            footer(sid); notes(sid, s["notes"]); continue

        # ---------- default text slide ----------
        paras = [x["raw"] for x in body if x["directive"]=="p"]
        if not title and not paras: continue
        n += 1; sid = f"s{n}"; slide(sid)
        ts, th_ = title_metrics(title)
        tb(sid, title, M, 40, W-2*M, th_, ts, INK, GSANS, bold=True, spacing=1.12)
        by = 40 + th_ + 12
        if paras:
            tb(sid, "\n\n".join(paras)[:900], M, by, W-2*M, FOOT_Y-by-10, 10.5, INK2, GTEXT, spacing=1.45)
        footer(sid); notes(sid, s["notes"])

    # ---------- closing ----------
    n += 1; sid = f"s{n}"
    slide(sid, DARK)
    img(sid, LOGO_URL, W-230, 118, 180, 137)
    shape(sid, M, 150, 62, 4, ACCENT)
    tb(sid, "Thank you", M, 172, 430, 70, 40, ONDARK, GSANS, bold=True)
    tb(sid, f"{fm.get('author','')}  ·  Google Cloud", M, 232, 420, 18, 11, ONDARK, GTEXT)
    return n

FIGMAP = {}

if __name__ == "__main__":
    src = sys.argv[1]
    if len(sys.argv) > 2:
        FIGMAP = json.loads(sys.argv[2])
    fm, slides = parse(pathlib.Path(src).read_text())
    total = build(fm, slides)
    pathlib.Path("batch.json").write_text(json.dumps(ops, indent=1))
    print(f"slides={total}  ops={len(ops)}")
