from __future__ import annotations

import os
import urllib.parse
import urllib.request


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    webhook_url = os.environ.get("TELEGRAM_WEBHOOK_URL")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required")
    if not webhook_url:
        raise SystemExit("TELEGRAM_WEBHOOK_URL is required")

    endpoint = f"https://api.telegram.org/bot{token}/setWebhook"
    payload = urllib.parse.urlencode({"url": webhook_url}).encode("utf-8")
    req = urllib.request.Request(endpoint, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        print(resp.read().decode("utf-8"))


if __name__ == "__main__":
    main()
