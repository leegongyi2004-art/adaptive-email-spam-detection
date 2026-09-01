"""Evaluate a trained model on a separate labelled test set (e.g. modern/AI threats).

Use this for test data that was NEVER used in training, to measure how well the
detector generalises to new threats (AI-assisted phishing, business-email-compromise).

    python -m spam_detection.evaluate_external models/email_spam_detector.joblib examples/modern_test.csv

Reports the full threshold picture, including recall at a low false-positive rate
(the operationally important spam-filter metric) and the best-F1 operating point.
"""
from __future__ import annotations

import argparse
import time

from sklearn.metrics import confusion_matrix, roc_auc_score

from .evaluate import load_csv
from .model import EmailSpamDetector


def counts(labels, preds):
    tn, fp, fn, tp = confusion_matrix(labels, preds, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return tn, fp, fn, tp, fpr, recall, precision, f1


def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained model on an external test CSV.")
    parser.add_argument("model", help="path to the trained .joblib model")
    parser.add_argument("test_csv", help="labelled test CSV (raw_email,label) NOT used in training")
    parser.add_argument("--target-fpr", type=float, default=0.05,
                        help="acceptable false-positive rate for the operating point (default 0.05)")
    args = parser.parse_args()

    emails, labels = load_csv(args.test_csv)
    model = EmailSpamDetector.load(args.model)

    latencies, probs = [], []
    for email in emails:
        start = time.perf_counter()
        probs.append(model.predict(email).spam_probability)
        latencies.append(time.perf_counter() - start)
    latencies.sort()
    n_phish = sum(labels)

    print(f"\n=== External test set: {args.test_csv} ===")
    print(f"emails: {len(emails)}  ({n_phish} spam/phishing, {len(emails)-n_phish} legitimate)")
    try:
        print(f"ROC-AUC: {roc_auc_score(labels, probs):.3f}  (1.0 = perfect ranking; 0.5 = random)")
    except ValueError:
        pass

    print(f"\n{'threshold':>9} | {'spam caught':>11} | {'legit wrongly flagged':>22} | {'FPR':>5} | {'precision':>9} | {'F1':>5}")
    print("-" * 80)
    best_f1 = (-1, None)
    best_low_fpr = None
    for thr in [0.30, 0.40, 0.50, 0.55, 0.65, 0.75, 0.85, 0.90, 0.95, 0.98]:
        preds = [1 if p >= thr else 0 for p in probs]
        tn, fp, fn, tp, fpr, recall, precision, f1 = counts(labels, preds)
        print(f"{thr:>9.2f} | {tp:>4}/{tp+fn:<6} ({recall:4.0%}) | {fp:>4}/{fp+tn:<6} ({fpr:4.0%})        | {fpr:>5.2f} | {precision:>9.2f} | {f1:>5.2f}")
        if f1 > best_f1[0]:
            best_f1 = (f1, (thr, recall, precision, fpr, tp, fn, fp, tn))
        if fpr <= args.target_fpr and (best_low_fpr is None or recall > best_low_fpr[1]):
            best_low_fpr = (thr, recall, precision, fpr, tp, fn, fp, tn)

    print("-" * 80)
    thr, recall, precision, fpr, tp, fn, fp, tn = best_f1[1]
    print(f"Best balance (F1={best_f1[0]:.2f}): threshold {thr:.2f} -> catches {recall:.0%} of phishing, "
          f"flags {fpr:.0%} of legitimate, precision {precision:.2f}.")
    if best_low_fpr:
        thr, recall, precision, fpr, tp, fn, fp, tn = best_low_fpr
        print(f"At <= {args.target_fpr:.0%} false positives (real-world setting): threshold {thr:.2f} "
              f"-> still catches {recall:.0%} of phishing ({tp}/{tp+fn}), only {fp} legit email(s) flagged.")
    else:
        print(f"No threshold achieved <= {args.target_fpr:.0%} false positives on this set.")
    print(f"latency: p50 {latencies[len(latencies)//2]*1000:.1f} ms / p95 {latencies[int(len(latencies)*0.95)]*1000:.1f} ms")
    print("Note: body-only test emails can't use header metadata (sender/SPF); real mail scores those too.\n")


if __name__ == "__main__":
    main()
