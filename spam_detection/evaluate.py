"""Train/evaluate the baseline on a held-out split and print report-ready metrics.

Usage:
    python -m spam_detection.evaluate data/reviewed_mail.csv [--save models/email_spam_detector.joblib]
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .model import EmailSpamDetector


def load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    emails = [r["raw_email"] for r in rows]
    labels = [int(r["label"]) for r in rows]
    if len(set(labels)) < 2:
        raise ValueError(f"{path} must contain both ham (0) and spam (1) labels")
    return emails, labels


def load_many(paths):
    emails, labels = [], []
    for path in paths:
        e, l = load_csv(path)
        emails.extend(e)
        labels.extend(l)
    if len(set(labels)) < 2:
        raise ValueError("Combined CSVs must contain both ham (0) and spam (1) labels")
    return emails, labels


def evaluate(emails, labels, threshold: float = 0.55, test_size: float = 0.25, seed: int = 42):
    x_train, x_test, y_train, y_test = train_test_split(
        emails, labels, test_size=test_size, random_state=seed, stratify=labels
    )
    model = EmailSpamDetector(threshold).fit(x_train, y_train)

    # Latency is measured per message, including feature extraction.
    latencies, probs = [], []
    for email in x_test:
        start = time.perf_counter()
        probs.append(model.predict(email).spam_probability)
        latencies.append(time.perf_counter() - start)
    preds = [1 if p >= threshold else 0 for p in probs]

    latencies.sort()
    metrics = {
        "messages": len(emails),
        "train_messages": len(x_train),
        "test_messages": len(x_test),
        "spam_share": sum(labels) / len(labels),
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "f1": f1_score(y_test, preds, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probs),
        "latency_p50_ms": latencies[len(latencies) // 2] * 1000,
        "latency_p95_ms": latencies[int(len(latencies) * 0.95)] * 1000,
    }
    tn, fp, fn, tp = confusion_matrix(y_test, preds, labels=[0, 1]).ravel()
    metrics["confusion_matrix"] = {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    return model, metrics


def print_report(metrics: dict) -> None:
    cm = metrics.pop("confusion_matrix")
    print("\n=== Baseline evaluation (held-out test split) ===")
    print(f"messages: {metrics['messages']} total ({metrics['train_messages']} train / {metrics['test_messages']} test), "
          f"{metrics['spam_share']:.1%} spam")
    print(f"accuracy:  {metrics['accuracy']:.3f}")
    print(f"precision: {metrics['precision']:.3f}   (flagged messages that really are spam)")
    print(f"recall:    {metrics['recall']:.3f}   (spam messages that were caught)")
    print(f"F1:        {metrics['f1']:.3f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.3f}   (ranking quality, threshold independent)")
    print(f"latency:   p50 {metrics['latency_p50_ms']:.1f} ms / p95 {metrics['latency_p95_ms']:.1f} ms per message")
    print(f"confusion: true spam caught={cm['tp']}, spam missed={cm['fn']}, "
          f"legit flagged={cm['fp']}, legit passed={cm['tn']}")
    print("=================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Evaluate the baseline detector on labeled CSV(s).")
    parser.add_argument("csv", nargs="+", help="CSV(s) with raw_email,label columns (base data + optional feedback)")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--save", default="", help="optional path to save the trained model (e.g. models/email_spam_detector.joblib)")
    args = parser.parse_args()

    emails, labels = load_many(args.csv)
    model, metrics = evaluate(emails, labels, threshold=args.threshold)
    print_report(dict(metrics))
    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        model.save(args.save)
        print(f"trained model saved to {args.save}")


if __name__ == "__main__":
    main()
