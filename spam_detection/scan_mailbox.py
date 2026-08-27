"""Scan a folder of email files (.eml/.txt) and label or quarantine them.

This simulates the system automatically processing incoming mail: drop message
files into a folder, run this, and spam is reported (and optionally moved to a
quarantine folder). Nothing is deleted; by default it only reports.

Examples:
    # Just print a report (safe, moves nothing):
    python -m spam_detection.scan_mailbox mail_inbox

    # Move spam into a quarantine folder (leaves legitimate mail in place):
    python -m spam_detection.scan_mailbox mail_inbox --action quarantine --quarantine-dir mail_quarantine
"""
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from .model import EmailSpamDetector


def find_emails(folder: Path, quarantine: Path) -> list[Path]:
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".eml", ".txt"):
            if quarantine.resolve() not in path.resolve().parents and path.parent != quarantine.resolve():
                files.append(path)
    return files


def main():
    parser = argparse.ArgumentParser(description="Scan a folder of emails for spam/phishing.")
    parser.add_argument("folder", help="folder containing .eml/.txt email files")
    parser.add_argument("--model", default="models/email_spam_detector.joblib")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--action", choices=["report", "quarantine"], default="report",
                        help="report = just list (default); quarantine = move spam files")
    parser.add_argument("--quarantine-dir", default="mail_quarantine")
    parser.add_argument("--report-csv", default="", help="optional path to write a CSV report")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder} (put some .eml files in it first).")
    if not Path(args.model).exists():
        raise SystemExit(f"Model not found: {args.model}. Train it first (see GETTING_STARTED.md).")

    quarantine = Path(args.quarantine_dir)
    files = find_emails(folder, quarantine)
    if not files:
        raise SystemExit(f"No .eml/.txt files found in {folder}.")

    model = EmailSpamDetector.load(args.model)
    model.threshold = args.threshold

    rows = []
    spam_count = ham_count = 0
    print(f"\nScanning {len(files)} email(s) from {folder} (threshold {args.threshold})\n")
    print(f"{'file':34s} {'verdict':9s} {'spam %':>7s}   signals")
    print("-" * 90)
    for path in files:
        raw = path.read_bytes()
        result = model.predict(raw)
        is_spam = result.label == "spam"
        spam_count += is_spam
        ham_count += not is_spam
        signals = ", ".join(result.signals.keys()) if result.signals else "-"
        print(f"{path.name[:34]:34s} {result.label.upper():9s} {result.spam_probability*100:6.1f}%   {signals}")
        rows.append({"file": str(path), "label": result.label,
                     "spam_probability": round(result.spam_probability, 4), "signals": signals})

        if args.action == "quarantine" and is_spam:
            quarantine.mkdir(parents=True, exist_ok=True)
            target = quarantine / path.name
            shutil.move(str(path), str(target))
            rows[-1]["moved_to"] = str(target)

    print("-" * 90)
    print(f"\nResult: {spam_count} spam/phishing, {ham_count} legitimate.")
    if args.action == "quarantine":
        print(f"Spam files were moved to: {quarantine.resolve()}")
    else:
        print("Report only (no files moved). Add --action quarantine to move spam into a folder.")

    if args.report_csv:
        report = Path(args.report_csv)
        report.parent.mkdir(parents=True, exist_ok=True)
        with open(report, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["file", "label", "spam_probability", "signals", "moved_to"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV report written to {report}")


if __name__ == "__main__":
    main()
