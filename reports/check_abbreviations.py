"""Check the List of Abbreviations against the acronyms actually used in the report.

Run:
    python reports/check_abbreviations.py

It scans REPORT_FYP2.md for capitalised acronyms, compares them with the entries in
the LIST OF ABBREVIATIONS section, and prints:

  * MISSING  - used in the text but not listed (add these)
  * UNUSED   - listed but never used (consider removing)
  * where each missing acronym first appears, so it can be checked in context

Nothing is modified; the script only reports.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "REPORT_FYP2.md"

# Words that look like acronyms but are ordinary text, headings or labels.
IGNORE = {
    "A", "I", "THE", "AND", "OR", "OF", "IN", "TO", "FOR", "ON", "AT", "BY", "AS", "IS",
    "CHAPTER", "APPENDIX", "REFERENCES", "ABSTRACT", "LIST", "TABLE", "FIGURE", "FIGURES",
    "TABLES", "CONTENTS", "SYSTEM", "DESIGN", "REVIEW", "LITERATURE", "INTRODUCTION",
    "CONCLUSION", "RECOMMENDATION", "IMPLEMENTATION", "EVALUATION", "DISCUSSION",
    "METHODOLOGY", "SPECIFICATIONS", "ABBREVIATIONS", "SYMBOLS", "DECLARATION",
    "ACKNOWLEDGEMENTS", "COPYRIGHT", "TITLE", "PAGE", "UTAR", "FYP", "FYP1", "FYP2",
    "WORK", "DONE", "PROBLEMS", "ENCOUNTERED", "SELF", "EVALUATION", "STUDENT", "ID",
    "NOTE", "IMPORTANT", "RUNNING", "HEADER", "FOOTER", "FILL", "SPAM", "HAM", "URGENT",
    "BE", "NOT", "NO", "ALL", "ONLY", "ONE", "TWO", "SIX", "OK", "PM", "AM", "US", "UK",
}

# Acronyms that are standard enough to allow, even if they appear rarely.
ALWAYS_OK = {"CPU", "GPU", "RAM", "SSD", "CSV", "API", "URL", "HTTP", "HTTPS", "JSON"}


def load_report() -> str:
    if not REPORT.exists():
        raise SystemExit(f"Report not found: {REPORT}")
    return REPORT.read_text(encoding="utf-8")


def listed_abbreviations(text: str) -> dict[str, str]:
    """Parse the existing LIST OF ABBREVIATIONS section."""
    match = re.search(r"#\s*LIST OF ABBREVIATIONS(.*?)(?=\n#\s|\Z)", text, re.S)
    if not match:
        return {}
    entries = {}
    for line in match.group(1).splitlines():
        m = re.match(r"\s*-\s*([A-Za-z0-9\-]+)\s*[—–-]\s*(.+)", line)
        if m:
            entries[m.group(1).strip().upper()] = m.group(2).strip()
    return entries


def used_acronyms(text: str) -> dict[str, int]:
    """Find capitalised tokens that look like acronyms, with a first-line number."""
    body = re.sub(r"#\s*LIST OF ABBREVIATIONS.*?(?=\n#\s|\Z)", "", text, flags=re.S)
    # Drop the reference list, HTML comments and all heading lines: they are full of
    # capitalised words and venue names that are not abbreviations used in the prose.
    body = re.sub(r"#\s*REFERENCES.*?(?=\n#\s|\Z)", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    found: dict[str, int] = {}
    for i, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("|", ">", "```", "#", "-", "*", "[")):
            continue
        if "[FILL IN" in stripped or "[FIGURE" in stripped:
            continue
        line = re.sub(r"`[^`]*`", " ", line)          # inline code
        line = re.sub(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})+\b", " ", line)  # ALL-CAPS phrases
        for token in re.findall(r"\b([A-Z][A-Z0-9\-]{1,9})\b", line):
            token = token.strip("-")
            if len(token) < 2 or token in IGNORE:
                continue
            if token.isdigit():
                continue
            found.setdefault(token, i)
    return found


def main() -> None:
    text = load_report()
    listed = listed_abbreviations(text)
    used = used_acronyms(text)

    missing = {a: ln for a, ln in sorted(used.items()) if a not in listed}
    unused = sorted(a for a in listed if a not in used and a not in ALWAYS_OK)

    print("=" * 72)
    print(f"LIST OF ABBREVIATIONS CHECK  -  {len(listed)} entries listed")
    print("=" * 72)

    if missing:
        print(f"\nMISSING ({len(missing)}) - used in the text but not in the list:")
        for a, line in missing.items():
            print(f"  {a:<10} first used at line {line}")
        print("\n  Review these: genuine acronyms should be added to the list;")
        print("  ordinary capitalised words can be ignored.")
    else:
        print("\nMISSING: none - every acronym found in the text is listed.")

    if unused:
        print(f"\nUNUSED ({len(unused)}) - listed but not found in the text:")
        for a in unused:
            print(f"  {a:<10} {listed[a]}")
        print("\n  Consider removing these, or check they are spelled the same way.")
    else:
        print("\nUNUSED: none - every listed abbreviation appears in the text.")

    print("\n" + "=" * 72)
    print("Current list, alphabetically sorted and ready to paste:")
    print("=" * 72)
    for a in sorted(listed):
        print(f"{a}\t{listed[a]}")
    print()


if __name__ == "__main__":
    main()
