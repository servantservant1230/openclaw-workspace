#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/WORK_SSD/workspace"
RUN="$ROOT/macro-forecast/scripts/run_and_send.sh"

TMP="$(mktemp)"
crontab -l 2>/dev/null > "$TMP" || true

add_line() {
  local line="$1"
  if ! grep -Fq "$line" "$TMP"; then
    echo "$line" >> "$TMP"
  fi
}

add_line "30 8 * * * cd $ROOT && TELEGRAM_BOT_TOKEN=\"\${TELEGRAM_BOT_TOKEN}\" ./macro-forecast/scripts/run_and_send.sh daily >> /tmp/macro-forecast-daily.log 2>&1"
add_line "40 8 * * 1 cd $ROOT && TELEGRAM_BOT_TOKEN=\"\${TELEGRAM_BOT_TOKEN}\" ./macro-forecast/scripts/run_and_send.sh weekly >> /tmp/macro-forecast-weekly.log 2>&1"
add_line "50 8 1 * * cd $ROOT && TELEGRAM_BOT_TOKEN=\"\${TELEGRAM_BOT_TOKEN}\" ./macro-forecast/scripts/run_and_send.sh monthly >> /tmp/macro-forecast-monthly.log 2>&1"

crontab "$TMP"
rm -f "$TMP"

echo "Installed/updated cron entries."
crontab -l
