#!/bin/bash
# Bootstrap do Jarvis no Mac. Idempotente.
set -euo pipefail

JARVIS_HOME="${JARVIS_HOME:-$HOME/Agent}"
cd "$JARVIS_HOME"

say() { printf "\033[1;36m▸\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m⚠\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m✖\033[0m %s\n" "$*" >&2; }

# ---------------------------------------------------------------- dependências
say "Checando dependências do sistema..."
if ! command -v brew >/dev/null 2>&1; then
    err "Homebrew não instalado. https://brew.sh"
    exit 1
fi

for pkg in ffmpeg yt-dlp jq gettext python@3.12 node tesseract; do
    if ! brew list "$pkg" >/dev/null 2>&1; then
        say "Instalando $pkg..."
        brew install "$pkg"
    fi
done

if ! command -v claude >/dev/null 2>&1; then
    say "Instalando Claude Code..."
    npm install -g @anthropic-ai/claude-code
fi

# ---------------------------------------------------------------- venv webhook
say "Configurando venv do webhook..."
if [ ! -d "$JARVIS_HOME/webhook/.venv" ]; then
    python3 -m venv "$JARVIS_HOME/webhook/.venv"
fi
"$JARVIS_HOME/webhook/.venv/bin/pip" install --quiet --upgrade pip
"$JARVIS_HOME/webhook/.venv/bin/pip" install --quiet \
    -r "$JARVIS_HOME/webhook/requirements.txt"
say "Instalando openai-whisper..."
"$JARVIS_HOME/webhook/.venv/bin/pip" install --quiet openai-whisper trafilatura

# ---------------------------------------------------------------- .env
if [ ! -f "$JARVIS_HOME/.env" ]; then
    say "Gerando .env com token aleatório..."
    TOKEN="$(openssl rand -hex 32)"
    cp "$JARVIS_HOME/.env.example" "$JARVIS_HOME/.env"
    # substitui JARVIS_TOKEN
    sed -i '' "s|^JARVIS_TOKEN=.*|JARVIS_TOKEN=$TOKEN|" "$JARVIS_HOME/.env"
    warn "PREENCHA os outros tokens em .env (Notion, GitHub, Tailscale, iMessage)"
else
    say ".env já existe, não sobrescrevendo."
fi

# ---------------------------------------------------------------- estrutura Obsidian
OBSIDIAN_VAULT="${OBSIDIAN_VAULT:-$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Main}"
if [ -d "$OBSIDIAN_VAULT" ]; then
    say "Criando estrutura no Obsidian..."
    for dir in \
        "Projects/Plataforma de Inglês" \
        "Projects/FinChat" \
        "Projects/Ana Dash" \
        "Projects/Meditar com Você" \
        "Areas/Saúde" \
        "Areas/Finanças" \
        "Areas/Relacionamento" \
        "Areas/Carreira" \
        "Resources" \
        "Archive" \
        "Daily" \
        "Inbox/videos" \
        "Inbox/notifications" \
        "Inbox/whatsapp" \
        "Ideas" \
        "Jarvis/log" \
        "Jarvis/briefings" \
        "Jarvis/reviews" \
        "Jarvis/weekly" \
        "Jarvis/monthly" \
        "Jarvis/team" \
        "Jarvis/email" \
        "Jarvis/meta" \
        "Jarvis/whatsapp" \
        "Finanças"; do
        mkdir -p "$OBSIDIAN_VAULT/$dir"
    done
else
    warn "Vault Obsidian não encontrado em $OBSIDIAN_VAULT"
    warn "Ajuste OBSIDIAN_VAULT no .env depois."
fi

# ---------------------------------------------------------------- permissões scripts
say "Dando permissão de execução aos scripts..."
chmod +x "$JARVIS_HOME"/scripts/*.sh "$JARVIS_HOME"/scripts/hooks/*.sh \
    "$JARVIS_HOME"/install.sh

# ---------------------------------------------------------------- launchd
say "Instalando launchd agents..."
LAUNCH_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_DIR"

for plist in "$JARVIS_HOME"/launchd/com.enzo.jarvis.*.plist; do
    name="$(basename "$plist")"
    dest="$LAUNCH_DIR/$name"
    cp "$plist" "$dest"
    launchctl bootout "gui/$(id -u)" "$dest" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$dest"
done

say "Jobs carregados:"
launchctl list | grep enzo.jarvis || warn "Nenhum job apareceu — verificar erros acima."

# ---------------------------------------------------------------- teste rápido
say "Testando webhook..."
sleep 2
if curl -sf http://localhost:8787/health >/dev/null; then
    say "Webhook rodando. ✓"
else
    warn "Webhook não respondeu. Ver /tmp/jarvis-webhook.err.log"
fi

echo
say "✅ Instalação concluída."
echo
echo "Próximos passos:"
echo "  1. Preencher os tokens restantes em .env"
echo "  2. Rodar 'claude login' se ainda não tiver feito"
echo "  3. Criar Shortcuts no iPhone (ver shortcuts/README.md)"
echo "  4. Compartilhar páginas do Notion com a integração 'Jarvis'"
echo "  5. Testar: bash scripts/briefing.sh"
