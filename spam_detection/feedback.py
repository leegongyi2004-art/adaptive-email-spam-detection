"""Turn human corrections from the review queue into training data (feedback loop).

A reviewer only fills the `correct_label` column in the review queue CSV
(`review_queue.csv`) for messages the model got WRONG - typing `spam` or `ham`.
This script reads those corrections, pulls in the email content, and appends
them to a feedback CSV used for the next scheduled retrain:

    python -m spam_detection.feedback review_queue.csv

Then retrain on base data + feedback (the scheduled "adaptation" step):

    python -m spam_detection.evaluate data/reviewed_mail.csv data/feedback.csv \
        --save models/email_spam_detector.joblib

Only corrected rows are added - rows left blank mean the model was right and
nothing is needed. This is the same idea as Gmail learning from 'Report spam' /
'Not spam' clicks: labels come from people, and the model adapts on retrain.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

SPAM_WORDS = {"spam", "phish", "phishing", "1", "junk", "scam"}
HAM_WORDS = {"ham", "legit", "legitimate", "safe", "0", "not spam", "not-spam"}


def to_label(value: str) -> int | None:
    v = (value or "").strip().lower()
    if v in SPAM_WORDS:
        return 1
    if v in HAM_WORDS:
        return 0
    return None


def find_email(queue_path: Path, recorded: str) -> str | None:
    """Read the email text; if the recorded path is stale (file was moved to
    quarantine), try the same filename in the current/quarantine folders."""
    candidates = [Path(recorded)]
    name = Path(recorded).name
    candidates.append(queue_path.parent / "mail_quarantine" / name)
    candidates.append(queue_path.parent / name)
    for path in candidates:
        try:
            if path.is_file():
                return path.read_bytes().decode("utf-8", errors="replace")
        except OSError:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description="Convert review-queue corrections into feedback training data.")
    parser.add_argument("queue", help="review queue CSV produced by scan_mailbox (default review_queue.csv)",
                        nargs="?", default="review_queue.csv")
    parser.add_argument("--output", default="data/feedback.csv")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise SystemExit(f"Review queue not found: {queue_path}. Run scan_mailbox first.")

    with open(queue_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    corrections = [r for r in rows if (r.get("correct_label") or "").strip()]
    if not corrections:
        raise SystemExit("No corrections found. In the review queue CSV, type 'spam' or 'ham' in the "
                         "correct_label column only for rows the model got WRONG, then re-run.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    wrote = missing = badlabel = 0
    with open(out, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["raw_email", "label"])
        if out.stat().st_size == 0:
            writer.writeheader()
        for row in corrections:
            label = to_label(row.get("correct_label", ""))
            if label is None:
                badlabel += 1
                continue
            email = find_email(queue_path, row.get("file", ""))
            if email is None:
                missing += 1
                continue
            writer.writerow({"raw_email": email, "label": label})
            wrote += 1

    print(f"Reviewed rows: {len(rows)} | corrections: {len(corrections)}")
    print(f"Feedback written to {out}: {wrote} labelled emails.")
    if missing:
        print(f"WARNING: {missing} correction(s) could not find the email file (it may have been "
              "deleted/moved). Keep the .eml files available.")
    if badlabel:
        print(f"WARNING: {badlabel} correction(s) had an unrecognised label - use 'spam' or 'ham'.")
    if wrote:
        print("\nNext scheduled retrain (includes the feedback):")
        print(f"  python -m spam_detection.evaluate data/reviewed_mail.csv {out} "
              "--save models/email_spam_detector.joblib")


if __name__ == "__main__":
    main()
