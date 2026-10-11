#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec runtime/llama.cpp/build/bin/llama-server -m models/reranker/Qwen3-Reranker-0.6B-rank-q8_0.gguf --reranking --embedding --pooling rank --host 127.0.0.1 --port 8083 --ctx-size 4096 --batch-size 4096 --ubatch-size 4096 --parallel 1 --n-gpu-layers 99 --no-webui --cors-origins http://127.0.0.1:8000
