from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .signals import build_signal_map


@dataclass
class TargetMetric:
    accuracy: float
    samples: int


def _acc(y_true: List[str], y_pred: List[str]) -> float:
    if not y_true:
        return 0.0
    hit = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return hit / len(y_true)


def evaluate_rows(rows: Iterable[Dict[str, str]], targets: List[str]) -> Dict[str, TargetMetric]:
    cache_true = {t: [] for t in targets}
    cache_pred = {t: [] for t in targets}

    for row in rows:
        features = {
            k: float(v)
            for k, v in row.items()
            if k not in {"date"} and not k.startswith("real_")
        }
        pred = build_signal_map(features)
        for t in targets:
            true_key = f"real_{t}_dir"
            if true_key not in row or t not in pred:
                continue
            cache_true[t].append(row[true_key])
            cache_pred[t].append(pred[t].label)

    return {
        t: TargetMetric(accuracy=_acc(cache_true[t], cache_pred[t]), samples=len(cache_true[t]))
        for t in targets
    }


def summarize(metrics: Dict[str, TargetMetric]) -> Dict[str, float]:
    valid = [m.accuracy for m in metrics.values() if m.samples > 0]
    overall = sum(valid) / len(valid) if valid else 0.0
    return {"overall_accuracy": overall, "target_count": float(len(valid))}
