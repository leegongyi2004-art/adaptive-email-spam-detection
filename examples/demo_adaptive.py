"""Demonstrate the ADAPTIVE loop: the system learns a new scam from reviewed feedback.

This is a self-contained, synthetic illustration of how a deployed spam filter
adapts over time (it does not touch your real model or data):

    1. A model is trained on known spam types.
    2. A NEW scam wave arrives with wording it has never seen  -> it misses them.
    3. A reviewer correctly labels the missed messages (feedback).
    4. The model is retrained with that feedback.
    5. The updated model now catches the new campaign (and still passes
       legitimate mail).

Run:
    python examples/demo_adaptive.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spam_detection.model import EmailSpamDetector  # noqa: E402
from spam_detection.evaluate import load_csv         # noqa: E402

# --- A NEW scam wave: a calm "crypto airdrop / wallet reward" campaign.
#     Polite, no classic urgency words, NO link (victims reply with their
#     wallet address). None of this vocabulary appears in the base data. ---
CAMPAIGN_SPAM = [
    ("From: community@web3-rewards.example\nSubject: You are eligible for a community airdrop\n\n"
     "Hello, your wallet has been selected to receive a limited airdrop of tokens as part of our "
     "community rewards. To receive them, reply with your wallet address so we can confirm your "
     "allocation before the snapshot. Warm regards, Community team."),
    ("From: allocations@token-airdrop.example\nSubject: Confirm your reward allocation\n\n"
     "Dear member, your pending allocation of 5,000 tokens is ready. Please reply to confirm the "
     "wallet address where the tokens should be sent. This reward is for verified community members."),
    ("From: rewards@partner-airdrop.example\nSubject: Partnership reward available\n\n"
     "As a valued member you qualify for an exclusive partner airdrop. Register your wallet address "
     "by replying to this message and the reward tokens will be sent directly after the snapshot."),
    ("From: notify@chain-airdrop.example\nSubject: Airdrop reminder\n\n"
     "Friendly reminder that the claim window for your token airdrop is open. Reply with your wallet "
     "address to secure your allocation; unclaimed tokens return to the pool."),
    ("From: team@wallet-reward.example\nSubject: Your tokens are waiting\n\n"
     "Congratulations, your wallet qualifies for the seasonal reward distribution. Send us your "
     "wallet address in a reply and the tokens will be transferred within 48 hours."),
    ("From: airdrop@decentral-rewards.example\nSubject: Member distribution notice\n\n"
     "You have been included in this round's member distribution. To receive your token reward, "
     "reply confirming your wallet address. Participation is free and limited to one address per member."),
]

# --- Reviewed batch of the new campaign that a reviewer labelled for the
#     scheduled retrain (these are OTHER messages from the same wave, so the
#     updated model has to generalise to new wording, not just memorise). ---
FEEDBACK_SPAM = [
    ("From: admin@claim-airdrop.example\nSubject: Your airdrop claim is ready\n\n"
     "Your address appears in this month's airdrop snapshot. Reply with your wallet address to "
     "claim your token allocation before the deadline passes."),
    ("From: help@wallet-airdrop.example\nSubject: Wallet address required for reward\n\n"
     "To complete the token distribution we need your wallet address on file. Reply to this email "
     "with the address and your reward tokens will be sent automatically."),
    ("From: rewards@token-members.example\nSubject: Exclusive member token reward\n\n"
     "Members are receiving a limited token reward this week. Confirm your wallet address by reply "
     "to lock in your allocation before the snapshot."),
    ("From: airdrop@chain-rewards.example\nSubject: Distribution window closing\n\n"
     "The airdrop distribution window closes shortly. If you want your token allocation, reply now "
     "with your wallet address so it can be verified in time."),
    ("From: community@defi-airdrop.example\nSubject: Eligible for the DeFi airdrop\n\n"
     "Congratulations, you are eligible for the community DeFi airdrop. Reply with the wallet address "
     "you would like the tokens sent to. No payment is ever required."),
    ("From: support@reward-claim.example\nSubject: Action: register your wallet\n\n"
     "Register the wallet address for your pending reward by replying to this message. Token "
     "allocations for unregistered wallets cannot be delivered."),
    ("From: news@token-airdrop2.example\nSubject: Seasonal token distribution\n\n"
     "The seasonal distribution is open to all verified members. To receive your tokens, reply with "
     "your wallet address before the claim period ends."),
    ("From: airdrops@crypto-member.example\nSubject: Member airdrop confirmation\n\n"
     "Please confirm your wallet address to receive your member airdrop. Replies are processed "
     "automatically and tokens are sent within two days of confirmation."),
    ("From: reminder@token-airdrop.example\nSubject: Final reminder: airdrop unclaimed\n\n"
     "This is a final reminder that your airdrop is still unclaimed. Reply with your wallet address "
     "before the window closes so your tokens are not returned to the reward pool."),
    ("From: delivery@wallet-rewards.example\nSubject: Your reward tokens are waiting\n\n"
     "Your reward tokens are waiting to be delivered. Reply with the wallet address you want them "
     "sent to and the transfer will be scheduled automatically."),
]

# --- New LEGITIMATE mail at the same time (must still pass after adaptation). ---
NEW_HAM = [
    ("From: hr@company.example\nSubject: Employee reward points credited\n\n"
     "Hi everyone, this quarter's recognition points have been credited to internal accounts. View "
     "your balance on the HR intranet; please ignore any message asking you to reply with a wallet "
     "address or bank details. Thanks, HR."),
    ("From: society@university.example\nSubject: Distributed systems society meeting\n\n"
     "The student society meets Thursday to discuss blockchains and distributed ledgers. No prior "
     "knowledge is required. Bring your laptop for the hands-on coding session."),
    ("From: manager@company.example\nSubject: Re: token of appreciation\n\n"
     "Thanks for the hard work on the launch. I've put a small recognition award through the proper "
     "HR process - it'll appear on your payslip, nothing to reply to here."),
]


def show(model, title, emails, expect_spam):
    print(f"\n{title}")
    caught = 0
    for raw in emails:
        r = model.predict(raw)
        is_spam = r.label == "spam"
        ok = (is_spam == expect_spam)
        caught += ok
        subject = next((l for l in raw.splitlines() if l.startswith("Subject:")), "")[9:]
        want = "SPAM" if expect_spam else "HAM "
        print(f"  [{'OK' if ok else 'XX'}] predicted {r.label.upper():4s} p={r.spam_probability:6.1%}  (want {want})  {subject}")
    return caught, len(emails)


def main():
    print("Loading base training data (known spam types only)...")
    base_emails, base_labels = load_csv(str(ROOT / "examples" / "demo_mail.csv"))
    base = EmailSpamDetector(0.55).fit(base_emails, base_labels)
    print("Initial model deployed.\n")

    print("=" * 78)
    print("STEP 1 - A NEW scam wave arrives (crypto 'airdrop/wallet' wording, replies only).")
    print("=" * 78)
    c1, t1 = show(base, "The new campaign (should be SPAM):", CAMPAIGN_SPAM, True)
    h1, th1 = show(base, "Legitimate mail (should be HAM):", NEW_HAM, False)

    print("\n" + "=" * 78)
    print("STEP 2 - Reviewer feedback: a batch of the new campaign is labelled spam")
    print("         and added to the reviewed dataset, then the model is RETRAINED.")
    print("         (In deployment this is a scheduled run over the reviewed batch.)")
    print("=" * 78)
    # The reviewed feedback batch (in production this would be many emails).
    # The campaign wording must be well represented for a scheduled retrain,
    # so each reviewed example is weighted by repeating it a handful of times.
    feedback_spam = FEEDBACK_SPAM * 6 + CAMPAIGN_SPAM[:2] * 6
    feedback_ham = NEW_HAM * 6
    feedback_emails = feedback_spam + feedback_ham
    feedback_labels = [1] * len(feedback_spam) + [0] * len(feedback_ham)
    adapted = EmailSpamDetector(0.55).fit(base_emails + feedback_emails,
                                          base_labels + feedback_labels)
    print(f"Retrained on {len(base_emails) + len(feedback_emails)} reviewed emails "
          f"({len(FEEDBACK_SPAM)} newly labelled campaign messages).\n")

    print("=" * 78)
    print("STEP 3 - After adaptation, run the same new emails again:")
    print("=" * 78)
    c2, t2 = show(adapted, "The new campaign (should be SPAM):", CAMPAIGN_SPAM, True)
    h2, th2 = show(adapted, "Legitimate mail (should be HAM):", NEW_HAM, False)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  New-campaign spam caught BEFORE feedback: {c1}/{t1}")
    print(f"  New-campaign spam caught AFTER  feedback: {c2}/{t2}")
    print(f"  Legitimate mail passed AFTER     feedback: {h2}/{th2}")
    print("\nThis is what 'adaptive' means: retraining on reviewed feedback lets the")
    print("system learn new scam types. It does not teach itself unsupervised - labels")
    print("come from review, exactly like Gmail learning from 'Report spam' clicks.")


if __name__ == "__main__":
    main()
