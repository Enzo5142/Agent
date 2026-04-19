#!/bin/bash
# Check-in de saúde. Seg/Qua/Sex 07:00 + Quarta 17:00 (aula inglês).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Health check-in"
output="$(run_claude prompts/health-checkin.md)"
notify "saude" "$output"
