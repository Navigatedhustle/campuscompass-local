#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/start.sh
exec xdg-open http://127.0.0.1:8000
