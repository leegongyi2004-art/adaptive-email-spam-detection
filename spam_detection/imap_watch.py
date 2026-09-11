"""Live-mailbox spam filter: connect to a real email account over IMAP, score new
messages automatically, and move spam to a quarantine folder.

This is the *live* version of scan_mailbox.py: instead of watching a local folder,
it connects to a real mailbox (Gmail, Outlook, a university account, etc.) using the
Internet Message Access Protocol (IMAP) — the same protocol email clients use to read
mail. Every new message is scored by the trained detector; spam is copied to a
quarantine folder and removed from the inbox, while legitimate mail is left in place.
Every decision is appended to the same review-queue CSV so reviewer corrections can
feed adaptive retraining.

SAFETY: the default action is "report" (read-only: it scores and logs but does NOT move
or delete anything). Only --action quarantine moves messages, and even then spam is
COPIED to a quarantine folder first (it is never permanently deleted).

------------------------------------------------------------------------------
ONE-TIME SETUP (Gmail example; Outlook/others are similar)
------------------------------------------------------------------------------
1. Use a TEST / throwaway account for the demo (not your main inbox).
2. Turn on 2-Step Verification for that Google account.
3. Create an "App password": Google Account -> Security -> 2-Step Verification ->
   App passwords -> generate one. Use that 16-character password below (NOT your
   normal login password). Gmail IMAP server: host imap.gmail.com, port 993.
   (Outlook/Hotmail: host outlook.office365.com, port 993, also use an app password.)

Credentials are read from command-line arguments or environment variables — never
hard-code a password. PowerShell examples:

    $env:IMAP_HOST="imap.gmail.com"
    $env:IMAP_USER="yourtestaddr@gmail.com"
    $env:IMAP_PASS="xxxxxxxxxxxxxxxx"      # the 16-char app password

Run a read-only check first (nothing is moved):
    python -m spam_detection.imap_watch --action report --watch

Then run the live auto-quarantine filter (leave it running, send it emails):
    python -m spam_detection.imap_watch --action quarantine --watch

Send a few normal emails and a few obvious phishing-style emails to the account and
watch them get scored; the phishing ones move to the "Spam_Quarantine" folder.
Press Ctrl+C to stop.
"""
from __future__ import annotations

import argparse
import imaplib
import os
import ssl
import time
from datetime import datetime
from pathlib import Path

from .model import EmailSpamDetector
from .scan_mailbox import append_queue

# Common providers so the user only needs the email address for these hosts.
PRESET_HOSTS = {
    "gmail.com": ("imap.gmail.com", 993),
    "googlemail.com": ("imap.gmail.com", 993),
    "outlook.com": ("outlook.office365.com", 993),
    "hotmail.com": ("outlook.office365.com", 993),
    "live.com": ("outlook.office365.com", 993),
    "yahoo.com": ("imap.mail.yahoo.com", 993),
}


def host_for(user: str, override: str | None, port: int) -> tuple[str, int]:
    if override:
        return override, port
    domain = user.split("@")[-1].lower().strip()
    if domain in PRESET_HOSTS:
        return PRESET_HOSTS[domain]
    raise SystemExit(
        f"Could not infer IMAP host for '@{domain}'. Pass --host and --port "
        f"(e.g. your provider's IMAP server, usually port 993)."
    )


def connect(host: str, port: int, user: str, password: str) -> imaplib.IMAP4_SSL:
    context = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(host, port, ssl_context=context)
    mail.login(user, password)
    return mail


def ensure_folder(mail: imaplib.IMAP4_SSL, folder: str) -> None:
    """Create the quarantine folder if it does not exist (ignore 'already exists')."""
    typ, _ = mail.create(folder)
    if typ not in ("OK", "NO"):  # NO here usually means the folder already exists
        print(f"  (note: could not create folder {folder!r}: {typ})")


def load_seen(state_path: Path) -> set[bytes]:
    if state_path.exists():
        return {line.strip().encode() for line in state_path.read_text().splitlines() if line.strip()}
    return set()


def mark_seen(state_path: Path, uid: bytes) -> None:
    with open(state_path, "a", encoding="utf-8") as f:
        f.write(uid.decode() + "\n")


