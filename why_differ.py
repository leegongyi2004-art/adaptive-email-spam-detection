"""Find WHY a saved message scores differently from the same text pasted in the console.

Usage:  python why_differ.py hardware      (or any word from the subject)

It scores the saved .eml, then strips one thing at a time to see what moves the score.
"""
import sys, re
from pathlib import Path
from email import policy
from email.parser import BytesParser
from spam_detection.model import EmailSpamDetector
from spam_detection.features import parse_email

needle = " ".join(sys.argv[1:]).lower()
m = EmailSpamDetector.load("models/email_spam_detector.joblib")

files = sorted(Path("review_messages").glob("*.eml"),
               key=lambda p: p.stat().st_mtime, reverse=True)
target = None
for f in files:
    if not needle or needle in parse_email(f.read_bytes())["text"].lower():
        target = f; break
if target is None:
    raise SystemExit(f"No saved message matched {needle!r}")

raw = target.read_bytes()
print(f"file: {target.name}\n")

def show(label, data):
    r = m.predict(data); md = parse_email(data)["metadata"]
    print(f"  {label:42s} {r.label:4s} {r.spam_probability*100:6.2f}%   "
          f"spf={md['spf_pass']:.0f} dkim={md['dkim_present']:.0f} "
          f"reply_to={md['has_reply_to']:.0f} urls={md['url_count']}")

show("1. saved file exactly as received", raw)

# Strip authentication headers only
no_auth = re.sub(rb"(?im)^(Authentication-Results|Received-SPF|DKIM-Signature|ARC-[^:]+):.*(?:\r?\n[ \t].*)*\r?\n",
                 b"", raw)
show("2. same, minus SPF/DKIM/ARC headers", no_auth)

# Rebuild as a minimal message: From + Subject + extracted body (what you paste)
msg = BytesParser(policy=policy.default).parsebytes(raw)
body = ""
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_content(); break
else:
    body = msg.get_content() or ""
minimal = (f"From: {msg.get('From','')}\r\nSubject: {msg.get('Subject','')}\r\n\r\n{body}").encode()
show("3. From + Subject + body (the paste box)", minimal)

print("\nIf 1 and 2 differ  -> the authentication metadata is driving it.")
print("If 2 and 3 differ  -> the remaining headers / MIME structure are driving it.")
