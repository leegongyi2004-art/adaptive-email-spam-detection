# PROJECT HANDOFF — Adaptive Email Spam Detection (FYP2)

**To continue in a new Arena chat:** paste this to the new agent —
> "I'm continuing my FYP adaptive email spam detection project. Read PROJECT_STATUS.md in
> the repo `leegongyi2004-art/adaptive-email-spam-detection`, branch
> `arena/01a038ce-adaptive-email-spam-detection`, and tell me my next step. I'm a beginner
> on Windows."

The user is a **student, beginner, time-limited (~10 days to FYP2 submission), English-only**,
on **Windows 11**. Give simple, explicit, copy-paste PowerShell steps. They do NOT run git.

---

## 1. Environment (their PC — do not change)
- Project folder: `C:\spam-project`. Python venv at `.venv` (prompt shows `(.venv)`).
- Python 3.13. **Intel UHD graphics — NO NVIDIA GPU** → transformer/Deep Learning must use
  **Google Colab** (notebook provided), never local GPU training.
- Smart App Control blocked scipy/sklearn DLLs; user turned it OFF and installed latest
  prebuilt scipy/scikit-learn — works now.
- VS Code terminal is used. All commands are run from `C:\spam-project` with `(.venv)` active.
- **File updates are delivered as raw GitHub downloads** (no git for the user):
  ```powershell
  Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leegongyi2004-art/adaptive-email-spam-detection/arena/01a038ce-adaptive-email-spam-detection/<path>" -OutFile "<local path>"
  ```

## 2. What the project is
Local, open-source **adaptive email spam/phishing detector using AI + content–metadata fusion**.
- **Baseline (classical ML):** word+char TF-IDF + 12 metadata signals → class-balanced
  Logistic Regression (`spam_detection/model.py`, `features.py`).
- Served via FastAPI (`spam_detection/api.py`) with a paste-and-check page at `/` that has
  **feedback buttons** writing `data/feedback.csv`.
