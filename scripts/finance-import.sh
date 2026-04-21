#!/bin/bash
# Importa extratos/faturas pro Notion. Uso: bash scripts/finance-import.sh [pasta]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

# Carrega IDs do Finance Hub
if [ -f "$JARVIS_HOME/.notion-dbs.env" ]; then
    set -a; source "$JARVIS_HOME/.notion-dbs.env"; set +a
fi

: "${NOTION_TOKEN:?NOTION_TOKEN ausente}"
: "${NOTION_FH_TRANSACOES:?Rodar finance_setup.sh primeiro}"

PY="$JARVIS_HOME/webhook/.venv/bin/python"
[ -x "$PY" ] || { echo "venv do webhook não encontrado. Rode install.sh."; exit 1; }

exec "$PY" "$SCRIPT_DIR/finance/import.py" "$@"
