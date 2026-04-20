#!/bin/bash
# Faz code review de um PR e posta o comentário.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

REPO="${1:?repo obrigatório}"
PR="${2:?número do PR obrigatório}"
log "PR review $REPO#$PR"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "Rode o subagent code-reviewer pro PR #$PR no repo $REPO.
Depois de revisar, poste o comentário via mcp__github__pull_request_review_write.
Retorne apenas a URL da review postada.")"

notify "review" "$output"
