# Setup — Jarvis no Mac

Tempo estimado: **30-45 min** (30 min de `install.sh` + 15 min colando
tokens + testando).

## Pré-requisitos

- macOS (Apple Silicon ou Intel)
- Homebrew instalado (https://brew.sh)
- Assinatura Claude Max ativa
- Conta Tailscale (grátis)

## Passo 1 — Clonar o repo

```bash
cd ~
git clone git@github.com:enzo5142/Agent.git
cd Agent
```

## Passo 2 — Instalar Claude Code

```bash
brew install node   # se ainda não tiver
npm install -g @anthropic-ai/claude-code
claude login        # faça login com sua conta Max
```

## Passo 3 — Rodar o bootstrap

```bash
bash install.sh
```

O script faz:
- `brew install ffmpeg yt-dlp jq gettext`
- cria `.venv` do webhook e instala deps Python
- instala `openai-whisper` via pip
- cria estrutura de pastas no Obsidian vault (`Jarvis/`, `Inbox/`, etc)
- gera `.env` com token aleatório se não existir
- instala todos os `launchd/*.plist` em `~/Library/LaunchAgents/`
- carrega os jobs (`launchctl bootstrap`)

## Passo 4 — Preencher `.env`

Abrir `.env` e colar:

```
NOTION_TOKEN=ntn_...
GITHUB_TOKEN=github_pat_...
JARVIS_IMESSAGE_RECIPIENT="+5511XXXXXXXXX"
JARVIS_TAILSCALE_HOST="enzo-mac.tailnet-xxx.ts.net"
```

O `JARVIS_TOKEN` e as demais variáveis já foram preenchidas pelo `install.sh`.

Ver `CREDENTIALS_NEEDED.md` pra detalhes de como gerar cada um.

## Passo 5 — Primeira autenticação Gmail/Calendar

```bash
# Gmail
npx -y @gongrzhe/server-gmail-autoauth-mcp auth

# Calendar: salva credentials.json em ~/.config/jarvis/
mkdir -p ~/.config/jarvis
# copia o JSON baixado do Google Cloud Console pra ~/.config/jarvis/gcal-credentials.json
npx -y @cocal/google-calendar-mcp auth
```

Cada comando abre o browser pra você autorizar.

## Passo 6 — Estrutura inicial no Notion

Criar uma página raiz "Jarvis" no Notion e, dentro dela, databases:

- `Tasks` — colunas: Nome, Status, Prioridade, Projeto, Due, Tags
- `Projects` — Nome, Status, Prioridade, Owner, Última atividade, Next action
- `Finanças / Transações` — Data, Descrição, Valor, Tipo, Categoria, Conta
- `Finanças / Contas a pagar` — Descrição, Valor, Vencimento, Status
- `Finanças / Metas` — Mês, Categoria, Limite, Realizado
- `Finanças / Categorias` — lista fixa
- `Hábitos` — Data, Hábito, Feito, Observação
- `Saúde / Consultas` — Tipo, Status, Data, Observações
- `Team` — Nome, GitHub, Role, Ativo
- `CRM` — Nome, Relação, Contato, Último contato, Notas

**Compartilhar a página raiz "Jarvis" com a integração Notion** (... →
Connect to → Jarvis). Todos os databases herdam acesso.

## Passo 7 — Estrutura inicial no Obsidian

Dentro do vault (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Main`):

```
Main/
├── Projects/
│   ├── Plataforma de Inglês/
│   ├── FinChat/
│   ├── Ana Dash/
│   └── Meditar com Você/
├── Areas/
│   ├── Saúde/
│   ├── Finanças/
│   ├── Relacionamento/
│   └── Carreira/
├── Resources/
├── Archive/
├── Daily/
├── Inbox/
│   ├── videos/
│   ├── notifications/
│   └── whatsapp/
├── Ideas/
└── Jarvis/
    ├── log/
    ├── briefings/
    ├── reviews/
    ├── weekly/
    ├── monthly/
    ├── team/
    ├── email/
    ├── meta/
    └── whatsapp/
```

O `install.sh` cria isso automaticamente se o vault for detectado.

## Passo 8 — Tailscale

Seguir instruções em `CREDENTIALS_NEEDED.md` (seção 6). Depois:

```bash
curl -H "X-Jarvis-Token: $(grep JARVIS_TOKEN .env | cut -d= -f2)" \
     http://localhost:8787/health
```

Deve retornar `{"status":"ok",...}`.

## Passo 9 — Shortcuts no iPhone

Seguir `shortcuts/README.md`. Criar ao menos:
1. Jarvis Captura Rápida
2. Jarvis Captura de Voz
3. Analisar Vídeo (Share Sheet)
4. Lançar Despesa

## Passo 10 — Validar

```bash
# Briefing on-demand
bash scripts/briefing.sh

# Check GitHub
bash scripts/github-monitor.sh

# Captura de teste
bash scripts/capture.sh text "Comprar filtro do ar" "tarefa"
```

Se tudo funcionar, o launchd vai disparar automaticamente nos horários
programados.

## Status dos jobs

```bash
launchctl list | grep enzo.jarvis
```

## Ver logs

```bash
tail -f /tmp/jarvis-*.log
tail -f "$OBSIDIAN_VAULT/Jarvis/log/$(date +%Y-%m-%d).md"
```

## Desligar tudo (emergência)

```bash
ls ~/Library/LaunchAgents/com.enzo.jarvis.* \
  | xargs -I{} launchctl bootout gui/$(id -u) {}
```

## Atualizar

```bash
cd ~/Agent
git pull
bash install.sh   # idempotente, só reaplica o que mudou
```
