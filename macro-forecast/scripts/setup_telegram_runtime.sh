#!/usr/bin/env bash
set -euo pipefail

# Required env vars:
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_WEBHOOK_URL  (e.g. https://example.com/telegram/webhook)

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN is required}"
: "${TELEGRAM_WEBHOOK_URL:?TELEGRAM_WEBHOOK_URL is required}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/3] Configure Telegram webhook"
PYTHONPATH=src python3 scripts/configure_telegram_webhook.py

echo "[2/3] Ensure webhook path is healthy (server must be running separately)"
echo "      expected path: /telegram/webhook"

echo "[3/3] Done"
echo "Next: run webhook server"
echo "  PYTHONPATH=src TELEGRAM_BOT_TOKEN=*** python3 scripts/serve_telegram_webhook.py"
