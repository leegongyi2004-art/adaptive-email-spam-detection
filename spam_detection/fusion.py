"""Transparent late-fusion inference. Train each branch separately first."""
from __future__ import annotations
from dataclasses import dataclass
from .model import EmailSpamDetector
from .transformer import TransformerEmailDetector

@dataclass(frozen=True)
class FusionPrediction:
    label: str
    spam_probability: float
    baseline_probability: float
    transformer_probability: float
    confidence: float
    signals: dict[str, float]

class FusionEmailDetector:
    """Weighted late fusion; weights must be chosen on validation data, not test data."""
    def __init__(self, baseline: EmailSpamDetector, transformer: TransformerEmailDetector,
                 baseline_weight: float = .4, transformer_weight: float = .6, threshold: float = .5):
        if not 0 <= baseline_weight <= 1 or not 0 < threshold < 1:
            raise ValueError("weights must be 0..1 and threshold must be 0..1")
        self.baseline, self.transformer = baseline, transformer
        self.baseline_weight, self.transformer_weight, self.threshold = baseline_weight, transformer_weight, threshold
        total = baseline_weight + transformer_weight
        if total == 0: raise ValueError("at least one branch must have non-zero weight")
        self.baseline_weight, self.transformer_weight = baseline_weight / total, transformer_weight / total

    def predict(self, raw_email: str | bytes) -> FusionPrediction:
        b, t = self.baseline.predict(raw_email), self.transformer.predict(raw_email)
        score = self.baseline_weight * b.spam_probability + self.transformer_weight * t.spam_probability
        return FusionPrediction("spam" if score >= self.threshold else "ham", score, b.spam_probability,
                               t.spam_probability, abs(score - .5) * 2, b.signals)
