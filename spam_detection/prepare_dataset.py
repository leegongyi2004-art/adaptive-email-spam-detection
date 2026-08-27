"""Convert public phishing/spam CSVs into this project's raw_email,label format.

Accepts one or more CSV files and/or folders (folders are scanned recursively
for *.csv), so a downloaded collection with several corpora (Enron, Ling,
SpamAssassin, CEAS, Nazario, Nigerian fraud, ...) can be converted in one run.
Duplicate emails across files are dropped automatically.

Usage:
    python -m spam_detection.prepare_dataset downloads --output data/reviewed_mail.csv
    python -m spam_detection.prepare_dataset downloads/enron.csv downloads/nazario.csv
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path

TEXT_COLUMNS = ("body", "email_body", "message", "text", "content", "email", "Email Text", "email_text", "raw")
SUBJECT_COLUMNS = ("subject", "Subject", "email_subject")
FROM_COLUMNS = ("sender", "from", "From", "email_sender")
LABEL_COLUMNS = ("label", "Label", "class", "Class", "spam", "is_spam", "Email Type", "email_type", "type", "category", "Category")
SPAM_VALUES = {"1", "spam", "phishing", "phish", "malicious", "true", "yes", "junk"}
HAM_VALUES = {"0", "ham", "legitimate", "safe", "benign", "false", "no"}


def choose(row, names):
    return next(
        (str(row[n]).strip() for n in names if n in row and row[n] and str(row[n]).strip().lower() not in ("nan", "none", "")),
        "",
    )


def normalise(value):
    v = str(value).strip().lower()
    if v in SPAM_VALUES:
        return 1
    if v in HAM_VALUES:
        return 0
    # Fallback for labels written as phrases, e.g. "Phishing Email" / "Safe Email".
    if any(token in v for token in ("phish", "spam", "malicious", "junk", "fraud", "scam")):
        return 1
    if any(token in v for token in ("safe", "ham", "legit", "benign", "normal")):
        return 0
    raise ValueError(f"Unrecognized label {value!r}; edit SPAM_VALUES/HAM_VALUES if required.")


def read_rows(path: Path):
    """Read a CSV as dicts, tolerating UTF-8 and latin-1 encodings."""
    last_error = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error


def gather_inputs(items: list[str], output: Path) -> list[Path]:
    files: list[Path] = []
    for item in items:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.csv")))
        elif path.is_file():
            files.append(path)
        else:
            print(f"WARNING: {item} was not found and was skipped.")
    resolved_output = output.resolve()
    return [f for f in files if f.resolve() != resolved_output]


def main():
    p = argparse.ArgumentParser(description="Prepare public email CSV(s) for model training.")
    p.add_argument("items", nargs="+", help="CSV file(s)/folder(s), and optionally the output CSV last")
    p.add_argument("--output", "-o", default=None, help="output CSV path (default: data/reviewed_mail.csv)")
    args = p.parse_args()

    # Backward-compatible shorthand: `prepare_dataset <input> <output.csv>`
    # i.e. exactly two positional items where the second ends in .csv and is
    # not an existing file/folder is treated as (input, output).
    if args.output is None:
        if len(args.items) >= 2 and args.items[-1].lower().endswith(".csv") and not Path(args.items[-1]).exists():
            args.output = args.items[-1]
            args.items = args.items[:-1]
        else:
            args.output = "data/reviewed_mail.csv"

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    files = gather_inputs(args.items, output)
    if not files:
        raise SystemExit("No CSV files found in the given locations.")

    seen: set[str] = set()
    total_kept = total_skipped = total_dupes = 0
    spam = ham = 0
    per_file: list[tuple[str, int, int, int]] = []

    with open(output, "w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["raw_email", "label"])
        writer.writeheader()
        for path in files:
            kept = skipped = dupes = 0
            try:
                rows = read_rows(path)
            except Exception as exc:  # noqa: BLE001 - report and continue with other files
                print(f"WARNING: could not read {path.name}: {exc}")
                per_file.append((path.name, 0, 0, 0))
                continue
            for row in rows:
                body, label = choose(row, TEXT_COLUMNS), choose(row, LABEL_COLUMNS)
                if not body or not label:
                    skipped += 1
                    continue
                try:
                    normalized = normalise(label)
                except ValueError:
                    skipped += 1
                    continue
                key = " ".join(body.split()).lower()
                if key in seen:
                    dupes += 1
                    continue
                seen.add(key)
                raw = f"From: {choose(row, FROM_COLUMNS)}\nSubject: {choose(row, SUBJECT_COLUMNS)}\n\n{body}"
                writer.writerow({"raw_email": raw, "label": normalized})
                kept += 1
                spam += normalized
                ham += 1 - normalized
            per_file.append((path.name, kept, skipped, dupes))
            total_kept += kept
            total_skipped += skipped
            total_dupes += dupes

    print(f"\n{'file':28s} {'kept':>8s} {'skipped':>8s} {'dupes':>8s}")
    print("-" * 56)
    for name, kept, skipped, dupes in per_file:
        print(f"{name[:28]:28s} {kept:>8d} {skipped:>8d} {dupes:>8d}")
    print("-" * 56)
    print(f"{'TOTAL':28s} {total_kept:>8d} {total_skipped:>8d} {total_dupes:>8d}")
    print(f"\nLabel balance: {ham} legitimate (0) / {spam} spam-or-phishing (1)")
    print(f"Wrote {total_kept} rows to {output}. Inspect the first rows in Excel before training.")
    if total_kept == 0:
        print("\nNothing was converted. Open one CSV and send me the FIRST ROW (column headings only).")
    elif ham == 0 or spam == 0:
        print("\nWARNING: only one class was found - the model needs BOTH legitimate and spam examples.")


if __name__ == "__main__":
    main()
