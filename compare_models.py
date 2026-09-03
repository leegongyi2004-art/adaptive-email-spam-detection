"""Compare classifiers and feature groups (Objective 3 / ablation study).

Trains Naive Bayes, Logistic Regression and a linear SVM on the held-out split,
for both content-only features and the full content+metadata fusion, then
prints accuracy / precision / recall / F1 / ROC-AUC.

    python compare_models.py data/reviewed_mail.csv
"""
from __future__ import annotations

import argparse
import csv
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--limit", type=int, default=0, help="optional cap on emails (0 = all)")
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

    configs = [
        ("Naive Bayes (content only)", "content", MultinomialNB()),
        ("Logistic Regression (content only)", "content", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ("Linear SVM (content only)", "content", LinearSVC(class_weight="balanced")),
        ("Logistic Regression (content+metadata FUSION)", "fusion", LogisticRegression(max_iter=1000, class_weight="balanced", C=1.5)),
        ("Linear SVM (content+metadata FUSION)", "fusion", LinearSVC(class_weight="balanced")),
    ]

    print(f"\n{'model':48s} {'acc':>6s} {'prec':>6s} {'rec':>6s} {'F1':>6s} {'AUC':>6s}")
    print("-" * 82)
    for name, kind, clf in configs:
        if kind == "content":
            pipe = content_pipeline(clf)
            pipe.fit(tr_text, y_train)
            m = scores(pipe, te_text, y_test)
        else:
            pipe = fusion_pipeline(clf)
            pipe.fit(x_train, y_train)
            m = scores(pipe, x_test, y_test)
        print(f"{name:48s} {m['accuracy']:6.3f} {m['precision']:6.3f} {m['recall']:6.3f} {m['f1']:6.3f} {m['roc_auc']:6.3f}")
    print("-" * 82)
    print("The deployed model is Logistic Regression on the content+metadata fusion.")


if __name__ == "__main__":
    main()
