"""
Generate the report figures (Figures 2.1, 3.1, 3.2, 3.3, 4.1) as PNG images.

Usage:
    python reports/make_figures.py

Outputs PNG files into reports/figures/. The diagrams are plain boxes-and-arrows in the
same style as past UTAR FICT FYP reports, so they can be inserted directly into the Word
template. Re-running the script overwrites the files.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#1f4e79"
LIGHT = "#dbe5f1"
GREEN = "#548235"
GREEN_LIGHT = "#e2efd9"
GREY = "#7f7f7f"
ORANGE = "#c55a11"
ORANGE_LIGHT = "#fbe5d6"


def box(ax, x, y, w, h, text, fc=LIGHT, ec=BLUE, fs=10.5, bold=False, tc="#1a1a1a"):
    """Draw a rounded box centred at (x, y) with width w and height h."""
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=1.6, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=tc, wrap=True)


def arrow(ax, p1, p2, color=BLUE, style="-|>", lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle=style, mutation_scale=14, linewidth=lw,
        color=color, linestyle=ls, shrinkA=2, shrinkB=2))


def new_ax(w=12, h=8):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", OUT / name)


# ---------------------------------------------------------------- Figure 2.1
def fig_2_1():
    fig, ax = new_ax(12, 8)
    weak_fc, weak_ec = "#f2dede", "#a94442"
    xs = [1.35, 3.65, 5.95, 8.25, 10.55]

    # Root
    box(ax, 6.0, 7.25, 5.6, 0.85, "Spam / Phishing Detection Approaches",
        fc=BLUE, ec=BLUE, bold=True, fs=12, tc="white")

    # Five family boxes
    fam = [
        ("1. Rule- / Keyword-\nBased (blacklists)", ORANGE_LIGHT, ORANGE),
        ("2. Content Statistical\n(TF-IDF + NB/SVM/LR)", LIGHT, BLUE),
        ("3. Metadata /\nReputation (headers)", LIGHT, BLUE),
        ("4. Hybrid / Fusion\n(content + metadata)", GREEN_LIGHT, GREEN),
        ("5. Commercial Cloud\n(Gmail, Defender)", LIGHT, GREY),
    ]
    for x, (t, fc, ec) in zip(xs, fam):
        box(ax, x, 5.55, 2.15, 1.05, t, fc=fc, ec=ec, bold=True, fs=9)
        arrow(ax, (6.0, 6.82), (x, 6.1), color=GREY)

    # Leaves under each family
    leaves = [
        ("Brittle; evaded by\nrewording; needs\nmanual upkeep", weak_fc, weak_ec),
        ("Ignores structure;\nweak on fluent,\nlink-less BEC", weak_fc, weak_ec),
        ("Weak alone (~93%\nin preliminary work);\nspoofed accounts", weak_fc, weak_ec),
        ("Most robust —\nthe basis of\nthis project", GREEN_LIGHT, GREEN),
        ("High block rate,\nbut proprietary;\nnot reproducible", LIGHT, GREY),
    ]
    for x, (t, fc, ec) in zip(xs, leaves):
        box(ax, x, 3.75, 2.15, 1.05, t, fc=fc, ec=ec, fs=8.5)
        arrow(ax, (x, 5.02), (x, 4.3), color=GREY)

    # Highlight: this project
    box(ax, 5.6, 1.7, 9.6, 1.25,
        "THIS PROJECT: content–metadata fusion (word + character TF-IDF, 12 metadata\n"
        "signals, logistic regression)  +  reviewed-feedback adaptive retraining\n"
        "local  ·  explainable  ·  runs on CPU  ·  reproducible",
        fc=GREEN_LIGHT, ec=GREEN, bold=True, fs=9.5)
    arrow(ax, (8.25, 3.22), (7.2, 2.35), color=GREEN, ls=(0, (4, 3)))

    ax.text(6.0, 0.4, "Figure 2.1 — Taxonomy of spam-detection approaches and the position of this project",
            ha="center", fontsize=10.5, fontweight="bold", color=BLUE)
    save(fig, "fig2_1_taxonomy.png")


# ---------------------------------------------------------------- Figure 3.1
def fig_3_1():
    fig, ax = new_ax(12, 9)
    cx = 4.6
    box(ax, cx, 8.4, 3.4, 0.7, "Data Input\n(.eml / API JSON / watched folder)", fc=GREEN_LIGHT, ec=GREEN, bold=True)
    box(ax, cx, 7.4, 3.4, 0.7, "Email Parsing (RFC 5322)", bold=True)

    # parallel feature extraction
    box(ax, 1.9, 6.0, 2.9, 0.8, "Word TF-IDF\n1–2 grams (40k)", fc=ORANGE_LIGHT, ec=ORANGE)
    box(ax, cx, 6.0, 2.9, 0.8, "Char TF-IDF\n3–5 grams (30k)", fc=ORANGE_LIGHT, ec=ORANGE)
    box(ax, 7.3, 6.0, 2.9, 0.8, "Metadata (12 signals)\nDictVectorizer", fc=ORANGE_LIGHT, ec=ORANGE)

    box(ax, cx, 4.7, 4.6, 0.8, "Feature Fusion  →  StandardScaler", bold=True)
    box(ax, cx, 3.6, 4.9, 0.9, "Class-balanced Logistic Regression\n(NB / Linear SVM compared)", fc=LIGHT, ec=BLUE, bold=True)
    box(ax, cx, 2.5, 4.6, 0.8, "Spam probability + fired signals", fc=GREEN_LIGHT, ec=GREEN)
    box(ax, cx, 1.5, 4.6, 0.8, "Threshold → Label / Quarantine", fc=GREEN_LIGHT, ec=GREEN, bold=True)

    # adaptation loop on the right
    box(ax, 9.9, 3.6, 3.2, 0.75, "Review queue\n& browser console", fc="#f2f2f2", ec=GREY)
    box(ax, 9.9, 2.5, 3.2, 0.75, "Feedback CSV", fc="#f2f2f2", ec=GREY)
    box(ax, 9.9, 1.4, 3.2, 0.8, "Scheduled retrain\n→ validate → redeploy", fc="#f2f2f2", ec=GREY, bold=True)

    arrow(ax, (cx, 8.05), (cx, 7.75))
    arrow(ax, (cx, 7.05), (1.9, 6.45))
    arrow(ax, (cx, 7.05), (cx, 6.45))
    arrow(ax, (cx, 7.05), (7.3, 6.45))
    arrow(ax, (1.9, 5.55), (cx - 1.6, 5.05))
    arrow(ax, (cx, 5.55), (cx, 5.1))
    arrow(ax, (7.3, 5.55), (cx + 1.6, 5.05))
    arrow(ax, (cx, 4.3), (cx, 4.05))
    arrow(ax, (cx, 3.15), (cx, 2.9))
    arrow(ax, (cx, 2.1), (cx, 1.9))
    # action -> review -> feedback -> retrain
    arrow(ax, (cx + 2.3, 1.5), (8.3, 3.6), color=GREY)
    arrow(ax, (9.9, 3.22), (9.9, 2.9), color=GREY)
    arrow(ax, (9.9, 2.12), (9.9, 1.8), color=GREY)
    # retrain feeds back to classifier
    arrow(ax, (8.3, 1.4), (7.1, 3.6), color=GREEN, ls=(0, (4, 3)))
    ax.text(7.0, 2.5, "redeploy\nmodel", fontsize=8.5, color=GREEN, ha="center", style="italic")

    save(fig, "fig3_1_system_architecture.png")


# ---------------------------------------------------------------- Figure 3.2
def fig_3_2():
    fig, ax = new_ax(12, 7)
    # actors (stick figures as boxes)
    box(ax, 1.6, 3.5, 2.2, 2.4, "REVIEWER /\nADMINISTRATOR", fc=GREEN_LIGHT, ec=GREEN, bold=True, fs=11)
    box(ax, 10.4, 3.5, 2.2, 2.4, "MAIL\nAUTOMATION", fc=ORANGE_LIGHT, ec=ORANGE, bold=True, fs=11)

    use = [
        (6.0, 6.1, "Submit email for scoring"),
        (6.0, 5.1, "View verdict & signals"),
        (6.0, 4.1, "Quarantine flagged mail"),
        (6.0, 3.1, "Correct misclassification"),
        (6.0, 2.1, "Retrain on feedback"),
        (6.0, 1.1, "Serve predictions (API)"),
    ]
    for x, y, t in use:
        box(ax, x, y, 3.6, 0.62, t, fc=LIGHT, ec=BLUE, fs=10)

    # reviewer associations
    for _, y, _ in use[:5]:
        arrow(ax, (2.7, y), (4.2, y), color=GREY)
    # automation association
    arrow(ax, (9.3, 1.1), (7.8, 1.1), color=GREY)

    ax.text(6.0, 6.85, "Use-Case Diagram", ha="center", fontsize=12, fontweight="bold", color=BLUE)
    save(fig, "fig3_2_use_case.png")


# ---------------------------------------------------------------- Figure 3.3
def fig_3_3():
    fig, ax = new_ax(11, 9)
    start = dict(fc=GREEN_LIGHT, ec=GREEN)
    proc = dict(fc=LIGHT, ec=BLUE)
    dec = dict(fc=ORANGE_LIGHT, ec=ORANGE)
    x = 3.4
    box(ax, x, 8.5, 2.6, 0.6, "Email arrives", **start, bold=True)
    box(ax, x, 7.6, 2.6, 0.6, "Parse & extract features", **proc)
    box(ax, x, 6.7, 2.6, 0.6, "Fuse & classify", **proc)
    box(ax, x, 5.6, 2.8, 0.8, "probability ≥\nthreshold ?", fc=dec["fc"], ec=dec["ec"], bold=True)

    box(ax, 7.3, 5.6, 2.6, 0.7, "Label SPAM\n/ quarantine", fc=GREEN_LIGHT, ec=GREEN)
    box(ax, x, 4.4, 2.6, 0.6, "Label HAM / deliver", fc=GREEN_LIGHT, ec=GREEN)

    box(ax, x, 3.3, 3.0, 0.7, "Log to review queue", fc="#f2f2f2", ec=GREY)
    box(ax, x, 2.3, 3.2, 0.7, "Reviewer corrects?", fc=ORANGE_LIGHT, ec=ORANGE)
    box(ax, 7.6, 2.3, 2.8, 0.7, "Append to feedback CSV", fc="#f2f2f2", ec=GREY)
    box(ax, 7.6, 1.2, 3.0, 0.8, "Retrain → validate\nmetrics kept?", fc=ORANGE_LIGHT, ec=ORANGE)
    box(ax, 3.6, 1.2, 2.8, 0.7, "Keep current model", fc="#f2f2f2", ec=GREY)
    box(ax, 10.7, 1.2, 1.9, 0.8, "Redeploy", fc=GREEN_LIGHT, ec=GREEN, bold=True)

    arrow(ax, (x, 8.2), (x, 7.9))
    arrow(ax, (x, 7.3), (x, 7.0))
    arrow(ax, (x, 6.4), (x, 6.0))
    arrow(ax, (x + 1.4, 5.6), (6.0, 5.6), color=ORANGE)
    ax.text(5.35, 5.85, "Yes", fontsize=9, color=ORANGE)
    arrow(ax, (x, 5.2), (x, 4.7), color=GREEN)
    ax.text(x - 0.5, 5.0, "No", fontsize=9, color=GREEN)
    arrow(ax, (7.3, 5.25), (5.0, 3.65), color=GREY)
    arrow(ax, (x, 4.1), (x, 3.65), color=GREY)
    arrow(ax, (x, 2.95), (x, 2.65))
    arrow(ax, (x + 1.6, 2.3), (6.2, 2.3), color=GREY)
    arrow(ax, (7.6, 1.95), (7.6, 1.6))
    arrow(ax, (6.1, 1.2), (5.0, 1.2), color=GREY)
    ax.text(6.3, 1.45, "No", fontsize=9, color=GREY)
    arrow(ax, (9.1, 1.2), (9.8, 1.2), color=GREEN)
    ax.text(9.35, 1.45, "Yes", fontsize=9, color=GREEN)
    # redeploy loops back to classify
    arrow(ax, (10.7, 1.6), (10.7, 6.7), color=GREEN, ls=(0, (4, 3)))
    arrow(ax, (10.7, 6.7), (4.7, 6.7), color=GREEN, ls=(0, (4, 3)))

    ax.text(x, 0.2, "Activity Diagram", ha="center", fontsize=12, fontweight="bold", color=BLUE)
    save(fig, "fig3_3_activity.png")


# ---------------------------------------------------------------- Figure 4.1
def fig_4_1():
    fig, ax = new_ax(12, 7)
    blocks = [
        (1.5, "1. INGESTION\nAPI / watcher / file", GREEN_LIGHT, GREEN),
        (4.0, "2. PARSING &\nFEATURE EXTRACTION", LIGHT, BLUE),
        (6.6, "3. FUSION CLASSIFIER\n(TF-IDF + metadata + LR)", LIGHT, BLUE),
        (9.2, "4. ACTION / DECISION\nlabel · quarantine · signals", ORANGE_LIGHT, ORANGE),
    ]
    for x, t, fc, ec in blocks:
        box(ax, x, 5.0, 2.2, 1.6, t, fc=fc, ec=ec, bold=True, fs=10)
    for x in (2.7, 5.3, 7.9):
        arrow(ax, (x, 5.0), (x + 0.45, 5.0))

    # adaptation block underneath
    box(ax, 6.6, 2.2, 7.4, 1.5,
        "5. ADAPTATION\nreview queue  →  feedback CSV  →  scheduled retrain  →  validate  →  redeploy",
        fc=GREEN_LIGHT, ec=GREEN, bold=True, fs=10)
    arrow(ax, (9.2, 4.2), (7.4, 2.95), color=GREY)
    arrow(ax, (5.8, 2.2), (6.6, 4.2), color=GREEN, ls=(0, (4, 3)))
    ax.text(5.4, 3.3, "redeploy\nmodel", fontsize=9, color=GREEN, ha="center", style="italic")

    ax.text(6.0, 6.5, "System Block Diagram", ha="center", fontsize=12, fontweight="bold", color=BLUE)
    save(fig, "fig4_1_block_diagram.png")


if __name__ == "__main__":
    fig_2_1()
    fig_3_1()
    fig_3_2()
    fig_3_3()
    fig_4_1()
    print("All figures generated in", OUT)
