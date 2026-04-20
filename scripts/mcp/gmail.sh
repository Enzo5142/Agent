#!/bin/bash
# Wrapper MCP Gmail. Credenciais OAuth vivem em ~/.gmail-mcp/.
set -euo pipefail
exec npx -y @gongrzhe/server-gmail-autoauth-mcp
