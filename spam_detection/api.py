from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .model import EmailSpamDetector

MODEL_PATH = Path("models/email_spam_detector.joblib")
app = FastAPI(title="Adaptive Email Spam Detection API", version="0.1.0")
_model: EmailSpamDetector | None = None


class EmailRequest(BaseModel):
    raw_email: str = Field(min_length=1, description="Full RFC 5322 email source")


@app.on_event("startup")
def load_model() -> None:
    global _model
    if MODEL_PATH.exists():
        _model = EmailSpamDetector.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ready" if _model else "model_not_loaded"}


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


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """A simple paste-and-check page for demos (metadata is extracted automatically)."""
    return """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Email Spam Detector</title>
<style>
  body { font-family: system-ui, Segoe UI, Arial, sans-serif; background:#0f172a; color:#e2e8f0;
         margin:0; padding:24px; }
  .card { max-width: 820px; margin: 0 auto; background:#1e293b; border-radius:14px; padding:24px;
          box-shadow:0 10px 30px rgba(0,0,0,.35); }
  h1 { font-size:20px; margin:0 0 4px; }
  p.sub { margin:0 0 16px; color:#94a3b8; font-size:13px; }
  textarea { width:100%; height:230px; box-sizing:border-box; background:#0f172a; color:#e2e8f0;
             border:1px solid #334155; border-radius:10px; padding:12px; font-family:ui-monospace,Consolas,monospace;
             font-size:13px; line-height:1.45; }
  .row { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
  button { background:#2563eb; color:#fff; border:0; border-radius:9px; padding:10px 16px; font-size:14px;
           cursor:pointer; }
  button.ghost { background:#334155; }
  button:hover { filter:brightness(1.1); }
  #result { margin-top:20px; display:none; }
  .verdict { font-size:26px; font-weight:700; padding:14px 16px; border-radius:10px; text-align:center; }
  .spam { background:#7f1d1d; color:#fecaca; }
  .ham  { background:#14532d; color:#bbf7d0; }
  .bar { height:12px; background:#0f172a; border-radius:8px; overflow:hidden; margin:12px 0 6px; }
  .bar > div { height:100%; width:0%; background:linear-gradient(90deg,#22c55e,#eab308,#ef4444); }
  .meta { font-size:13px; color:#94a3b8; }
  .chips { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
  .chip { background:#3b1d1d; color:#fca5a5; border:1px solid #7f1d1d; border-radius:999px; padding:4px 10px; font-size:12px; }
  .note { margin-top:16px; font-size:12px; color:#64748b; }
</style>
</head>
<body>
<div class="card">
  <h1>Adaptive Email Spam Detector</h1>
  <p class="sub">Paste a <b>full email</b> (From / Subject / body). The model extracts the metadata
  automatically — links, reply-to, sender mismatch, urgency terms — and fuses it with the text.</p>
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
  </div>
  <p class="note">Risk score only — not proof a message was AI-written. Use synthetic/public data;
  do not paste other people's private email without approval.</p>
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

function loadSample(k){ document.getElementById('email').value = (k==='phish')?PHISH:HAM; }
loadSample('phish');

async function check(){
  const raw_email = document.getElementById('email').value;
  if(!raw_email.trim()){ alert('Paste an email first.'); return; }
  const r = await fetch('/predict', {method:'POST', headers:{'Content-Type':'application/json'},
                                     body: JSON.stringify({raw_email})});
  const data = await r.json();
  if(!r.ok){ alert(data.detail || 'Error'); return; }
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
</script>
</body>
</html>
"""
