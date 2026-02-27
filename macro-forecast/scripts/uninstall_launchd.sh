#!/usr/bin/env bash
set -euo pipefail

LABEL="ai.econdevkr.polling"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
rm -f "$PLIST"

echo "Uninstalled: ${LABEL}"
