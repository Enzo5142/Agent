#!/bin/bash
# Analisa vídeo Instagram/YouTube/TikTok.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

URL="${1:?URL obrigatório}"
log "Analisando vídeo: $URL"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "Rode o subagent video-analyzer com URL=$URL.")"

notify "video" "$output"
