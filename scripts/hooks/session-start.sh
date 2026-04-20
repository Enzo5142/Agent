#!/bin/bash
# Hook: rodado ao início de cada sessão Claude Code.
# Garante que o log do dia exista e registra início.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"
log "Sessão Claude iniciada (cwd=$(pwd))"
