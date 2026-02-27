#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/WORK_SSD/workspace"
ENV_FILE="${ECONDEV_ENV_FILE:-$HOME/.config/econdevkr_bot.env}"
START_POLLING="$ROOT/macro-forecast/scripts/start_polling.sh"
RUN_SEND="$ROOT/macro-forecast/scripts/run_and_send.sh"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  echo "Create it with TELEGRAM_BOT_TOKEN='...'"
  exit 1
fi

TMP="$(mktemp)"
crontab -l 2>/dev/null > "$TMP" || true

add_line() {
  local line="$1"
  if ! grep -Fq "$line" "$TMP"; then
    echo "$line" >> "$TMP"
  fi
}

# polling watchdog: every minute ensure process is running
add_line "* * * * * pgrep -f 'run_telegram_polling.py' >/dev/null || (cd $ROOT/macro-forecast && ECONDEV_ENV_FILE=$ENV_FILE ./scripts/start_polling.sh >> /tmp/econdevkr-polling.log 2>&1 &)"

# reports
add_line "30 8 * * * cd $ROOT/macro-forecast && source $ENV_FILE && ./scripts/run_and_send.sh daily >> /tmp/macro-forecast-daily.log 2>&1"
add_line "40 8 * * 1 cd $ROOT/macro-forecast && source $ENV_FILE && ./scripts/run_and_send.sh weekly >> /tmp/macro-forecast-weekly.log 2>&1"
add_line "50 8 1 * * cd $ROOT/macro-forecast && source $ENV_FILE && ./scripts/run_and_send.sh monthly >> /tmp/macro-forecast-monthly.log 2>&1"

crontab "$TMP"
rm -f "$TMP"

echo "Installed/updated cron entries."
crontab -l
