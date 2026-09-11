import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .model import EmailSpamDetector

MODEL_PATH = Path("models/email_spam_detector.joblib")
FEEDBACK_PATH = Path("data/feedback.csv")  # corrections from the review UI feed retraining
QUEUE_PATH = Path("review_queue.csv")      # messages scanned by the mailbox/IMAP watchers
BASE_DATA_PATH = Path("data/reviewed_mail.csv")  # historical corpus used for retraining
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


@app.get("/queue")
def queue():
    """Return messages scanned by the mailbox watchers that still need review."""
    if not QUEUE_PATH.exists():
        return {"rows": [], "message": "No review queue yet. Run a mailbox or IMAP scan first."}
    with open(QUEUE_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pending, reviewed = [], []
    for i, r in enumerate(rows):
        item = {
            "row": i,
            "file": r.get("file", ""),
            "sender": r.get("sender", ""),
            "subject": r.get("subject", ""),
            "predicted_label": r.get("predicted_label", ""),
            "spam_probability": r.get("spam_probability", ""),
            "signals": r.get("signals", ""),
            "correct_label": (r.get("correct_label") or "").strip(),
        }
        (reviewed if item["correct_label"] else pending).append(item)
    return {"rows": pending, "reviewed": reviewed,
            "total": len(rows), "pending": len(pending)}


@app.get("/queue/{row}/message")
def queue_message(row: int):
    """Return the readable text of one queued message so a reviewer can read it
    in the console instead of opening the mailbox separately."""
    if not QUEUE_PATH.exists():
        raise HTTPException(404, "No review queue found.")
    with open(QUEUE_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if row >= len(rows):
        raise HTTPException(404, f"Row {row} not in the queue.")
    source = Path(rows[row].get("file", ""))
    if not source.is_file():
        raise HTTPException(404, "The stored copy of this message is no longer available.")

    from email import policy
    from email.parser import BytesParser
    raw = source.read_bytes()
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    break
        else:
            body = msg.get_content()
        if not body:
            body = raw.decode("utf-8", errors="replace")
        headers = {k: str(msg.get(k, "")) for k in ("From", "To", "Subject", "Date", "Reply-To")}
    except Exception:  # noqa: BLE001 - display only
        body = raw.decode("utf-8", errors="replace")
        headers = {}
    if len(body) > 8000:
        body = body[:8000] + "\n\n[... truncated for display ...]"
    return {"headers": headers, "body": body}


class QueueFeedbackRequest(BaseModel):
    row: int = Field(ge=0, description="row index from /queue")
    correct_label: str = Field(description="'spam', 'ham', or 'correct'")


@app.post("/queue/feedback")
def queue_feedback(req: QueueFeedbackRequest):
    """Record a verdict for one queued message: mark the queue row as reviewed and,
    when the model was wrong, append the email text to the feedback training file."""
    if not QUEUE_PATH.exists():
        raise HTTPException(404, "No review queue found.")
    with open(QUEUE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    if req.row >= len(rows):
        raise HTTPException(404, f"Row {req.row} not in the queue.")
    row = rows[req.row]
    predicted = (row.get("predicted_label") or "").strip()
    verdict = "spam" if req.correct_label == "correct" and predicted == "spam" else req.correct_label
    if verdict == "correct":
        verdict = predicted
    if verdict not in ("spam", "ham"):
        raise HTTPException(400, "correct_label must be 'spam', 'ham', or 'correct'.")

    row["correct_label"] = verdict
    with open(QUEUE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    if verdict == predicted:
        return {"status": "agreed", "message": "Marked as reviewed; the model was right."}

    source = Path(row.get("file", ""))
    if not source.is_file():
        raise HTTPException(404, f"Original message not found at {source}. "
                                 "Re-run the scan so the message copy is saved.")
    text = source.read_bytes().decode("utf-8", errors="replace")
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    new = not FEEDBACK_PATH.exists()
    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["raw_email", "label"])
        if new:
            writer.writeheader()
        writer.writerow({"raw_email": text, "label": 1 if verdict == "spam" else 0})
    return {"status": "saved", "correct_label": verdict, "feedback_rows": feedback_count(),
            "message": f"Correction saved as {verdict}; it joins the next retrain."}


@app.post("/queue/{row}/undo")
def queue_undo(row: int):
    """Reverse a verdict recorded by mistake.

    The queue row is returned to the unreviewed state and, if the correction had
    been written to the feedback file, that entry is removed so it cannot reach
    the next retraining cycle.
    """
    if not QUEUE_PATH.exists():
        raise HTTPException(404, "No review queue found.")
    with open(QUEUE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    if row >= len(rows):
        raise HTTPException(404, f"Row {row} not in the queue.")
    entry = rows[row]
    previous = (entry.get("correct_label") or "").strip()
    if not previous:
        return {"status": "nothing_to_undo", "message": "That message has not been reviewed yet."}

    entry["correct_label"] = ""
    with open(QUEUE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    removed = 0
    source = Path(entry.get("file", ""))
    if FEEDBACK_PATH.exists() and source.is_file():
        text = source.read_bytes().decode("utf-8", errors="replace")
        with open(FEEDBACK_PATH, newline="", encoding="utf-8", errors="replace") as f:
            fb_rows = list(csv.DictReader(f))
        kept = [r for r in fb_rows if (r.get("raw_email") or "") != text]
        removed = len(fb_rows) - len(kept)
        if removed:
            with open(FEEDBACK_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["raw_email", "label"])
                writer.writeheader()
                writer.writerows([{"raw_email": r.get("raw_email", ""),
                                   "label": r.get("label", "")} for r in kept])
    return {"status": "undone", "previous_label": previous,
            "corrections_removed": removed, "feedback_rows": feedback_count(),
            "message": f"Verdict '{previous}' removed; the message is back in the review list."}


@app.post("/retrain")
def retrain():
    """Retrain on the historical corpus plus the accumulated reviewer corrections.

    This is triggered explicitly by a reviewer; the system never retrains on its own.
    The replacement model is accepted only if it still performs at least as well as
    the current one on a held-out split, so a bad batch of corrections cannot silently
    degrade the deployed detector.
    """
    global _model
    if not BASE_DATA_PATH.exists():
        raise HTTPException(404, f"Training corpus not found at {BASE_DATA_PATH}.")
    if feedback_count() == 0:
        raise HTTPException(400, "No corrections recorded yet - review some messages first.")

    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split

    from .evaluate import load_csv as load_training_csv

    emails, labels = load_training_csv(str(BASE_DATA_PATH))
    # The corrections file legitimately holds a single class (e.g. only missed spam),
    # so it is read directly rather than through the two-class training loader.
    fb_emails: list[str] = []
    fb_labels: list[int] = []
    with open(FEEDBACK_PATH, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            text = (row.get("raw_email") or "").strip()
            lab = (row.get("label") or "").strip()
            if text and lab in ("0", "1"):
                fb_emails.append(text)
                fb_labels.append(int(lab))
    if not fb_emails:
        raise HTTPException(400, "No usable corrections found in the feedback file.")

    x_tr, x_te, y_tr, y_te = train_test_split(
        emails, labels, test_size=0.25, random_state=42, stratify=labels)

    def auc_of(model) -> float:
        probs = [model.predict(e).spam_probability for e in x_te]
        return roc_auc_score(y_te, probs) if len(set(y_te)) > 1 else float("nan")

    candidate = EmailSpamDetector(0.55).fit(x_tr + fb_emails, y_tr + fb_labels)
    new_auc = auc_of(candidate)
    old_auc = auc_of(_model) if _model is not None else 0.0

    if new_auc + 1e-4 < old_auc:
        return {"status": "rejected", "previous_auc": round(old_auc, 4),
                "candidate_auc": round(new_auc, 4),
                "message": "Retrained model scored worse on the held-out split; "
                           "the existing model was kept."}

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    candidate.save(MODEL_PATH)
    _model = candidate
    return {"status": "deployed", "previous_auc": round(old_auc, 4),
            "new_auc": round(new_auc, 4), "corrections_used": len(fb_emails),
            "message": f"Retrained on {len(x_tr) + len(fb_emails):,} emails "
                       f"({len(fb_emails)} reviewer corrections) and deployed."}


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
  <div class="feedback" style="margin-top:22px">
    <h2 style="font-size:17px;margin:0 0 6px">Review inbox</h2>
    <div class="meta">Messages picked up by the mailbox / IMAP watchers. Click one button per
    message - corrections are added to the next retrain automatically.</div>
    <div class="row" style="margin-top:10px">
      <button class="ghost" onclick="loadQueue()">Refresh queue</button>
      <button onclick="retrain()">Retrain model with corrections</button>
      <span class="meta" id="qcount" style="align-self:center"></span>
    </div>
    <div id="queue"></div>
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
loadQueue();

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

async function retrain(){
  const el = document.getElementById('qcount');
  el.textContent = 'Retraining - this can take several minutes on the full corpus ...';
  try {
    const res = await fetch('/retrain', {method:'POST'});
    const data = await res.json();
    el.textContent = data.message || data.detail || 'Done.';
  } catch (e) {
    el.textContent = 'Retrain failed: ' + e;
  }
}

async function loadQueue(){
  const box = document.getElementById('queue');
  const res = await fetch('/queue');
  const data = await res.json();
  const rows = data.rows || [];
  document.getElementById('qcount').textContent =
      rows.length ? rows.length + ' awaiting review' : (data.message || 'Nothing to review.');
  box.innerHTML = '';
  for (const r of rows){
    const spam = (r.predicted_label === 'spam');
    const pct = (parseFloat(r.spam_probability) * 100).toFixed(1);
    const card = document.createElement('div');
    card.style.cssText = 'border:1px solid #334155;border-radius:8px;padding:10px;margin-top:10px';

    const t = document.createElement('div');
    t.innerHTML = '<b></b>';
    t.firstChild.textContent = r.subject || '(no subject)';
    card.appendChild(t);

    const who = document.createElement('div');
    who.className = 'meta';
    who.textContent = 'from ' + (r.sender || '(unknown)');
    card.appendChild(who);

    const verdictLine = document.createElement('div');
    verdictLine.className = 'meta';
    verdictLine.style.margin = '6px 0';
    verdictLine.textContent = 'Model says ' + (spam ? 'SPAM' : 'LEGITIMATE') + ' at ' + pct +
                              '%  -  signals: ' + (r.signals || '-');
    verdictLine.style.color = spam ? '#f87171' : '#4ade80';
    card.appendChild(verdictLine);

    const pane = document.createElement('pre');
    pane.style.cssText = 'display:none;white-space:pre-wrap;word-break:break-word;' +
        'background:#0f172a;border:1px solid #334155;border-radius:6px;padding:10px;' +
        'margin:8px 0;max-height:320px;overflow:auto;font-size:12.5px;line-height:1.45';

    const readBtn = document.createElement('button');
    readBtn.className = 'ghost';
    readBtn.textContent = 'Read message';
    readBtn.onclick = async function(){
      if (pane.style.display === 'block'){
        pane.style.display = 'none';
        readBtn.textContent = 'Read message';
        return;
      }
      pane.style.display = 'block';
      readBtn.textContent = 'Hide message';
      if (!pane.dataset.loaded){
        pane.textContent = 'Loading ...';
        try {
          const mres = await fetch('/queue/' + r.row + '/message');
          const mdata = await mres.json();
          if (mdata.detail){ pane.textContent = mdata.detail; return; }
          let head = '';
          for (const k in (mdata.headers || {})){
            if (mdata.headers[k]) head += k + ': ' + mdata.headers[k] + '\\n';
          }
          pane.textContent = head + '\\n' + (mdata.body || '');
          pane.dataset.loaded = '1';
        } catch (e){ pane.textContent = 'Could not load message: ' + e; }
      }
    };
    const readRow = document.createElement('div');
    readRow.className = 'row';
    readRow.appendChild(readBtn);
    card.appendChild(readRow);
    card.appendChild(pane);

    const btnRow = document.createElement('div');
    btnRow.className = 'row';
    const defs = [['\u2713 Correct', 'correct'],
                  ['\u2717 Actually SPAM', 'spam'],
                  ['\u2717 Actually LEGITIMATE', 'ham']];
    for (const d of defs){
      const b = document.createElement('button');
      b.className = 'fb';
      b.textContent = d[0];
      b.onclick = function(){ queueVerdict(r.row, d[1], b); };
      btnRow.appendChild(b);
    }
    card.appendChild(btnRow);

    const msg = document.createElement('div');
    msg.className = 'meta';
    msg.id = 'qm' + r.row;
    card.appendChild(msg);

    box.appendChild(card);
  }

  const done = data.reviewed || [];
  if (done.length){
    const h = document.createElement('div');
    h.className = 'meta';
    h.style.marginTop = '16px';
    h.textContent = 'Already reviewed (' + done.length + ') - use Undo if a verdict was a mistake:';
    box.appendChild(h);
    for (const r of done){
      const line = document.createElement('div');
      line.style.cssText = 'border:1px solid #1e293b;border-radius:8px;padding:8px 10px;margin-top:8px';
      const label = document.createElement('span');
      label.className = 'meta';
      label.textContent = (r.subject || '(no subject)') + '  -  marked ' + r.correct_label;
      line.appendChild(label);
      const u = document.createElement('button');
      u.className = 'ghost';
      u.style.marginLeft = '10px';
      u.textContent = 'Undo';
      u.onclick = async function(){
        u.disabled = true;
        const res = await fetch('/queue/' + r.row + '/undo', {method:'POST'});
        const d = await res.json();
        label.textContent = d.message || d.detail || 'Undone.';
        loadQueue();
      };
      line.appendChild(u);
      box.appendChild(line);
    }
  }
}

async function queueVerdict(row, verdict, btn){
  const res = await fetch('/queue/feedback', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({row: row, correct_label: verdict})});
  const data = await res.json();
  const msg = document.getElementById('qm' + row);
  if (msg) msg.textContent = data.message || data.detail || 'Saved.';
  btn.parentElement.querySelectorAll('button').forEach(b => b.disabled = true);
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
