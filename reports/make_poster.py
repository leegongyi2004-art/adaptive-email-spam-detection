"""Generate the FYP2 A4 poster as a high-resolution image (PNG + TIFF + JPEG)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.image as mpimg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "reports" / "figures"
OUT = ROOT / "reports" / "poster"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palette
NAVY = "#0d2b45"
BLUE = "#1f5f8b"
ACCENT = "#e8912d"
LIGHT = "#f2f5f8"
BORDER = "#c7d3dd"
TEXT = "#16222c"

plt.rcParams["font.family"] = "DejaVu Sans"

# A4 portrait at 200 dpi
W, H = 8.27, 11.69
fig = plt.figure(figsize=(W, H), dpi=200)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, fc=LIGHT, ec=BORDER, lw=0.8, r=0.6, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z))


def head(x, y, w, label):
    """Section heading bar."""
    ax.add_patch(Rectangle((x, y), w, 2.1, facecolor=BLUE, edgecolor="none", zorder=3))
    ax.text(x + 0.8, y + 1.05, label.upper(), va="center", ha="left",
            fontsize=9.5, color="white", fontweight="bold", zorder=4)


def body(x, y, s, size=6.4, w="normal", color=TEXT, ha="left", style="normal"):
    return ax.text(x, y, s, va="top", ha=ha, fontsize=size, color=color,
                   fontweight=w, style=style, zorder=4, linespacing=1.45)


# ---------------------------------------------------------------- header
ax.add_patch(Rectangle((0, 88.2), 100, 11.8, facecolor=NAVY, edgecolor="none", zorder=2))
ax.add_patch(Rectangle((0, 87.6), 100, 0.6, facecolor=ACCENT, edgecolor="none", zorder=2))

ax.text(50, 96.4, "Adaptive Email Spam Detection Using Artificial Intelligence",
        ha="center", va="center", fontsize=15.5, color="white", fontweight="bold", zorder=4)
ax.text(50, 93.6, "and Content\u2013Metadata Fusion",
        ha="center", va="center", fontsize=15.5, color="white", fontweight="bold", zorder=4)
ax.text(50, 90.7, "Lee Gong Yi   \u00b7   Supervisor: Dr Abdulrahman",
        ha="center", va="center", fontsize=8.2, color="#cfe0ee", zorder=4)
ax.text(50, 89.1, "Bachelor of Information Technology (Honours) Communications and Networking   \u00b7   "
                  "Faculty of Information and Communication Technology, UTAR Kampar Campus",
        ha="center", va="center", fontsize=5.9, color="#a9c4d8", zorder=4)

# ---------------------------------------------------------------- geometry
M = 2.2                      # outer margin
G = 1.8                      # gutter
CW = (100 - 2 * M - 2 * G) / 3
C1, C2, C3 = M, M + CW + G, M + 2 * (CW + G)
TOP = 85.4

# ================================================================ COLUMN 1
y = TOP
box(C1, y - 22.6, CW, 22.6)
head(C1, y - 2.1, CW, "1. Introduction")
body(C1 + 0.9, y - 3.0,
     "Phishing is the most common entry point for cyber\n"
     "intrusion. Large language models now let attackers\n"
     "write fluent, error-free phishing mail at scale.",
     6.3)
body(C1 + 0.9, y - 7.6, "The problem", 6.6, "bold", BLUE)
body(C1 + 0.9, y - 9.1,
     "\u2022 Content-only filters miss fluent phishing that\n"
     "   avoids known trigger words.\n"
     "\u2022 Metadata-only filters miss well-formed mail sent\n"
     "   from correctly configured accounts.\n"
     "\u2022 Commercial filters cannot be reproduced,\n"
     "   audited or retrained by the user.",
     6.1)
body(C1 + 0.9, y - 18.3,
     "This project fuses both signal types in one\n"
     "explainable classical model that runs locally.",
     6.3, style="italic")

y -= 24.2
box(C1, y - 20.4, CW, 20.4)
head(C1, y - 2.1, CW, "2. Objectives")
objs = [
    "Build a detector combining message content\nwith structural metadata.",
    "Compare classical ML models and select the\nstrongest fused configuration.",
    "Evaluate against modern threats, including\nAI-generated phishing.",
    "Implement and measure a reviewed-feedback\nadaptation loop.",
]
oy = y - 3.2
for i, o in enumerate(objs, 1):
    ax.add_patch(plt.Circle((C1 + 1.9, oy - 0.55), 0.85, facecolor=ACCENT,
                            edgecolor="none", zorder=4))
    ax.text(C1 + 1.9, oy - 0.55, str(i), ha="center", va="center",
            fontsize=6.2, color="white", fontweight="bold", zorder=5)
    body(C1 + 3.6, oy, o, 6.1)
    oy -= 4.25

y -= 22.0
box(C1, y - 22.4, CW, 22.4)
head(C1, y - 2.1, CW, "3. Dataset")
rows = [
    ("Merged public corpus", "82,500"),
    ("After de-duplication", "81,152"),
    ("Held-out test split", "20,288"),
    ("AI phishing (test only)", "4,986"),
]
ry = y - 3.6
for i, (k, v) in enumerate(rows):
    if i % 2 == 0:
        ax.add_patch(Rectangle((C1 + 0.6, ry - 1.55), CW - 1.2, 2.5,
                               facecolor="#e6edf3", edgecolor="none", zorder=2))
    body(C1 + 1.2, ry, k, 6.0)
    body(C1 + CW - 1.2, ry, v, 6.4, "bold", NAVY, ha="right")
    ry -= 2.55
body(C1 + 0.9, ry - 0.6,
     "Six public corpora: Enron, Ling, CEAS-2008,\n"
     "Nazario, Nigerian-Fraud and SpamAssassin.\n"
     "De-duplicated on normalised content so no\n"
     "message appears in both training and test.\n\n"
     "AI phishing set: 4,986 messages written by\n"
     "GPT-4.1, DeepSeek 3.2 and LLaMA 3.3 \u2014 used\n"
     "for testing only, never for training.",
     6.0)

# ================================================================ COLUMN 2
y = TOP
box(C2, y - 46.0, CW, 46.0)
head(C2, y - 2.1, CW, "4. Method")

arch = FIGS / "fig3_1_system_architecture.png"
if arch.exists():
    im = mpimg.imread(arch)
    iw = CW - 5.0
    ih = iw * im.shape[0] / im.shape[1] * (W / H)
    axi = fig.add_axes([(C2 + 2.5) / 100, (y - 3.0 - ih) / 100, iw / 100, ih / 100], zorder=6)
    axi.imshow(im)
    axi.axis("off")
    ny = y - 3.6 - ih
else:
    ny = y - 4.0
body(C2 + CW / 2, ny, "System architecture", 5.6, color="#5b6b78", ha="center", style="italic")

ny -= 2.4
body(C2 + 0.9, ny, "Two parallel feature streams", 6.6, "bold", BLUE)
ny -= 1.6
body(C2 + 0.9, ny,
     "Every message is parsed as RFC 5322, then turned\n"
     "into two feature streams:", 6.1)
ny -= 3.4
ax.add_patch(Rectangle((C2 + 0.9, ny - 6.4), CW - 1.8, 6.4,
                       facecolor="#fdf1e0", edgecolor=ACCENT, linewidth=0.7, zorder=3))
body(C2 + 1.6, ny - 0.5, "CONTENT", 5.8, "bold", "#a8620f")
body(C2 + 1.6, ny - 2.0,
     "Word TF-IDF (1\u20132 grams, 40k features)\n"
     "Character TF-IDF (3\u20135 grams, 30k features)", 5.9)
ny -= 7.2
ax.add_patch(Rectangle((C2 + 0.9, ny - 8.2), CW - 1.8, 8.2,
                       facecolor="#e8f1f7", edgecolor=BLUE, linewidth=0.7, zorder=3))
body(C2 + 1.6, ny - 0.5, "13 STRUCTURAL METADATA SIGNALS", 5.8, "bold", "#14506f")
body(C2 + 1.6, ny - 2.0,
     "URL count \u00b7 distinct link domains \u00b7 sender/link\n"
     "domain mismatch \u00b7 Reply-To present \u00b7 SPF \u00b7 DKIM \u00b7\n"
     "subject length \u00b7 body length \u00b7 attachments \u00b7 sender\n"
     "domain \u00b7 capitals ratio \u00b7 exclamation count \u00b7\n"
     "urgency term count", 5.9)
ny -= 9.2
body(C2 + 0.9, ny,
     "The streams are joined by a feature union and\n"
     "classified by logistic regression with balanced\n"
     "class weights at a 0.55 decision threshold.", 6.1)

y -= 47.6
box(C2, y - 35.8, CW, 35.8)
head(C2, y - 2.1, CW, "5. Adaptation loop")
steps = [
    ("Score", "Incoming mail is scored by the\ndeployed model."),
    ("Queue", "Every verdict is written to a\nreview queue."),
    ("Review", "A human confirms or corrects\nthe label."),
    ("Retrain", "Batch retraining on corpus\nplus corrections."),
    ("Gate", "Candidate is deployed ONLY if\nheld-out ranking does not drop."),
]
sy = y - 3.4
for i, (t, dsc) in enumerate(steps):
    fc = ACCENT if i == 4 else BLUE
    ax.add_patch(FancyBboxPatch((C2 + 1.0, sy - 4.2), CW - 2.0, 4.2,
                                boxstyle="round,pad=0,rounding_size=0.5",
                                facecolor="white", edgecolor=fc, linewidth=0.9, zorder=4))
    ax.add_patch(Rectangle((C2 + 1.0, sy - 4.2), 0.7, 4.2, facecolor=fc,
                           edgecolor="none", zorder=5))
    body(C2 + 2.3, sy - 0.7, t.upper(), 5.9, "bold", fc)
    body(C2 + 2.3, sy - 2.2, dsc, 5.6)
    sy -= 4.8
    if i < 4:
        ax.annotate("", xy=(C2 + CW / 2, sy + 0.05), xytext=(C2 + CW / 2, sy + 0.55),
                    arrowprops=dict(arrowstyle="-|>", color="#8fa3b2", lw=1.0), zorder=5)
        sy -= 0.75
body(C2 + 1.0, sy - 0.4,
     "The human checkpoint is a security control: no\n"
     "correction reaches the deployed model without an\n"
     "explicit, reviewer-triggered retraining cycle.",
     5.9, style="italic")

# ================================================================ COLUMN 3
y = TOP
box(C3, y - 34.0, CW, 34.0)
head(C3, y - 2.1, CW, "6. Results")
res = [
    ("Accuracy", "99.2%", True),
    ("Precision", "0.991", False),
    ("Recall", "0.992", False),
    ("F1 score", "0.992", False),
    ("ROC-AUC", "1.000", True),
    ("False-positive rate", "0.9%", True),
    ("Latency (CPU, median)", "13 ms", False),
]
ry = y - 3.6
for i, (k, v, b) in enumerate(res):
    if i % 2 == 0:
        ax.add_patch(Rectangle((C3 + 0.6, ry - 1.5), CW - 1.2, 2.4,
                               facecolor="#e6edf3", edgecolor="none", zorder=2))
    body(C3 + 1.2, ry, k, 6.0)
    body(C3 + CW - 1.2, ry, v, 6.6 if b else 6.2, "bold",
         ACCENT if b else NAVY, ha="right")
    ry -= 2.5

ry -= 0.6
body(C3 + 0.9, ry, "Held-out confusion matrix (n = 20,288)", 5.9, "bold", BLUE)
ry -= 1.9
cm = np.array([[9719, 90], [80, 10399]])
axc = fig.add_axes([(C3 + 3.2) / 100, (ry - 8.6) / 100, (CW - 6.0) / 100, 8.0 / 100], zorder=6)
axc.imshow(cm, cmap="Blues", vmin=0, vmax=12000)
for (r, c), v in np.ndenumerate(cm):
    axc.text(c, r, f"{v:,}", ha="center", va="center", fontsize=6.4,
             fontweight="bold", color="white" if v > 6000 else "#16222c")
axc.set_xticks([0, 1]); axc.set_xticklabels(["Pred\nham", "Pred\nspam"], fontsize=4.8)
axc.set_yticks([0, 1]); axc.set_yticklabels(["Ham", "Spam"], fontsize=4.8)
axc.tick_params(length=0)
for s in axc.spines.values():
    s.set_visible(False)

y -= 35.6
box(C3, y - 17.6, CW, 17.6)
head(C3, y - 2.1, CW, "7. AI phishing & adaptation")
body(C3 + 0.9, y - 3.2, "Unseen AI-generated phishing", 6.3, "bold", BLUE)
body(C3 + 0.9, y - 4.7,
     "4,565 of 4,986 caught \u2014 92% \u2014 with no AI-written\n"
     "mail in the training set at all.", 6.0)
ax.add_patch(Rectangle((C3 + 1.0, y - 8.6), (CW - 2.0), 1.5,
                       facecolor="#dde5eb", edgecolor="none", zorder=3))
ax.add_patch(Rectangle((C3 + 1.0, y - 8.6), (CW - 2.0) * 0.92, 1.5,
                       facecolor=ACCENT, edgecolor="none", zorder=4))
ax.text(C3 + CW / 2, y - 7.85, "92% CATCH RATE", ha="center", va="center",
        fontsize=5.8, color="white", fontweight="bold", zorder=5)

body(C3 + 0.9, y - 10.2, "One reviewed retraining cycle", 6.3, "bold", BLUE)
body(C3 + 0.9, y - 11.7,
     "ROC-AUC on held-out modern threats improved\n"
     "0.810 \u2192 0.945 (+16.7% relative), recall held at\n"
     "95% and main-corpus accuracy maintained at 0.991.", 6.0)

y -= 19.2
box(C3, y - 17.0, CW, 17.0)
head(C3, y - 2.1, CW, "8. Discussion")
body(C3 + 0.9, y - 3.2,
     "\u2022 Fusion beat content alone: metadata signals such\n"
     "   as sender/link domain mismatch catch mail that\n"
     "   reads perfectly but is structurally suspicious.\n\n"
     "\u2022 Character n-grams resist the obfuscation that\n"
     "   defeats word-level features.\n\n"
     "\u2022 Runs on an ordinary CPU laptop with no cloud\n"
     "   service \u2014 no email ever leaves the machine.\n\n"
     "\u2022 Every verdict is explainable through its\n"
     "   contributing metadata signals.", 6.0)

y -= 18.6
box(C3, y - 11.8, CW, 11.8, fc="#eaf2f8", ec=BLUE, lw=1.0)
head(C3, y - 2.1, CW, "9. Conclusion")
body(C3 + 0.9, y - 3.2,
     "A classical, explainable, locally deployable\n"
     "detector reaches 99.2% accuracy and generalises to\n"
     "AI-generated phishing it never saw in training, while\n"
     "a human-gated feedback loop lets it adapt to new\n"
     "campaigns without exposing the model to poisoned\n"
     "labels. All four objectives were met.", 5.9)

# ---------------------------------------------------------------- footer
ax.add_patch(Rectangle((0, 0), 100, 1.5, facecolor=NAVY, edgecolor="none", zorder=2))
ax.text(50, 0.75,
        "Final Year Project 2  \u00b7  Faculty of Information and Communication Technology  \u00b7  "
        "Universiti Tunku Abdul Rahman",
        ha="center", va="center", fontsize=5.2, color="#a9c4d8", zorder=4)

png = OUT / "fyp2_poster.png"
fig.savefig(png, dpi=200, facecolor="white")
fig.savefig(OUT / "fyp2_poster.jpg", dpi=200, facecolor="white",
            pil_kwargs={"quality": 95})
fig.savefig(OUT / "fyp2_poster.tiff", dpi=200, facecolor="white")
print("written:", png)
