#!/bin/bash
# Review mensal. Dia 1 do mês 09:00.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Iniciando review mensal"
output="$(run_claude prompts/monthly.md)"
notify "monthly" "$output"
log "Review mensal enviado"
