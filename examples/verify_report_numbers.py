"""Verify the headline numbers printed in the report against the actual data.

This script only MEASURES. It never edits the report, the model or any dataset.
Run it, read the summary, and change the report only where a number differs.

    python examples/verify_report_numbers.py

Optional arguments let you point at files in other locations:

    python examples/verify_report_numbers.py --base data/reviewed_mail.csv ^
        --llm data/llm_test.csv --uot data/uot_test.csv

Each check is independent: if a file is missing the check is reported as
SKIPPED and the remaining checks still run.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,  # noqa: E402
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split  # noqa: E402

from spam_detection.model import EmailSpamDetector  # noqa: E402

REPORT = {
    "corpus_total": 81152,
    "holdout": 20288,
    "accuracy": 0.992,
    "precision": 0.991,
    "recall": 0.992,
    "f1": 0.992,
    "roc_auc": 1.000,
    "fpr": 0.009,
    "llm_catch": 0.92,
    "adapt_auc_before": 0.81,
    "adapt_auc_after": 0.945,
    "adapt_recall_before": 0.20,
    "adapt_recall_after": 0.85,
}


def load_csv(path: Path):
    csv.field_size_limit(10_000_000)
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))
    emails, labels = [], []
    for r in rows:
        text = (r.get("raw_email") or "").strip()
        lab = (r.get("label") or "").strip().lower()
        if not text or not lab:
            continue
        emails.append(text)
        labels.append(1 if lab in {"1", "spam", "phishing", "phish"} else 0)
    return emails, labels


def verdict(name: str, measured, claimed, tol: float) -> str:
    if measured is None:
        return f"  {name:<26} SKIPPED"
    ok = abs(measured - claimed) <= tol
    mark = "MATCHES " if ok else "DIFFERS "
    return (f"  {name:<26} report {claimed:<8.3f} measured {measured:<8.3f} {mark}"
            + ("" if ok else "  <-- update the report"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="data/reviewed_mail.csv")
    ap.add_argument("--llm", default="data/llm_test.csv")
    ap.add_argument("--uot", default="data/uot_test.csv")
    ap.add_argument("--threshold", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    lines: list[str] = []
    base_model = None

    # ---- Check 1: the main held-out evaluation --------------------------------
    print("\n" + "=" * 76)
    print("CHECK 1  Main held-out evaluation (Table 6.1)")
    print("=" * 76)
    base_path = Path(args.base)
    if not base_path.exists():
        print(f"  SKIPPED - {base_path} not found.")
    else:
        emails, labels = load_csv(base_path)
        print(f"  corpus rows: {len(emails):,}   (report claims {REPORT['corpus_total']:,})")
        x_tr, x_te, y_tr, y_te = train_test_split(
            emails, labels, test_size=0.25, random_state=args.seed, stratify=labels)
        print(f"  held-out rows: {len(x_te):,}   (report claims {REPORT['holdout']:,})")
        print("  training ... (this is the slow part)")
        base_model = EmailSpamDetector(args.threshold).fit(x_tr, y_tr)
        probs = [base_model.predict(e).spam_probability for e in x_te]
        preds = [1 if p >= args.threshold else 0 for p in probs]
        tn, fp, fn, tp = confusion_matrix(y_te, preds, labels=[0, 1]).ravel()
        lines += [
            verdict("accuracy", accuracy_score(y_te, preds), REPORT["accuracy"], 0.003),
            verdict("precision", precision_score(y_te, preds, zero_division=0), REPORT["precision"], 0.003),
            verdict("recall", recall_score(y_te, preds, zero_division=0), REPORT["recall"], 0.003),
            verdict("F1", f1_score(y_te, preds, zero_division=0), REPORT["f1"], 0.003),
            verdict("ROC-AUC", roc_auc_score(y_te, probs), REPORT["roc_auc"], 0.003),
            verdict("false-positive rate", fp / (fp + tn) if (fp + tn) else 0.0, REPORT["fpr"], 0.004),
        ]
        for line in lines:
            print(line)
        print(f"  confusion matrix: TN={tn:,}  FP={fp:,}  FN={fn:,}  TP={tp:,}")

        # latency
        sample = x_te[:400]
        times = []
        for e in sample:
            t0 = time.perf_counter()
            base_model.predict(e)
            times.append((time.perf_counter() - t0) * 1000)
        times.sort()
        print(f"  latency: p50 {statistics.median(times):.1f} ms   "
              f"p95 {times[int(len(times) * 0.95)]:.1f} ms   (n={len(times)})")

    # ---- Check 2: AI-generated phishing catch rate ----------------------------
    print("\n" + "=" * 76)
    print("CHECK 2  AI-generated phishing catch rate (Table 6.3)")
    print("=" * 76)
    llm_path = Path(args.llm)
    if base_model is None or not llm_path.exists():
        print(f"  SKIPPED - needs a trained model and {llm_path}.")
    else:
        e_llm, y_llm = load_csv(llm_path)
        probs = [base_model.predict(e).spam_probability for e in e_llm]
        print(f"  rows: {len(e_llm):,}   phishing: {sum(y_llm):,}")
        for th in (0.30, 0.40, 0.50, 0.55):
            caught = sum(1 for p in probs if p >= th)
            print(f"    threshold {th:.2f}: caught {caught:,}/{len(probs):,} = {caught / len(probs):.1%}")
        best = sum(1 for p in probs if p >= args.threshold) / len(probs)
        print(verdict("catch rate @ threshold", best, REPORT["llm_catch"], 0.02))

    # ---- Check 3: adaptation before/after on the clean holdout ---------------
    print("\n" + "=" * 76)
    print("CHECK 3  Adaptation before/after (Table 6.4)")
    print("=" * 76)
    uot_path = Path(args.uot)
    fb_path = ROOT / "examples" / "modern_feedback.csv"
    test_path = ROOT / "examples" / "modern_test.csv"
    if not test_path.exists() or base_path.exists() is False:
        print("  SKIPPED - needs the base corpus and examples/modern_test.csv.")
    else:
        e_test, y_test = load_csv(test_path)
        e_fb, y_fb = load_csv(fb_path) if fb_path.exists() else ([], [])
        emails, labels = load_csv(base_path)
        x_tr, _, y_tr, _ = train_test_split(
            emails, labels, test_size=0.25, random_state=args.seed, stratify=labels)

        def score(model, e, y):
            probs = [model.predict(t).spam_probability for t in e]
            preds = [1 if p >= args.threshold else 0 for p in probs]
            auc = roc_auc_score(y, probs) if len(set(y)) > 1 else float("nan")
            return auc, recall_score(y, preds, zero_division=0)

        print("  training baseline ...")
        m0 = base_model if base_model is not None else EmailSpamDetector(args.threshold).fit(x_tr, y_tr)
        a0, r0 = score(m0, e_test, y_test)
        print("  retraining with the reviewed feedback batch ...")
        m1 = EmailSpamDetector(args.threshold).fit(x_tr + e_fb, y_tr + y_fb)
        a1, r1 = score(m1, e_test, y_test)
        print(f"  BEFORE  ROC-AUC {a0:.3f}   recall {r0:.1%}")
        print(f"  AFTER   ROC-AUC {a1:.3f}   recall {r1:.1%}")
        print(verdict("adapt AUC before", a0, REPORT["adapt_auc_before"], 0.03))
        print(verdict("adapt AUC after", a1, REPORT["adapt_auc_after"], 0.03))
        print(verdict("adapt recall before", r0, REPORT["adapt_recall_before"], 0.05))
        print(verdict("adapt recall after", r1, REPORT["adapt_recall_after"], 0.05))
        if uot_path.exists():
            e_u, y_u = load_csv(uot_path)
            au0, ru0 = score(m0, e_u, y_u)
            au1, ru1 = score(m1, e_u, y_u)
            print(f"\n  Same comparison on {uot_path.name} (separate holdout):")
            print(f"    BEFORE  ROC-AUC {au0:.3f}   recall {ru0:.1%}")
            print(f"    AFTER   ROC-AUC {au1:.3f}   recall {ru1:.1%}")
            print("    (If adaptation does not improve this set, report that honestly:")
            print("     a baseline that is already near-perfect leaves no headroom.)")

    print("\n" + "=" * 76)
    print("Every line marked DIFFERS is a number to change in the report.")
    print("Lines marked MATCHES are confirmed and need no edit.")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
