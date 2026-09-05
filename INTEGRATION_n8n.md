# Connecting real email to the detector with n8n (no coding)

This is the deployment/integration layer. The detector already runs as a web API
(`POST /predict`). **n8n** is free, open-source automation software that can watch a
Gmail (or any IMAP) mailbox and call that API for every new message, then act on the
result — so users do not manually copy emails in.

> Status / scope: this is an **integration**, not part of the core ML project. It needs
> your own Google account and runs n8n locally. Only connect test/non-sensitive mail for
> your FYP; do not route other people's private email without approval.

## The architecture (for your report)

```
 Gmail inbox
     │  (new email trigger)
     ▼
   n8n workflow
     │  POST /predict  { raw_email: "From: ...\nSubject:...\n\nbody" }
     ▼
 Spam Detector API  ──► { label, spam_probability, signals }
     │
     ├─ label == "spam"  → n8n adds label "SPAM-REVIEW" / moves it / forwards to quarantine
     └─ label == "ham"   → leave it
     ▼
 reviewer corrects mistakes (web UI / review queue) → feedback → scheduled retrain
```

This matches real-world mail filtering: the ML model scores mail, automation enforces a
policy, and human feedback drives adaptation.

## Option A — Gmail + n8n (simplest, free)

1. **Install Docker Desktop** (Windows): https://www.docker.com/products/docker-desktop
   (n8n runs most reliably this way).
2. Start n8n locally:
   ```powershell
   docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
   ```
   Open http://localhost:5678 and create a free local account.
3. Make sure your detector API is running (in another terminal):
   ```powershell
   .venv\Scripts\python.exe -m uvicorn spam_detection.api:app --host 0.0.0.0 --port 8000
   ```
4. In n8n create a workflow with these nodes:
   - **Gmail Trigger** node: sign in with your Google account; set it to trigger on new
     email ("On Message Received"). n8n uses Google OAuth for you.
   - **HTTP Request** node: method `POST`, URL `http://host.docker.internal:8000/predict`,
     body type JSON, body:
     ```json
     { "raw_email": "From: {{ $json.from }}\nSubject: {{ $json.subject }}\n\n{{ $json.text }}" }
     ```
     (Use n8n's expression editor; field names like `text`/`snippet` may differ — pick the
     node's body field.)
   - **IF** node: condition `{{ $json.label }}` equals `spam`.
   - On the **true** branch: **Gmail** node → "Add Label" (create a label such as
     `SPAM-REVIEW`) or "Move to Trash". Leave the false branch empty.
5. Save and **Activate** the workflow. Send a test scam email to that Gmail account; watch
   n8n label it automatically.

For a dashboard/feedback UI, the detector's own page (http://localhost:8000) already has
"Correct / Actually spam / Actually legitimate" buttons that write `data/feedback.csv`.

## Option B — Any IMAP mailbox (no Gmail OAuth)

If your mail is Outlook/IMAP, replace the Gmail Trigger with n8n's **Email Trigger (IMAP)**
node, pointing at your mail server's IMAP host with an app password; the rest is identical.

## Option C — Production shape (mention in the report)

In a real organization this would sit on a mail server: messages are passed to the API by
the mail-transfer agent (e.g. Postfix/MailScanner) or a Google Workspace admin integration,
high-risk mail is quarantined, and a scheduled job retrains on reviewed feedback. The local
n8n setup demonstrates the same data flow without server infrastructure.

## Honest notes

- Never hardcode passwords in the workflow; use n8n credentials.
- Keep actions non-destructive for the demo (add a review **label**, don't auto-delete).
- Latency headroom: the model scores an email in ~16 ms on CPU, so an automation pipeline
  is comfortably real-time.
