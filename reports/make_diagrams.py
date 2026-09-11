#!/usr/bin/env python3
"""
make_diagrams.py
----------------
Draws the professional engineering diagrams for the FYP2 report using matplotlib
shapes (no graphviz dependency):
  * fig3_1_system_architecture.png  - end-to-end data-flow + adaptation loop
  * fig3_2_use_case.png             - UML use-case diagram
  * fig3_3_activity.png             - UML activity diagram
  * fig4_1_block_diagram.png        - high-level five-block system block diagram

Labels are descriptive (no code identifiers) to match the report prose.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Polygon, Circle, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures")

BLUE_F, BLUE_E = "#D9E2F3", "#1F4E79"
ORG_F,  ORG_E  = "#FCE4D6", "#C55A11"
GRN_F,  GRN_E  = "#E2EFDA", "#548235"
GRY_F,  GRY_E  = "#F2F2F2", "#7F7F7F"
YEL_F,  YEL_E  = "#FFF2CC", "#BF9000"


def new_ax(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=BLUE_F, ec=BLUE_E, fs=11, bold=True, round_pad=0.08):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle=f"round,pad=0.02,rounding_size={round_pad}",
                       linewidth=1.8, edgecolor=ec, facecolor=fc)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#1a1a1a", wrap=True)


def arrow(ax, p1, p2, color=BLUE_E, lw=1.8, dashed=False, label=None, lx=0, ly=0, rad=0.0):
    ar = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16,
                         linewidth=lw, color=color,
                         linestyle=(0, (6, 4)) if dashed else "-",
                         connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(ar)
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + lx, (p1[1] + p2[1]) / 2 + ly
        ax.text(mx, my, label, ha="center", va="center", fontsize=9.5,
                color=color, style="italic", fontweight="bold")


def use_case(ax, x, y, w, h, text, fs=10.5):
    e = Ellipse((x, y), w, h, facecolor=BLUE_F, edgecolor=BLUE_E, linewidth=1.6)
    ax.add_patch(e)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color="#1a1a1a")


def actor(ax, x, y, label, scale=1.0):
    s = scale
    ax.add_patch(Circle((x, y + 0.55 * s), 0.18 * s, fill=False, edgecolor="black", lw=1.8))
    ax.plot([x, x], [y + 0.37 * s, y - 0.35 * s], color="black", lw=1.8)
    ax.plot([x - 0.35 * s, x + 0.35 * s], [y + 0.1 * s, y + 0.1 * s], color="black", lw=1.8)
    ax.plot([x, x - 0.3 * s], [y - 0.35 * s, y - 0.8 * s], color="black", lw=1.8)
    ax.plot([x, x + 0.3 * s], [y - 0.35 * s, y - 0.8 * s], color="black", lw=1.8)
    ax.text(x, y - 1.1 * s, label, ha="center", va="top", fontsize=10.5, fontweight="bold")


def diamond(ax, x, y, w, h, text, fs=9.5):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=YEL_F, edgecolor=YEL_E, linewidth=1.8))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold")


def start_node(ax, x, y, r=0.14):
    ax.add_patch(Circle((x, y), r, facecolor="black", edgecolor="black"))


def end_node(ax, x, y, r=0.16):
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor="black", lw=1.6))
    ax.add_patch(Circle((x, y), r * 0.55, facecolor="black", edgecolor="black"))


# =============================================================== Fig 3.1
def fig_3_1():
    fig, ax = new_ax(13, 9.5, (0, 14), (0, 10))
    cx = 4.8
    # main flow
    box(ax, cx, 9.3, 6.0, 0.85, "Email input\nmessage / service request / watched folder", GRN_F, GRN_E, 10)
    box(ax, cx, 8.1, 6.0, 0.8, "Email parsing (RFC 5322)\nheaders, subject, body and attachments", BLUE_F, BLUE_E, 10)
    arrow(ax, (cx, 8.87), (cx, 8.5))

    # three feature branches
    ys = 6.9
    box(ax, 1.8, ys, 2.9, 1.0, "Word content features\n(TF-IDF: 1-2 word\nn-grams)", ORG_F, ORG_E, 9)
    box(ax, cx, ys, 2.9, 1.0, "Character content\nfeatures (TF-IDF:\n3-5 char. n-grams)", ORG_F, ORG_E, 9)
    box(ax, 7.8, ys, 2.9, 1.0, "Structural metadata\n(13 signals: links,\nsender auth., urgency)", ORG_F, ORG_E, 9)
    arrow(ax, (cx, 7.7), (1.8, 7.4))
    arrow(ax, (cx, 7.7), (cx, 7.4))
    arrow(ax, (cx, 7.7), (7.8, 7.4))

    box(ax, cx, 5.6, 5.6, 0.7, "Feature fusion and scaling", BLUE_F, BLUE_E, 11)
    arrow(ax, (1.8, 6.4), (cx - 1.8, 5.95))
    arrow(ax, (cx, 6.4), (cx, 5.95))
    arrow(ax, (7.8, 6.4), (cx + 1.8, 5.95))

    box(ax, cx, 4.4, 5.8, 0.85, "Classifier: class-balanced logistic regression\n(Naive Bayes and linear SVM also evaluated)", BLUE_F, BLUE_E, 9.5)
    arrow(ax, (cx, 5.25), (cx, 4.83))

    box(ax, cx, 3.2, 5.6, 0.7, "Spam probability and fired signals", GRN_F, GRN_E, 10)
    arrow(ax, (cx, 3.97), (cx, 3.55))

    box(ax, cx, 2.1, 5.6, 0.7, "Threshold decision: spam or legitimate", GRN_F, GRN_E, 10)
    arrow(ax, (cx, 2.85), (cx, 2.45))

    box(ax, cx, 1.0, 5.6, 0.7, "Action: deliver to inbox or quarantine", GRN_F, GRN_E, 10)
    arrow(ax, (cx, 1.75), (cx, 1.35))

    # adaptation panel (right)
    px = 11.7
    box(ax, px, 3.2, 3.4, 0.9, "Review console:\nhuman confirms or corrects", GRY_F, GRY_E, 9)
    box(ax, px, 2.1, 3.4, 0.75, "Feedback store\n(labelled corrections)", GRY_F, GRY_E, 9)
    box(ax, px, 1.0, 3.4, 0.9, "Scheduled retrain,\nvalidate and redeploy", GRY_F, GRY_E, 9)
    arrow(ax, (cx + 2.8, 2.1), (px - 1.7, 2.1), color=GRY_E)
    arrow(ax, (px, 2.75), (px, 2.48), color=GRY_E)
    arrow(ax, (px, 1.72), (px, 1.45), color=GRY_E)
    # redeploy feedback loop back to classifier (routed on far right)
    arrow(ax, (px + 1.4, 1.45), (13.3, 1.45), color=GRN_E, dashed=True)
    arrow(ax, (13.3, 1.45), (13.3, 4.4), color=GRN_E, dashed=True)
    arrow(ax, (13.3, 4.4), (cx + 2.9, 4.4), color=GRN_E, dashed=True, label="redeploy updated model", lx=0, ly=0.3)

    fig.savefig(os.path.join(OUT, "fig3_1_system_architecture.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# =============================================================== Fig 3.2
def fig_3_2():
    fig, ax = new_ax(10, 8.8, (0, 10), (0, 10))
    # system boundary
    ax.add_patch(Rectangle((3.2, 0.35), 6.4, 9.1, fill=False, edgecolor="black", linewidth=1.6))
    ax.text(6.4, 9.15, "Adaptive Spam Detection System", ha="center", va="center",
            fontsize=11, fontweight="bold")

    ucs = [
        (6.9, 8.3, 3.2, 0.85, "Submit email for scoring"),
        (6.9, 7.1, 3.2, 0.85, "View prediction and fired signals"),
        (6.9, 5.9, 3.2, 0.95, "Correct a misclassification\n(provide feedback)"),
        (6.9, 4.7, 3.2, 0.85, "Train and evaluate models"),
        (6.9, 3.5, 3.2, 0.85, "Run the detection service"),
        (6.9, 2.3, 3.2, 0.85, "Scan mailbox and quarantine"),
        (6.9, 1.1, 3.2, 0.9, "Review feedback and retrain"),
    ]
    for (x, y, w, h, t) in ucs:
        use_case(ax, x, y, w, h, t)

    actor(ax, 1.3, 5.0, "Reviewer /\nAdministrator", scale=1.25)
    for (x, y, w, h, t) in ucs:
        ax.plot([1.65, x - w / 2], [5.0, y], color="black", linewidth=1.0)

    fig.savefig(os.path.join(OUT, "fig3_2_use_case.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# =============================================================== Fig 3.3
def fig_3_3():
    fig, ax = new_ax(11, 11, (0, 11), (0, 12))
    cx = 4.6
    start_node(ax, cx, 11.4)
    box(ax, cx, 10.7, 5.0, 0.6, "Email enters system (console / service / mailbox)", BLUE_F, BLUE_E, 9.5)
    arrow(ax, (cx, 11.26), (cx, 11.0))
    box(ax, cx, 9.8, 5.2, 0.7, "Parse email; extract content\nand 13 metadata signals", BLUE_F, BLUE_E, 9.5)
    arrow(ax, (cx, 10.4), (cx, 10.1))
    box(ax, cx, 8.9, 5.0, 0.6, "Build fused content-metadata feature vector", BLUE_F, BLUE_E, 9.5)
    arrow(ax, (cx, 9.5), (cx, 9.2))
    box(ax, cx, 8.0, 5.0, 0.6, "Classifier produces a spam probability", BLUE_F, BLUE_E, 9.5)
    arrow(ax, (cx, 8.6), (cx, 8.3))

    diamond(ax, cx, 6.9, 2.8, 1.1, "Probability\n>= threshold ?", 9.5)
    arrow(ax, (cx, 7.7), (cx, 7.45))

    box(ax, 1.8, 6.9, 2.6, 0.75, "Label legitimate", GRN_F, GRN_E, 9.5)
    box(ax, 7.7, 6.9, 2.6, 0.75, "Label spam", ORG_F, ORG_E, 9.5)
    arrow(ax, (cx - 1.4, 6.9), (3.1, 6.9), label="No", ly=0.28)
    arrow(ax, (cx + 1.4, 6.9), (6.4, 6.9), label="Yes", ly=0.28)

    box(ax, 1.8, 5.8, 2.6, 0.7, "Deliver to inbox", GRN_F, GRN_E, 9.5)
    box(ax, 7.7, 5.8, 2.6, 0.7, "Quarantine message", ORG_F, ORG_E, 9.5)
    arrow(ax, (1.8, 6.52), (1.8, 6.15))
    arrow(ax, (7.7, 6.52), (7.7, 6.15))

    box(ax, cx, 4.7, 5.2, 0.7, "Log decision to the review queue", GRY_F, GRY_E, 9.5)
    arrow(ax, (1.8, 5.45), (cx - 1.7, 5.0), color=GRY_E)
    arrow(ax, (7.7, 5.45), (cx + 1.7, 5.0), color=GRY_E)

    diamond(ax, cx, 3.5, 2.8, 1.1, "Reviewer\ncorrects it ?", 9.5)
    arrow(ax, (cx, 4.35), (cx, 4.05))

    # right-side feedback path, routed on the far right to avoid the action boxes
    box(ax, 8.2, 3.5, 2.7, 0.85, "Save correction to\nfeedback store", GRY_F, GRY_E, 9)
    arrow(ax, (cx + 1.4, 3.5), (6.85, 3.5), label="Yes", ly=0.28)
    box(ax, 8.2, 2.1, 2.7, 0.9, "Retrain and validate;\nredeploy if improved", GRY_F, GRY_E, 9)
    arrow(ax, (8.2, 3.07), (8.2, 2.55), color=GRY_E)

    loop_x = 10.4
    arrow(ax, (9.55, 2.1), (loop_x, 2.1), color=GRN_E, dashed=True)
    arrow(ax, (loop_x, 2.1), (loop_x, 8.0), color=GRN_E, dashed=True)
    arrow(ax, (loop_x, 8.0), (cx + 2.5, 8.0), color=GRN_E, dashed=True, label="updated model", lx=-0.2, ly=0.3)

    end_node(ax, 1.8, 3.5)
    arrow(ax, (cx - 1.4, 3.5), (2.0, 3.5), label="No", ly=0.28)

    fig.savefig(os.path.join(OUT, "fig3_3_activity.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# =============================================================== Fig 4.1
def fig_4_1():
    fig, ax = new_ax(12, 7.5, (0, 12), (0, 8))
    # external inputs (left) and outputs (right)
    ax.text(1.0, 7.6, "External inputs", ha="center", fontsize=10, fontweight="bold", color=GRY_E)
    box(ax, 1.0, 6.7, 1.7, 0.7, "Emails\n(.eml / folder)", GRN_F, GRN_E, 9)
    box(ax, 1.0, 5.6, 1.7, 0.7, "Service / console\nrequests", GRN_F, GRN_E, 9)
    box(ax, 1.0, 1.4, 1.7, 0.8, "Reviewer\ncorrections", GRY_F, GRY_E, 9)

    # five blocks
    bx = [3.6, 5.9, 8.2, 10.5]
    box(ax, 3.6, 6.0, 2.0, 1.0, "1. Ingestion\n(console, service,\nmail watcher)", BLUE_F, BLUE_E, 9)
    box(ax, 6.0, 6.0, 2.0, 1.0, "2. Parsing &\nfeature extraction\n(content + metadata)", BLUE_F, BLUE_E, 9)
    box(ax, 8.4, 6.0, 2.0, 1.0, "3. Fusion\nclassifier\n(LR; NB/SVM)", BLUE_F, BLUE_E, 9)
    box(ax, 10.8, 6.0, 2.0, 1.0, "4. Action &\ndecision\n(label / quarantine)", GRN_F, GRN_E, 9)

    box(ax, 8.4, 3.4, 4.4, 1.0, "5. Adaptation\nreview queue, feedback store,\nscheduled validated retraining", GRY_F, GRY_E, 9.5)

    # flow arrows inputs -> blocks
    arrow(ax, (1.85, 6.7), (2.6, 6.2))
    arrow(ax, (1.85, 5.6), (2.6, 5.9))
    for a, b in zip(bx[:-1], bx[1:]):
        arrow(ax, (a + 1.0, 6.0), (b - 1.0, 6.0))
    # decision -> adaptation
    arrow(ax, (10.0, 5.5), (9.2, 3.9), color=GRY_E)
    # reviewer corrections -> adaptation
    arrow(ax, (1.85, 1.5), (6.2, 3.2), color=GRY_E)
    # adaptation -> classifier (redeploy, dashed)
    arrow(ax, (7.6, 3.7), (8.2, 5.5), color=GRN_E, dashed=True, label="redeploy", lx=-0.5, ly=0.2)

    # outputs
    box(ax, 10.8, 1.4, 2.0, 0.8, "Delivered /\nquarantined mail", GRN_F, GRN_E, 9)
    arrow(ax, (10.8, 5.5), (10.8, 1.8), color=GRN_E)

    fig.savefig(os.path.join(OUT, "fig4_1_block_diagram.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_3_1()
    fig_3_2()
    fig_3_3()
    fig_4_1()
    print("diagrams written to", OUT)
