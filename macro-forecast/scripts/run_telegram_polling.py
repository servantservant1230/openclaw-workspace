from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

from macro_forecast.telegram_webhook import process_update

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "subscribers.json"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_TIMEOUT", "25"))
SLEEP_SEC = float(os.environ.get("TELEGRAM_POLL_SLEEP", "1.5"))


def api_call(method: str, params: dict) -> dict:
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    payload = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=POLL_TIMEOUT + 10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(chat_id: str, text: str) -> None:
    _ = api_call(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
    )


def main() -> None:
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")

    # webhook을 비활성화해 polling 충돌 방지
    _ = api_call("deleteWebhook", {"drop_pending_updates": "false"})

    offset = 0
    print("telegram polling started")
    while True:
        try:
            result = api_call(
                "getUpdates",
                {
                    "timeout": str(POLL_TIMEOUT),
                    "offset": str(offset),
                    "allowed_updates": json.dumps(["message", "edited_message"]),
                },
            )
            if not result.get("ok"):
                time.sleep(SLEEP_SEC)
                continue

            updates = result.get("result", [])
            for upd in updates:
                update_id = int(upd.get("update_id", 0))
                offset = max(offset, update_id + 1)
                action = process_update(DB, upd)
                if action.chat_id and action.reply_text:
                    send_message(action.chat_id, action.reply_text)
        except KeyboardInterrupt:
            print("stopped")
            return
        except Exception as e:
            print(f"WARN polling loop error: {e}")
            time.sleep(SLEEP_SEC)


if __name__ == "__main__":
    main()
