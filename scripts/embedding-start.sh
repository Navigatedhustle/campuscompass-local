#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec runtime/llama.cpp/build/bin/llama-server -m models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf --embedding --pooling last --host 127.0.0.1 --port 8082 --ctx-size 4096 --batch-size 4096 --ubatch-size 4096 --parallel 1 --n-gpu-layers 99 --no-webui --cors-origins http://127.0.0.1:8000
