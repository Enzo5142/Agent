#!/bin/bash
# Wrapper MCP Notion. Carrega .env antes porque Claude Code não expande ${VAR}
# dentro de mcpServers no settings.json.
set -euo pipefail
ENV_FILE="${JARVIS_ENV_FILE:-$HOME/Agent/.env}"
[ -f "$ENV_FILE" ] && { set -a; source "$ENV_FILE"; set +a; }
: "${NOTION_TOKEN:?NOTION_TOKEN ausente em $ENV_FILE}"
export OPENAPI_MCP_HEADERS="{\"Authorization\":\"Bearer $NOTION_TOKEN\",\"Notion-Version\":\"2022-06-28\"}"
exec npx -y @notionhq/notion-mcp-server
