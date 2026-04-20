#!/bin/bash
# Review semanal. Domingo 09:00.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Iniciando review semanal"
output="$(run_claude prompts/weekly.md)"
notify "weekly" "$output"
log "Review semanal enviado"
