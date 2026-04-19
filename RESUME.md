# Continuação da sessão

> Este arquivo é o contexto pra retomar o trabalho na sessão local do Mac.
> Claude: lê isto, executa o "Próximo passo" e segue. Não precisa repetir
> o que já foi feito.

---

## Onde paramos

O Enzo está montando o **Jarvis**, agente pessoal dele. Construímos o
scaffold completo na sessão anterior (cloud sandbox) e commitamos em `main`.
Agora ele abriu `~/Agent` em modo local no claude.ai/code e quer continuar
a instalação direto no Mac dele.

## Contexto do Enzo (resumo — detalhe completo em `CLAUDE.md`)

- Founder, lidera 5 devs.
- Usa só iPhone + Mac. Odeia aprovar permissões.
- Sempre português, direto, sem enrolação.
- Claude Max ($200) — tudo roda pela assinatura, sem API paga.
- Quer Jarvis cuidando de trabalho + vida pessoal.

## O que já está pronto no repo

- `CLAUDE.md` com perfil completo
- `.claude/settings.json` com MCP servers (Notion, GitHub, Gmail, GCal, FS)
- 17 subagents em `.claude/agents/`
- 17 scripts em `scripts/`
- Webhook FastAPI em `webhook/server.py`
- 11 plists launchd em `launchd/`
- Templates em `templates/`
- Guia Shortcuts iOS em `shortcuts/README.md`
- `SETUP.md`, `CREDENTIALS_NEEDED.md`, `README.md`, `install.sh`, `.env.example`

**Total: ~77 arquivos, 2800 linhas. Commits: `38d7e20` + `2bd1447`.**

## Bugs já corrigidos

- Settings.json usava `~/...` que criava pasta literal `~/` quando hook
  rodava → trocado pra `${HOME}/...`.
- `common.sh` ganhou expansão de til + guarda contra criar dir relativo.

## Próximo passo — EXECUTAR AGORA

Você (Claude) está com Bash ligado no Mac do Enzo. Faz o seguinte em
sequência, tudo de uma vez, sem pedir permissão:

### 1. Validar estado
```bash
pwd
git status
git log --oneline -3
which claude
which brew
```

### 2. Rodar install
```bash
bash install.sh
```

O script é idempotente. Se der erro em alguma dependência, resolve e roda
de novo.

### 3. Verificar jobs carregados
```bash
launchctl list | grep enzo.jarvis
curl -sf http://localhost:8787/health || echo "webhook não subiu"
```

### 4. Preencher .env parcial
O `install.sh` já gera `JARVIS_TOKEN`. Você deve checar se `.env` existe
e quais campos ainda faltam:
```bash
grep -E "^(NOTION_TOKEN|GITHUB_TOKEN|JARVIS_IMESSAGE_RECIPIENT|JARVIS_TAILSCALE_HOST)=" .env
```

Pros campos vazios/placeholder, **perguntar ao Enzo** (ver próxima seção).

### 5. Apresentar o que falta de input dele
Listar em até 6 linhas o que ele ainda precisa fornecer pra Jarvis ficar
100%. Ordem:

1. **Notion token** — ele gera em https://www.notion.so/my-integrations
   (nome: Jarvis). Colar em `.env` como `NOTION_TOKEN=ntn_...`.
2. **GitHub token (fine-grained)** — https://github.com/settings/tokens.
   Permissões: contents:read, issues:rw, PRs:rw, actions:read.
   Colar como `GITHUB_TOKEN=`.
3. **Número pro iMessage** — `JARVIS_IMESSAGE_RECIPIENT="+5511..."`.
4. **Tailscale** — instalar no Mac + iPhone, copiar MagicDNS do Mac pro
   `.env` como `JARVIS_TAILSCALE_HOST=...`.
5. **Gmail OAuth** — rodar
   `npx -y @gongrzhe/server-gmail-autoauth-mcp auth` (abre browser).
6. **GCal OAuth** — criar projeto em console.cloud.google.com, baixar
   `credentials.json` pra `~/.config/jarvis/gcal-credentials.json`, daí
   rodar `npx -y @cocal/google-calendar-mcp auth`.

### 6. Testes após Enzo colar tokens
```bash
bash scripts/briefing.sh   # dispara briefing on-demand
bash scripts/github-monitor.sh
bash scripts/capture.sh text "Comprar filtro do ar" "tarefa"
```

Se der erro em algum, diagnosticar e corrigir antes de seguir.

### 7. Databases no Notion
Listar as databases que o Enzo precisa criar manualmente no Notion
(ou se você tem token, criar via API). Estão em `SETUP.md` passo 6:
Tasks, Projects, Finanças/Transações, Finanças/Contas a pagar,
Finanças/Metas, Finanças/Categorias, Hábitos, Saúde/Consultas, Team, CRM.

**Se o token Notion já estiver colado, CRIAR as databases automaticamente
via `mcp__notion__*`** em vez de pedir pra ele fazer na mão.

### 8. Shortcuts iOS
Apresentar o resumo de `shortcuts/README.md` (só os 4 essenciais:
Captura rápida, Voz, Video share, Finance) e oferecer: "quer que eu
monte um `.shortcut` exportável pra você importar de um clique?"

---

## Estilo ao responder ao Enzo

- Sem "vou fazer X, Y e Z" longo. Executa e reporta no fim.
- Em cada etapa, só mostra o resultado relevante (não despeja stdout).
- Se travou em algo, 1 frase de diagnóstico + pergunta objetiva.
- Nunca pede aprovação pra comandos seguros (install, test, curl health).
  Só pede se for destrutivo.
