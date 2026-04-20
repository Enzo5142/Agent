# Continuação da sessão

> Este arquivo é o contexto pra retomar o trabalho entre sessões do Claude Code.
> Claude: lê isto, executa o "Próximo passo" e segue. Não repete o que já foi feito.

Última atualização: **2026-04-19** (sessão local no Mac do Enzo, `~/Agent` → `~/Repositório/Pessoal/Agent`).

---

## Status atual — o que já está pronto

### Infra
- `install.sh` rodou limpo. 11 jobs launchd carregados.
- Webhook FastAPI respondendo em `localhost:8787/health` e em
  `http://mac-mini-de-enzo.taila196a5.ts.net:8787/health` via Tailscale.
- Symlink `~/Agent` → `~/Repositório/Pessoal/Agent`.
- Dependências Homebrew instaladas (ffmpeg, yt-dlp, tesseract, etc).
- venv do webhook com whisper + trafilatura.

### Credenciais (em `.env`, gitignored)
- `NOTION_TOKEN` — integração "Jarvis" no workspace "Enzo Pruano's Notion".
- `GITHUB_TOKEN` — classic PAT do usuário Enzo5142 (scopes repo, read:org,
  workflow). Enxerga Enzo5142, RCO-Tecnologia, OTM-Invest.
- `JARVIS_IMESSAGE_RECIPIENT` = `+5511955901012`.
- `JARVIS_TAILSCALE_HOST` = `mac-mini-de-enzo.taila196a5.ts.net`.
- Gmail OAuth autenticado (`~/.gmail-mcp/credentials.json`).
- Google Calendar OAuth autenticado
  (`~/.config/google-calendar-mcp/tokens.json`).
- Conta Google usada nos dois: **enzopruano@gmail.com** (pessoal, NÃO
  otmtech). Projeto GCP: `jarvenzo`.

### Notion — databases criadas na página "Jarvis"
IDs salvos em `.notion-dbs.env` (gitignored, auto-carregado pelo `common.sh`):
Projects, Tasks, Transações, Contas a Pagar, Categorias Financeiras,
Metas Financeiras, Hábitos, Consultas Médicas, Team, CRM.

### Obsidian vault
Migrado de PARA numerado (`00 - Inbox`, `01 - Projects`...) pra PARA sem
números (`Inbox`, `Projects`...). 16 arquivos preservados. Subpastas
criadas conforme scripts esperam (`Jarvis/log`, `Projects/Plataforma de
Inglês`, etc).

### MCP servers (.mcp.json + scripts/mcp/)
Todos conectando em sub-sessão `claude --print`:
- `mcp__notion__*` ✓
- `mcp__github__*` ✓
- `mcp__gmail__*` ✓
- `mcp__filesystem__*` ✓ (Obsidian vault)
- `mcp__gcal__*` ⚠️ conecta, mas **Google Calendar API desabilitada no
  projeto GCP** — tem que ativar.

---

## Bugs raiz corrigidos nesta sessão

1. **`${HOME}`/`${VAR}` não expandem em settings.json**. Claude Code passa
   o texto literal. Causa original do diretório estranho `~/` criado
   dentro do repo e dos MCPs nunca conectarem.
   Fix: `common.sh:expand_home()` + wrappers bash em `scripts/mcp/` que
   fazem `source .env` antes de exec-ar cada servidor MCP.

2. **mcpServers em .claude/settings.json não carrega em --print mode**.
   Fix: mover configuração MCP pra `.mcp.json` na raiz (config
   project-scoped que Claude Code carrega de fato).

3. **@cocal/google-calendar-mcp imprimia mensagem em stdout**,
   poluindo protocolo stdio. Revisto: o pacote já manda pra stderr, o
   bug anterior era meu wrapper com pipe atrapalhando.

4. **Vault Obsidian real era `Enzo Vault`, não `Main`**. `.env` e
   `.mcp.json` apontam pro path correto.

Commits nesta sessão: `b98630b` (MCP fix + expansão tilde).

---

## Próximo passo — EXECUTAR

### 1. Habilitar Google Calendar API
Enzo tem que abrir:
```
https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=852396376540
```
Clicar "Ativar". Espera ~30s propagar.

### 2. Rodar testes end-to-end
Depois que a API propagar:
```bash
bash scripts/capture.sh text "Comprar filtro do ar condicionado" "tarefa"
# esperar: task aparecer em Notion Tasks DB
bash scripts/briefing.sh
# esperar: iMessage com briefing + nota em Obsidian Jarvis/briefings/
bash scripts/github-monitor.sh
# esperar: lista de PRs travados / devs com backlog
```
Validar cada um via API/Obsidian antes de declarar ok.

### 3. Popular database Team no Notion
Precisa de input do Enzo: nome + GitHub username + cargo dos 5 devs.
Inserir via `mcp__notion__*`.

### 4. Shortcuts iOS
Oferecer gerar `.shortcut` exportável pros 4 essenciais:
- Captura rápida (texto → webhook)
- Captura por voz (áudio → whisper → webhook)
- Video share (share sheet → yt-dlp + whisper + resumo)
- Finance (valor + descrição → Notion Finanças)
Ver `shortcuts/README.md`.

### 5. Push pro GitHub
Enzo ainda não autorizou `git push`. Perguntar antes.

---

## Pendências menores / dívida técnica

- `scripts/hooks/session-start.sh` pode ainda criar log num path errado
  se `.env` não estiver carregado — validar que sempre expande
  corretamente. Em teoria o fix em `common.sh` já cobre.
- 2 orgs GitHub disponíveis além de Enzo5142 (RCO-Tecnologia,
  OTM-Invest). Os 5 devs estão em **OTM-Invest** — github-monitor.sh
  deve escopar por lá por padrão.
- Estrutura das 10 databases é um chute inicial. Ajustar campos
  conforme Enzo for usando.

## Estilo ao responder ao Enzo

- Português, direto, sem enrolação.
- Em cada etapa, só resultado relevante (não despeja stdout).
- Se travou em algo, 1 frase de diagnóstico + pergunta objetiva.
- Nunca pede aprovação pra comandos seguros (install, test, curl health).
  Só pede se for destrutivo ou ação externa visível (git push, enviar
  mensagem, criar issue).
