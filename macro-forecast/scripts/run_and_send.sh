#!/usr/bin/env bash
set -euo pipefail

CADENCE="${1:-daily}"

cd "$(dirname "$0")/.."

PYTHONPATH=src python3 scripts/run_live_or_sample.py
PYTHONPATH=src python3 scripts/send_telegram_reports.py "$CADENCE"
