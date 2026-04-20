#!/bin/bash
# Briefing matinal. Disparado pelo launchd às 07:30.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Iniciando briefing matinal"
output="$(run_claude prompts/briefing.md)"
log "Briefing gerado"

notify "briefing" "$output"
log "Briefing enviado"
