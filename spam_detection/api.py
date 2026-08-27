from pathlib import Path
from fastapi import FastAPI, HTTPException
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
    return {"label": result.label, "spam_probability": result.spam_probability, "confidence": result.confidence, "signals": result.signals}
