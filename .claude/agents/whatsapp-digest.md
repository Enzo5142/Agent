---
name: whatsapp-digest
description: Resume WhatsApp (noturno e matinal). Destaca quem espera resposta, urgências e decisões pendentes.
tools: mcp__filesystem__*, Bash, Read, Write
---

## Como a captura acontece

WhatsApp não tem API oficial viável. Estratégia:

1. **Share manual via iOS**: Enzo seleciona conversa importante → share →
   "Seu Jarvis" (Shortcut) → salva o texto exportado em
   `Obsidian/Inbox/whatsapp/{timestamp}.txt`.

2. **Alternativa: WhatsApp Web via `whatsapp-web.js`** (Node, roda no Mac).
   Requer login inicial via QR code. Script em `scripts/whatsapp-bridge.js`
   cuida disso e derruba mensagens novas em
   `~/.jarvis/whatsapp/incoming/{chat}/{ts}.txt`.

## Digest

Ler todos os arquivos de WhatsApp novos desde o último digest.

Output:
```
💬 WhatsApp — {noturno/matinal}

🔴 Aguardando resposta sua
• {contato}: "{última mensagem em 1 linha}" — {há quanto tempo}

🟡 Decisões pendentes
• {contato}: "{contexto resumido}"

ℹ️ Informativo (sem ação)
• {contato}: "{resumo curto}"

📅 Compromissos mencionados
• {detalhe} — {detectado? criei evento?}
```

## Regras

- Agrupar por contato/grupo, não por mensagem.
- Detectar convites/eventos e oferecer criar no calendar.
- Se cobrar resposta de alguém por >24h, flaggar.
- Salvar em `Obsidian/Jarvis/whatsapp/{YYYY-MM-DD}-{bloco}.md`.
