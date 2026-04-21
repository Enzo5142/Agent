# Shortcuts iOS — Jarvis

Guia prático pros 5 atalhos essenciais. Cada um leva ~5 minutos pra montar no
app **Atalhos** do iPhone.

---

## Configuração base (fazer 1 vez)

Antes de montar qualquer atalho, tenha essas duas informações à mão:

| Variável | Valor |
|---|---|
| `JARVIS_URL` | `http://mac-mini-de-enzo.taila196a5.ts.net:8787` |
| `JARVIS_TOKEN` | Valor do campo `JARVIS_TOKEN=` no seu `~/Agent/.env` |

> **Tailscale**: tanto iPhone quanto Mac precisam estar logados na mesma conta
> Tailscale, estado "Connected". Sem isso, os atalhos não conseguem acessar o
> webhook.

### Dica: guarda o token num Shortcut separado

1. No app Atalhos → **+** (novo atalho) → nome "Jarvis Token"
2. Ação única: **Texto** → cola o valor do token
3. Salva. Os outros atalhos vão chamar `Get Contents of Shortcut "Jarvis Token"` pra obter o token sem repetir o valor.

Mesma coisa pro URL: atalho "Jarvis URL" com o MagicDNS.

---

## 1️⃣ Jarvis Captura Rápida

**O que faz**: você digita uma nota rápida e o Jarvis classifica e salva no
lugar certo (Notion Tasks, Obsidian, etc).

**Passo a passo**:

1. Novo atalho → nome **"Jarvis Captura"** → ícone 📝
2. Adicionar ação **Pedir entrada** (Ask for Input)
   - Tipo: **Texto**
   - Mensagem: *"O que você quer salvar?"*
3. Adicionar ação **Obter conteúdo do URL** (Get Contents of URL)
   - URL: `http://mac-mini-de-enzo.taila196a5.ts.net:8787/capture`
   - Método: **POST**
   - Cabeçalhos: `X-Jarvis-Token` → valor do token
   - Corpo do pedido: **Formulário**
     - Campo `content` → **Entrada fornecida** (da ação 2)
     - Campo `type` → texto fixo `text`
4. Adicionar ação **Mostrar notificação** → **Conteúdo do URL** (resposta)
5. Salvar. Adicionar à tela de início.

---

## 2️⃣ Jarvis Voz

**O que faz**: grava áudio, transcreve via Whisper no Mac, classifica e salva.

**Passo a passo**:

1. Novo atalho → **"Jarvis Voz"** → ícone 🎙️
2. Ação **Gravar áudio** (Record Audio)
   - Iniciar gravação: **Imediatamente**
   - Parar gravação: **Ao tocar**
3. Ação **Obter conteúdo do URL**
   - URL: `{JARVIS_URL}/voice`
   - Método: POST
   - Cabeçalhos: `X-Jarvis-Token` → token
   - Corpo: **Formulário**
     - Campo `audio` → **Arquivo** → Áudio gravado (da ação 2)
4. Ação **Mostrar notificação** → conteúdo da resposta
5. Salvar.

**Bônus**: configure *Atalhos de Acessibilidade → Toque nas costas duplo* pra
disparar esse atalho sem tocar na tela.

---

## 3️⃣ Jarvis Video Share (Share Sheet)

**O que faz**: você compartilha um reel do Instagram / vídeo do YouTube /
TikTok → Jarvis baixa, transcreve e salva resumo no Obsidian.

**Passo a passo**:

1. Novo atalho → **"Jarvis Video"** → ícone 🎬
2. No topo do atalho, toque no **ⓘ** (info) → **Mostrar na Folha de Compart.** (Show in Share Sheet) ✅
   - Tipos aceitos: **URL**
3. Ação **Obter conteúdo do URL**
   - URL: `{JARVIS_URL}/video`
   - Método: POST
   - Cabeçalhos: `X-Jarvis-Token` → token
   - Corpo: Formulário
     - Campo `url` → **Entrada do atalho** (Shortcut Input)
4. Ação **Mostrar notificação**: *"🎬 Jarvis está processando o vídeo. Te aviso quando terminar."*
5. Salvar.

**Uso**: no Instagram, abre o reel → botão de compartilhar → rola a lista →
Jarvis Video.

---

## 4️⃣ Jarvis Finance Quick (Despesa rápida por voz)

**O que faz**: você fala *"Gastei R$ 50 no posto Shell"* → Jarvis classifica e
lança na database Transações do Notion com a regra certa.

**Passo a passo**:

1. Novo atalho → **"Jarvis Finance"** → ícone 💸
2. Ação **Ditar texto** (Dictate Text)
   - Idioma: **Português**
   - Parar após: **Pausar ao falar**
3. Ação **Obter conteúdo do URL**
   - URL: `{JARVIS_URL}/finance`
   - Método: POST
   - Cabeçalhos: `X-Jarvis-Token` → token
   - Corpo: Formulário
     - Campo `text` → **Texto ditado**
4. Ação **Mostrar notificação** com resposta
5. Salvar. Opcional: ativar **"Ei Siri, lançar despesa"**.

---

## 5️⃣ Jarvis Finance Import (Share Sheet, PDF/XLS)

**O que faz**: você recebe fatura do cartão ou extrato por email no celular →
compartilha pelo share sheet → Jarvis processa e insere 50-200 transações no
Notion em ~1 minuto.

**Passo a passo**:

1. Novo atalho → **"Jarvis Finance Import"** → ícone 🏦
2. No **ⓘ** → **Mostrar na Folha de Compart.** ✅
   - Tipos aceitos: **Arquivos** (Files)
3. Ação **Obter conteúdo do URL**
   - URL: `{JARVIS_URL}/finance/upload`
   - Método: POST
   - Cabeçalhos: `X-Jarvis-Token` → token
   - Corpo: **Formulário**
     - Campo `file` → **Arquivo** → Entrada do atalho
4. Ação **Mostrar notificação**: *"🏦 Processando fatura/extrato..."*
5. Ação **Mostrar alerta** → exibe o `stdout` da resposta (resumo do import)
6. Salvar.

**Uso típico**:
- Chega email do Itaú com a fatura PDF → abre anexo → compartilhar → **Jarvis Finance Import**
- Abre app do BTG → exporta extrato XLS → compartilhar → **Jarvis Finance Import**

> ⚠️ **Primeiro uso de cada origem**: vai demorar ~60s porque o parser
> baixa dependências. Próximas execuções: ~20s.

---

## Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Erro 401 | Token errado | Confere `.env` vs Shortcut |
| Timeout | Mac dormiu | Abre o Mac, acorda a tela |
| "Não foi possível conectar" | Tailscale desconectado | Abre o app Tailscale → ambos "Connected" |
| Resposta vazia | Script quebrou | `tail -f /tmp/jarvis-webhook.err.log` no Mac |
| Arquivo Finance Import não importa | Origem não reconhecida | Nome do arquivo ou conteúdo fora do padrão — ver log |

**Teste rápido**: no iPhone, Safari → `http://mac-mini-de-enzo.taila196a5.ts.net:8787/health` deve retornar `{"status":"ok",...}`.

---

## Ordem de montagem sugerida

1. **Finance Import** primeiro (você vai usar já esta semana com extratos de Abril)
2. **Captura Rápida** (uso diário)
3. **Finance Quick** (lançar gastos do dia)
4. **Video Share** (quando compartilhar reels)
5. **Voz** (último, porque back-tap precisa configurar em Acessibilidade)

Total: ~25min de setup.
