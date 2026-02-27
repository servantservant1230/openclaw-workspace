from __future__ import annotations

import csv
from pathlib import Path

from macro_forecast.data_sources import build_snapshot
from macro_forecast.features import DEFAULTS, derive_features_from_levels
from macro_forecast.report_templates import (
    build_daily_report,
    build_monthly_report,
    build_weekly_report,
)
from macro_forecast.signals import build_signal_map

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
STATE = ROOT / "data" / "latest_levels.csv"
FEATURES_STATE = ROOT / "data" / "latest_features.csv"


def _load_last_levels(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    return {k: float(v) for k, v in row.items() if k != "asof"}


def _save_features(path: Path, features: dict) -> None:
    fields = sorted(features.keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerow(features)


def _save_levels(path: Path, asof: str, values: dict) -> None:
    fields = ["asof"] + sorted(values.keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        row = {"asof": asof}
        row.update(values)
        w.writerow(row)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    prev_levels = _load_last_levels(STATE)
    snap = build_snapshot()

    if snap.values and prev_levels:
        features = derive_features_from_levels(snap.values, prev_levels)
    else:
        features = dict(DEFAULTS)

    if snap.values:
        _save_levels(STATE, snap.asof, snap.values)
    _save_features(FEATURES_STATE, features)

    signals = build_signal_map(features)
    (OUT / "daily.md").write_text(build_daily_report(signals), encoding="utf-8")
    (OUT / "weekly.md").write_text(build_weekly_report(signals), encoding="utf-8")
    (OUT / "monthly.md").write_text(build_monthly_report(signals, features), encoding="utf-8")

    print("live_values_count:", len(snap.values))
    print("generated reports in:", OUT)


if __name__ == "__main__":
    main()
