#!/bin/bash
# Hook: rodado ao fim de cada sessão Claude Code.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib/common.sh"
log "Sessão Claude finalizada"
