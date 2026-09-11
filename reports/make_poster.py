"""Generate the FYP2 A4 poster (simple layout, UTAR logo) as PNG / JPEG / TIFF."""
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
TEXT = "#16222c"
BORDER = "#cdd7e0"

plt.rcParams["font.family"] = "DejaVu Sans"

W, H = 8.27, 11.69          # A4 portrait
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
    ax.add_patch(Rectangle((x, y), w, 2.6, facecolor=NAVY, edgecolor="none", zorder=3))
    ax.add_patch(Rectangle((x, y), 1.0, 2.6, facecolor=ACCENT, edgecolor="none", zorder=4))
    ax.text(x + 2.0, y + 1.3, label.upper(), va="center", ha="left",
            fontsize=11, color="white", fontweight="bold", zorder=5)


def body(x, y, s, size=7.6, w="normal", color=TEXT, ha="left", style="normal"):
    ax.text(x, y, s, va="top", ha=ha, fontsize=size, color=color, fontweight=w,
            style=style, zorder=4, linespacing=1.55)


# ------------------------------------------------------------------ header
ax.add_patch(Rectangle((0, 88.0), 100, 12.0, facecolor=NAVY, edgecolor="none", zorder=2))
ax.add_patch(Rectangle((0, 87.4), 100, 0.6, facecolor=ACCENT, edgecolor="none", zorder=2))

logo = ASSETS / "utar_logo.png"
if logo.exists():
    im = mpimg.imread(logo)
    lw = 15.0
    lh = lw * im.shape[0] / im.shape[1] * (W / H)
    axl = fig.add_axes([3.0 / 100, (92.0 - lh / 2) / 100, lw / 100, lh / 100], zorder=6)
    axl.imshow(im)
    axl.axis("off")

ax.text(58, 96.0, "Adaptive Email Spam Detection Using",
        ha="center", va="center", fontsize=16, color="white", fontweight="bold", zorder=4)
ax.text(58, 93.1, "AI and Content\u2013Metadata Fusion",
        ha="center", va="center", fontsize=16, color="white", fontweight="bold", zorder=4)
ax.text(58, 90.2, "Lee Gong Yi   \u00b7   Supervisor: Dr Abdulrahman",
        ha="center", va="center", fontsize=8.6, color="#c9d3e6", zorder=4)
ax.text(58, 88.8, "Faculty of Information and Communication Technology, UTAR Kampar Campus",
        ha="center", va="center", fontsize=7.0, color="#9aa7c4", zorder=4)

M = 4.0
CW = 100 - 2 * M
HALF = (CW - 3.0) / 2
LX, RX = M, M + HALF + 3.0
GAP = 1.4

# ------------------------------------------------------------------ 1 intro
y = 86.0
h = 11.2
panel(M, y - h, CW, h)
head(M, y - 2.6, CW, "Introduction")
body(M + 2.0, y - 4.3,
     "Phishing is the most common entry point for cyber intrusion, and large language models now let\n"
     "attackers write fluent, error-free phishing mail at scale. Filters that read only the words of a message\n"
     "let well-written phishing through, while filters that read only headers miss mail sent from correctly\n"
     "configured accounts. Commercial filters work, but cannot be reproduced, audited or retrained. This\n"
     "project fuses both signal types in one explainable classical model that runs entirely on a laptop.",
     7.3)

# ------------------------------------------------------------------ 2 objectives / dataset
y -= h + GAP
h = 16.2
panel(LX, y - h, HALF, h)
head(LX, y - 2.6, HALF, "Objectives")
oy = y - 4.3
for i, o in enumerate([
        "Build a detector combining message\ncontent with structural metadata.",
        "Compare classical ML models and select\nthe strongest fused configuration.",
        "Evaluate against modern threats,\nincluding AI-generated phishing.",
        "Implement and measure a\nreviewed-feedback adaptation loop."], 1):
    ax.add_patch(plt.Circle((LX + 3.0, oy - 0.7), 1.05, facecolor=ACCENT,
                            edgecolor="none", zorder=4))
    ax.text(LX + 3.0, oy - 0.7, str(i), ha="center", va="center",
            fontsize=7.2, color=NAVY, fontweight="bold", zorder=5)
    body(LX + 5.2, oy, o, 7.2)
    oy -= 3.1

panel(RX, y - h, HALF, h)
head(RX, y - 2.6, HALF, "Dataset")
ry = y - 4.4
for i, (k, v) in enumerate([("Merged public corpus", "82,500"),
                            ("After de-duplication", "81,152"),
                            ("Held-out test split", "20,288"),
                            ("AI phishing (test only)", "4,986")]):
    if i % 2 == 0:
        ax.add_patch(Rectangle((RX + 1.2, ry - 1.8), HALF - 2.4, 2.8,
                               facecolor="#eef2f7", edgecolor="none", zorder=2))
    body(RX + 2.2, ry, k, 7.2)
    body(RX + HALF - 2.2, ry, v, 7.6, "bold", NAVY, ha="right")
    ry -= 2.5
body(RX + 2.2, ry - 0.3,
     "Enron, Ling, CEAS-2008, Nazario, Nigerian-Fraud\n"
     "and SpamAssassin. AI phishing: test only.", 6.8)

