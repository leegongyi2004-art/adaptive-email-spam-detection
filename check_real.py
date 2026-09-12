"""Score saved .eml messages and show exactly what the model sees.

Usage:
    python check_real.py                 newest 5 messages
    python check_real.py hardware        only messages whose text matches "hardware"
"""
import sys
from pathlib import Path
from spam_detection.model import EmailSpamDetector
from spam_detection.features import parse_email

needle = " ".join(sys.argv[1:]).lower()
m = EmailSpamDetector.load("models/email_spam_detector.joblib")
print(f"model: models/email_spam_detector.joblib   threshold: {m.threshold}")

files = sorted(Path("review_messages").glob("*.eml"),
               key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
    raise SystemExit("No .eml files in review_messages/ - run the scanner first.")

shown = 0
for f in files:
    raw = f.read_bytes()
    rec = parse_email(raw)
    if needle and needle not in rec["text"].lower():
        continue
    r = m.predict(raw)
    md = rec["metadata"]
    print(f"\n--- {f.name}  ({len(raw):,} bytes)  modified {f.stat().st_mtime:.0f} ---")
    print(f"  verdict : {r.label}  {r.spam_probability:.4f}")
    print(f"  body_len: {md['body_len']}   url_count: {md['url_count']}   "
          f"suspicious_terms: {md['suspicious_term_count']}   spf_pass: {md['spf_pass']}")
    print("  TEXT THE MODEL SEES (first 500 chars):")
    print("   ", repr(rec["text"][:500]))
    shown += 1
    if shown >= (20 if needle else 5):
        break

if not shown:
    print(f"\nNo saved message matched {needle!r}.")
