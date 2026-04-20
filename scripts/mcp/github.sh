#!/bin/bash
# Wrapper MCP GitHub.
set -euo pipefail
ENV_FILE="${JARVIS_ENV_FILE:-$HOME/Agent/.env}"
[ -f "$ENV_FILE" ] && { set -a; source "$ENV_FILE"; set +a; }
: "${GITHUB_TOKEN:?GITHUB_TOKEN ausente em $ENV_FILE}"
export GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_TOKEN"
exec npx -y @modelcontextprotocol/server-github
