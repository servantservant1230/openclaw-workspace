#!/bin/zsh
set -euo pipefail

BASE="/Volumes/WORK_SSD/workspace/shorts-factory"
TOPIC_LIMIT="${1:-5}"

python3 "$BASE/src/orchestrator.py" --topic-limit "$TOPIC_LIMIT"

echo "[shorts-factory] batch done: topic_limit=$TOPIC_LIMIT"