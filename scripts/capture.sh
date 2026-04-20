#!/bin/bash
# Capture on-demand. Chamado pelo webhook a partir de Shortcuts iOS.
# Args: <type> <content> [hint]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

TYPE="${1:?tipo obrigatório}"
CONTENT="${2:?conteúdo obrigatório}"
HINT="${3:-}"

log "Capture type=$TYPE hint=$HINT content=${CONTENT:0:80}..."

export CAPTURE_TYPE="$TYPE"
export CAPTURE_CONTENT="$CONTENT"
export CAPTURE_HINT="$HINT"

output="$(claude --dangerously-skip-permissions --print \
    --model claude-opus-4-7 \
    "$(cat <<EOF
Você recebeu uma captura.
Type: $TYPE
Hint: $HINT
Content: $CONTENT

Execute o fluxo definido em prompts/capture-router.md e retorne APENAS a
resposta curta pro iMessage.
EOF
)")"

echo "$output"
notify "capture" "$output"
