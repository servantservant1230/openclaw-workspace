from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from macro_forecast.subscriptions import SubscriptionStore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DATA = ROOT / "data"

REPORT_BY_CADENCE = {
    "daily": OUT / "daily.md",
    "weekly": OUT / "weekly.md",
    "monthly": OUT / "monthly.md",
}


def send_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8")
        data = json.loads(body)
        if not data.get("ok"):
            raise RuntimeError(f"telegram send failed: {data}")


def main(cadence: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")

    report_path = REPORT_BY_CADENCE[cadence]
    if not report_path.exists():
        raise SystemExit(f"missing report file: {report_path}")
    message = report_path.read_text(encoding="utf-8")

    store = SubscriptionStore(DATA / "subscribers.json")
    subs = [s for s in store.for_cadence(cadence) if s.channel == "telegram"]

    sent = 0
    for s in subs:
        try:
            send_message(token, s.target, message)
            sent += 1
        except Exception as e:
            print(f"WARN send failed target={s.target}: {e}")

    print(f"cadence={cadence} sent={sent} total={len(subs)}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in REPORT_BY_CADENCE:
        raise SystemExit("usage: python scripts/send_telegram_reports.py [daily|weekly|monthly]")
    main(sys.argv[1])
