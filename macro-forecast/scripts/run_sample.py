from __future__ import annotations

import csv
from pathlib import Path

from macro_forecast.report_templates import (
    build_daily_report,
    build_monthly_report,
    build_weekly_report,
)
from macro_forecast.signals import build_signal_map

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample_features.csv"
OUT = ROOT / "outputs"


def load_features(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)
    return {k: float(v) for k, v in row.items()}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    features = load_features(DATA)
    signals = build_signal_map(features)

    (OUT / "daily.md").write_text(build_daily_report(signals), encoding="utf-8")
    (OUT / "weekly.md").write_text(build_weekly_report(signals), encoding="utf-8")
    (OUT / "monthly.md").write_text(build_monthly_report(signals), encoding="utf-8")

    print("generated:", OUT / "daily.md")
    print("generated:", OUT / "weekly.md")
    print("generated:", OUT / "monthly.md")


if __name__ == "__main__":
    main()