- Adaptive loop: reviewed corrections → retrain. Demo `examples/demo_adaptive.py`.
- Mail auto-processing: `spam_detection/scan_mailbox.py` (report/quarantine/**watch** modes),
  feedback CLI `spam_detection/feedback.py`.
- Optional deep-learning branch: `spam_detection/transformer.py` + Colab notebook
  `notebooks/distilbert_colab.ipynb` (NOT run yet; optional/ future work unless scope demands it).
- Integration with live Gmail documented in `INTEGRATION_n8n.md` (n8n automation).

## 3. Dataset
Kaggle "Phishing Email Dataset" (CC BY-SA 4.0) = Enron/Ling/SpamAssassin (legit) +
CEAS_08/Nazario/Nigerian_Fraud (phish). Converted with `prepare_dataset.py` (folder mode,
dedup, long-CSV-field fix). Result in `data/reviewed_mail.csv`:
**81,152 unique emails = 39,234 legitimate + 41,918 phishing** (75/25 stratified split).
`phishing_email.csv` in that download is a redundant pre-merged copy (all rows duplicate → skipped).

## 4. RESULTS OBTAINED (real numbers — used in REPORT.md)
- **Main held-out test (81k):** accuracy **0.992**, precision 0.991, recall 0.992, F1 0.992,
  ROC-AUC 1.000, latency p50 ~16 ms / p95 ~41 ms CPU. Confusion: TP 10,399 / FN 80 / FP 90 /
  TN 9,719 (false-positive rate ≈ 0.9%). Adapted v2 re-run: accuracy 0.991 (unchanged).
- **Modern AI-style/BEC external test** (`examples/modern_test.csv`, 30 emails, NEVER trained on):
  - Model v1: ROC-AUC 0.81; at ≤5% FPR only 20% recall (miscalibrated at threshold 0.55).
  - **Model v2 after adaptive retrain** (81k + `examples/modern_feedback.csv`, 404 balanced
    reviewed examples, disjoint from test): **ROC-AUC 0.945; 85% phishing caught (17/20) with
    0 false positives** at threshold ~0.75. ← the "accuracy improves via adaptation" headline.
- **Qualitative AI-phishing demo** (`examples/test_ai_phishing.py`): **6/6 modern AI-style
  phishing caught**, incl. a no-link CEO wire-fraud BEC; 1 false positive (legit courier email)
  used to motivate adaptation/transformer.
- **UoT validation set** (Zenodo 13474746): only **100 unique emails repeated ~20×** (2000 rows),
  body-only/templated → small sanity check, NOT a headline result. ROC-AUC 0.96.
- Mechanism proof `examples/demo_adaptive.py`: a new crypto-airdrop scam goes 0/6 → 5/6 caught
  after one reviewed retraining cycle.

## 5. Framing rules (IMPORTANT — keep claims defensible)
- Model detects **phishing/spam INTENT**, NOT whether an email was AI-written (AI-authorship
  detectors are unreliable; cite NIST https://ai-challenges.nist.gov/text-2026).
- Do NOT claim "better than Gmail" overall. Google claims >99.9% blocked; a Gmail comparison is
  only a small, **supervisor-approved** black-box test on a disposable account with the same
  labelled set. Report as "on this controlled subset," never overall.
- Test sets are for SCORING only until reported; train on `reviewed_mail.csv` + reviewed
  feedback, never on the held-out test emails. (After reporting, mail may join future retrains,
  but always grade on fresh unseen mail.)
- Body-only external emails can't use header metadata; real mail has headers and scores better.
- Speed: report own latency (~16 ms, ~60 emails/s CPU); do not claim faster than Gmail.
- Cite supporting research: Phish-Master (LLM phishing evaded a campus filter ~99%, ML detector
  caught ~99.9% of LLM phishing) https://www.mdpi.com/2076-3417/15/22/12203 ; BEC-2 dataset
  https://link.springer.com/article/10.1007/s11416-024-00544-y

## 6. Files / commands (Windows)
```powershell
# train + evaluate baseline (already done) / retrain with feedback:
.venv\Scripts\python.exe -m spam_detection.evaluate data\reviewed_mail.csv --save models\email_spam_detector.joblib --threshold 0.55
.venv\Scripts\python.exe -m spam_detection.evaluate data\reviewed_mail.csv examples\modern_feedback.csv --save models\email_spam_detector_adapted.joblib --threshold 0.55

# score a model on an external held-out test CSV (prints threshold sweep + recall@<=5% FPR):
.venv\Scripts\python.exe -m spam_detection.evaluate_external models\email_spam_detector.joblib examples\modern_test.csv

# web app (paste/check + feedback buttons):
.venv\Scripts\python.exe -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000   # open http://127.0.0.1:8000/

# auto-process incoming mail folder / live watch + quarantine:
.venv\Scripts\python.exe -m spam_detection.scan_mailbox mail_inbox --action quarantine --watch

# demos:
.venv\Scripts\python.exe examples\run_demo.py
.venv\Scripts\python.exe examples\test_ai_phishing.py
.venv\Scripts\python.exe examples\demo_adaptive.py
```
Model artifacts (`models/*.joblib`) and data (`data/`, downloads) are gitignored — never commit them.

## 7. STATUS checklist
- [x] Full package, API + feedback UI, mailbox watch/quarantine, feedback→retrain loop.
- [x] Dataset converted (81,152); baseline trained (0.992); adaptive v1→v2 result (0.81→0.945).
- [x] AI-style/BEC detection demo (6/6); threshold-sweep evaluator; n8n + Colab docs.
- [x] **Full report draft written: `REPORT.md`** (Chapters 1–5, abstract, citations, real numbers).
- [ ] NEXT (user): open REPORT.md, copy into faculty template, add name/cover; tell the agent the
      faculty's required chapter list/template if they want reformatting.
- [ ] Optional extras (only if time/advisor wants):
  - Zenodo LLM-phishing set https://zenodo.org/records/20250116 (`cross-model-phishing.zip`,
    4,986 GPT-4/DeepSeek/LLaMA emails) → **test-only** scoring for a "catches X% of AI-generated
    phishing" number. First inspect columns (may be stylometric features, not raw text):
    `python -c "import csv,glob; [print('\nFILE:',f,'\n cols:',next(csv.reader(open(f,encoding='utf-8',errors='ignore')))) for f in glob.glob(r'downloads\**\*.csv',recursive=True)]"`
  - Authorised disposable-Gmail black-box comparison (ask advisor first).
  - DistilBERT via Colab (only if scope explicitly requires deep learning / neural network).
- [ ] Ask advisor: (1) ML-only sufficient or neural network required? (2) Gmail test allowed?
      (3) required report structure/length.

## 8. Known pitfalls already fixed (don't reintroduce)
- CSV 131 KB field limit → raised on package import (`spam_detection/__init__.py`).
- Metadata must be StandardScaled or raw lengths dominate TF-IDF.
- Malformed bracketed/IPv6 URLs crash urlparse → `features.py` has safe `_url_domain` + a
  crash-safe `parse_email` fallback.
- `TfidfVectorizer`/`DictVectorizer` import from `sklearn.feature_extraction(.text)`.
- `evaluate.py`/`train.py` accept multiple CSVs (base + feedback) via `load_many`.
- `prepare_dataset.py` handles folder input, dedupe (sha1), utf-8/latin-1, "Email Type" labels.
