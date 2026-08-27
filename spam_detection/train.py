"""Train from a CSV with `raw_email,label` columns, where label is 0/1."""
import argparse
import csv
from pathlib import Path
from .model import EmailSpamDetector

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--output", default="models/email_spam_detector.joblib")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    model = EmailSpamDetector(args.threshold).fit([r["raw_email"] for r in rows], [int(r["label"]) for r in rows])
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    print(f"trained on {len(rows)} messages; saved {args.output}")
if __name__ == "__main__": main()
