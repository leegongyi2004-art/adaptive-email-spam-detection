#!/usr/bin/env python3
"""
make_changes_sheet.py
---------------------
Produces reports/paste/CHANGES_ONLY.txt - a paste-ready file containing ONLY the
sections that changed in the latest polishing round (the red and yellow items in
the change map), in chapter order. Each block is clearly labelled with the section
number and a short instruction, so the user can replace just that part of their
Word document without scrolling the full report.

Paragraphs are unwrapped to single lines; tables are emitted tab-separated
(Insert > Table > Convert Text to Table, separator: Tabs).
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "REPORT_FYP2.md")
OUT = os.path.join(HERE, "paste", "CHANGES_ONLY.txt")

sys.path.insert(0, HERE)
from make_paste_version import clean  # reuse the same text cleaner  # noqa: E402

# (banner title, start anchor, end anchor)  -- anchors match heading/substrings
BLOCKS = [
    ("FRONT MATTER - List of Figures (added Figures 1.2 and 1.3)",
        "# LIST OF FIGURES", "# LIST OF TABLES"),
    ("FRONT MATTER - List of Tables (renumbered 5.1/5.2/5.3)",
        "# LIST OF TABLES", "# LIST OF SYMBOLS"),
    ("CHAPTER 1 - opener (new Figures 1.2/1.3 + BEC/phishing/Verizon stats)",
        "# CHAPTER 1: INTRODUCTION", "## 1.1"),
    ("SECTION 1.1 - added citations [4][5][19]",
        "## 1.1 Problem Statement", "## 1.2"),
    ("REFERENCES - new entries [18] Kaspersky, [19] FBI IC3, [20] APWG",
        None, None),  # special-cased below
    ("SECTION 2.1.2 - removed 'also tested on Linux' claim (Windows 11 only)",
        "### 2.1.2 Firmware", "### 2.1.3"),
    ("SECTION 2.4 - 'Python virtual environment' wording",
        "## 2.4 Summary", "## 2.5"),
    ("SECTION 3.1 (use-case table) - generic service wording",
        "### 3.1.2 Use Case", "### 3.1.3"),
    ("SECTION 3.3 - added plain-English TF-IDF explanation",
        "## 3.3 Feature Extraction", "## 3.4"),
    ("SECTION 3.4 - added plain definitions of TP/FP/FN/TN and the metrics",
        "## 3.4 Evaluation Design", "## 3.5"),
    ("SECTION 4.1 - fixed broken sentence / removed code names",
        "## 4.1 System Block Diagram", "## 4.2"),
    ("SECTION 4.2 - RESTRUCTURED: overview Table 4.1 + new subsections 4.2.1-4.2.5",
        "## 4.2 System Components", "## 4.3"),
    ("SECTION 4.3 - Table 4.2 signals in plain English; code snippets removed",
        "## 4.3 Data and Feature Design", "## 4.4"),
    ("SECTION 4.4 - removed 'one-line commands' phrase",
        "## 4.4 System Components Interaction", "## 4.5"),
    ("CHAPTER 5 - opener + 5.1 Hardware + 5.2 Software + 5.3 Config + 5.4 Operation",
        "# CHAPTER 5: SYSTEM IMPLEMENTATION", "## 5.5"),
    ("CHAPTER 6 - new opener paragraph",
        "# CHAPTER 6: SYSTEM EVALUATION", "## 6.1"),
    ("SECTION 6.2.2 - classifier comparison rewritten as prose (no commands)",
        "### 6.2.2 Classifier", "### 6.2.3"),
    ("SECTION 6.2.4 - adaptive demonstration sentence fixed",
        "### 6.2.4 Adaptive", "## 6.3"),
    ("SECTION 6.4 - objectives table cells genericised",
        "## 6.4 Objectives Evaluation", "## 6.5"),
    ("CHAPTER 7 - new opener paragraph",
        "# CHAPTER 7: CONCLUSION", "## 7.1"),
    ("APPENDIX B - placeholder wording genericised",
        "## Appendix B", "## Appendix C"),
    ("APPENDIX D - NOW contains the full command reference",
        "## Appendix D", "## Appendix E"),
]


def slice_lines(lines, start, end):
    s = e = None
    for i, ln in enumerate(lines):
        if s is None and start in ln:
            s = i
        elif s is not None and end in ln:
            e = i
            break
    return lines[s:e] if s is not None and e is not None else []


def render(lines):
    out = []
    buf = []

    def flush():
        if buf:
            txt = clean(" ".join(buf))
            if txt:
                out.append(txt)
                out.append("")
            buf.clear()

    i = 0
    in_comment = False
    while i < len(lines):
        s = lines[i].strip()
        if "<!--" in s:
            in_comment = True
        if in_comment:
            if "-->" in s:
                in_comment = False
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        if s.startswith("#"):
            flush()
            out.append("[" + clean(s.lstrip("#").strip()) + "]")
            out.append("")
        elif s.startswith(">"):
            # drop build-note blockquotes
            pass
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells):
                    rows.append(cells)
                i += 1
            out.append("--- TABLE START (tab-separated -> Convert Text to Table) ---")
            for cells in rows:
                out.append("\t".join(clean(c) for c in cells))
            out.append("--- TABLE END ---")
            out.append("")
            continue
        elif s.startswith("[FIGURE"):
            flush()
            out.append("<<< " + clean(s).strip("[]") + " >>>")
            out.append("")
        elif s.startswith("```"):
            # code block: keep verbatim, fence to fence
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.extend(code)
            out.append("")
        else:
            buf.append(s)
        i += 1
    flush()
    return out


def references_block(lines):
    out = []
    grab = False
    for ln in lines:
        if re.match(r"^\[18\]", ln.strip()):
            grab = True
        if grab:
            if ln.strip().startswith("---"):
                break
            out.append(ln)
    # unwrap the three entries
    text = clean(" ".join(l.strip() for l in out if l.strip()))
    # split back into [18],[19],[20]
    parts = re.split(r"(?=\[(?:18|19|20)\])", text)
    res = []
    for p in parts:
        p = p.strip()
        if p:
            res.append(p)
            res.append("")
    return res


def main():
    with open(SRC, encoding="utf-8") as f:
        lines = f.read().splitlines()

    r = []
    r.append("=" * 78)
    r.append("CHANGES ONLY - paste-ready sections to replace in your Word document")
    r.append("Each block is labelled. Replace the matching section in your report.")
    r.append("Tables are tab-separated: paste, then Insert > Table > Convert Text")
    r.append("to Table (separator: Tabs). <<< FIGURE ... >>> = insert the PNG there.")
    r.append("Anything NOT listed here is unchanged - leave it as is.")
    r.append("=" * 78)

    for n, (title, start, end) in enumerate(BLOCKS, 1):
        r.append("")
        r.append("#" * 78)
        r.append(f"CHANGE {n} OF {len(BLOCKS)}:  {title}")
        r.append("#" * 78)
        r.append("")
        if start is None:
            r.extend(references_block(lines))
        else:
            r.extend(render(slice_lines(lines, start, end)))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(r) + "\n")
    print("wrote", OUT)
    print("blocks:", len(BLOCKS))


if __name__ == "__main__":
    main()