def describe(raw: bytes) -> tuple[str, str]:
    """Return (sender, subject) as readable text for logging and display."""
    try:
        from email import policy
        from email.parser import BytesParser
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        sender = str(msg.get("From", "") or "(no sender)")
        subject = str(msg.get("Subject", "") or "(no subject)")
    except Exception:  # noqa: BLE001 - display only; never abort a scan
        sender, subject = "(unreadable)", "(unreadable)"
    return sender.strip(), " ".join(subject.split())


def fetch_new(mail: imaplib.IMAP4_SSL, seen: set[bytes],
              source_folder: str = "INBOX") -> list[tuple[bytes, bytes]]:
    """Return list of (uid, raw_rfc822_bytes) for messages not yet processed.

    ``source_folder`` allows scanning a folder other than the inbox. This matters
    for a live demonstration: the mail provider applies its own spam filter first,
    so test phishing messages are often placed in the provider's spam folder and
    never reach the inbox. Pointing the scanner at that folder (for Gmail,
    ``"[Gmail]/Spam"``) lets the classifier score those messages independently.
    """
    typ, _ = mail.select(source_folder)
    if typ != "OK":
        print(f"  (could not open folder {source_folder!r}; check the name with --list-folders)")
        return []
    typ, data = mail.uid("search", None, "ALL")
    if typ != "OK":
        return []
    uids = [u for u in data[0].split() if u not in seen]
    messages = []
    for uid in uids:
        typ, msg_data = mail.uid("fetch", uid, "(RFC822)")
        if typ == "OK" and msg_data and msg_data[0] and isinstance(msg_data[0], tuple):
            messages.append((uid, msg_data[0][1]))
    return messages


def quarantine_message(mail: imaplib.IMAP4_SSL, uid: bytes, folder: str) -> bool:
    """Copy the message to the quarantine folder, then remove the inbox copy."""
    ensure_folder(mail, folder)
    typ, _ = mail.uid("copy", uid, folder)
    if typ != "OK":
        return False
    mail.uid("store", uid, "+FLAGS", r"(\Deleted)")
    mail.expunge()
    return True


def process_once(mail, model, args, queue_path: Path, state_path: Path, seen: set[bytes]) -> tuple[int, int]:
    # Fetch everything first so moving/deleting later does not shift UIDs mid-loop.
    try:
        messages = fetch_new(mail, seen, args.source_folder)
    except imaplib.IMAP4Error as exc:
        print(f"  (connection issue: {exc}; will retry)")
        return 0, 0

    n_spam = n_ham = 0
    for uid, raw in messages:
        result = model.predict(raw)
        sender, subject = describe(raw)
        # Keep a local copy so a reviewer correction can be turned back into training
        # data: the review queue stores a path, and an IMAP message has no local file.
        saved = Path(args.save_dir) / f"imap_{uid.decode()}.eml"
        try:
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(raw)
            recorded = str(saved)
        except OSError:
            recorded = f"imap:{uid.decode()}"
        signals = ", ".join(result.signals.keys()) if result.signals else "-"
        is_spam = result.label == "spam"
        moved = False
        if is_spam and args.action == "quarantine":
            moved = quarantine_message(mail, uid, args.quarantine_folder)
        else:
            # Mark as read so it is not re-fetched; leave the message in the inbox.
            mail.uid("store", uid, "+FLAGS", r"(\Seen)")

        append_queue(queue_path, {
            "scanned_at": datetime.now().isoformat(timespec="seconds"),
            "file": recorded,
            "sender": sender,
            "subject": subject,
            "predicted_label": result.label,
            "spam_probability": round(result.spam_probability, 4),
            "signals": signals,
            "correct_label": "",
        })
        mark_seen(state_path, uid)
        seen.add(uid)

        n_spam += is_spam
        n_ham += not is_spam
        flag = "SPAM " if is_spam else "ham  "
        action = f"  -> moved to {args.quarantine_folder}" if moved else ""
        shown = subject if len(subject) <= 58 else subject[:55] + "..."
        print(f"  [{flag}] {result.spam_probability*100:6.1f}%  {shown}")
        print(f"                    from {sender}   (uid {uid.decode()}){action}")
    return n_spam, n_ham


