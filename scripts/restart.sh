#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
systemctl --user restart campuscompass-model campuscompass-embedding campuscompass-reranker campuscompass-app
.venv/bin/python scripts/wait-health.py
