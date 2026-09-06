"""Build a submission-ready Word (.docx) from REPORT_FYP2.md.

Produces REPORT_FYP2.docx with:
  * Times New Roman 12 pt body, 1.5 line spacing, UK English
  * real Word tables (all comparison/results tables included)
  * chapter headings (each chapter/back-matter section starts on a new page)
  * ready-made figures embedded automatically where the PNG exists
     (run reports/make_figures.py and reports/make_result_figures.py first)
  * [FILL IN] and [FIGURE ...] placeholders left visible for the student
  * code blocks in a monospace font; HTML comment instructions skipped

Usage (from the project root):
    python reports/build_docx.py
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "REPORT_FYP2.md"
OUT = ROOT / "REPORT_FYP2.docx"
FIGS = ROOT / "reports" / "figures"

FIG_MAP = {
    "FIGURE 2.1": "fig2_1_taxonomy.png",
    "FIGURE 2.2": "fig2_2_rule_based.png",
    "FIGURE 2.3": "fig2_3_content_statistical.png",
    "FIGURE 2.4": "fig2_4_metadata.png",
    "FIGURE 2.5": "fig2_5_hybrid_fusion.png",
    "FIGURE 3.1": "fig3_1_system_architecture.png",
    "FIGURE 3.2": "fig3_2_use_case.png",
    "FIGURE 3.3": "fig3_3_activity.png",
    "FIGURE 4.1": "fig4_1_block_diagram.png",
    "FIGURE 6.1": "fig6_1_confusion_matrix.png",
    "FIGURE 6.2": "fig6_2_roc.png",
    "FIGURE 6.3": "fig6_3_threshold_catch.png",
    "FIGURE 6.4": "fig6_4_adaptive_roc.png",
}

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*)")


def add_runs(par, text):
    """Add inline **bold** and *italic* runs to a paragraph."""
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = par.add_run(part[2:-2]); r.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = par.add_run(part[1:-1]); r.italic = True
        else:
            par.add_run(part)


def style_base(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(6)


def set_caption(par):
    for r in par.runs:
        r.font.size = Pt(10.5)
        r.bold = True
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(4)


def add_image(doc, marker):
    key = marker[1:marker.index(":")].strip().upper()
    fname = FIG_MAP.get(key)
    if fname:
        path = FIGS / fname
        if path.exists():
            doc.add_picture(str(path), width=Inches(6.0))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap = marker.split(":", 1)[1].strip().rstrip("].")
            p = doc.add_paragraph(); add_runs(p, key.title() + " — " + cap); set_caption(p)
            return
    # no PNG yet -> placeholder
    p = doc.add_paragraph(); r = p.add_run("[" + marker[1:] if marker.startswith("[") else marker)
    r.italic = True
    for run in p.runs:
        run.font.color.rgb = None


def parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(cells)
        i += 1
    # drop the separator row (---|---)
    rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
    return rows, i


def add_table(doc, rows):
    ncol = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncol)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, r in enumerate(rows):
        for ci in range(ncol):
            txt = r[ci] if ci < len(r) else ""
            cell = table.cell(ri, ci)
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            par.paragraph_format.space_after = Pt(2)
            add_runs(par, txt)
            for run in par.runs:
                run.font.size = Pt(10.5)
                if ri == 0:
                    run.bold = True
    doc.add_paragraph()


def main():
    lines = MD.read_text(encoding="utf-8").splitlines()
    doc = Document()
    style_base(doc)

    i = 0
    in_code = False
    skip_comment = False
    while i < len(lines):
        line = lines[i]

        # HTML comments: <!-- ... -> ... -->  (possibly multi-line)
        if line.strip().startswith("<!--"):
            skip_comment = True
            if "-->" in line:
                skip_comment = False
            i += 1
            continue
        if skip_comment:
            if "-->" in line:
                skip_comment = False
            i += 1
            continue

        # code fences
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            p = doc.add_paragraph()
            r = p.add_run(line if line else " ")
            r.font.name = "Consolas"; r.font.size = Pt(9.5)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            p.paragraph_format.space_after = Pt(0)
            i += 1
            continue

        # table
        if line.strip().startswith("|"):
            rows, ni = parse_table(lines, i)
            add_table(doc, rows)
            i = ni
            continue

        # figure marker  [FIGURE X.Y: ...]
        if line.strip().startswith("[FIGURE"):
            add_image(doc, line.strip())
            i += 1
            continue

        # ready-made image blockquote  > **Ready-made image:** path
        if "Ready-made image" in line:
            i += 1
            continue
        if line.strip().startswith(">") and ("reports/figures" in line or "regenerate" in line):
            i += 1
            continue

        # horizontal rule
        if line.strip() == "---":
            i += 1
            continue

        # headings
        if line.startswith("#"):
            m = re.match(r"^(#+)\s+(.*)", line)
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1:
                doc.add_page_break()
                h = doc.add_heading(level=1)
            elif level == 2:
                h = doc.add_heading(level=2)
            else:
                h = doc.add_heading(level=min(level - 1, 4))
            run = h.add_run(text)
            run.font.name = "Times New Roman"
            i += 1
            continue

        # blank
        if not line.strip():
            i += 1
            continue

        # table caption  **Table X.Y — ...**
        if line.strip().startswith("**Table"):
            p = doc.add_paragraph(); add_runs(p, line.strip()); set_caption(p)
            i += 1
            continue

        # normal paragraph
        p = doc.add_paragraph(); add_runs(p, line.strip())
        i += 1

    doc.save(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
