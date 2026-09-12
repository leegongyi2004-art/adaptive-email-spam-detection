"""Demonstration helper: score live mailbox messages with the authentication
headers removed, so the corpus artefact described in Section 6.3 does not
dominate the verdict.

The public training corpus contains almost no legitimate mail carrying SPF or
DKIM headers, so the model associates their presence with spam. Every message
in a live Gmail mailbox carries them, which inflates scores. Removing those two
headers before scoring restores the content-based verdict. The model itself is
unchanged - this only affects what is shown in a live demonstration.

Usage:
    python demo_strip_auth.py                 score the newest 10 saved messages
    python demo_strip_auth.py meeting         only messages matching "meeting"
"""
import re
import sys
from pathlib import Path

from spam_detection.model import EmailSpamDetector
from spam_detection.features import parse_email

AUTH_RE = re.compile(
    rb"(?im)^(Authentication-Results|Received-SPF|DKIM-Signature|ARC-Seal|"
    rb"ARC-Message-Signature|ARC-Authentication-Results):.*(?:\r?\n[ \t].*)*\r?\n")


def strip_auth(raw: bytes) -> bytes:
    """Remove provider authentication headers before scoring."""
    return AUTH_RE.sub(b"", raw)


def main() -> None:
    needle = " ".join(sys.argv[1:]).lower()
    model = EmailSpamDetector.load("models/email_spam_detector.joblib")
    files = sorted(Path("review_messages").glob("*.eml"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit("No saved messages in review_messages/ - run the watcher first.")

    print(f"{'subject':52s} {'as received':>13s} {'content only':>14s}")
    print("-" * 82)
    shown = 0
    for f in files:
        raw = f.read_bytes()
        rec = parse_email(raw)
        if needle and needle not in rec["text"].lower():
            continue
        subject = rec["text"].split("\n", 1)[0].replace("subject: ", "")[:50]
        a = model.predict(raw)
        b = model.predict(strip_auth(raw))
        print(f"{subject:52s} {a.label:>5s} {a.spam_probability*100:6.1f}% "
              f"{b.label:>6s} {b.spam_probability*100:6.1f}%")
        shown += 1
        if shown >= 10:
            break


if __name__ == "__main__":
    main()
