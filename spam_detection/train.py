"""Train from CSV(s) with `raw_email,label` columns, where label is 0/1.

Multiple CSVs can be given (e.g. base data plus reviewed feedback):
    python -m spam_detection.train data/reviewed_mail.csv data/feedback.csv --output models/email_spam_detector.joblib
"""
import argparse
import csv
from pathlib import Path
from .model import EmailSpamDetector
from .evaluate import load_many


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="+", help="CSV file(s) with raw_email,label columns")
    parser.add_argument("--output", default="models/email_spam_detector.joblib")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    emails, labels = load_many(args.csv)
    model = EmailSpamDetector(args.threshold).fit(emails, labels)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    print(f"trained on {len(emails)} messages; saved {args.output}")


if __name__ == "__main__":
    main()
