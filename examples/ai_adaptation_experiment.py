"""Adaptive-retraining experiment on AI-generated phishing (Objective 4).

WHAT THIS PROVES
----------------
The deployed model is trained ONLY on the classic public corpus, so AI-generated
phishing is an unseen threat. This experiment measures the catch rate on AI mail
BEFORE adaptation, then adds a SMALL reviewed feedback batch of AI phishing to the
training data, retrains, and measures the catch rate again ON THE SAME HELD-OUT
AI TEST SET.

The AI corpus is split into two DISJOINT parts:
  * feedback split  - a small batch that simulates reviewer-corrected mistakes;
                      this IS added to training.
  * held-out split  - the evaluation set; this is NEVER trained on, before or after.

Because the held-out rows are never trained on, the "after" number is still an
honest generalisation result - it is not memorisation of the test data.

USAGE
-----
    python examples/ai_adaptation_experiment.py ^
        --base data/reviewed_mail.csv ^
        --ai data/llm_test.csv ^
        --feedback-fraction 0.2

Both CSVs need `raw_email,label` columns (label 1 = spam/phishing, 0 = legitimate).
A phishing-only AI file is fine: catch rate (recall) is the metric reported.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spam_detection.model import EmailSpamDetector  # noqa: E402


def load_csv(path: str) -> tuple[list[str], list[int]]:
    csv.field_size_limit(10_000_000)
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))
    if not rows or "raw_email" not in rows[0] or "label" not in rows[0]:
        raise SystemExit(f"{path} must have 'raw_email' and 'label' columns.")
    emails, labels = [], []
    for r in rows:
        text = (r.get("raw_email") or "").strip()
        raw_label = (r.get("label") or "").strip().lower()
        if not text or raw_label == "":
            continue
        label = 1 if raw_label in {"1", "spam", "phishing", "phish"} else 0
        emails.append(text)
        labels.append(label)
    return emails, labels


def catch_rate(model: EmailSpamDetector, emails, labels, threshold: float):
    """Return (recall on phishing rows, false-positive rate on legitimate rows)."""
    model.threshold = threshold
    tp = fn = fp = tn = 0
    latencies = []
    for text, truth in zip(emails, labels):
        start = time.perf_counter()
        pred = model.predict(text)
        latencies.append((time.perf_counter() - start) * 1000)
        is_spam = pred.label == "spam"
        if truth == 1:
            tp += is_spam
            fn += not is_spam
        else:
            fp += is_spam
            tn += not is_spam
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0.0
    return recall, fpr, tp, fn, fp, tn, p50


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="main training CSV (raw_email,label)")
    parser.add_argument("--ai", required=True, help="AI-generated phishing CSV (raw_email,label)")
    parser.add_argument("--feedback-fraction", type=float, default=0.2,
                        help="fraction of the AI set used as the reviewed feedback batch (default 0.2)")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save-before", default="", help="optional path to save the base model")
    parser.add_argument("--save-after", default="", help="optional path to save the adapted model")
    args = parser.parse_args()

    if not 0.0 < args.feedback_fraction < 1.0:
        raise SystemExit("--feedback-fraction must be between 0 and 1")

    print("Loading data ...")
    base_emails, base_labels = load_csv(args.base)
    ai_emails, ai_labels = load_csv(args.ai)
    print(f"  base training corpus : {len(base_emails):,} emails")
    print(f"  AI-generated corpus  : {len(ai_emails):,} emails")

    # --- disjoint split of the AI corpus -------------------------------------
    rng = random.Random(args.seed)
    index = list(range(len(ai_emails)))
    rng.shuffle(index)
    cut = int(len(index) * args.feedback_fraction)
    fb_idx, test_idx = index[:cut], index[cut:]

    fb_emails = [ai_emails[i] for i in fb_idx]
    fb_labels = [ai_labels[i] for i in fb_idx]
    test_emails = [ai_emails[i] for i in test_idx]
    test_labels = [ai_labels[i] for i in test_idx]

    print(f"\nAI corpus split (disjoint, seed {args.seed}):")
    print(f"  reviewed feedback batch : {len(fb_emails):,}  (added to training in step 2)")
    print(f"  held-out AI test set    : {len(test_emails):,}  (NEVER trained on)")

    # --- step 1: base model, no AI mail seen ---------------------------------
    print("\n" + "=" * 78)
    print("STEP 1 - BASE MODEL (trained on the classic corpus only; no AI mail seen)")
    print("=" * 78)
    base_model = EmailSpamDetector(args.threshold).fit(base_emails, base_labels)
    if args.save_before:
        base_model.save(args.save_before)
    r0, fpr0, tp0, fn0, fp0, tn0, p50_0 = catch_rate(base_model, test_emails, test_labels, args.threshold)
    print(f"  AI phishing caught : {tp0:,}/{tp0 + fn0:,}  ({r0:.1%})")
    if (fp0 + tn0):
        print(f"  false-positive rate: {fpr0:.2%} on AI legitimate mail")
    print(f"  latency            : p50 {p50_0:.1f} ms/email")

    # --- step 2: adapt with the reviewed feedback batch ----------------------
    print("\n" + "=" * 78)
    print("STEP 2 - ADAPTIVE RETRAIN (base corpus + reviewed AI feedback batch)")
    print("=" * 78)
    adapted_model = EmailSpamDetector(args.threshold).fit(
        base_emails + fb_emails, base_labels + fb_labels)
    if args.save_after:
        adapted_model.save(args.save_after)
    print(f"  retrained on {len(base_emails) + len(fb_emails):,} emails "
          f"({len(base_emails):,} base + {len(fb_emails):,} reviewed)")

    # --- step 3: re-measure on the SAME held-out AI test set -----------------
    print("\n" + "=" * 78)
    print("STEP 3 - RE-EVALUATE ON THE SAME HELD-OUT AI TEST SET")
    print("=" * 78)
    r1, fpr1, tp1, fn1, fp1, tn1, p50_1 = catch_rate(adapted_model, test_emails, test_labels, args.threshold)
    print(f"  AI phishing caught : {tp1:,}/{tp1 + fn1:,}  ({r1:.1%})")
    if (fp1 + tn1):
        print(f"  false-positive rate: {fpr1:.2%} on AI legitimate mail")
    print(f"  latency            : p50 {p50_1:.1f} ms/email")

    # --- summary table for the report ----------------------------------------
    print("\n" + "=" * 78)
    print("SUMMARY  (paste these numbers into the report table)")
    print("=" * 78)
    print(f"{'Model':<34} | {'AI phishing caught':>19} | {'catch rate':>10}")
    print("-" * 70)
    print(f"{'Before adaptation (no AI seen)':<34} | {f'{tp0:,}/{tp0 + fn0:,}':>19} | {r0:>9.1%}")
    print(f"{'After adaptive retraining':<34} | {f'{tp1:,}/{tp1 + fn1:,}':>19} | {r1:>9.1%}")
    print("-" * 70)
    print(f"{'Improvement':<34} | {'':>19} | {r1 - r0:>+9.1%}")
    print(f"\nHeld-out AI test rows were never used for training in either step "
          f"(threshold {args.threshold}).")
    print("Re-run the main evaluation on the base corpus to confirm the adapted model")
    print("maintains its accuracy on ordinary mail before deploying it.\n")


if __name__ == "__main__":
    main()
