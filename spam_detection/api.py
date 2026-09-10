import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .model import EmailSpamDetector

MODEL_PATH = Path("models/email_spam_detector.joblib")
FEEDBACK_PATH = Path("data/feedback.csv")  # corrections from the review UI feed retraining
app = FastAPI(title="Adaptive Email Spam Detection API", version="0.2.0")
_model: EmailSpamDetector | None = None


class EmailRequest(BaseModel):
    raw_email: str = Field(min_length=1, description="Full RFC 5322 email source")


class FeedbackRequest(BaseModel):
    raw_email: str = Field(min_length=1)
    predicted_label: str = Field(description="what the model said: 'spam' or 'ham'")
    correct_label: str = Field(description="reviewer verdict: 'spam', 'ham', or 'correct'")


@app.on_event("startup")
def load_model() -> None:
    global _model
    if MODEL_PATH.exists():
        _model = EmailSpamDetector.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ready" if _model else "model_not_loaded",
            "feedback_rows": feedback_count()}


@app.post("/predict")
def predict(request: EmailRequest):
    if _model is None:
        raise HTTPException(503, "Model unavailable. Train one and place it at models/email_spam_detector.joblib.")
    result = _model.predict(request.raw_email)
    return {
        "label": result.label,
        "spam_probability": result.spam_probability,
        "confidence": result.confidence,
        "signals": result.signals,
    }


def feedback_count() -> int:
    if not FEEDBACK_PATH.exists():
        return 0
    with open(FEEDBACK_PATH, newline="", encoding="utf-8") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """Record a reviewer correction. 'correct' means the model was right (nothing
    to learn); 'spam'/'ham' means the model was wrong and the email is appended
    to data/feedback.csv for the next scheduled retrain."""
    if req.correct_label == "correct":
        return {"status": "agreed", "message": "Model was correct - no correction needed."}
    if req.correct_label not in ("spam", "ham"):
        raise HTTPException(400, "correct_label must be 'spam', 'ham', or 'correct'.")
    if req.correct_label == req.predicted_label:
        return {"status": "agreed", "message": "That matches the model's verdict."}
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    new = not FEEDBACK_PATH.exists()
    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["raw_email", "label"])
        if new:
            writer.writeheader()
        writer.writerow({"raw_email": req.raw_email,
                         "label": 1 if req.correct_label == "spam" else 0})
    return {"status": "saved", "correct_label": req.correct_label,
            "feedback_rows": feedback_count(),
            "message": f"Saved as {req.correct_label}. It joins data/feedback.csv for the next retrain."}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Paste-and-check page plus an inline feedback console."""
    return """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Adaptive Email Spam Detector</title>
