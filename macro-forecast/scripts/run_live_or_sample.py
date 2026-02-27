from __future__ import annotations

import csv
from pathlib import Path

from macro_forecast.data_sources import build_snapshot
from macro_forecast.features import DEFAULTS
from macro_forecast.report_templates import (
    build_daily_report,
    build_monthly_report,
    build_weekly_report,
)
from macro_forecast.signals import build_signal_map

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
STATE = ROOT / "data" / "latest_levels.csv"


def _load_last_levels(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
    return {k: float(v) for k, v in row.items() if k != "asof"}


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

    snap = build_snapshot()
    features = dict(DEFAULTS)
    # live level만 있으면 변화율 계산이 제한적이므로 기본값+수동 보정 구조 유지
    # 차기 단계에서 히스토리 축적 후 자동 변화율 계산 강화 예정.

    if snap.values:
        _save_levels(STATE, snap.asof, snap.values)

    signals = build_signal_map(features)
    (OUT / "daily.md").write_text(build_daily_report(signals), encoding="utf-8")
    (OUT / "weekly.md").write_text(build_weekly_report(signals), encoding="utf-8")
    (OUT / "monthly.md").write_text(build_monthly_report(signals, features), encoding="utf-8")

    print("live_values_count:", len(snap.values))
    print("generated reports in:", OUT)


if __name__ == "__main__":
    main()