# ------------------------------------------------------------------ 3 method
y -= h + GAP
h = 19.6
panel(M, y - h, CW, h)
head(M, y - 2.6, CW, "Methodology")

arch = FIGS / "fig3_1_system_architecture.png"
if arch.exists():
    im = mpimg.imread(arch)
    iw = 26.0
    ih = iw * im.shape[0] / im.shape[1] * (W / H)
    axi = fig.add_axes([(M + 6.0) / 100, (y - 3.6 - ih) / 100, iw / 100, ih / 100], zorder=6)
    axi.imshow(im)
    axi.axis("off")

tx = M + 42.0
body(tx, y - 4.3, "Two parallel feature streams", 7.8, "bold", BLUE)
body(tx, y - 6.3,
     "\u2022 Content: word TF-IDF (1\u20132 grams) and\n"
     "   character TF-IDF (3\u20135 grams)\n"
     "\u2022 Metadata: 13 structural signals \u2014 URL count,\n"
     "   sender/link domain mismatch, SPF, DKIM,\n"
     "   Reply-To, capitals ratio, urgency terms\n"
     "\u2022 Joined by feature union, classified by\n"
     "   class-balanced logistic regression at 0.55", 7.1)
body(tx, y - 15.2, "Adaptation loop", 7.8, "bold", BLUE)
body(tx, y - 17.0,
     "Score \u2192 review queue \u2192 human confirms or\n"
     "corrects \u2192 batch retrain \u2192 deployed only if\n"
     "held-out ranking quality does not drop.", 7.1)

# ------------------------------------------------------------------ 4 results
y -= h + GAP
h = 21.6
panel(M, y - h, CW, h)
head(M, y - 2.6, CW, "Results")

ry = y - 4.4
for i, (k, v, b) in enumerate([("Accuracy", "99.2%", True),
                               ("Precision / Recall / F1", "0.991 / 0.992 / 0.992", False),
                               ("ROC-AUC", "1.000", True),
                               ("False-positive rate", "0.9%", True),
                               ("Latency (CPU, median)", "13 ms", False)]):
    if i % 2 == 0:
        ax.add_patch(Rectangle((M + 1.2, ry - 1.8), 51.0, 2.8,
                               facecolor="#eef2f7", edgecolor="none", zorder=2))
    body(M + 2.2, ry, k, 7.3)
    body(M + 51.0, ry, v, 7.8 if b else 7.4, "bold", ACCENT if b else NAVY, ha="right")
    ry -= 2.6

body(M + 2.2, ry - 0.4,
     "Unseen AI-generated phishing: 4,565 of 4,986 caught (92%), with no AI-written mail in training.\n"
     "After one reviewed retraining cycle, ROC-AUC on held-out modern threats rose 0.810 \u2192 0.945,\n"
     "with main-corpus accuracy maintained at 0.991.", 7.2)

cm = np.array([[9719, 90], [80, 10399]])
axc = fig.add_axes([(M + 58.0) / 100, (y - 15.2) / 100, 22.0 / 100, 9.8 / 100], zorder=6)
axc.imshow(cm, cmap="Blues", vmin=0, vmax=12000)
for (r, c), v in np.ndenumerate(cm):
    axc.text(c, r, f"{v:,}", ha="center", va="center", fontsize=8,
             fontweight="bold", color="white" if v > 6000 else TEXT)
axc.set_xticks([0, 1]); axc.set_xticklabels(["Pred ham", "Pred spam"], fontsize=6)
axc.set_yticks([0, 1]); axc.set_yticklabels(["Ham", "Spam"], fontsize=6)
axc.set_title("Held-out confusion matrix (n = 20,288)", fontsize=6.6, color=BLUE,
              fontweight="bold", pad=4)
axc.tick_params(length=0)
for sp in axc.spines.values():
    sp.set_visible(False)

# ------------------------------------------------------------------ 5 conclusion
y -= h + GAP
h = 10.4
panel(M, y - h, CW, h, fc="#eef2f7", ec=NAVY)
head(M, y - 2.6, CW, "Conclusion")
body(M + 2.0, y - 4.3,
     "A classical, explainable, locally deployable detector reaches 99.2% accuracy and generalises to\n"
     "AI-generated phishing it never saw in training, while a human-gated feedback loop lets it adapt to new\n"
     "campaigns without exposing the model to poisoned labels. No email leaves the machine, and every\n"
     "verdict is explainable through its metadata signals. All four objectives were met.", 7.2)

# ------------------------------------------------------------------ footer
ax.add_patch(Rectangle((0, 0), 100, 2.0, facecolor=NAVY, edgecolor="none", zorder=2))
ax.text(50, 0.9, "Final Year Project 2  \u00b7  Universiti Tunku Abdul Rahman",
        ha="center", va="center", fontsize=6.4, color="#9aa7c4", zorder=4)

fig.savefig(OUT / "fyp2_poster.png", dpi=200, facecolor="white")
fig.savefig(OUT / "fyp2_poster.jpg", dpi=200, facecolor="white",
            pil_kwargs={"quality": 95})
fig.savefig(OUT / "fyp2_poster.tiff", dpi=200, facecolor="white")
print("written:", OUT / "fyp2_poster.png")
