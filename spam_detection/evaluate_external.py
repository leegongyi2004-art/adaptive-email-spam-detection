"""Evaluate a trained model on a separate labelled test set (e.g. modern/AI threats).

Use this for test data that was NEVER used in training, to measure how well the
detector generalises to new threats (AI-assisted phishing, business-email-compromise).

    python -m spam_detection.evaluate_external models/email_spam_detector.joblib examples/modern_test.csv

The CSV needs raw_email,label columns (0 = legitimate, 1 = spam/phishing).
"""
from __future__ import annotations

import argparse
import time

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from .evaluate import load_csv
from .model import EmailSpamDetector


def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained model on an external test CSV.")
    parser.add_argument("model", help="path to the trained .joblib model")
    parser.add_argument("test_csv", help="labelled test CSV (raw_email,label) NOT used in training")
    parser.add_argument("--threshold", type=float, default=0.55)
    args = parser.parse_args()

    emails, labels = load_csv(args.test_csv)
    model = EmailSpamDetector.load(args.model)
    model.threshold = args.threshold

    latencies, probs = [], []
    for email in emails:
        start = time.perf_counter()
        probs.append(model.predict(email).spam_probability)
        latencies.append(time.perf_counter() - start)
    preds = [1 if p >= args.threshold else 0 for p in probs]
    latencies.sort()

    tn, fp, fn, tp = confusion_matrix(labels, preds, labels=[0, 1]).ravel()
    print(f"\n=== External test set: {args.test_csv} ===")
    print(f"emails: {len(emails)}  ({sum(labels)} spam/phishing, {len(labels)-sum(labels)} legitimate)")
    print(f"accuracy:  {accuracy_score(labels, preds):.3f}")
    print(f"precision: {precision_score(labels, preds, zero_division=0):.3f}")
    print(f"recall:    {recall_score(labels, preds, zero_division=0):.3f}   (phishing caught)")
    print(f"F1:        {f1_score(labels, preds, zero_division=0):.3f}")
    try:
        print(f"ROC-AUC:   {roc_auc_score(labels, probs):.3f}")
    except ValueError:
        pass
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    print(f"false-positive rate: {fpr:.3f}   (legit emails wrongly flagged: {fp})")
    print(f"phishing missed (false negatives): {fn}")
    print(f"latency:   p50 {latencies[len(latencies)//2]*1000:.1f} ms / p95 {latencies[int(len(latencies)*0.95)]*1000:.1f} ms")
    print("=================================================\n")


if __name__ == "__main__":
    main()
