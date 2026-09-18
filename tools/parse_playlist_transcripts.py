#!/usr/bin/env python3
"""Parse all 16 playlist video .info.json and .vtt files into clean .txt files."""
import glob
import json
import os
import re

TDIR = "/usr/local/google/home/sanchitalekh/Code/pca-crash-course/data/reference/playlist_transcripts"


def clean_vtt(vtt_path):
    lines = []
    seen = set()
    with open(vtt_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if (
                not line
                or line.startswith("WEBVTT")
                or line.startswith("Kind:")
                or line.startswith("Language:")
                or "-->" in line
            ):
                continue
            line = re.sub(r"<[^>]+>", "", line).strip()
            if line and line not in seen:
                lines.append(line)
                seen.add(line)
    return "\n".join(lines)


def main():
    infos = sorted(glob.glob(f"{TDIR}/[0-9][0-9]_*.info.json"))
    total_chapters = 0
    for p in infos:
        base = os.path.basename(p).replace(".info.json", "")
        if base.startswith("00_"):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        chapters = d.get("chapters") or []
        total_chapters += len(chapters)
        vtts = sorted(glob.glob(f"{TDIR}/{base}*.vtt"))
        txt = clean_vtt(vtts[0]) if vtts else ""
        out_txt = f"{TDIR}/{base}.txt"
        title = d.get("title", "")
        vid = d.get("id", "")
        desc = d.get("description", "")
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {title}\nURL: https://www.youtube.com/watch?v={vid}\nDESCRIPTION:\n{desc}\n\nCHAPTERS:\n")
            for c in chapters:
                f.write(f"- [{c.get('start_time')}s] {c.get('title')}\n")
            f.write("\nTRANSCRIPT:\n" + txt + "\n")
        print(f"{base}: {len(chapters):2d} chapters | {len(txt.split()):5d} words | {title}")
    print(f"TOTAL CHAPTERS ACROSS 16 VIDEOS: {total_chapters}")


if __name__ == "__main__":
    main()
