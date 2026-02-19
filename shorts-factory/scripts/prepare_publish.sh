#!/bin/zsh
set -euo pipefail
BASE="/Volumes/WORK_SSD/workspace/shorts-factory"

python3 "$BASE/src/orchestrator.py" --topic-limit 4
python3 "$BASE/src/select_candidate.py"
python3 "$BASE/src/build_publish_package.py"

echo "[shorts-factory] publish package ready: $BASE/outputs/publish_package.json"
