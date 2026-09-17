"""Compare classifiers and feature groups (Objective 3 / ablation study).

Trains Naive Bayes, Logistic Regression and a linear SVM on the held-out split,
for both content-only features and the full content+metadata fusion, then
reports accuracy / precision / recall / F1 / ROC-AUC.

    python compare_models.py data/reviewed_mail.csv
    python compare_models.py data/reviewed_mail.csv --limit 20000   # faster run

In addition to the console table it writes (under --out-dir, default reports/):
  * model_comparison.csv         machine-readable results
  * table6_2.md                  ready-to-paste Markdown rows for the report
  * figures/fig6_model_comparison.png   grouped bar chart (if matplotlib present)
"""
from __future__ import annotations

import argparse
import csv
import os
import time

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.svm import LinearSVC

from spam_detection.features import parse_email


def extract_text(records):
    return [r["text"] for r in records]


def extract_metadata(records):
    return [r["metadata"] for r in records]


def content_pipeline(clf):
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=40_000)),
        ("clf", clf),
    ])


def fusion_pipeline(clf):
    return Pipeline([
        ("features", FeatureUnion([
            ("words", Pipeline([("extract", FunctionTransformer(extract_text, validate=False)),
                                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=40_000))])),
            ("chars", Pipeline([("extract", FunctionTransformer(extract_text, validate=False)),
                                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, max_features=30_000))])),
            ("metadata", Pipeline([("extract", FunctionTransformer(extract_metadata, validate=False)),
                                   ("vectorize", DictVectorizer(sparse=True)),
                                   ("scale", StandardScaler(with_mean=False))])),
        ])),
        ("clf", clf),
    ])


def scores(model, x_test, y_test):
    pred = model.predict(x_test)
    out = {
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
    }
    try:
        if hasattr(model, "predict_proba"):
            score = model.predict_proba(x_test)[:, 1]
        else:  # LinearSVC
            score = model.decision_function(x_test)
        out["roc_auc"] = roc_auc_score(y_test, score)
    except Exception:
        out["roc_auc"] = float("nan")
    return out


# (label, feature kind, estimator, deployed?)
CONFIGS = [
    ("Naive Bayes (content only)", "content", MultinomialNB(), False),
    ("Logistic Regression (content only)", "content",
     LogisticRegression(max_iter=1000, class_weight="balanced"), False),
    ("Linear SVM (content only)", "content",
     LinearSVC(class_weight="balanced", max_iter=10_000), False),
    ("Logistic Regression (content+metadata FUSION)", "fusion",
     LogisticRegression(max_iter=1000, class_weight="balanced", C=1.5), True),
    ("Linear SVM (content+metadata FUSION)", "fusion",
     LinearSVC(class_weight="balanced", max_iter=10_000), False),
]

METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]


def write_outputs(results, out_dir):
    os.makedirs(os.path.join(out_dir, "figures"), exist_ok=True)

    # CSV
    csv_path = os.path.join(out_dir, "model_comparison.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["configuration"] + METRICS)
        for r in results:
            w.writerow([r["name"]] + [f"{r[m]:.3f}" for m in METRICS])

    # Markdown table (report Table 6.2)
    md_path = os.path.join(out_dir, "table6_2.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("| Configuration | Accuracy | Precision | Recall | F1 | ROC-AUC |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in results:
            name = f"**{r['name']} (deployed)**" if r["deployed"] else r["name"]
            vals = " | ".join(f"{r[m]:.3f}" for m in METRICS)
            f.write(f"| {name} | {vals} |\n")

    # Bar chart
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = [r["name"].replace(" (content+metadata FUSION)", "\n(fusion)")
                            .replace(" (content only)", "\n(content)") for r in results]
        metrics_show = ["accuracy", "precision", "recall", "f1"]
        x = np.arange(len(labels))
        width = 0.2
        fig, ax = plt.subplots(figsize=(11, 5.5))
        for i, m in enumerate(metrics_show):
            ax.bar(x + (i - 1.5) * width, [r[m] for r in results], width, label=m.capitalize())
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("Score")
        ax.set_ylim(min(min(r[m] for r in results) for m in metrics_show) - 0.03, 1.005)
        ax.set_title("Classifier and feature-group comparison (held-out split)")
        ax.legend(ncol=4, loc="lower center")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig_path = os.path.join(out_dir, "figures", "fig6_model_comparison.png")
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        chart = fig_path
    except Exception as exc:  # matplotlib missing is fine
        chart = f"(chart skipped: {exc})"

    return csv_path, md_path, chart


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--limit", type=int, default=0, help="optional cap on emails (0 = all)")
    ap.add_argument("--out-dir", default="reports", help="where to write table/csv/figure")
    args = ap.parse_args()

    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]
    emails = [r["raw_email"] for r in rows]
    labels = [int(r["label"]) for r in rows]
    print(f"Loaded {len(emails)} emails ({sum(labels)} spam). Extracting features...")
    t0 = time.time()
    records = [parse_email(e) for e in emails]
    print(f"Feature extraction took {time.time()-t0:.0f}s")

    x_train, x_test, y_train, y_test = train_test_split(
        records, labels, test_size=0.25, random_state=42, stratify=labels)

    # Content-only classifiers operate on text strings; fusion on record dicts.
    tr_text = [r["text"] for r in x_train]
    te_text = [r["text"] for r in x_test]

    results = []
    print(f"\n{'model':48s} {'acc':>6s} {'prec':>6s} {'rec':>6s} {'F1':>6s} {'AUC':>6s}")
    print("-" * 82)
    for name, kind, clf, deployed in CONFIGS:
        if kind == "content":
            pipe = content_pipeline(clf)
            pipe.fit(tr_text, y_train)
            m = scores(pipe, te_text, y_test)
        else:
            pipe = fusion_pipeline(clf)
            pipe.fit(x_train, y_train)
            m = scores(pipe, x_test, y_test)
        m["name"] = name
        m["deployed"] = deployed
        results.append(m)
        print(f"{name:48s} {m['accuracy']:6.3f} {m['precision']:6.3f} "
              f"{m['recall']:6.3f} {m['f1']:6.3f} {m['roc_auc']:6.3f}")
    print("-" * 82)
    print("The deployed model is Logistic Regression on the content+metadata fusion.")

    csv_path, md_path, chart = write_outputs(results, args.out_dir)
    print(f"\nSaved CSV : {csv_path}")
    print(f"Saved table: {md_path}  (paste these rows into report Table 6.2)")
    print(f"Saved chart: {chart}")


if __name__ == "__main__":
    main()
