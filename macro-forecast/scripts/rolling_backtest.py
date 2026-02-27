from __future__ import annotations

import csv
import json
from pathlib import Path

from macro_forecast.backtest import evaluate_rows

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "historical_sample.csv"
OUT = ROOT / "outputs"
TARGETS = ["nasdaq", "qqq", "kospi", "samsung_electronics", "sk_hynix", "naver"]


def load_rows(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rolling_eval(rows, targets):
    windows = []
    for i in range(3, len(rows) + 1):
        sub = rows[:i]
        m = evaluate_rows(sub, targets)
        windows.append(
            {
                "end_date": sub[-1]["date"],
                "targets": {k: {"accuracy": v.accuracy, "samples": v.samples} for k, v in m.items()},
            }
        )
    return windows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows(DATA)
    windows = rolling_eval(rows, TARGETS)
    payload = {"windows": windows, "window_count": len(windows)}
    (OUT / "rolling_backtest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Rolling Backtest", ""]
    for w in windows:
        lines.append(f"## up to {w['end_date']}")
        for t, mv in w["targets"].items():
            lines.append(f"- {t}: acc={mv['accuracy']:.2f} (n={mv['samples']})")
        lines.append("")
    (OUT / "rolling_backtest.md").write_text("\n".join(lines), encoding="utf-8")

    print("generated:", OUT / "rolling_backtest.json")
    print("generated:", OUT / "rolling_backtest.md")


if __name__ == "__main__":
    main()
