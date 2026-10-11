#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec runtime/llama.cpp/build/bin/llama-server --model models/generation/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf --host 127.0.0.1 --port 8081 --ctx-size 16384 --parallel 1 --n-gpu-layers 99 --jinja --reasoning off --no-reasoning-preserve --no-webui --cors-origins http://127.0.0.1:8000 -lv 4 --temp 0.7 --top-p 0.8 --top-k 20 --min-p 0 --presence-penalty 1.5
