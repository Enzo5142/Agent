#!/bin/bash
# Digest WhatsApp. Matinal (07:00) e noturno (22:00).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MODE="${1:-evening}"
log "WhatsApp digest — $MODE"
export WA_MODE="$MODE"
output="$(run_claude prompts/whatsapp-digest.md)"
notify "whatsapp" "$output"
