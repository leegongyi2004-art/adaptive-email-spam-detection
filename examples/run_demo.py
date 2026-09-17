"""5-minute smoke test: train the baseline on the built-in demo data and try it.

Run from the project folder (with your venv activated):

    python examples/run_demo.py

This uses examples/demo_mail.csv (160 synthetic English emails - fake senders,
inert .example domains). It does NOT download anything and uses NO real email.
After it finishes you can start the API and it will use the trained model:

    uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spam_detection.evaluate import evaluate, load_csv, print_report  # noqa: E402

DEMO_CSV = ROOT / "examples" / "demo_mail.csv"
MODEL_OUT = ROOT / "models" / "email_spam_detector.joblib"

TRY_THESE = [
    (
        "From: sarah.chen@acme.example\n"
        "Subject: Re: quarterly report\n\n"
        "Hi, thanks for sending the draft. I left a couple of comments on page 4. "
        "Can we discuss on Tuesday? Best, Sarah"
    ),
    (
        "From: it.support@acme-helpdesk.example\n"
        "Reply-To: collector@webmail.example\n"
        "Subject: Action required: mailbox verification\n\n"
        "Dear valued user, our system has detected unusual activity on your email account. "
        "To prevent suspension, verify your identity within 24 hours by signing in at the "
        "secure portal below with your email address and password.\n\n"
        "Verify now: https://acme-helpdesk.example/secure\n\n"
        "This is an automated message from the IT services team."
    ),
]


def main():
    print("Loading demo dataset ...", DEMO_CSV)
    emails, labels = load_csv(str(DEMO_CSV))
    model, metrics = evaluate(emails, labels, threshold=0.55)
    print_report(dict(metrics))
    print("NOTE: these scores are on small synthetic demo data and are NOT meaningful\n"
          "performance numbers. Retrain on a real reviewed dataset for real results.\n")

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")

    print("\nTrying two example emails:\n")
    for i, raw in enumerate(TRY_THESE, 1):
        result = model.predict(raw)
        subject = next((line for line in raw.splitlines() if line.startswith("Subject: ")), "")
        print(f"--- Example {i} ---")
        print(subject)
        print(f"Prediction : {result.label.upper()} (spam probability {result.spam_probability:.2%})")
        if result.signals:
            print(f"Signals    : {result.signals}")
        print()

    print("Next: start the API with:  uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000")
    print("Then open http://127.0.0.1:8000/docs in your browser to test it.")


if __name__ == "__main__":
    main()
