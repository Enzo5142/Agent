# Jarvis — Agente Pessoal do Enzo

Agente pessoal rodando via Claude Code (assinatura Max) no Mac, disparado
por cron (launchd) e por webhooks de Shortcuts do iPhone (via Tailscale).

## Ver também

- `SETUP.md` — passo a passo de instalação (amanhã, ~45 min)
- `CREDENTIALS_NEEDED.md` — lista de tokens/credenciais que você precisa gerar
- `CLAUDE.md` — perfil e regras de comportamento
- `shortcuts/README.md` — atalhos iOS
- `.claude/agents/` — subagents especializados

## Visão rápida

```
iPhone Shortcut ──► Tailscale ──► Mac (webhook FastAPI)
                                        │
                                        ▼
                                  scripts/*.sh
                                        │
                                        ▼
                             Claude Code (Max plan)
                                        │
                       ┌────────────────┼────────────────┐
                       ▼                ▼                ▼
                    Notion         Obsidian          GitHub/Gmail/Calendar
                       │                │                │
                       └────────────────┴────────────────┘
                                        │
                                        ▼
                            iMessage / Obsidian Inbox
```

## O que está incluso

- **11 subagents** (briefing, review, captura, vídeo, código, email,
  finanças, projetos, saúde, whatsapp, meta)
- **14 scripts** (entrypoints para cron e webhook)
- **11 plists launchd** (agenda matinal, review, weekly, monthly, github,
  email, financeiro, whatsapp, saúde, meta, webhook)
- **1 webhook FastAPI** com 10 endpoints pra Shortcuts
- **8 templates** (issue, review, daily, weekly, kickoff, meeting)
- **Guia de Shortcuts iOS** prontos pra recriar em 10 min cada

## Custo

**R$ 0/mês extra.** Tudo roda pela assinatura Max (sem API paga). Apenas
Tailscale (grátis), Whisper local (grátis), yt-dlp (grátis).

## Próximos passos (você)

1. Abrir `CREDENTIALS_NEEDED.md` e gerar os tokens.
2. Rodar `bash install.sh` no Mac.
3. Abrir o iPhone e criar os Shortcuts (`shortcuts/README.md`).
4. Primeiro briefing deve rolar 07:30 do próximo dia útil.
