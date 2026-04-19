#!/bin/bash
# Triagem de email. A cada 2h entre 08-20.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

log "Triagem de email"
output="$(run_claude prompts/email-check.md)"
if ! echo "$output" | grep -q "Inbox sob controle"; then
    notify "email" "$output"
fi
