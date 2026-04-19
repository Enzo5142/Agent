#!/bin/bash
# Monitoramento do time. 09:00, 13:00, 17:00.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Monitoramento GitHub"
output="$(run_claude prompts/github-check.md)"
# Só notificar se houver alerta real
if echo "$output" | grep -qi "alerta\|travado\|backlog vazio\|CI vermelho"; then
    notify "github" "$output"
fi
log "GitHub check concluído"
