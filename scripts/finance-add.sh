#!/bin/bash
# Lança despesa/receita a partir de texto natural.
# Uso: finance-add.sh "Gastei 150 no mercado ontem"
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

TEXT="${1:?texto obrigatório}"
log "Finance add: $TEXT"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "Rode o subagent finance-tracker na ação 'lançar transação'.
Input: $TEXT
Retorne APENAS a confirmação curta pro iMessage.")"

notify "financas" "$output"
