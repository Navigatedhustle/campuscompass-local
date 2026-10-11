#!/usr/bin/env bash
set -euo pipefail
systemctl --user stop campuscompass-app campuscompass-reranker campuscompass-embedding campuscompass-model
