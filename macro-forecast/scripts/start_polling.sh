#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ECONDEV_ENV_FILE:-$HOME/.config/econdevkr_bot.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  echo "Create it with:"
  echo "  TELEGRAM_BOT_TOKEN='your_new_token'"
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN is required in $ENV_FILE}"

cd "$ROOT"
exec PYTHONPATH=src python3 scripts/run_telegram_polling.py
