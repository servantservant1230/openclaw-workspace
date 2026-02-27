#!/usr/bin/env bash
set -euo pipefail

LABEL="ai.econdevkr.polling"
ROOT="/Volumes/WORK_SSD/workspace/macro-forecast"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
ENV_FILE="${ECONDEV_ENV_FILE:-$HOME/.config/econdevkr_bot.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  echo "Create it with TELEGRAM_BOT_TOKEN='...'"
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>cd ${ROOT} &amp;&amp; source ${ENV_FILE} &amp;&amp; PYTHONPATH=src /usr/bin/python3 scripts/run_telegram_polling.py</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>WorkingDirectory</key>
  <string>${ROOT}</string>

  <key>StandardOutPath</key>
  <string>/tmp/econdevkr-polling.out.log</string>

  <key>StandardErrorPath</key>
  <string>/tmp/econdevkr-polling.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

echo "Installed and started: ${LABEL}"
launchctl print "gui/$(id -u)/${LABEL}" | head -n 30
