#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
systemctl --user stop campuscompass-app
.venv/bin/python - <<'PYRESET'
from pathlib import Path
from datetime import datetime,timezone
p=Path('var/campuscompass.sqlite3')
archive=Path('var/archive');archive.mkdir(exist_ok=True)
if p.exists():p.rename(archive/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.sqlite3'))
PYRESET
.venv/bin/python scripts/expand-fixtures.py
systemctl --user start campuscompass-app
.venv/bin/python scripts/wait-health.py
