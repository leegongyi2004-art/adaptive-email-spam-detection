"""Generate the FYP2 A4 poster (sparse two-column layout, UTAR logo)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.image as mpimg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "reports" / "figures"
ASSETS = ROOT / "reports" / "assets"
OUT = ROOT / "reports" / "poster"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#1b1b52"
BLUE = "#1f5f8b"
ACCENT = "#f2b705"
TEXT = "#1a1a1a"
BORDER = "#d3dae2"

plt.rcParams["font.family"] = "DejaVu Sans"

W, H = 8.27, 11.69
fig = plt.figure(figsize=(W, H), dpi=200)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def panel(x, y, w, h, fc="white", ec=BORDER):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0,rounding_size=0.7",
                                facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=1))


def head(x, y, w, label):
    ax.add_patch(Rectangle((x, y), w, 3.0, facecolor=NAVY, edgecolor="none", zorder=3))
    ax.add_patch(Rectangle((x, y), 1.1, 3.0, facecolor=ACCENT, edgecolor="none", zorder=4))
    ax.text(x + 2.4, y + 1.5, label.upper(), va="center", ha="left",
            fontsize=13, color="white", fontweight="bold", zorder=5)


def body(x, y, s, size=9.5, w="normal", color=TEXT, ha="left"):
    ax.text(x, y, s, va="top", ha=ha, fontsize=size, color=color, fontweight=w,
            zorder=4, linespacing=1.6)


# ---------------------------------------------------------------- header
ax.add_patch(Rectangle((0, 87.5), 100, 12.5, facecolor=NAVY, edgecolor="none", zorder=2))
ax.add_patch(Rectangle((0, 86.8), 100, 0.7, facecolor=ACCENT, edgecolor="none", zorder=2))

logo = ASSETS / "utar_logo.png"
if logo.exists():
    im = mpimg.imread(logo)
    lw = 16.0
    lh = lw * im.shape[0] / im.shape[1] * (W / H)
    axl = fig.add_axes([3.0 / 100, (91.8 - lh / 2) / 100, lw / 100, lh / 100], zorder=6)
    axl.imshow(im)
    axl.axis("off")

ax.text(59, 95.8, "Adaptive Email Spam Detection Using",
        ha="center", va="center", fontsize=17, color="white", fontweight="bold", zorder=4)
ax.text(59, 92.8, "AI and Content\u2013Metadata Fusion",
        ha="center", va="center", fontsize=17, color="white", fontweight="bold", zorder=4)
ax.text(59, 89.8, "Lee Gong Yi   \u00b7   Supervisor: Dr. Abdulrahman Aminu Ghali",
        ha="center", va="center", fontsize=10, color="#cbd4e8", zorder=4)
ax.text(59, 88.3, "Faculty of Information and Communication Technology, UTAR",
        ha="center", va="center", fontsize=8, color="#9aa7c4", zorder=4)

M = 4.0
CW = 100 - 2 * M
GAP = 1.6
COLGAP = 2.2
HALF = (CW - COLGAP) / 2
LX = M
RX = M + HALF + COLGAP

TOP = 85.5

# ============================================================ LEFT COLUMN
y = TOP
h = 20.0
panel(LX, y - h, HALF, h)
head(LX, y - 3.0, HALF, "Introduction")
body(LX + 2.2, y - 5.0,
     "Phishing is the most common entry\n"
     "point for cyber intrusion, and large\n"
     "language models now write fluent\n"
     "phishing mail at scale.\n\n"
     "Filters reading only words let clean\n"
     "phishing through. Filters reading only\n"
     "headers miss valid-looking senders.", 9.2)

y -= h + GAP
h = 18.0
panel(LX, y - h, HALF, h)
head(LX, y - 3.0, HALF, "Objectives")
oy = y - 5.2
for i, o in enumerate([
        "Combine content with metadata.",
        "Compare models, select best fusion.",
        "Evaluate on AI-generated phishing.",
        "Measure the adaptation loop."], 1):
    ax.add_patch(plt.Circle((LX + 3.0, oy - 0.65), 1.15, facecolor=ACCENT,
                            edgecolor="none", zorder=4))
    ax.text(LX + 3.0, oy - 0.65, str(i), ha="center", va="center",
            fontsize=8, color=NAVY, fontweight="bold", zorder=5)
    body(LX + 5.4, oy, o, 9.2)
    oy -= 2.9

y -= h + GAP
h = 38.6
panel(LX, y - h, HALF, h)
head(LX, y - 3.0, HALF, "Methods")

arch = FIGS / "fig3_1_system_architecture.png"
if arch.exists():
    im = mpimg.imread(arch)
    iw = 29.0
    ih = iw * im.shape[0] / im.shape[1] * (W / H)
    axi = fig.add_axes([(LX + (HALF - iw) / 2) / 100, (y - 4.4 - ih) / 100,
                        iw / 100, ih / 100], zorder=6)
    axi.imshow(im)
    axi.axis("off")
    ny = y - 5.8 - ih
else:
    ny = y - 5.0

body(LX + 2.2, ny,
     "Word and character TF-IDF plus 13\n"
     "structural metadata signals: links,\n"
     "domain mismatch, SPF, DKIM,\n"
     "urgency terms.\n\n"
     "Fused, then classified by balanced\n"
     "logistic regression at 0.55.\n\n"
     "Reviewer corrections feed gated\n"
     "batch retraining.", 9.2)

# ============================================================ RIGHT COLUMN
y = TOP
h = 31.0
panel(RX, y - h, HALF, h)
head(RX, y - 3.0, HALF, "Results")

ry = y - 5.2
for i, (k, v, b) in enumerate([("Accuracy", "99.2%", True),
                               ("False positives", "0.9%", True),
                               ("Speed (laptop CPU)", "13 ms", False),
                               ("AI phishing caught", "92%", True)]):
    if i % 2 == 0:
        ax.add_patch(Rectangle((RX + 1.4, ry - 2.0), HALF - 2.8, 3.1,
                               facecolor="#eef2f7", edgecolor="none", zorder=2))
    body(RX + 2.6, ry, k, 9.2)
    body(RX + HALF - 2.6, ry, v, 10.5 if b else 9.8, "bold",
         ACCENT if b else NAVY, ha="right")
    ry -= 3.2

cm = np.array([[9719, 90], [80, 10399]])
axc = fig.add_axes([(RX + 8.5) / 100, (y - 29.5) / 100, 24.0 / 100, 10.0 / 100],
                   zorder=6)
axc.imshow(cm, cmap="Blues", vmin=0, vmax=12000)
for (r, c), v in np.ndenumerate(cm):
    axc.text(c, r, f"{v:,}", ha="center", va="center", fontsize=8.5,
             fontweight="bold", color="white" if v > 6000 else TEXT)
axc.set_xticks([0, 1]); axc.set_xticklabels(["Ham", "Spam"], fontsize=6.5)
axc.set_yticks([0, 1]); axc.set_yticklabels(["Ham", "Spam"], fontsize=6.5)
axc.set_title("Confusion matrix (20,288 emails)", fontsize=7.5, color=BLUE,
              fontweight="bold", pad=4)
axc.tick_params(length=0)
for sp in axc.spines.values():
    sp.set_visible(False)

y -= h + GAP
h = 29.5
panel(RX, y - h, HALF, h)
head(RX, y - 3.0, HALF, "Discussion")
body(RX + 2.2, y - 5.0,
     "Fusion beat content alone. Metadata\n"
     "such as sender/link domain mismatch\n"
     "catches mail that reads perfectly but\n"
     "is structurally suspicious.\n\n"
     "Character n-grams resist obfuscation\n"
     "that defeats word-level features.\n\n"
     "The 92% catch rate came with no\n"
     "AI-written mail in training, so the\n"
     "gain is from fusion, not exposure.\n\n"
     "Retraining stays human-gated, which\n"
     "blocks label-flipping poisoning.", 9.2)

y -= h + GAP
h = 16.1
panel(RX, y - h, HALF, h, fc="#eef2f7", ec=NAVY)
head(RX, y - 3.0, HALF, "Conclusion")
body(RX + 2.2, y - 5.0,
     "An explainable detector reaching\n"
     "99.2% accuracy that generalises to\n"
     "AI-generated phishing it never saw\n"
     "in training, with a human-gated\n"
     "feedback loop. Runs on an ordinary\n"
     "laptop \u2014 no email leaves the machine.", 9.2)

# ---------------------------------------------------------------- footer
ax.add_patch(Rectangle((0, 0), 100, 2.0, facecolor=NAVY, edgecolor="none", zorder=2))
ax.text(50, 0.9, "Final Year Project 2  \u00b7  Universiti Tunku Abdul Rahman",
        ha="center", va="center", fontsize=7, color="#9aa7c4", zorder=4)

fig.savefig(OUT / "fyp2_poster.png", dpi=200, facecolor="white")
fig.savefig(OUT / "fyp2_poster.jpg", dpi=200, facecolor="white",
            pil_kwargs={"quality": 95})
fig.savefig(OUT / "fyp2_poster.tiff", dpi=200, facecolor="white")
print("written")
