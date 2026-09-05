"""Generate the Chapter-6 result figures from the real corpus/artefacts.

Produces, under reports/figures/:
  fig6_1_confusion_matrix.png   held-out confusion matrix of the deployed fusion model
  fig6_2_roc.png                ROC curve (AUC) on the held-out split
  fig6_3_threshold_catch.png    catch rate vs decision threshold on the LLM-phishing set
  fig6_4_adaptive_roc.png       ROC on held-out modern-threat email, before vs after retraining

Usage (run from the project root, in your virtual environment):
    python reports/make_result_figures.py data/reviewed_mail.csv \
        --llm data/llm_test.csv \
        --modern-test examples/modern_test.csv \
        --modern-feedback examples/modern_feedback.csv

Add --limit 20000 for a fast trial run. Requires matplotlib and scikit-learn.
The deployed model's hyper-parameters match model.py / compare_models.py exactly.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    confusion_matrix, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split  # noqa: E402

from spam_detection.features import parse_email  # noqa: E402
from compare_models import fusion_pipeline  # noqa: E402


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    emails = [r["raw_email"] for r in rows]
    labels = [int(r["label"]) for r in rows] if "label" in rows[0] else None
    return emails, labels


def deployed_model():
    return fusion_pipeline(
        LogisticRegression(max_iter=1000, class_weight="balanced", C=1.5))


def fig_confusion(cm, out):
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = ax.imshow(cm, cmap="Blues")
    classes = ["Ham (0)", "Spam (1)"]
    ax.set_xticks([0, 1]); ax.set_xticklabels(classes)
    ax.set_yticks([0, 1]); ax.set_yticklabels(classes)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_title("Figure 6.1 — Confusion matrix (held-out test split)")
    names = [["TN", "FP"], ["FN", "TP"]]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{names[i][j]}\n{cm[i, j]:,}", ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=12)
    fig.colorbar(im, fraction=0.046, pad=0.04)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def fig_roc(y, probs, auc, out):
    fpr, tpr, _ = roc_curve(y, probs)
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    ax.plot(fpr, tpr, lw=2, label=f"Fusion LR (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], "--", color="grey", lw=1, label="Random (AUC = 0.5)")
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate (recall)")
    ax.set_title("Figure 6.2 — ROC curve on the held-out split")
    ax.legend(loc="lower right"); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def fig_threshold(probs, out):
    thresholds = np.linspace(0.05, 0.95, 19)
    catch = [(probs >= t).mean() * 100 for t in thresholds]
    at55 = (probs >= 0.55).mean() * 100
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.plot(thresholds, catch, marker="o", lw=2)
    ax.axvline(0.55, color="red", ls="--", lw=1)
    ax.scatter([0.55], [at55], color="red", zorder=5)
    ax.annotate(f"0.55 → {at55:.0f}% caught", (0.55, at55),
                textcoords="offset points", xytext=(8, -14), color="red")
    ax.set_xlabel("Decision threshold"); ax.set_ylabel("Catch rate (%)")
    ax.set_title(f"Figure 6.3 — AI-phishing catch rate vs threshold (n = {len(probs):,})")
    ax.grid(alpha=0.3); ax.set_ylim(0, 105)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def fig_adaptive(y, before, after, auc_b, auc_a, out):
    fig, ax = plt.subplots(figsize=(6.0, 5.0))
    for probs, auc, lab, c in [(before, auc_b, f"Before retraining (AUC = {auc_b:.3f})", "tab:orange"),
                              (after, auc_a, f"After retraining (AUC = {auc_a:.3f})", "tab:green")]:
        fpr, tpr, _ = roc_curve(y, probs)
        ax.plot(fpr, tpr, lw=2, color=c, label=lab)
    ax.plot([0, 1], [0, 1], "--", color="grey", lw=1)
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate (recall)")
    ax.set_title("Figure 6.4 — ROC before/after one adaptive retraining cycle")
    ax.legend(loc="lower right"); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", help="main prepared corpus CSV (raw_email,label)")
    ap.add_argument("--llm", default="", help="LLM-phishing CSV (all spam) for Fig 6.3")
    ap.add_argument("--modern-test", default="examples/modern_test.csv")
    ap.add_argument("--modern-feedback", default="examples/modern_feedback.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="reports/figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print(f"Loading corpus {args.corpus} ...")
    emails, labels = load_rows(args.corpus)
    if args.limit:
        emails, labels = emails[: args.limit], labels[: args.limit]
    t0 = time.time()
    records = [parse_email(e) for e in emails]
    print(f"  {len(records)} emails; features in {time.time()-t0:.0f}s")

    tr, te, ytr, yte = train_test_split(
        records, labels, test_size=0.25, random_state=42, stratify=labels)

    print("Training deployed fusion model ...")
    model = deployed_model(); model.fit(tr, ytr)
    probs = model.predict_proba(te)[:, 1]
    pred = (probs >= 0.55).astype(int)

    cm = confusion_matrix(yte, pred, labels=[0, 1])
    acc = (pred == np.array(yte)).mean()
    auc = roc_auc_score(yte, probs)
    print(f"  held-out accuracy={acc:.3f}  ROC-AUC={auc:.3f}")
    print(f"  confusion matrix (rows actual ham/spam; cols pred ham/spam):\n{cm}")
    fig_confusion(cm, os.path.join(args.out, "fig6_1_confusion_matrix.png"))
    fig_roc(yte, probs, auc, os.path.join(args.out, "fig6_2_roc.png"))
    print("  wrote fig6_1_confusion_matrix.png, fig6_2_roc.png")

    # Fig 6.3 — LLM-phishing catch vs threshold
    if args.llm and os.path.exists(args.llm):
        llm_emails, _ = load_rows(args.llm)
        llm_rec = [parse_email(e) for e in llm_emails]
        p = model.predict_proba(llm_rec)[:, 1]
        fig_threshold(p, os.path.join(args.out, "fig6_3_threshold_catch.png"))
        print(f"  wrote fig6_3_threshold_catch.png (n={len(p)}, "
              f"catch@0.55={ (p>=0.55).mean()*100:.0f}%)")
    else:
        print("  (skipped Fig 6.3 — pass --llm data/llm_test.csv)")

    # Fig 6.4 — adaptive before/after on modern-threat set
    if os.path.exists(args.modern_test) and os.path.exists(args.modern_feedback):
        mt_emails, mt_labels = load_rows(args.modern_test)
        fb_emails, fb_labels = load_rows(args.modern_feedback)
        mt_rec = [parse_email(e) for e in mt_emails]
        fb_rec = [parse_email(e) for e in fb_emails]
        before = model.predict_proba(mt_rec)[:, 1]
        model2 = deployed_model()
        model2.fit(tr + fb_rec, list(ytr) + list(fb_labels))
        after = model2.predict_proba(mt_rec)[:, 1]
        if len(set(mt_labels)) == 2:
            auc_b = roc_auc_score(mt_labels, before)
            auc_a = roc_auc_score(mt_labels, after)
            fig_adaptive(mt_labels, before, after, auc_b, auc_a,
                         os.path.join(args.out, "fig6_4_adaptive_roc.png"))
            print(f"  wrote fig6_4_adaptive_roc.png (AUC {auc_b:.3f} -> {auc_a:.3f})")
        else:
            print("  (skipped Fig 6.4 — modern-test set needs both classes for a ROC curve)")
    else:
        print("  (skipped Fig 6.4 — modern test/feedback CSV not found)")

    print("\nDone. Insert the PNGs from", args.out, "at the Figure 6.1–6.4 markers.")


if __name__ == "__main__":
    main()
