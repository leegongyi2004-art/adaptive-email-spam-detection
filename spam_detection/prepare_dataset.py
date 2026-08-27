"""Convert common public phishing/spam CSVs into this project's raw_email,label format."""
from __future__ import annotations
import argparse, csv
from pathlib import Path

TEXT_COLUMNS = ("body", "email_body", "message", "text", "content", "email", "Email Text")
SUBJECT_COLUMNS = ("subject", "Subject", "email_subject")
FROM_COLUMNS = ("sender", "from", "From", "email_sender")
LABEL_COLUMNS = ("label", "Label", "class", "Class", "spam", "is_spam")
SPAM_VALUES = {"1", "spam", "phishing", "phish", "malicious", "true", "yes"}
HAM_VALUES = {"0", "ham", "legitimate", "safe", "benign", "false", "no"}

def choose(row, names): return next((row[n] for n in names if n in row and row[n]), "")
def normalise(value):
    v = str(value).strip().lower()
    if v in SPAM_VALUES: return 1
    if v in HAM_VALUES: return 0
    raise ValueError(f"Unrecognized label {value!r}; edit SPAM_VALUES/HAM_VALUES if required.")

def main():
    p = argparse.ArgumentParser(description="Prepare a public email CSV for model training.")
    p.add_argument("input_csv"); p.add_argument("output_csv", nargs="?", default="data/reviewed_mail.csv")
    args = p.parse_args(); Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    kept = skipped = 0
    with open(args.input_csv, encoding="utf-8-sig", newline="") as source, open(args.output_csv, "w", encoding="utf-8", newline="") as target:
        reader, writer = csv.DictReader(source), csv.DictWriter(target, fieldnames=["raw_email", "label"]); writer.writeheader()
        if not reader.fieldnames: raise SystemExit("Input must be a CSV with a header row.")
        for row in reader:
            body, label = choose(row, TEXT_COLUMNS), choose(row, LABEL_COLUMNS)
            if not body or not label: skipped += 1; continue
            try: normalized = normalise(label)
            except ValueError: skipped += 1; continue
            raw = f"From: {choose(row, FROM_COLUMNS)}\nSubject: {choose(row, SUBJECT_COLUMNS)}\n\n{body}"
            writer.writerow({"raw_email": raw, "label": normalized}); kept += 1
    print(f"Wrote {kept} usable rows to {args.output_csv}; skipped {skipped}. Inspect the first rows before training.")
if __name__ == "__main__": main()
