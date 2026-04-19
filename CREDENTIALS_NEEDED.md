# Credenciais necessárias

Gere cada uma e cole em `.env` (use `.env.example` como base).

---

## 1. Notion API Token — OBRIGATÓRIO

1. Abrir https://www.notion.so/my-integrations
2. **+ New integration**
3. Nome: `Jarvis`. Associated workspace: seu workspace.
4. Capabilities: **Read content**, **Update content**, **Insert content**,
   **Read user information** (sem email, por segurança).
5. Submit → copiar o **Internal Integration Token** (`ntn_...`).
6. Colar em `.env` como `NOTION_TOKEN`.
7. **Compartilhar páginas com a integração**: em cada página/database que o
   Jarvis deve acessar, abrir `...` → `Connect to` → `Jarvis`.
   Recomendado fazer isso na página raiz "Jarvis" (explicada no SETUP).

## 2. GitHub Personal Access Token — OBRIGATÓRIO

1. https://github.com/settings/tokens (Fine-grained recomendado)
2. **Generate new token (fine-grained)**
3. Nome: `jarvis-agent`. Expira: 1 ano.
4. Resource owner: você (e orgs que quer monitorar).
5. Repository access: **All repositories** (ou só as relevantes).
6. Permissions:
   - Actions: Read
   - Contents: Read
   - Issues: Read and write
   - Pull requests: Read and write
   - Metadata: Read (auto)
7. Generate → copiar `github_pat_...` → `.env` como `GITHUB_TOKEN`.

## 3. Gmail — OBRIGATÓRIO

O MCP `@gongrzhe/server-gmail-autoauth-mcp` cuida do OAuth na primeira
execução. Ele abre o navegador e você autoriza.

Não precisa colar nada agora — só rodar uma vez e autorizar.

## 4. Google Calendar — OBRIGATÓRIO

1. https://console.cloud.google.com/ → criar projeto "Jarvis"
2. APIs & Services → **Enable APIs** → Google Calendar API
3. OAuth consent screen → External → preencher o básico.
4. Credentials → **Create Credentials** → OAuth client ID → Desktop app.
5. Download JSON → salvar como `~/.config/jarvis/gcal-credentials.json`.
6. Primeira execução do MCP vai pedir autorização no browser.

## 5. Jarvis Token (webhook) — GERA AUTOMÁTICO

`install.sh` gera um token aleatório e coloca em `.env` como `JARVIS_TOKEN`.
Copia o valor pra usar nos Shortcuts iOS.

## 6. Tailscale — OBRIGATÓRIO pra iPhone ↔ Mac

1. Instalar Tailscale no **Mac** (https://tailscale.com/download)
2. Logar com sua conta.
3. Instalar no **iPhone** (App Store).
4. Logar com a mesma conta.
5. Anotar o MagicDNS do Mac (Tailscale menu bar → clica no nome).
   Fica tipo `enzo-mac.tailnet-xxx.ts.net`.
6. Colar em `.env` como `JARVIS_TAILSCALE_HOST`.

## 7. iMessage — usa automaticamente

Seu número/email já tá logado no Messages do Mac. Só precisa definir o
destinatário em `.env`:

```
JARVIS_IMESSAGE_RECIPIENT="+5511XXXXXXXXX"
```

## 8. Claude Code — já tem

Você já paga Max. Só precisa rodar `claude login` uma vez no Mac antes
do install.

---

## Opcionais (podem ficar pra depois)

### Whisper (transcrição local)

Instalado automaticamente pelo install.sh via pip.

### yt-dlp + ffmpeg (análise de vídeo)

Instalado automaticamente pelo install.sh via homebrew.

### WhatsApp bridge

Manual. Ver `scripts/whatsapp-bridge.js` (TODO). Por enquanto, captura é via
share do iOS → Shortcut pro endpoint `/capture` com hint `whatsapp`.
