#!/bin/bash
# Fechamento financeiro. Dia 10 do mês 09:00.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Fechamento financeiro"
output="$(run_claude prompts/finance-close.md)"
notify "financas" "$output"
