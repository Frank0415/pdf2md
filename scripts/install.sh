#!/usr/bin/env bash
# Repo wrapper — canonical install lives in skill/pdf2md/scripts/
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDF2MD_REPO="$ROOT"
exec "${ROOT}/skill/pdf2md/scripts/install.sh" --repo "$ROOT" "$@"
