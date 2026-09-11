"""Demonstrate the trained detector on modern, AI-assisted-style phishing.

Run AFTER training the real model:

    python examples/test_ai_phishing.py

The emails below are SYNTHETIC, hand-written imitations of today's polished
phishing (calm tone, no typos, impersonates IT/HR/management - the style an AI
writing assistant produces). They are NOT real emails and use inert .example
domains. This shows the model flags modern social-engineering mail; it is not a
scientific claim that an email was AI-authored (no tool can prove that reliably).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spam_detection.model import EmailSpamDetector  # noqa: E402

MODEL_PATH = ROOT / "models" / "email_spam_detector.joblib"

# Polished, AI-style PHISHING (should be flagged spam).
AI_PHISHING = [
    ("From: it.support@company-helpdesk.example\nSubject: Scheduled security verification\n\n"
     "Hello, as part of our routine security maintenance, your account requires a brief "
     "verification to remain active. The process takes under a minute and helps us protect "
     "your data. Please confirm your credentials at your earliest convenience.\n\n"
     "Verify: https://company-helpdesk.example/secure\n\nKind regards, IT Services"),
    ("From: hr@company-portal.example\nSubject: Confidential document shared with you\n\n"
     "Good morning, a compensation review document has been prepared for your department. "
     "For privacy reasons it requires sign-in to view. Please review and acknowledge receipt "
     "by end of day.\n\nOpen document: https://company-portal.example/payroll\n\nHuman Resources"),
    ("From: ceo@company-exec.example\nSubject: Quick request while I travel\n\n"
     "Hi, I'm in back-to-back meetings and cannot take calls. I need you to arrange a payment "
     "for a vendor today. Reply to this email and I will send the account details. Please keep "
     "this discreet until processed. Thank you."),
    ("From: no-reply@microsoft-365-verify.example\nSubject: Action required: unusual sign-in\n\n"
     "We noticed a sign-in to your account from an unrecognised device. If this was you, no "
     "action is needed. Otherwise, secure your account now by confirming your identity.\n\n"
     "Review activity: https://microsoft-365-verify.example/auth\n\nMicrosoft account team"),
    ("From: ap@vendor-invoice.example\nSubject: Invoice 2026-4471 overdue\n\n"
     "Dear accounts, our records show invoice 2026-4471 remains outstanding. To avoid a pause "
     "in services, please settle today using the updated remittance details linked below and "
     "reply with confirmation.\n\nPay now: https://vendor-invoice.example/remit\n\nAccounts receivable"),
    ("From: delivery@secure-parcel.example\nSubject: Delivery update needed\n\n"
     "Your parcel is held pending a small address correction fee of $1.99. Update your details "
     "within 48 hours to avoid the parcel being returned.\n\n"
     "Continue: https://secure-parcel.example/track\n\nParcel support"),
]

# Modern LEGITIMATE mail (should pass ham) - some deliberately contain
# spam-like words to show the model is not just keyword matching.
LEGIT = [
    ("From: it.helpdesk@company.example\nSubject: Reminder: password expiry Friday\n\n"
     "Hi all, your network password expires this Friday. Change it via the official settings "
     "page on your work laptop (Settings > Account), not via any email link. The IT desk in "
     "Building B can help if needed. Thanks, IT"),
    ("From: ap@realcompany.example\nSubject: Invoice 4471 attached\n\n"
     "Hi, please find attached invoice 4471 for the September retainer, per our signed contract. "
     "Payment terms are net 30 to the bank account already on file. No action needed if already "
     "scheduled. Thanks, Accounts."),
    ("From: sarah.lee@company.example\nSubject: Re: security review\n\n"
     "Thanks for the heads-up. I verified with IT on the phone and the maintenance window is "
     "confirmed for Saturday. No one should click links in unsolicited emails - we'll announce "
     "everything on the intranet. See you Tuesday."),
    ("From: manager@company.example\nSubject: Re: vendor payment\n\n"
     "Let's discuss the vendor payment in our 2pm call rather than over email - I'd like finance "
     "on the line before we change any bank details. I'll book the room. Thanks."),
    ("From: hr@company.example\nSubject: Compensation reviews\n\n"
     "Reminder that compensation review meetings are scheduled with each manager next week. "
     "Salary details are discussed in person and never sent as links or attachments by email."),
    ("From: tracking@realcourier.example\nSubject: Your delivery is out for delivery\n\n"
     "Your parcel is out for delivery today and will arrive by 6pm. You can track it in our app. "
     "No payment is required; all fees were paid at checkout."),
]


def main():
    if not MODEL_PATH.exists():
        raise SystemExit("Train the real model first: python -m spam_detection.evaluate "
                         "data/reviewed_mail.csv --save models/email_spam_detector.joblib")
    model = EmailSpamDetector.load(MODEL_PATH)

    def run(emails, expected, label):
        correct = 0
        print(f"\n=== {label} ===")
        for raw in emails:
            r = model.predict(raw)
            got = r.label
            ok = (got == expected)
            correct += ok
            subject = next((l for l in raw.splitlines() if l.startswith("Subject:")), "")
            print(f"  [{'OK ' if ok else 'XX '}] p={r.spam_probability:6.2%} {got:5s}  {subject[9:]}")
        return correct, len(emails)

    p_caught, p_total = run(AI_PHISHING, "spam", "AI-style phishing (should all be SPAM)")
    h_pass, h_total = run(LEGIT, "ham", "Legitimate mail (should all be HAM)")

    print("\n=== Summary ===")
    print(f"AI-style phishing caught : {p_caught}/{p_total} ({p_caught/p_total:.0%})")
    print(f"Legitimate mail passed   : {h_pass}/{h_total} ({h_pass/h_total:.0%})")
    print("\nReminder: these are synthetic imitations; report this as an illustrative")
    print("demonstration, not a proof that the model detects 'AI-written' text as such.")


if __name__ == "__main__":
    main()
