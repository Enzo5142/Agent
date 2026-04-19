#!/bin/bash
# Analisa artigo de texto.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

URL="${1:?URL obrigatório}"
log "Analisando artigo: $URL"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "Rode o subagent article-analyzer com URL=$URL.")"

notify "article" "$output"
