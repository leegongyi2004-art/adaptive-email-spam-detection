"""Score the .eml files the IMAP scanner actually saved, and show what the model sees.

Run:  python check_real.py
This reads real messages from review_messages/ rather than synthetic test strings,
so it reproduces exactly what the scanner did.
"""
import sys
from pathlib import Path
from spam_detection.model import EmailSpamDetector
from spam_detection.features import parse_email

model_path = sys.argv[1] if len(sys.argv) > 1 else "models/email_spam_detector.joblib"
m = EmailSpamDetector.load(model_path)
print(f"model: {model_path}   threshold: {m.threshold}")

files = sorted(Path("review_messages").glob("*.eml"))[:6]
if not files:
    raise SystemExit("No .eml files in review_messages/ - run the scanner first.")

for f in files:
    raw = f.read_bytes()
    rec = parse_email(raw)
    r = m.predict(raw)
    md = rec["metadata"]
    print(f"\n--- {f.name}  ({len(raw):,} bytes) ---")
    print(f"  verdict : {r.label}  {r.spam_probability:.4f}")
    print(f"  body_len: {md['body_len']}   url_count: {md['url_count']}   "
          f"suspicious_terms: {md['suspicious_term_count']}")
    print(f"  TEXT THE MODEL SEES (first 300 chars):")
    print("   ", repr(rec["text"][:300]))
