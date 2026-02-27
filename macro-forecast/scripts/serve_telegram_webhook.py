from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from macro_forecast.telegram_webhook import process_update

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "subscribers.json"
HOST = os.environ.get("TELEGRAM_WEBHOOK_HOST", "127.0.0.1")
PORT = int(os.environ.get("TELEGRAM_WEBHOOK_PORT", "8787"))
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def send_message(token: str, chat_id: str, text: str) -> None:
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        _ = resp.read()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/telegram/webhook":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        try:
            update = json.loads(raw.decode("utf-8"))
            action = process_update(DB, update)
            if action.chat_id and action.reply_text:
                send_message(TOKEN, action.chat_id, action.reply_text)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"telegram webhook server listening on http://{HOST}:{PORT}/telegram/webhook")
    server.serve_forever()
