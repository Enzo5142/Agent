#!/bin/bash
# Wrapper MCP Google Calendar.
set -euo pipefail
ENV_FILE="${JARVIS_ENV_FILE:-$HOME/Agent/.env}"
[ -f "$ENV_FILE" ] && { set -a; source "$ENV_FILE"; set +a; }
export GOOGLE_OAUTH_CREDENTIALS="${GOOGLE_OAUTH_CREDENTIALS:-$HOME/.config/jarvis/gcal-credentials.json}"
exec npx -y @cocal/google-calendar-mcp
