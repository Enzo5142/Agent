#!/bin/bash
# Cria issue no GitHub a partir de ideia crua.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

REPO="${1:?repo obrigatório (owner/name)}"
IDEA="${2:?ideia obrigatória}"
log "Issue create em $REPO: $IDEA"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "Rode o subagent issue-creator.
Repo: $REPO
Ideia: $IDEA
Retorne a URL da issue criada.")"

notify "issue" "$output"
