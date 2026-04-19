#!/bin/bash
# Biblioteca comum dos scripts Jarvis.

set -euo pipefail

export JARVIS_HOME="${JARVIS_HOME:-$HOME/Agent}"
export OBSIDIAN_VAULT="${OBSIDIAN_VAULT:-$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Main}"
export JARVIS_LOG_DIR="${JARVIS_LOG_DIR:-$OBSIDIAN_VAULT/Jarvis/log}"
export JARVIS_TMP="${JARVIS_TMP:-/tmp/jarvis}"

mkdir -p "$JARVIS_LOG_DIR" "$JARVIS_TMP"

# Carrega .env se existir
if [ -f "$JARVIS_HOME/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$JARVIS_HOME/.env"
    set +a
fi

log() {
    local msg="$1"
    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    local day
    day="$(date '+%Y-%m-%d')"
    echo "[$ts] $msg" >> "$JARVIS_LOG_DIR/$day.md"
    echo "[$ts] $msg"
}

# Envia iMessage via AppleScript (só funciona no Mac)
send_imessage() {
    local recipient="${JARVIS_IMESSAGE_RECIPIENT:-}"
    local message="$1"
    if [ -z "$recipient" ]; then
        log "ERRO: JARVIS_IMESSAGE_RECIPIENT não definido em .env"
        return 1
    fi
    osascript <<EOF
tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant "$recipient" of targetService
    send "$message" to targetBuddy
end tell
EOF
}

# Fallback: escreve na Inbox do Obsidian como notificação
notify_fallback() {
    local title="$1"
    local body="$2"
    local ts
    ts="$(date '+%Y-%m-%d-%H%M')"
    mkdir -p "$OBSIDIAN_VAULT/Inbox/notifications"
    cat > "$OBSIDIAN_VAULT/Inbox/notifications/$ts-$title.md" <<EOF
# $title

$body

*Gerado em $(date '+%Y-%m-%d %H:%M')*
EOF
}

# Tenta iMessage, cai pra Obsidian Inbox
notify() {
    local title="$1"
    local body="$2"
    if ! send_imessage "$body" 2>/dev/null; then
        notify_fallback "$title" "$body"
    fi
}

# Roda Claude Code com um prompt de arquivo, sem interação e sem permissões.
# Uso: run_claude prompts/briefing.md
run_claude() {
    local prompt_file="$1"
    shift || true
    local prompt
    prompt="$(envsubst < "$JARVIS_HOME/$prompt_file")"
    cd "$JARVIS_HOME"
    claude \
        --dangerously-skip-permissions \
        --print \
        --model claude-opus-4-7 \
        "$prompt" "$@"
}
