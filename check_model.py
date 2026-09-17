"""Diagnose a trained model: is it degenerate (predicting one class for everything)?"""
import sys
from spam_detection.model import EmailSpamDetector
path = sys.argv[1] if len(sys.argv) > 1 else "models/email_spam_detector.joblib"
m = EmailSpamDetector.load(path)
print(f"model: {path}")
print(f"threshold: {m.threshold}")
tests = {
 "obvious ham (meeting)": b"From: friend@gmail.com\r\nSubject: Meeting Tuesday\r\n\r\nHi, are we still on for the meeting Tuesday at 3pm?",
 "obvious ham (thanks)":  b"From: mum@gmail.com\r\nSubject: Dinner\r\n\r\nThanks for calling yesterday. See you on Sunday for dinner.",
 "obvious spam (lottery)": b"From: win@lotto.ru\r\nSubject: YOU WON $1,000,000\r\n\r\nClick http://claim.ru/x NOW and send your bank details urgently!",
 "obvious spam (phish)":  b"From: it@helpdesk.ru\r\nSubject: URGENT verify account\r\n\r\nYour account will be suspended. Verify password at http://secure-login.ru/verify",
}
probs = []
for k, v in tests.items():
    r = m.predict(v)
    probs.append(r.spam_probability)
    print(f"  {k:24s} -> {r.label:4s} {r.spam_probability:.4f}")
spread = max(probs) - min(probs)
print(f"\nspread between most-ham and most-spam: {spread:.4f}")
if spread < 0.05:
    print("VERDICT: DEGENERATE. The model outputs nearly the same score for everything.")
    print("         It must be retrained - see the instructions from the assistant.")
else:
    print("VERDICT: model discriminates normally.")