def main():
    parser = argparse.ArgumentParser(description="Live IMAP mailbox spam filter (auto-score and quarantine).")
    parser.add_argument("--host", default=os.environ.get("IMAP_HOST"), help="IMAP server host (e.g. imap.gmail.com)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("IMAP_PORT", "993")))
    parser.add_argument("--user", default=os.environ.get("IMAP_USER"), help="full email address")
    parser.add_argument("--password", default=os.environ.get("IMAP_PASS"), help="app password (or use IMAP_PASS env var)")
    parser.add_argument("--model", default="models/email_spam_detector.joblib")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--action", choices=["report", "quarantine"], default="report",
                        help="report = read-only; quarantine = move spam to the quarantine folder")
    parser.add_argument("--quarantine-folder", default="Spam_Quarantine")
    parser.add_argument("--source-folder", default="INBOX",
                        help='folder to scan; use "[Gmail]/Spam" to score mail the '
                             "provider already filtered, or \"[Gmail]/All Mail\" for everything")
    parser.add_argument("--save-dir", default="review_messages",
                        help="folder where scanned messages are saved so corrections can be retrained")
    parser.add_argument("--list-folders", action="store_true",
                        help="print the mailbox folder names available on the server and exit")
    parser.add_argument("--queue", default="review_queue.csv", help="review/feedback queue CSV")
    parser.add_argument("--state", default="imap_seen.txt", help="local file tracking processed message IDs")
    parser.add_argument("--watch", action="store_true", help="keep running and process new mail as it arrives")
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    args = parser.parse_args()

    if not args.user or not args.password:
        raise SystemExit("Provide credentials with --user/--password or the IMAP_USER/IMAP_PASS "
                         "environment variables (use an app password, not your normal password).")
    if not Path(args.model).exists():
        raise SystemExit(f"Model not found: {args.model}. Train it first (see GETTING_STARTED.md).")

    host, port = host_for(args.user, args.host, args.port)
    model = EmailSpamDetector.load(args.model)
    model.threshold = args.threshold
    queue_path = Path(args.queue)
    # IMAP UIDs are unique only WITHIN a folder, so the processed-UID state must be
    # kept per folder; otherwise switching folders makes unrelated messages look seen.
    state_path = Path(args.state)
    if args.source_folder.upper() != "INBOX":
        safe = "".join(c if c.isalnum() else "_" for c in args.source_folder)
        state_path = state_path.with_name(f"{state_path.stem}_{safe}{state_path.suffix}")
    seen = load_seen(state_path)

    print(f"Connecting to {host}:{port} as {args.user} ...")
    mail = connect(host, port, args.user, args.password)
    if args.list_folders:
        typ, folders = mail.list()
        print("Folders available on this account:")
        for entry in (folders or []):
            if isinstance(entry, bytes):
                print("   " + entry.decode(errors="replace"))
        mail.logout()
        return
    print(f"Scanning folder: {args.source_folder}")
    print(f"Connected. Action = {args.action} "
          f"({'READ-ONLY' if args.action == 'report' else 'spam will be moved to ' + args.quarantine_folder}).")

    if not args.watch:
        mail.select("INBOX")
        s, h = process_once(mail, model, args, queue_path, state_path, seen)
        print(f"\nResult: {s} spam/phishing, {h} legitimate. Logged to {queue_path.resolve()}.")
        mail.logout()
        return

    print(f"Watching INBOX every {args.poll_seconds}s. Send emails to {args.user}; Ctrl+C to stop.\n")
    total_spam = total_ham = 0
    try:
        while True:
            try:
                s, h = process_once(mail, model, args, queue_path, state_path, seen)
                total_spam += s
                total_ham += h
                if s or h:
                    print(f"  (running total: {total_spam} spam, {total_ham} legitimate)\n")
            except (imaplib.IMAP4.error, OSError) as exc:
                print(f"  (reconnecting after error: {exc})")
                try:
                    mail.logout()
                except Exception:
                    pass
                time.sleep(args.poll_seconds)
                mail = connect(host, port, args.user, args.password)
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        print(f"\nStopped. Review queue: {queue_path.resolve()}")
        try:
            mail.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()
