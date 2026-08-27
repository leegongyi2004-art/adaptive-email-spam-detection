"""Feature extraction with no external network calls or private data transfer."""
from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser
from typing import Any
from urllib.parse import urlparse

SUSPICIOUS_TERMS = (
    "urgent", "verify", "password", "invoice", "wire transfer", "gift card",
    "click here", "suspended", "act now", "winner", "crypto",
)
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.IGNORECASE)


def _text(part: Any) -> str:
    """Extract plain message text, gracefully handling malformed email."""
    try:
        if part.is_multipart():
            return "\n".join(_text(p) for p in part.walk() if p.get_content_type() == "text/plain")
        if part.get_content_type() == "text/plain":
            return part.get_content() or ""
    except (LookupError, UnicodeError, ValueError):
        pass
    return ""


def parse_email(raw: str | bytes) -> dict[str, Any]:
    """Return normalized content and privacy-preserving structural metadata."""
    raw_bytes = raw.encode("utf-8", errors="replace") if isinstance(raw, str) else raw
    message = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    subject = str(message.get("Subject", ""))
    sender = str(message.get("From", ""))
    body = _text(message)
    if not body:
        body = raw_bytes.decode("utf-8", errors="replace")
    urls = URL_RE.findall(body)
    domains = {urlparse(u).netloc.lower() for u in urls if urlparse(u).netloc}
    sender_domain_match = EMAIL_RE.search(sender)
    sender_domain = sender_domain_match.group().rsplit("@", 1)[-1].lower() if sender_domain_match else ""
    auth_headers = " ".join(str(message.get(h, "")) for h in ("Authentication-Results", "Received-SPF", "DKIM-Signature"))
    return {
        "text": f"subject: {subject}\nbody: {body}",
        "metadata": {
            "subject_len": len(subject), "body_len": len(body), "url_count": len(urls),
            "unique_url_domains": len(domains), "attachment_count": len(list(message.iter_attachments())),
            "sender_has_domain": float(bool(sender_domain)),
            "sender_url_domain_mismatch": float(bool(domains and sender_domain and sender_domain not in domains)),
            "has_reply_to": float(bool(message.get("Reply-To"))),
            "spf_pass": float("spf=pass" in auth_headers.lower()),
            "dkim_present": float(bool(message.get("DKIM-Signature"))),
            "all_caps_ratio": sum(c.isupper() for c in subject) / max(len(subject), 1),
            "exclamation_count": (subject + body).count("!"),
            "suspicious_term_count": sum(term in (subject + " " + body).lower() for term in SUSPICIOUS_TERMS),
        },
    }
