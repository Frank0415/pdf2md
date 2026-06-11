#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDF2MD_REPO="$ROOT"
exec "${ROOT}/skill/pdf2md/scripts/detect-platform.sh" --repo "$ROOT" "$@"
