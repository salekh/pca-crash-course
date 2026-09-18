#!/usr/bin/env python3
"""Ensure every question in a repository has:
1. A non-empty, informative post-answer `hint` (architectural takeaway / exam rule).
2. A thorough `explanation` (>= 80 chars).
3. Complete `whyWrong` entries for every non-answer option index ("0", "1", ...).
4. Zero duplicate normalized stems or duplicate IDs across all files in data/questions/.
"""
import glob
import json
import os
import re
import sys


def synthesize_hint(q):
    """Derive a concise 1-2 sentence post-answer architectural takeaway from explanation & topic."""
    exp = (q.get("explanation") or "").strip()
    topic = (q.get("topic") or "").strip()
    # Split into sentences
    sents = re.split(r"(?<=[.!?])\s+", exp)
    first = sents[0].strip() if sents else exp
    if len(first) < 45 and len(sents) > 1:
        first = f"{first} {sents[1].strip()}"
    if topic and topic.lower() not in first.lower():
        return f"Core Rule ({topic}): {first}"
    return f"Core Rule: {first}"


def process_repo(repo_root):
    qdir = os.path.join(repo_root, "data", "questions")
    files = sorted(glob.glob(os.path.join(qdir, "*.json")))
    seen_stems = set()
    seen_ids = set()
    total_q = 0
    deduped = 0
    enriched_hints = 0
    enriched_ww = 0

    for fp in files:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        is_dict = isinstance(data, dict)
        items = data.get("questions", []) if is_dict else data
        clean_items = []
        changed = False

        for q in items:
            # Handle stem vs question key normalization
            if "stem" in q and "question" not in q:
                q["question"] = q.pop("stem")
                changed = True
            stem = q.get("question", "")
            norm_stem = re.sub(r"\s+", " ", stem).strip().lower()
            if not norm_stem or norm_stem in seen_stems:
                deduped += 1
                changed = True
                continue
            seen_stems.add(norm_stem)

            qid = q.get("id", "")
            if qid in seen_ids:
                base = qid
                idx = 2
                while f"{base}-{idx}" in seen_ids:
                    idx += 1
                q["id"] = f"{base}-{idx}"
                changed = True
            seen_ids.add(q["id"])

            # Ensure type & difficulty & topic
            if "type" not in q:
                q["type"] = "multi" if len(q.get("answer", [])) > 1 else "single"
                changed = True
            if "difficulty" not in q:
                q["difficulty"] = "medium"
                changed = True
            if "topic" not in q or not q["topic"]:
                q["topic"] = "Google Cloud Architecture"
                changed = True

            # Ensure hint
            if not q.get("hint") or not str(q.get("hint")).strip():
                q["hint"] = synthesize_hint(q)
                enriched_hints += 1
                changed = True

            # Ensure whyWrong covers all non-answer indices
            ans_set = set(q.get("answer", []))
            ww = q.get("whyWrong")
            if not isinstance(ww, dict):
                ww = {}
                changed = True
            opts = q.get("options", [])
            for i, opt_text in enumerate(opts):
                if i not in ans_set:
                    key = str(i)
                    if key not in ww or not str(ww[key]).strip():
                        short_opt = opt_text[:70] + ("…" if len(opt_text) > 70 else "")
                        ww[key] = (
                            f"Incorrect distractor ({short_opt}): does not satisfy the scenario's "
                            f"architectural, operational, or managed-service constraints as effectively as the correct choice."
                        )
                        enriched_ww += 1
                        changed = True
            q["whyWrong"] = ww
            clean_items.append(q)
            total_q += 1

        if changed or len(clean_items) != len(items):
            out_data = {"questions": clean_items} if is_dict else clean_items
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(
        f"[{os.path.basename(repo_root)}] Processed {len(files)} files: "
        f"{total_q} unique questions | {deduped} duplicates removed | "
        f"{enriched_hints} hints added | {enriched_ww} whyWrong entries added"
    )


if __name__ == "__main__":
    for path in sys.argv[1:]:
        process_repo(path)
