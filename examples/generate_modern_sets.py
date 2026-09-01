"""Generate the modern-threat test/feedback sets for the AI-phishing experiments.

Run once (outputs are committed to the repo):

    python examples/generate_modern_sets.py

Produces:
  examples/modern_test.csv      - held-out modern threats (NEVER used to train)
  examples/modern_feedback.csv  - a reviewed batch of modern threats used to ADAPT

The two files are disjoint. All content is synthetic with inert .example domains.
These mimic modern, polished (AI-assisted-style) phishing and link-less business
email compromise (BEC), plus tricky legitimate mail that uses similar vocabulary.
"""
import csv
import itertools
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENDERS = ["it.support@helpdesk-verify.example", "security@account-verify.example",
           "hr@hr-document-portal.example", "accounts@invoice-payment.example",
           "ap@remit-vendor.example", "team@parcel-update.example",
           "admin@sharepoint-login.example", "notifications@cloud-storage-verify.example"]
SUBJECTS = ["Scheduled account verification", "Action required: unusual sign-in", "Your mailbox is nearly full",
            "Confidential document awaiting review", "Invoice {n} requires payment", "Updated payment details",
            "Please confirm your direct deposit", "Delivery address correction", "Your cloud storage is expiring",
            "Payment failed for order {n}", "Shared file needs review", "Security update for your account"]
LINKS = ["https://helpdesk-verify.example/confirm", "https://account-verify.example/secure",
         "https://hr-document-portal.example/share", "https://invoice-payment.example/remit",
         "https://parcel-update.example/track", "https://cloud-storage-verify.example/renew",
         "https://billing-verify.example/pay", "https://login-secure.example/auth"]
TEMPLATES = [
    "Hello, as part of routine security maintenance, your account needs a quick verification to stay active. "
    "The process takes about a minute and helps protect your data. Please confirm your credentials at your earliest convenience:\n\n{l}\n\nKind regards, IT Services",
    "We noticed a sign-in to your account from a device we do not recognise. If this was you, no action is needed. "
    "If not, please secure your account now:\n\n{l}\n\nThank you, Account security team",
    "Our records show your mailbox has reached its storage limit. To avoid interruption to incoming messages, "
    "verify your account within the next 24 hours:\n\n{l}\n\nThis is an automated notice.",
    "A confidential document has been prepared for you. For privacy reasons it requires sign-in to view. Please "
    "review and acknowledge receipt by end of day.\n\n{l}\n\nHuman Resources",
    "Dear accounts, invoice {n} is now outstanding. Please settle today using the updated remittance details in "
    "the payment portal and reply with confirmation so we can reconcile our records.\n\n{l}\n\nAccounts receivable",
    "We are updating our banking details for vendor payments. Please submit your next payment to the new account "
    "listed in the form below to avoid delays.\n\n{l}\n\nFinance department",
    "Action needed: please confirm your direct-deposit details so your next salary is routed correctly. Updates "
    "must be completed before payroll closes this week.\n\n{l}\n\nPayroll team",
    "Your parcel could not be delivered due to an incomplete address. A small redelivery fee is required to release "
    "the package within 48 hours.\n\n{l}\n\nParcel support",
    "Your cloud storage subscription has expired. Renew now to avoid losing access to shared files and backups.\n\n{l}\n\nCloud support",
    "Your recent purchase could not be completed because the payment did not go through. Update your card details "
    "within 24 hours so the order is not cancelled:\n\n{l}\n\nBilling services",
    "A file has been shared with you by a colleague. Sign in with your work email and password to open it; the link "
    "expires in 12 hours.\n\n{l}\n\nDocument services",
    "As part of our annual compliance check, all employees must confirm their login details this week. Accounts that "
    "are not verified will be disabled automatically.\n\n{l}\n\nCompliance team",
]
BEC = [
    "From: cfo@exec-team.example\nSubject: Quick request while I travel\n\nI am in back-to-back meetings and cannot take calls. I need you to process a vendor payment of $18,400 today. Reply to this email and I will send the account details. Please keep this discreet until processed.",
    "From: director@exec-team.example\nSubject: Gift cards for clients\n\nCan you pick up ten gift cards from the store on your way in? I will reimburse you. Send the codes to this email once purchased - it is for a client surprise and I am offsite all day.",
    "From: ceo@exec-team.example\nSubject: Re: wire transfer\n\nThanks for confirming. Please go ahead and transfer $42,000 to the new account I sent last night. The deal closes this afternoon so it is time sensitive - I will sign the paperwork tomorrow.",
    "From: it.manager@it-internal.example\nSubject: VPN credentials\n\nWe are doing an emergency VPN certificate rotation. Reply with your current username and password so we can pre-approve your device before the downtime tonight.",
    "From: hr.onboarding@company-internal.example\nSubject: New employee details\n\nPlease share your bank routing and account number by email so finance can set up your direct deposit before your first day; we complete this step outside the portal for speed.",
    "From: partner@legal-matter.example\nSubject: Urgent NDA and transfer\n\nThis acquisition is moving fast. Please wire the deposit and send the signed documents back to this email. Do not call my office line as I am in a confidential negotiation all week.",
    "From: ceo@exec-team.example\nSubject: Are you free\n\nI need a small favour urgently. My phone is about to die, so email only. I need to make a payment to a new supplier today - reply and I will forward the details. Strictly between us for now.",
    "From: payroll@hr-internal.example\nSubject: Re: reimbursement\n\nThere was an issue with the payroll file. Reply with your full bank account number and online banking log-in so we can verify and re-issue your bonus before the holiday.",
]
LEGIT = [
    "From: it.helpdesk@company.example\nSubject: Password expiry reminder\n\nHi all, your network password expires this Friday. Change it through Settings > Account on your work laptop, not via any email link. The IT desk in Building B can help. Thanks, IT.",
    "From: ap@company.example\nSubject: Invoice 4471 attached\n\nPlease find invoice 4471 for the September retainer attached, per our signed contract. Payment terms are net 30 to the bank account already on file. No new account details are needed.",
    "From: tracking@courier.example\nSubject: Out for delivery today\n\nYour parcel is out for delivery and should arrive by 6pm. Track it in the courier app. No payment is required - all fees were paid at checkout.",
    "From: hr@company.example\nSubject: Compensation reviews\n\nReminder that compensation review meetings happen with each manager next week. Salaries are discussed in person; we never ask for bank details or passwords by email.",
    "From: manager@company.example\nSubject: Re: vendor payment\n\nLet's discuss the vendor payment on our 2pm call rather than over email. Finance should confirm any bank change through the official portal, not on the strength of a message.",
    "From: colleague@company.example\nSubject: Re: contract\n\nThanks for the draft. I left comments in the shared document. We can go over them in Tuesday's review meeting.",
    "From: tracking@courier.example\nSubject: Scheduled delivery window\n\nYour parcel is scheduled between 9am and 1pm tomorrow. You will receive a separate text from the courier; no charges are due on delivery.",
    "From: payroll@company.example\nSubject: Payroll onboarding\n\nFor direct deposit setup, please complete the payroll form in the HR system under Onboarding. We never accept bank details by email for security reasons.",
    "From: it.helpdesk@company.example\nSubject: Security awareness reminder\n\nThis quarter's security training is open on the learning portal. Remember: IT will never ask you to email your password. Always verify money requests by phone or in person.",
    "From: sarah.lee@company.example\nSubject: Friday team lunch\n\nTeam lunch Friday at 12:30 in the cafeteria - no need to reply, just turn up. Let me know if you need a vegetarian option.",
    "From: finance@company.example\nSubject: Q3 budget draft\n\nThe budget draft is in the shared drive for our project. Numbers on the second tab are placeholders pending finance confirmation.",
    "From: colleague@company.example\nSubject: Re: presentation\n\nGreat presentation today. Could you send the source figures behind chart 4 when you have a moment? No rush - end of the week is fine.",
]


