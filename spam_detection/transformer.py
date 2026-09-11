"""Optional local Transformer branch for semantic phishing detection.

The heavy dependencies are intentionally optional. Install
`pip install -r requirements-transformer.txt` before using this module.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .features import parse_email

@dataclass(frozen=True)
class TransformerPrediction:
    spam_probability: float
    label: str

class TransformerEmailDetector:
    """Hugging Face sequence classifier, kept local after the initial download."""
    def __init__(self, model_path: str | Path, threshold: float = 0.5, max_length: int = 256):
        if not 0 < threshold < 1 or not 16 <= max_length <= 512:
            raise ValueError("threshold must be 0..1 and max_length must be 16..512")
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ImportError as error:
            raise ImportError("Install transformer support: pip install -r requirements-transformer.txt") from error
        self.torch = torch
        self.threshold, self.max_length = threshold, max_length
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    @staticmethod
    def email_text(raw_email: str | bytes) -> str:
        return parse_email(raw_email)["text"]

    def predict(self, raw_email: str | bytes) -> TransformerPrediction:
        encoded = self.tokenizer(self.email_text(raw_email), return_tensors="pt", truncation=True,
                                 max_length=self.max_length, padding=True).to(self.device)
        with self.torch.inference_mode():
            probability = float(self.torch.softmax(self.model(**encoded).logits, dim=-1)[0][1])
        return TransformerPrediction(probability, "spam" if probability >= self.threshold else "ham")

    def predict_many(self, emails: Iterable[str | bytes]) -> list[float]:
        return [self.predict(email).spam_probability for email in emails]
