"""Adaptive content and metadata fusion for email spam detection."""
import csv as _csv
import sys as _sys


def _raise_csv_field_limit() -> None:
    """Allow very long email fields (Python defaults to a ~131 KB CSV cap)."""
    limit = _sys.maxsize
    while True:
        try:
            _csv.field_size_limit(limit)
            return
        except OverflowError:
            limit = int(limit / 10)


_raise_csv_field_limit()

from .model import EmailSpamDetector, Prediction  # noqa: E402

__all__ = ["EmailSpamDetector", "Prediction"]
