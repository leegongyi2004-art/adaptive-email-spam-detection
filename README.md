# Adaptive Email Spam Detection

A local, open-source **content–metadata fusion** baseline for adaptive email spam detection. It turns raw RFC 5322 emails into:

- content features — word and character TF-IDF, resilient to obfuscation such as `v e r i f y`;
- metadata features — URL/attachment counts, reply-to presence, sender-to-URL domain mismatch, subject casing, and SPF/DKIM signals;
- a calibrated-style probability from a class-balanced logistic-regression classifier.

The implementation is deliberately lightweight, explainable, and deployable without sending mail to an external service. It is a strong operational baseline before introducing a larger transformer. It uses only open-source Python libraries (scikit-learn, FastAPI, joblib).

> **Safety note:** treat this as a triage signal, not the only control. Keep SPF/DKIM/DMARC enforcement, attachment sandboxing, URL reputation checks, and a human review path for high-impact mail decisions.

## Try it in five minutes (no dataset needed)

A synthetic demo dataset ships in the repo so you can verify the whole pipeline immediately:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python examples/run_demo.py         # trains on demo data, prints metrics, saves the model
python -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000   # then open /docs
```

The demo's perfect scores are on toy data only and are not real performance; see `GETTING_STARTED.md` for the real dataset route and Windows commands.

## Train from feedback

Create a CSV with `raw_email,label` columns. Labels are `0` for ham and `1` for spam. Use reviewed messages; do not train on a model's own unreviewed predictions.

```bash
python -m spam_detection.train reviewed_mail.csv --output models/email_spam_detector.joblib --threshold 0.55
```

Set the threshold from a held-out validation set to match your false-positive tolerance. Retrain on a scheduled, reviewed feedback batch and retain a validation set to detect drift.

## Integrate in Python

```python
from spam_detection.model import EmailSpamDetector

model = EmailSpamDetector.load("models/email_spam_detector.joblib")
result = model.predict(raw_rfc822_email)
print(result.label, result.spam_probability, result.signals)
```

`signals` identifies observed operational risk indicators, rather than claiming causal feature attribution.

## Serve an API

```bash
uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
```

`POST /predict` accepts `{ "raw_email": "From: ...\nSubject: ...\n\nBody" }` and returns the label, probability, confidence, and observed signals. Put the trained model at `models/email_spam_detector.joblib` (model files are ignored by Git).

## Test

```bash
pytest -q
```

## Upgrade path

For multilingual or semantically subtle social engineering, add a locally fine-tuned transformer content branch (recommended starting point: `distilbert-base-uncased`) while retaining the metadata branch and validating against your organization’s mail. Start with this baseline because it trains quickly on your own labeled mail, has lower serving cost, and provides a measurable comparison for any larger model.

See [EVALUATION_PLAN.md](EVALUATION_PLAN.md) for model parameters, a fusion architecture, AI-assisted phishing evaluation, Gmail-comparison claim boundaries, and a report-ready benchmark protocol.

## Need a guided setup?

Follow **[GETTING_STARTED.md](GETTING_STARTED.md)** from top to bottom. It includes the dataset format, exact commands, transformer training, fusion inference, and the four non-sensitive details to send back for tailoring.
