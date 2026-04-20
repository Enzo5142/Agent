#!/bin/bash
# Meta-agente. Sexta 18:00.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Meta review"
claude --dangerously-skip-permissions --print \
    "Rode o subagent meta-agent e salve o relatório em Obsidian." \
    > /dev/null
log "Meta review concluído"