<style>
  body { font-family: system-ui, Segoe UI, Arial, sans-serif; background:#0f172a; color:#e2e8f0;
         margin:0; padding:24px; }
  .card { max-width: 820px; margin: 0 auto; background:#1e293b; border-radius:14px; padding:24px;
          box-shadow:0 10px 30px rgba(0,0,0,.35); }
  h1 { font-size:20px; margin:0 0 4px; }
  p.sub { margin:0 0 16px; color:#94a3b8; font-size:13px; }
  textarea { width:100%; height:210px; box-sizing:border-box; background:#0f172a; color:#e2e8f0;
             border:1px solid #334155; border-radius:10px; padding:12px; font-family:ui-monospace,Consolas,monospace;
             font-size:13px; line-height:1.45; }
  .row { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
  button { background:#2563eb; color:#fff; border:0; border-radius:9px; padding:10px 16px; font-size:14px;
           cursor:pointer; }
  button.ghost { background:#334155; }
  button.fb { background:#1e293b; border:1px solid #475569; }
  button:hover { filter:brightness(1.15); }
  #result { margin-top:20px; display:none; }
  .verdict { font-size:26px; font-weight:700; padding:14px 16px; border-radius:10px; text-align:center; }
  .spam { background:#7f1d1d; color:#fecaca; }
  .ham  { background:#14532d; color:#bbf7d0; }
  .bar { height:12px; background:#0f172a; border-radius:8px; overflow:hidden; margin:12px 0 6px; }
  .bar > div { height:100%; width:0%; background:linear-gradient(90deg,#22c55e,#eab308,#ef4444); }
  .meta { font-size:13px; color:#94a3b8; }
  .chips { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
  .chip { background:#3b1d1d; color:#fca5a5; border:1px solid #7f1d1d; border-radius:999px; padding:4px 10px; font-size:12px; }
  .feedback { margin-top:18px; border-top:1px solid #334155; padding-top:14px; }
  .note { margin-top:16px; font-size:12px; color:#64748b; }
  #fbmsg { margin-top:10px; font-size:13px; color:#7dd3fc; }
</style>
</head>
<body>
<div class="card">
  <h1>Adaptive Email Spam Detector</h1>
  <p class="sub">Paste a <b>full email</b> (From / Subject / body). Metadata (links, reply-to,
  sender mismatch, urgency terms) is extracted automatically and fused with the text. Use the
  buttons under each result to give feedback - corrections teach the next model version.</p>
  <textarea id="email"></textarea>
  <div class="row">
    <button onclick="check()">Check email</button>
    <button class="ghost" onclick="loadSample('phish')">Load sample phishing</button>
    <button class="ghost" onclick="loadSample('ham')">Load sample legitimate</button>
  </div>
  <div id="result">
    <div id="verdict" class="verdict"></div>
    <div class="bar"><div id="bar"></div></div>
    <div class="meta" id="prob"></div>
    <div class="chips" id="chips"></div>
    <div class="feedback">
      <div class="meta">Was this right? Your feedback is saved for retraining:</div>
      <div class="row">
        <button class="fb" onclick="sendFeedback('correct')">&#10003; Correct</button>
        <button class="fb" onclick="sendFeedback('spam')">&#10007; It's actually SPAM</button>
        <button class="fb" onclick="sendFeedback('ham')">&#10007; It's actually LEGITIMATE</button>
      </div>
      <div id="fbmsg"></div>
    </div>
  </div>
  <p class="note">Risk score only - not proof a message was AI-written. In production, mail arrives
  automatically via an integration (e.g. n8n / a mail server calling /predict); this page is the
  manual check + review console. Use synthetic/public data; don't paste others' private email.</p>
</div>
<script>
const PHISH = `From: it.support@company-helpdesk.example
Reply-To: collector@webmail.example
Subject: Action required: mailbox verification

Dear valued user, our system detected unusual activity on your email account.
To prevent suspension, verify your identity within 24 hours by signing in with
your email address and password.

Verify now: https://company-helpdesk.example/secure

This is an automated message from the IT services team.`;
const HAM = `From: sarah.lee@company.example
Subject: Re: quarterly report

Hi, thanks for sending the draft. I left a couple of comments on page 4.
Can we discuss on Tuesday at 10am? Best, Sarah`;

let lastEmail = "", lastLabel = "";
function loadSample(k){ document.getElementById('email').value = (k==='phish')?PHISH:HAM; }
loadSample('phish');

async function check(){
  lastEmail = document.getElementById('email').value;
  if(!lastEmail.trim()){ alert('Paste an email first.'); return; }
  document.getElementById('fbmsg').textContent = '';
  const r = await fetch('/predict', {method:'POST', headers:{'Content-Type':'application/json'},
                                     body: JSON.stringify({raw_email: lastEmail})});
  const data = await r.json();
  if(!r.ok){ alert(data.detail || 'Error'); return; }
  lastLabel = data.label;
  const box = document.getElementById('result'); box.style.display='block';
  const v = document.getElementById('verdict');
  const isSpam = data.label === 'spam';
  v.textContent = (isSpam ? '⚠ SPAM / PHISHING' : '✓ LEGITIMATE') +
                  '  (' + (data.spam_probability*100).toFixed(1) + '% spam)';
  v.className = 'verdict ' + (isSpam ? 'spam' : 'ham');
  document.getElementById('bar').style.width = (data.spam_probability*100).toFixed(1) + '%';
  document.getElementById('prob').textContent =
      'Confidence: ' + (data.confidence*100).toFixed(1) + '%   (0% = clearly legitimate, 100% = clearly spam)';
  const chips = document.getElementById('chips'); chips.innerHTML = '';
  const labels = {url_count:'contains link(s)', attachment_count:'attachment(s)',
    sender_url_domain_mismatch:'sender/link domain mismatch', has_reply_to:'has Reply-To address',
    suspicious_term_count:'urgency/verification terms', spf_pass:'SPF pass'};
  Object.entries(data.signals || {}).forEach(([k,val]) => {
    if(val){ const c=document.createElement('span'); c.className='chip';
      c.textContent = '⚑ ' + (labels[k]||k) + (val>1?': '+val:''); chips.appendChild(c); }
  });
  if(!Object.values(data.signals||{}).some(x=>x)){
    chips.innerHTML = '<span class="chip" style="background:#122b1c;color:#86efac;border-color:#14532d">no structural risk signals fired</span>';
  }
}

async function sendFeedback(correct){
  if(!lastEmail){ alert('Check an email first.'); return; }
  const r = await fetch('/feedback', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({raw_email: lastEmail, predicted_label: lastLabel, correct_label: correct})});
  const data = await r.json();
  const msg = document.getElementById('fbmsg');
  if(correct === 'correct'){ msg.textContent = '✓ Noted - the model was right.'; }
  else { msg.textContent = '✓ ' + data.message + '  (total corrections saved: ' +
                           (data.feedback_rows ?? 0) + ')'; }
}
</script>
</body>
</html>
"""
