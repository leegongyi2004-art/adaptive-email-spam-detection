# Project Status & Handoff Notes

**Hand this to a fresh assistant chat to continue.** It records exactly where the
user (a student, Windows 11, beginner, time-constrained) is in the project.

## What this is
An **adaptive email spam / phishing detector using AI + content–metadata fusion**:
- **Baseline (classical ML):** TF-IDF word + character features + structural/metadata
  features -> class-balanced Logistic Regression (`spam_detection/model.py`).
- **Deep learning branch (optional):** fine-tuned `distilbert-base-uncased`
  (`spam_detection/transformer.py`, `spam_detection/train_transformer.py`).
- **Fusion (`spam_detection/fusion.py`):** weighted late-fusion of the two.
- Served via FastAPI (`spam_detection/api.py`); trained baseline is at
  `models/email_spam_detector.joblib` (gitignored).

All training is local/offline; no real/private emails used.

## User's environment (their PC — do not change these facts)
- Windows 11, project folder `C:\spam-project`, venv at `.venv` (activate prompt `(.venv)`).
- Python 3.13. **Intel UHD Graphics — NO NVIDIA GPU.**
  → Do NOT ask them to train DistilBERT locally (hours on CPU). Use **Google Colab**
  free GPU for the transformer stage, or keep it optional.
- **Smart App Control was blocking scipy/scikit-learn DLLs**; user turned it off and
  `pip install` of latest scipy/scikit-learn (prebuilt wheels) then worked.
- VS Code terminal is used; user pastes PowerShell commands and reports output.
- Do not tell them to run Git commands; updates are delivered as raw GitHub file
  downloads via `Invoke-WebRequest ... raw.githubusercontent.com/leegongyi2004-art/.../arena/01a038ce-adaptive-email-spam-detection/<file>`.

## Dataset
Kaggle "Phishing Email Dataset" (naserabdullahalam), ~82k emails from Enron/Ling/
SpamAssassin/CEAS_08/Nazario/Nigerian_Fraud. Downloaded to `C:\spam-project\downloads\`
as separate CSVs. Converted with:
`python -m spam_detection.prepare_dataset downloads --output data\reviewed_mail.csv`
Result: **81,152 unique, balanced emails (39,234 legitimate / 41,918 phishing)**
at `data\reviewed_mail.csv`. (`phishing_email.csv` is the redundant pre-merged copy;
its rows are all duplicates and get skipped — expected.)

## Progress checkpoints (all completed on GitHub branch `arena/01a038ce-...`)
- [x] Package code: model, features, api, train, fusion, transformer, train_transformer.
- [x] `prepare_dataset.py`: folder combine + dedupe + long-CSV-field fix + label mapping.
- [x] `evaluate.py`: held-out metrics (accuracy/precision/recall/F1/ROC-AUC/latency/confusion).
- [x] Demo data + `examples/run_demo.py` (verified working on the user's PC).
- [x] Metadata StandardScaler bug fix (raw lengths were dominating TF-IDF).
- [x] CSV long-field limit raised on package import (`spam_detection/__init__.py`).
- [ ] **IMMEDIATE NEXT STEP (user was about to do this when blocked):**
      run baseline training/evaluation on real data:
      `python -m spam_detection.evaluate data\reviewed_mail.csv --save models\email_spam_detector.joblib --threshold 0.55`
      (offline, ~5–15 min CPU; keep laptop awake). Collect the metrics table.
- [ ] Tune threshold on validation; optionally test the live API via `uvicorn`.
- [ ] Deep-learning stage on **Google Colab** (no local GPU): give notebook cells.
- [ ] Build a small set of **AI-assisted phishing test emails** to demonstrate detection;
      report findings defensively (do NOT overclaim "better than Gmail"; see EVALUATION_PLAN.md).
- [ ] Final **report/documentation** using the printed metrics.

## Fixed pitfalls (don't re-introduce)
- `DictVectorizer`/`TfidfVectorizer` import from `sklearn.feature_extraction.text` /
  `sklearn.feature_extraction` directly.
- Always call the CSV field-limit helper for files with long email bodies.
- Model artifacts and `data/` are gitignored — never commit the dataset or .joblib.
- Keep claims honest: `spam_probability` is a risk score, not proof an email was AI-written.

## Key commands (Windows, in `C:\spam-project` with `(.venv)` active)
```powershell
# update one helper file from GitHub (change the filename)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leegongyi2004-art/adaptive-email-spam-detection/arena/01a038ce-adaptive-email-spam-detection/spam_detection/<FILE>.py" -OutFile "spam_detection\<FILE>.py"

# train + evaluate the baseline (NEXT)
.venv\Scripts\python.exe -m spam_detection.evaluate data\reviewed_mail.csv --save models\email_spam_detector.joblib --threshold 0.55

# serve the API, then open http://127.0.0.1:8000/docs
.venv\Scripts\python.exe -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
```