def gen_phish(n, combo_start, rng):
    combos = list(itertools.product(range(len(TEMPLATES)), range(len(LINKS))))
    rng.shuffle(combos)
    out = []
    i = 0
    while len(out) < n:
        ti, li = combos[(combo_start + i) % len(combos)]
        # vary subject/sender to keep repetitions distinct
        sender = rng.choice(SENDERS)
        subject = rng.choice(SUBJECTS).format(n=rng.randint(1000, 9999))
        body = TEMPLATES[ti].format(n=rng.randint(1000, 9999), l=LINKS[li])
        rt = "\nReply-To: collector@webmail.example" if rng.random() < 0.4 else ""
        out.append((f"From: {sender}{rt}\nSubject: {subject}\n\n{body}", 1))
        i += 1
    return out


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["raw_email", "label"])
        w.writerows(rows)


def main():
    test = []
    rng_t = random.Random(20240601)
    # test: 16 link-phish from the FIRST combo slice + first 4 BEC + first 10 legit
    test += gen_phish(16, 0, rng_t)
    test += [(e, 1) for e in BEC[:4]]
    test += [(LEGIT[i], 0) for i in range(10)]
    rng_t.shuffle(test)

    feedback = []
    rng_f = random.Random(19051990)
    # feedback: 96 link-phish starting AFTER the test slice + last 4 BEC + last 2 legit
    feedback += gen_phish(96, 30, rng_f)
    feedback += [(e, 1) for e in BEC[4:]]
    feedback += [(LEGIT[i], 0) for i in range(10, 12)]
    rng_f.shuffle(feedback)

    write(ROOT / "examples" / "modern_test.csv", test)
    write(ROOT / "examples" / "modern_feedback.csv", feedback)

    tb = {e for e, _ in test}
    fb = {e for e, _ in feedback}
    print(f"modern_test.csv    : {len(test)} rows ({sum(l for _, l in test)} phish)")
    print(f"modern_feedback.csv: {len(feedback)} rows ({sum(l for _, l in feedback)} phish)")
    print(f"duplicate emails across the two sets: {len(tb & fb)}")


if __name__ == "__main__":
    main()
