#!/usr/bin/env bash
# Install pdf2md with uv; MinerU backend is chosen from platform profile.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS_ARGS=()
while [[ $# -gt 0 ]]; do
  PASS_ARGS+=("$1")
  shift
done

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install: https://docs.astral.sh/uv/" >&2
  exit 1
fi

bash "${ROOT}/scripts/detect-platform.sh" "${PASS_ARGS[@]}"

MANIFEST="${ROOT}/.pdf2md/platform.json"
if [[ ! -f "$MANIFEST" ]]; then
  echo "platform.json not found after detection" >&2
  exit 1
fi

PROFILE="$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['profile'])")"
GPU_BACKEND="$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['gpu_backend'])")"
TORCH_INDEX="$(python3 -c "import json; d=json.load(open('${MANIFEST}')); print(d.get('torch_index',''))")"

echo "Installing for profile: $PROFILE"

bash "${ROOT}/scripts/install-system-deps.sh" || true

if [[ ! -d .venv ]]; then
  uv venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

uv pip install -U pip

case "$PROFILE" in
  mac_arm)
    uv pip install -U "mineru[core,mlx]"
    ;;
  linux_gpu)
    if [[ -n "$TORCH_INDEX" ]]; then
      uv pip install -U torch torchvision --index-url "https://download.pytorch.org/whl/${TORCH_INDEX}"
    fi
    uv pip install -U "mineru[core,vllm]"
    ;;
  linux_cpu)
    uv pip install -U "mineru[core]"
    ;;
  *)
    echo "Unknown profile: $PROFILE" >&2
    exit 1
    ;;
esac

# MinerU 3.2.x is incompatible with transformers 5.x (PPDocLayoutV2Config).
uv pip install 'transformers>=4.49,<5'

uv pip install -e .

if command -v mineru-models-download >/dev/null 2>&1; then
  echo "Downloading MinerU models (this may take a while)..."
  mineru-models-download -s huggingface -m all || mineru-models-download -m all || true
fi

BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "${ROOT}/.venv/bin/pdf2md" "${BIN_DIR}/pdf2md"

echo ""
echo "Install complete."
echo "  profile:      $PROFILE"
echo "  gpu_backend:  $GPU_BACKEND"
echo "  pdf2md:       ${BIN_DIR}/pdf2md"
echo "Run: pdf2md doctor"
