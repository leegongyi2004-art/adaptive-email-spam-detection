#!/usr/bin/env python3
"""
make_paste_version.py
---------------------
Turns REPORT_FYP2.md (hard-wrapped Markdown) into a PASTE-FRIENDLY plain-text file
reports/paste/REPORT_FYP2_paste.txt that is easy to copy section-by-section into Word.

Properties of the output:
  * Each paragraph is ONE continuous line (no mid-sentence breaks).
  * Headings are kept on their own line and clearly labelled.
  * Tables are output as tab-separated rows -> in Word, paste and use
    Insert > Table > Convert Text to Table (separate at Tabs) to get a real table.
  * Figure markers become obvious  <<< FIGURE x.y: ... >>>  lines, each with the
    image file name right underneath so you know which PNG to insert.
  * List items each sit on their own line.
  * Markdown symbols (#, *, **, >, |, <!-- -->) are removed/cleaned.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "REPORT_FYP2.md")
OUT_DIR = os.path.join(HERE, "paste")
OUT = os.path.join(OUT_DIR, "REPORT_FYP2_paste.txt")

FIG_MAP = {
    "1.1": "fig1_1_spam_share.png",
    "1.2": "fig1_2_phishing_attacks.png",
    "1.3": "fig1_3_threat_stats.png",
    "2.1": "fig2_1_taxonomy.png",
    "2.2": "fig2_2_rule_based.png",
    "2.3": "fig2_3_content_statistical.png",
    "2.4": "fig2_4_metadata.png",
    "2.5": "fig2_5_hybrid_fusion.png",
    "3.1": "fig3_1_system_architecture.png",
    "3.2": "fig3_2_use_case.png",
    "3.3": "fig3_3_activity.png",
    "4.1": "fig4_1_block_diagram.png",
    "6.1": "fig6_1_confusion_matrix.png",
    "6.2": "fig6_2_roc.png",
    "6.3": "fig6_3_threshold_catch.png",
    "6.4": "fig6_4_adaptive_roc.png",
}


def clean(text):
    """Remove inline Markdown so it reads as plain text."""
    text = text.replace("**", "")
    text = text.replace("*", "")          # emphasis / italics
    text = text.replace("`", "")
    text = text.replace("[Online].", "[Online].")
    text = re.sub(r"\[([0-9]{1,2}(?:\]|,\s*\[?[0-9]{1,2})*)\]",
                  lambda m: "[" + m.group(1).replace("][", ", ").replace("[", "").replace("]", "") + "]",
                  text)
    text = text.replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    with open(SRC, encoding="utf-8") as f:
        lines = f.read().splitlines()

    blocks = []          # list of (kind, content)
    buf = []             # paragraph buffer (list of wrapped lines)
    in_comment = False

    def flush():
        nonlocal buf
        if buf:
            joined = clean(" ".join(buf))
            if joined:
                blocks.append(("p", joined))
            buf = []

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()

        # track HTML comment blocks (drop them)
        if "<!--" in s:
            in_comment = True
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if not s:
            flush()
            continue
        if s in ("---", "***", "___"):
            flush()
            blocks.append(("rule", ""))
            continue
        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            title = clean(s.lstrip("#").strip())
            blocks.append(("h", (level, title)))
            continue
        if s.startswith("|"):
            flush()
            blocks.append(("table_raw", s))
            continue
        if s.startswith(">"):
            # ready-made image note -> skip (image shown at figure marker instead)
            flush()
            continue
        if re.match(r"^[-*]\s+", s) or re.match(r"^\d+\.\s+", s):
            flush()
            blocks.append(("li", clean(re.sub(r"^([-*]|\d+\.)\s+", "", s))))
            continue
        if s.startswith("[FIGURE"):
            flush()
            blocks.append(("fig", clean(s)))
            continue
        if s.startswith("EQ#"):
            flush()
            blocks.append(("p", "    " + s[3:].strip()))
            continue
        # normal prose: accumulate wrapped lines
        buf.append(s)
    flush()

    # merge consecutive table_raw lines into tables
    out = []
    i = 0
    while i < len(blocks):
        kind, content = blocks[i]
        if kind == "table_raw":
            rows = []
            while i < len(blocks) and blocks[i][0] == "table_raw":
                row = blocks[i][1]
                cells = [c.strip() for c in row.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells):  # skip |---|
                    rows.append(cells)
                i += 1
            out.append(("table", rows))
            continue
        out.append((kind, content))
        i += 1

    # render
    r = []
    r.append("=" * 78)
    r.append("PASTE-FRIENDLY VERSION OF THE FYP2 REPORT")
    r.append("Copy one section at a time into your Word template.")
    r.append("- Plain paragraphs: paste directly.")
    r.append("- Tables: paste the tab-separated block, then in Word use")
    r.append("  Insert > Table > Convert Text to Table (separator: Tabs).")
    r.append("- <<< FIGURE ... >>> lines tell you where to insert a PNG; the file")
    r.append("  name is shown on the next line (images live in reports/figures/).")
    r.append("=" * 78)
    r.append("")

    for kind, content in out:
        if kind == "rule":
            r.append("")
            r.append("-" * 78)
            r.append("")
        elif kind == "h":
            level, title = content
            r.append("")
            if level == 1:
                r.append("#" * 78)
                r.append(">>> " + title.upper() + " <<<")
                r.append("#" * 78)
            else:
                r.append(("  " * (level - 2)) + "[" + title + "]")
            r.append("")
        elif kind == "p":
            r.append(content)
            r.append("")
        elif kind == "li":
            r.append("   - " + content)
        elif kind == "fig":
            m = re.search(r"FIGURE\s+([0-9]+\.[0-9]+)\s*[:\]]?\s*(.*)", content)
            num = m.group(1) if m else "?"
            cap = m.group(2).rstrip("]").strip() if m else content
            img = FIG_MAP.get(num, "reports/figures/fig" + num.replace(".", "_") + ".png")
            r.append("")
            r.append("<<<  FIGURE " + num + ": " + cap + "  >>>")
            r.append("     [insert image file: reports/figures/" + img + "]")
            r.append('     [Word caption: "Figure ' + num + " " + cap + '"]')
            r.append("")
        elif kind == "table":
            rows = content
            r.append("--- TABLE START (tab-separated -> Convert Text to Table) ---")
            for cells in rows:
                r.append("\t".join(clean(c) for c in cells))
            r.append("--- TABLE END ---")
            r.append("")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(r) + "\n")
    print("wrote", OUT)
    print("paragraphs/blocks rendered:", len(out))


if __name__ == "__main__":
    main()
