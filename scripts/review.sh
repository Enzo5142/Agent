#!/bin/bash
# Review de fim de dia. Disparado pelo launchd às 18:30.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Iniciando review fim de dia"
output="$(run_claude prompts/review.md)"
notify "review" "$output"
log "Review enviado"
