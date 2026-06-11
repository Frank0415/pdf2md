#!/usr/bin/env bash
# Start vLLM serving KDLAI/KDL-Frontier-Parser-nano for pdf2md --mode frontier.
set -euo pipefail

MODEL="${KDL_NANO_MODEL:-KDLAI/KDL-Frontier-Parser-nano}"
SERVED_NAME="${KDL_NANO_SERVED_NAME:-kdl-frontier-parser-nano}"
PORT="${KDL_NANO_PORT:-8000}"

if ! command -v vllm >/dev/null 2>&1; then
  echo "vllm not found. Install with: uv pip install vllm" >&2
  exit 1
fi

echo "Serving ${MODEL} as ${SERVED_NAME} on :${PORT}"
echo "Then: export KDL_NANO_ENDPOINT_URL=http://localhost:${PORT}/v1"

exec vllm serve "${MODEL}" \
  --served-model-name "${SERVED_NAME}" \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --max-num-seqs 24 \
  --trust-remote-code \
  --limit-mm-per-prompt '{"image":1}'
