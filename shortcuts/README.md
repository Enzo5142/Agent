# Shortcuts iOS — Jarvis

Cada atalho abaixo manda POST pro webhook rodando no seu Mac
(`https://<mac-tailscale>:8787`). Todos usam o header
`X-Jarvis-Token: <seu token>` (definido em `~/Agent/.env`).

## Variáveis base (crie um atalho "Jarvis Config" com Text → clipboard)

- `JARVIS_URL` = `https://enzo-mac.tailnet.ts.net:8787` (substitua pelo seu)
- `JARVIS_TOKEN` = valor que está em `.env`

## 1. Jarvis Captura Rápida

**Gatilho**: ícone na home/widget.
**Ações**:
1. **Ask for Input** (tipo: Text) — prompt "O que vc quer salvar?"
2. **Get Contents of URL**
   - URL: `{JARVIS_URL}/capture`
   - Method: POST
   - Headers: `X-Jarvis-Token: {token}`
   - Request Body: Form
     - `content`: provided input
     - `type`: `text`
3. **Show Result** — conteúdo retornado (texto).

## 2. Jarvis Captura de Voz

**Gatilho**: botão de ação (back tap duplo / botão da Dynamic Island /
widget).
**Ações**:
1. **Record Audio** (Start immediately: ✅, Stop: on tap)
2. **Get Contents of URL**
   - URL: `{JARVIS_URL}/voice`
   - Method: POST
   - Headers: `X-Jarvis-Token: {token}`
   - Request Body: Form
     - `audio`: File = Recorded Audio
3. **Show Notification** com resultado.

## 3. Analisar Vídeo (Share Sheet)

**Tipo**: Share sheet, aceita URL.
**Ações**:
1. **Get Contents of URL**
   - URL: `{JARVIS_URL}/video`
   - Method: POST
   - Headers: `X-Jarvis-Token: {token}`
   - Request Body: Form
     - `url`: Shortcut Input
2. **Show Notification**: "🎬 Vídeo sendo processado. Te aviso ao fim."

## 4. Salvar Artigo (Share Sheet)

Igual ao 3, endpoint `/article`.

## 5. Lançar Despesa (por voz)

**Gatilho**: Siri "Ei Siri, gastei [X] no [Y]".
**Ações**:
1. **Dictate Text** (Português)
2. **Get Contents of URL**
   - URL: `{JARVIS_URL}/finance`
   - Method: POST
   - Body: `text` = dictated text

## 6. Criar Issue GitHub

**Ações**:
1. **Choose from List**: escolhe repo (preenche manualmente primeiro uso)
2. **Dictate Text** → ideia crua
3. **Get Contents of URL** → `/issue` com `repo` + `idea`

## 7. Briefing On-Demand

**Ações**: apenas POST pra `/briefing`. Útil quando quiser um extra fora do
horário agendado.

## 8. Analisar Foto (OCR)

**Gatilho**: Share sheet, aceita imagem.
**Ações**:
1. **Get Text from Image** (iOS nativo)
2. **Get Contents of URL** → `/capture`
   - `content`: texto extraído
   - `type`: `text`
   - `hint`: `image-ocr`

---

## Importação rápida

Cada atalho acima pode ser criado manualmente (10-15min) OU você pode:

1. Criar um dos atalhos no iPhone
2. Duplicar e ajustar apenas o endpoint/campo pros outros

**Dica**: crie um widget "Jarvis" com 4 atalhos (texto, voz, briefing,
despesa).

## Tailscale

Pra o iPhone falar com o Mac em qualquer rede:
1. Instale Tailscale no Mac + iPhone (mesma conta).
2. Anote o nome MagicDNS do Mac (ex: `enzo-mac.tailnet.ts.net`).
3. Use esse hostname como `{JARVIS_URL}`.

## Troubleshooting

- Erro 401 → token errado, conferir `.env` vs Shortcut.
- Timeout → Mac dormiu ou webhook caiu. Ver `tail /tmp/jarvis-webhook.*.log`.
- Resposta vazia → rodar o script no terminal pra ver erro (`bash
  scripts/capture.sh text "teste"`).
