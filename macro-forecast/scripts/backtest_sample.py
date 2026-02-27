from __future__ import annotations

import csv
import json
from pathlib import Path

from macro_forecast.backtest import evaluate_rows, summarize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "historical_sample.csv"
OUT = ROOT / "outputs"
TARGETS = ["nasdaq", "qqq", "kospi", "samsung_electronics", "sk_hynix", "naver"]


def load_rows(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows(DATA)
    metrics = evaluate_rows(rows, TARGETS)
    summary = summarize(metrics)

    payload = {
        "summary": summary,
        "targets": {
            k: {"accuracy": v.accuracy, "samples": v.samples}
            for k, v in metrics.items()
        },
    }
    (OUT / "backtest_metrics.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = ["# Backtest Summary", "", f"- overall_accuracy: {summary['overall_accuracy']:.2f}"]
    for k, v in metrics.items():
        lines.append(f"- {k}: acc={v.accuracy:.2f} (n={v.samples})")
    (OUT / "backtest_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("generated:", OUT / "backtest_metrics.json")
    print("generated:", OUT / "backtest_summary.md")


if __name__ == "__main__":
    main()
