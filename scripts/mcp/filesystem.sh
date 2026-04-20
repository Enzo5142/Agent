#!/bin/bash
# Wrapper MCP Filesystem. Aponta pro vault Obsidian.
set -euo pipefail
ENV_FILE="${JARVIS_ENV_FILE:-$HOME/Agent/.env}"
[ -f "$ENV_FILE" ] && { set -a; source "$ENV_FILE"; set +a; }
VAULT="${OBSIDIAN_VAULT:-$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Enzo Vault}"
# Expande ${HOME}/$HOME/~ literais
VAULT="${VAULT//\$\{HOME\}/$HOME}"
VAULT="${VAULT//\$HOME/$HOME}"
case "$VAULT" in "~") VAULT="$HOME" ;; "~/"*) VAULT="$HOME/${VAULT#~/}" ;; esac
exec npx -y @modelcontextprotocol/server-filesystem "$VAULT"
