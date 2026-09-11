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
ax.text(59, 89.8, "Lee Gong Yi   \u00b7   Supervisor: Dr Abdulrahman",
        ha="center", va="center", fontsize=10, color="#cbd4e8", zorder=4)
ax.text(59, 88.3, "Faculty of Information and Communication Technology, UTAR",
        ha="center", va="center", fontsize=8, color="#9aa7c4", zorder=4)

M = 4.0
CW = 100 - 2 * M
GAP = 1.4

# ---------------------------------------------------------------- introduction
y = 85.5
h = 12.0
panel(M, y - h, CW, h)
head(M, y - 3.0, CW, "Introduction")
body(M + 2.5, y - 5.0,
     "Phishing is the most common entry point for cyber intrusion, and\n"
     "large language models now write fluent phishing mail at scale.\n"
     "Filters that read only words let well-written phishing through;\n"
     "filters that read only headers miss properly configured senders.", 9.5)

# ---------------------------------------------------------------- objectives
y -= h + GAP
h = 14.0
panel(M, y - h, CW, h)
head(M, y - 3.0, CW, "Objectives")
oy = y - 4.8
for i, o in enumerate([
        "Combine message content with structural metadata.",
        "Compare classical models; select the best fusion.",
        "Evaluate against AI-generated phishing.",
        "Measure a reviewed-feedback adaptation loop."], 1):
    ax.add_patch(plt.Circle((M + 3.4, oy - 0.75), 1.2, facecolor=ACCENT,
                            edgecolor="none", zorder=4))
    ax.text(M + 3.4, oy - 0.75, str(i), ha="center", va="center",
            fontsize=8.5, color=NAVY, fontweight="bold", zorder=5)
    body(M + 6.0, oy, o, 9.5)
    oy -= 2.5

# ---------------------------------------------------------------- methodology
y -= h + GAP
h = 23.0
panel(M, y - h, CW, h)
head(M, y - 3.0, CW, "Methodology")

arch = FIGS / "fig3_1_system_architecture.png"
if arch.exists():
    im = mpimg.imread(arch)
    iw = 36.0
    ih = iw * im.shape[0] / im.shape[1] * (W / H)
    axi = fig.add_axes([(M + 3.0) / 100, (y - 4.2 - ih) / 100, iw / 100, ih / 100], zorder=6)
    axi.imshow(im)
    axi.axis("off")

tx = M + 45.0
body(tx, y - 5.2,
     "Word and character TF-IDF\n"
     "plus 13 metadata signals:\n"
     "links, domain mismatch,\n"
     "SPF, DKIM, urgency terms.\n\n"
     "Fused and classified by\n"
     "balanced logistic regression.\n\n"
     "Reviewer corrections feed\n"
     "gated batch retraining.", 9.5)

# ---------------------------------------------------------------- results
y -= h + GAP
h = 17.5
panel(M, y - h, CW, h)
head(M, y - 3.0, CW, "Results")

ry = y - 4.8
for i, (k, v, b) in enumerate([("Accuracy", "99.2%", True),
                               ("False positives", "0.9%", True),
                               ("Speed on a laptop CPU", "13 ms", False),
                               ("AI phishing caught", "92%", True)]):
    if i % 2 == 0:
        ax.add_patch(Rectangle((M + 1.5, ry - 2.0), 48.0, 3.1,
                               facecolor="#eef2f7", edgecolor="none", zorder=2))
    body(M + 3.0, ry, k, 9.5)
    body(M + 48.0, ry, v, 11 if b else 10, "bold", ACCENT if b else NAVY, ha="right")
    ry -= 3.2

cm = np.array([[9719, 90], [80, 10399]])
axc = fig.add_axes([(M + 56.0) / 100, (y - 15.6) / 100, 24.0 / 100, 10.0 / 100], zorder=6)
axc.imshow(cm, cmap="Blues", vmin=0, vmax=12000)
for (r, c), v in np.ndenumerate(cm):
    axc.text(c, r, f"{v:,}", ha="center", va="center", fontsize=9,
             fontweight="bold", color="white" if v > 6000 else TEXT)
axc.set_xticks([0, 1]); axc.set_xticklabels(["Ham", "Spam"], fontsize=7)
axc.set_yticks([0, 1]); axc.set_yticklabels(["Ham", "Spam"], fontsize=7)
axc.set_title("Confusion matrix (20,288 emails)", fontsize=8, color=BLUE,
              fontweight="bold", pad=5)
axc.tick_params(length=0)
for sp in axc.spines.values():
    sp.set_visible(False)

# ---------------------------------------------------------------- conclusion
y -= h + GAP
h = 10.5
panel(M, y - h, CW, h, fc="#eef2f7", ec=NAVY)
head(M, y - 3.0, CW, "Conclusion")
body(M + 2.5, y - 5.0,
     "An explainable detector reaching 99.2% accuracy that generalises to\n"
     "AI-generated phishing it never saw in training, with a human-gated\n"
     "feedback loop. Runs on a laptop \u2014 no email leaves the machine.", 9.5)

# ---------------------------------------------------------------- footer
ax.add_patch(Rectangle((0, 0), 100, 2.0, facecolor=NAVY, edgecolor="none", zorder=2))
ax.text(50, 0.9, "Final Year Project 2  \u00b7  Universiti Tunku Abdul Rahman",
        ha="center", va="center", fontsize=7, color="#9aa7c4", zorder=4)

fig.savefig(OUT / "fyp2_poster.png", dpi=200, facecolor="white")
fig.savefig(OUT / "fyp2_poster.jpg", dpi=200, facecolor="white",
            pil_kwargs={"quality": 95})
fig.savefig(OUT / "fyp2_poster.tiff", dpi=200, facecolor="white")
print("written")
