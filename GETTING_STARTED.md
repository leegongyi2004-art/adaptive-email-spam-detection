# Start here: get a result quickly

You do **not** need to understand all of the code to begin. Follow this order. Do not use real employee/customer email without your supervisor's approval; remove unnecessary personal data and keep the dataset local.

## 0. Five-minute demo (Windows, no downloads)

This proves everything works on your PC before you touch any dataset.

1. Install Python 3.10 or newer from https://www.python.org/downloads/ — tick **"Add python.exe to PATH"** during install.
2. Open **PowerShell** in the project folder (in File Explorer: hold Shift, right-click the folder, "Open PowerShell window here"), then run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe examples\run_demo.py
```

The demo trains on 800 **synthetic** emails that ship in the repo (`examples/demo_mail.csv` — fake senders, inert `.example` domains), prints evaluation numbers, tries two example emails, and saves a working model to `models/email_spam_detector.joblib`.

> The demo's 100% scores are on toy data and are **not** real performance — they just prove the pipeline runs. Real numbers come from step 3 onward.

3. Start the API and try it in your browser:

```powershell
.venv\Scripts\python.exe -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs → click **POST /predict** → **Try it out** → paste an email into `raw_email` → **Execute**. You will get back `spam`/`ham`, a probability, and the signals that fired. Press Ctrl+C to stop the server.

Once that works, swap in real data below.

## 1. Set up once

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-transformer.txt   # only for the transformer stage (step 4)
```

(Linux/macOS: activate with `source .venv/bin/activate`.)

## 2. Make your reviewed dataset

Create `data/reviewed_mail.csv` with exactly these columns. Each `raw_email` value is a complete raw email; CSV line breaks must be quoted. `0` means legitimate/ham and `1` means spam or phishing.

```csv
raw_email,label
"From: support@yourcompany.example\nSubject: Project meeting\n\nYour meeting is at 10am.",0
"From: reset@lookalike.example\nReply-To: collect@evil.example\nSubject: Urgent account verification\n\nClick https://example.invalid/login now.",1
```

Aim for at least 500 examples of each class for a prototype; more diverse, **human-reviewed** data is much better. Keep the newest 20% in a separate `data/test_mail.csv` file and do not use it to select parameters.

## 3. Train and evaluate the fast baseline first

```powershell
# Train on 75% of the data, test on the held-out 25%, print metrics, then save:
.venv\Scripts\python.exe -m spam_detection.evaluate data\reviewed_mail.csv --save models\email_spam_detector.joblib --threshold 0.55
```

This prints accuracy, precision, recall, F1, ROC-AUC, the confusion matrix, and per-message latency (p50/p95) — exactly the numbers your report needs. It must succeed before you continue; it gives you a usable local model even if the transformer takes too long. (To just train without the report, use `python -m spam_detection.train data\reviewed_mail.csv --output models\email_spam_detector.joblib`.)

## 4. Train the Transformer (optional, needs the transformer requirements)

```powershell
.venv\Scripts\python.exe -m spam_detection.train_transformer data\reviewed_mail.csv --output models\distilbert-email --max-length 256 --epochs 3 --batch-size 8
```

The first run downloads the open model (~66M parameters, ~250 MB); later runs use the local saved model. On CPU this can take hours for a large dataset; an NVIDIA GPU makes it minutes. The saved `models/distilbert-email/training_config.json` records your settings and validation loss for the report. Skip this step entirely until your baseline works.

### No NVIDIA GPU? Use the Google Colab notebook (free T4 GPU)

If your machine only has Intel/AMD integrated graphics, don't train DistilBERT locally. Use
`notebooks/distilbert_colab.ipynb`:

1. Upload `data/reviewed_mail.csv` to your Google Drive.
2. Open [colab.research.google.com](https://colab.research.google.com) → **File > Upload notebook** → choose `notebooks/distilbert_colab.ipynb`.
3. **Runtime > Change runtime type > T4 GPU**, then run the cells top to bottom (Shift+Enter).

It installs everything on the Colab machine, fine-tunes on a balanced 24k subset (~20–30 min),
prints a held-out report, and reruns the AI-style phishing test through the transformer. The
trained model is saved back to your Google Drive.

## 5. Try one email locally

```python
from spam_detection.model import EmailSpamDetector
from spam_detection.transformer import TransformerEmailDetector
from spam_detection.fusion import FusionEmailDetector

baseline = EmailSpamDetector.load("models/email_spam_detector.joblib")
transformer = TransformerEmailDetector("models/distilbert-email", max_length=256)
model = FusionEmailDetector(baseline, transformer, baseline_weight=.4, transformer_weight=.6, threshold=.55)

raw = "From: sender@example.com\nSubject: Hello\n\nYour message here"
result = model.predict(raw)
print(result)
```

The `spam_probability` is a risk score—not proof that a message was AI-written. Start with `.55`; select the final threshold only after measuring false positives on the validation set.

## 6. Run the basic API

```powershell
.venv\Scripts\python.exe -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
```

Then open http://127.0.0.1:8000/docs for an interactive test page (POST /predict → Try it out).

The existing `/predict` API serves the fast baseline from `models/email_spam_detector.joblib`. Once you have reviewed the results, we can expose the final fusion model in the API with the threshold you approve.

## What to send back for feedback

Tell me:

1. your operating system and whether you have an NVIDIA GPU;
2. how many legitimate and spam emails you have, and their current file format (do **not** paste private email content);
3. whether the emails are English only or multilingual;
4. your desired action for a high-risk email: label only, quarantine, or reject.

Then I can adjust the data-import path, model size, labels, threshold, and API response without needing access to your private messages.

## Fastest public-data route (English, Windows)

The project does **not** contain a training dataset yet; it is code waiting for labeled email. For a fast academic prototype, download the **Phishing Email Dataset** CSV from Kaggle, which describes roughly 82,500 combined samples from Enron, Ling, CEAS, Nazario, Nigerian Fraud, and SpamAssassin sources and is published under CC BY-SA 4.0. Record its version, licence, and citation in your report. [Dataset page](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset/)

The download contains **several CSVs** (enron, ling, spamassassin, ceas_08, nazario, nigerian_fraud, phishing_email). Keep them all — the legitimate corpora (enron/ling/spamassassin) and the phishing corpora (ceas/nazario/nigerian_fraud/phishing_email) are both needed so the model learns each class. Put the extracted files in a `downloads` folder, then convert the **whole folder at once** (it combines them, drops duplicates, and prints a per-file table):

```powershell
.venv\Scripts\python.exe -m spam_detection.prepare_dataset downloads --output data\reviewed_mail.csv
.venv\Scripts\python.exe -m spam_detection.evaluate .\data\reviewed_mail.csv --save .\models\email_spam_detector.joblib --threshold 0.55
.venv\Scripts\python.exe -m spam_detection.train_transformer .\data\reviewed_mail.csv --output .\models\distilbert-email --max-length 256 --epochs 3 --batch-size 8
```

The converter prints a `kept / skipped / dupes` table per file and a final `X legitimate / Y spam` balance. If a file shows a large **skipped** count, open that CSV and send me the **column headings only** (not email content) so I can add its format.

Before training, open `data/reviewed_mail.csv` in Excel and verify it has `raw_email,label`, both labels occur, and no sensitive local data was included. The converter recognizes common columns (`body`, `text`, `Email Text`, `subject`, `sender`, `label`, `class`). If it reports many skipped rows, send me the **column headings only**, not the email content, and I will adapt it.
