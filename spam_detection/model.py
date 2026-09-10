from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from .features import parse_email


def extract_text(records):
    return [record["text"] for record in records]


def extract_metadata(records):
    return [record["metadata"] for record in records]

@dataclass(frozen=True)
class Prediction:
    label: str
    spam_probability: float
    confidence: float
    signals: dict[str, float]

class EmailSpamDetector:
    """Local, auditable content + metadata fusion classifier.

    It combines word and character TF-IDF email content with structural and
    authentication metadata. Retraining stays local and needs no cloud API.
    """
    def __init__(self, threshold: float = 0.5):
        if not 0 < threshold < 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        text = FunctionTransformer(extract_text, validate=False)
        metadata = FunctionTransformer(extract_metadata, validate=False)
        self.pipeline = Pipeline([
            ("features", FeatureUnion([
                ("words", Pipeline([( "extract", text), ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=40_000, sublinear_tf=True))])),
                ("chars", Pipeline([( "extract", FunctionTransformer(extract_text, validate=False)), ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_features=30_000, sublinear_tf=True))])),
                # Scale metadata so raw lengths (e.g. body_len ~500) do not
                # swamp the normalized TF-IDF text features. with_mean=False
                # keeps the matrix sparse.
                ("metadata", Pipeline([( "extract", metadata), ("vectorize", DictVectorizer(sparse=True)), ("scale", StandardScaler(with_mean=False))])),
            ])),
            ("classifier", LogisticRegression(class_weight="balanced", max_iter=1_000, C=1.5)),
        ])
        self.is_fitted = False

    @staticmethod
    def _records(emails: Iterable[str | bytes]):
        return [parse_email(email) for email in emails]

    def fit(self, emails: Iterable[str | bytes], labels: Iterable[int | bool]):
        records, labels = self._records(emails), list(labels)
        if len(records) != len(labels) or len(set(map(int, labels))) < 2:
            raise ValueError("provide equally sized emails/labels containing both ham (0) and spam (1)")
        self.pipeline.fit(records, [int(x) for x in labels])
        self.is_fitted = True
        return self

    def predict(self, raw_email: str | bytes) -> Prediction:
        if not self.is_fitted:
            raise RuntimeError("model is not trained; call fit() or load() first")
        record = parse_email(raw_email)
        probability = float(self.pipeline.predict_proba([record])[0][1])
        label = "spam" if probability >= self.threshold else "ham"
        m = record["metadata"]
        signals = {k: float(v) for k, v in m.items() if v and k in {"url_count", "attachment_count", "sender_url_domain_mismatch", "has_reply_to", "suspicious_term_count", "spf_pass"}}
        return Prediction(label, probability, abs(probability - 0.5) * 2, signals)

    def save(self, path: str | Path) -> None:
        if not self.is_fitted:
            raise RuntimeError("cannot save an untrained model")
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> "EmailSpamDetector":
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError("file is not an EmailSpamDetector model")
        return model
