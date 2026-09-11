"""Scan a folder of email files (.eml/.txt): label, quarantine, log, and collect feedback.

This simulates a mail filter automatically processing incoming messages.

* One-shot report:     python -m spam_detection.scan_mailbox mail_inbox
* Auto-quarantine:     python -m spam_detection.scan_mailbox mail_inbox --action quarantine
* Live watch mode:     python -m spam_detection.scan_mailbox mail_inbox --action quarantine --watch
  (leave it running; drop new .eml files into the folder and they are scored immediately)

Every prediction is appended to a review queue CSV (default review_queue.csv) with a blank
`correct_label` column. A reviewer only fills that column for messages the model got wrong
(type `spam` or `ham`); then run `python -m spam_detection.feedback review_queue.csv` to turn
those corrections into training data for the next scheduled retrain.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import time
from datetime import datetime
from pathlib import Path

from .model import EmailSpamDetector

QUEUE_FIELDS = ["scanned_at", "file", "predicted_label", "spam_probability", "signals", "correct_label"]


def find_emails(folder: Path, quarantine: Path) -> list[Path]:
    files = []
    q = quarantine.resolve()
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".eml", ".txt"):
            if q not in path.resolve().parents:
                files.append(path)
    return files


def load_processed(queue_path: Path) -> set[str]:
    names = set()
    if queue_path.exists():
        with open(queue_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                names.add(Path(row["file"]).name)
    return names


def append_queue(queue_path: Path, row: dict) -> None:
    new = not queue_path.exists()
    with open(queue_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUEUE_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow(row)


def process_file(model, path: Path, args, quarantine: Path) -> dict:
    result = model.predict(path.read_bytes())
    signals = ", ".join(result.signals.keys()) if result.signals else "-"
    row = {
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "file": str(path),
        "predicted_label": result.label,
        "spam_probability": round(result.spam_probability, 4),
        "signals": signals,
        "correct_label": "",
    }
    if args.action == "quarantine" and result.label == "spam":
        quarantine.mkdir(parents=True, exist_ok=True)
        target = quarantine / path.name
        shutil.move(str(path), str(target))
        row["file"] = str(target)  # record where the file now lives
    return row


def main():
    parser = argparse.ArgumentParser(description="Scan a folder of emails for spam/phishing.")
    parser.add_argument("folder", help="folder containing .eml/.txt email files")
    parser.add_argument("--model", default="models/email_spam_detector.joblib")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--action", choices=["report", "quarantine"], default="report")
    parser.add_argument("--quarantine-dir", default="mail_quarantine")
    parser.add_argument("--queue", default="review_queue.csv", help="review/feedback queue CSV")
    parser.add_argument("--watch", action="store_true", help="keep running and process new mail as it arrives")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder} (put some .eml files in it first).")
    if not Path(args.model).exists():
        raise SystemExit(f"Model not found: {args.model}. Train it first (see GETTING_STARTED.md).")

    model = EmailSpamDetector.load(args.model)
    model.threshold = args.threshold
    quarantine = Path(args.quarantine_dir)
    queue_path = Path(args.queue)
    processed = load_processed(queue_path)

    def scan_once():
        files = [f for f in find_emails(folder, quarantine) if f.name not in processed]
        n_spam = n_ham = 0
        for path in files:
            row = process_file(model, path, args, quarantine)
            processed.add(path.name)
            append_queue(queue_path, row)
            is_spam = row["predicted_label"] == "spam"
            n_spam += is_spam
            n_ham += not is_spam
            flag = "SPAM " if is_spam else "ham  "
            move = "  -> quarantined" if (is_spam and args.action == "quarantine") else ""
            print(f"  [{flag}] {float(row['spam_probability'])*100:6.1f}%  {path.name}{move}")
        return n_spam, n_ham

    if args.watch:
        print(f"Watching {folder} every {args.poll_seconds}s. Drop .eml files in to scan them.")
        print(f"Predictions are logged to {queue_path}. Press Ctrl+C to stop.\n")
        try:
            total_spam = total_ham = 0
            while True:
                s, h = scan_once()
                total_spam += s
                total_ham += h
                if s or h:
                    print(f"  (running total: {total_spam} spam, {total_ham} legitimate)\n")
                time.sleep(args.poll_seconds)
        except KeyboardInterrupt:
            print(f"\nStopped. Review queue: {queue_path}")
            return

    # One-shot mode
    files = find_emails(folder, quarantine)
    if not files:
        raise SystemExit(f"No .eml/.txt files found in {folder}.")
    print(f"\nScanning {len(files)} email(s) from {folder} (threshold {args.threshold})\n")
    spam_count = ham_count = 0
    for path in files:
        row = process_file(model, path, args, quarantine)
        append_queue(queue_path, row)
        is_spam = row["predicted_label"] == "spam"
        spam_count += is_spam
        ham_count += not is_spam
        move = "  -> quarantined" if (is_spam and args.action == "quarantine") else ""
        print(f"  [{'SPAM ' if is_spam else 'ham  '}] {float(row['spam_probability'])*100:6.1f}%  {path.name}{move}")

    print(f"\nResult: {spam_count} spam/phishing, {ham_count} legitimate.")
    if args.action == "quarantine":
        print(f"Spam moved to: {quarantine.resolve()}")
    print(f"\nReview queue written to: {queue_path.resolve()}")
    print("To give feedback: open that CSV, type 'spam' or 'ham' in the correct_label column")
    print("only for rows the model got WRONG, save, then run:")
    print(f"  python -m spam_detection.feedback {queue_path}")


if __name__ == "__main__":
    main()
