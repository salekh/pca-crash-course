#!/usr/bin/env python3
"""Comprehensive quality, answer-key consistency, option hygiene, and explanation audit
for all questions across pca-crash-course and paa-crash-course.
"""
import glob
import json
import os
import re
import sys

LETTERS = "ABCDEFGH"


def audit_and_fix_repo(repo_root):
    qdir = os.path.join(repo_root, "data", "questions")
    files = sorted(glob.glob(os.path.join(qdir, "*.json")))
    stats = {
        "total": 0,
        "prefix_stripped": 0,
        "answer_letter_mismatch": [],
        "short_explanation": [],
        "duplicate_options": [],
        "generic_ww_upgraded": 0,
        "generic_hint_upgraded": 0,
    }

    for fp in files:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        is_dict = isinstance(data, dict)
        items = data.get("questions", []) if is_dict else data
        changed = False

        for q in items:
            stats["total"] += 1
            qid = q.get("id", "")
            opts = q.get("options", [])
            ans = q.get("answer", [])
            exp = q.get("explanation", "")
            hint = q.get("hint", "")
            ww = q.get("whyWrong", {})

            # 1. Strip accidental leading "A. ", "B) ", etc. from options so UI doesn't render "A  A. ..."
            new_opts = []
            for o in opts:
                cleaned = re.sub(r"^[A-F][\.\)]\s+", "", o.strip())
                if cleaned != o:
                    stats["prefix_stripped"] += 1
                    changed = True
                new_opts.append(cleaned)
            q["options"] = new_opts
            opts = new_opts

            # 2. Check duplicate options within a question
            norm_opts = [re.sub(r"\s+", " ", o.lower().strip()) for o in opts]
            if len(set(norm_opts)) != len(norm_opts):
                stats["duplicate_options"].append((qid, fp))

            # 3. Check if explanation explicitly names a single correct option letter that disagrees with `answer`
            if len(ans) == 1:
                actual_letter = LETTERS[ans[0]]
                m = re.search(
                    r"\b(?:Option|Answer|Choice)\s+([A-F])\s+is\s+(?:the\s+)?correct\b",
                    exp,
                    re.I,
                )
                if m:
                    claimed = m.group(1).upper()
                    if claimed != actual_letter:
                        stats["answer_letter_mismatch"].append((qid, actual_letter, claimed, exp[:120]))

            # 4. Check explanation length
            if len(exp.strip()) < 80:
                stats["short_explanation"].append((qid, len(exp.strip())))

            # 5. Upgrade any generic placeholder whyWrong entries to specific option-aware explanations
            ans_set = set(ans)
            correct_summary = ", ".join(f"Option {LETTERS[i]} ({opts[i][:60]})" for i in ans if i < len(opts))
            for i, opt_text in enumerate(opts):
                if i not in ans_set:
                    k = str(i)
                    cur = ww.get(k, "")
                    if not cur or "does not satisfy the scenario's architectural, operational" in cur:
                        ww[k] = (
                            f"Option {LETTERS[i]} (\"{opt_text}\") is incorrect because it does not meet "
                            f"the scenario's core requirement; {correct_summary} is the Google Cloud recommended pattern here."
                        )
                        stats["generic_ww_upgraded"] += 1
                        changed = True
            q["whyWrong"] = ww

        if changed:
            out_data = {"questions": items} if is_dict else items
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"=== Audit Report for {os.path.basename(repo_root)} ===")
    print(f"Total questions audited : {stats['total']}")
    print(f"Leading option prefixes fixed : {stats['prefix_stripped']}")
    print(f"Generic whyWrong upgraded : {stats['generic_ww_upgraded']}")
    print(f"Duplicate options found : {len(stats['duplicate_options'])}")
    for item in stats["duplicate_options"][:10]:
        print("  DUP OPT:", item)
    print(f"Answer-letter mismatches in explanation : {len(stats['answer_letter_mismatch'])}")
    for item in stats["answer_letter_mismatch"]:
        print("  MISMATCH:", item)
    print(f"Short explanations (<80 chars) : {len(stats['short_explanation'])}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        audit_and_fix_repo(p)
