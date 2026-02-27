from __future__ import annotations

import json
from pathlib import Path

from macro_forecast.subscriptions import SubscriptionStore

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"

REPORT_BY_CADENCE = {
    "daily": OUT / "daily.md",
    "weekly": OUT / "weekly.md",
    "monthly": OUT / "monthly.md",
}


def main(cadence: str) -> None:
    store = SubscriptionStore(DATA / "subscribers.json")
    subs = store.for_cadence(cadence)

    report_path = REPORT_BY_CADENCE[cadence]
    if not report_path.exists():
        raise SystemExit(f"missing report file: {report_path}")

    text = report_path.read_text(encoding="utf-8")
    jobs = [
        {
            "channel": s.channel,
            "target": s.target,
            "cadence": cadence,
            "message": text,
        }
        for s in subs
    ]
    out = OUT / f"dispatch_{cadence}.json"
    out.write_text(json.dumps({"jobs": jobs}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated: {out} jobs={len(jobs)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in REPORT_BY_CADENCE:
        raise SystemExit("usage: python scripts/build_dispatch_queue.py [daily|weekly|monthly]")
    main(sys.argv[1])
