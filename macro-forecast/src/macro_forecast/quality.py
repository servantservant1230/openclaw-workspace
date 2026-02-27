from __future__ import annotations

from typing import Dict

from .signals import DirectionResult


def confidence_tag(score: float) -> str:
    a = abs(score)
    if a >= 0.6:
        return "HIGH"
    if a >= 0.25:
        return "MED"
    return "LOW"


def summarize_signal_quality(signals: Dict[str, DirectionResult]) -> Dict[str, str]:
    return {k: confidence_tag(v.score) for k, v in signals.items()}
