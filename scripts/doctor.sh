#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
hostname
systemctl --user is-active campuscompass-model campuscompass-embedding campuscompass-reranker campuscompass-app
loginctl show-user demo -p Linger
curl --noproxy '*' -fsS http://127.0.0.1:8000/api/health
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
free -h
df -h .
