Você recebeu uma captura do Enzo via Shortcut iOS.

Input:
- `type`: text | voice | url | image
- `content`: conteúdo principal (texto, caminho do áudio, URL, caminho da imagem)
- `hint` (opcional): categoria sugerida

Fluxo:
1. Se type=voice, transcreva com whisper primeiro.
2. Se type=image, rode OCR (tesseract) primeiro.
3. Se type=url, detecte se é vídeo (instagram.com/reel, youtube.com,
   tiktok.com) → rode subagent `video-analyzer`.
4. Se url de artigo → rode `article-analyzer`.
5. Senão → rode `note-organizer` com o conteúdo.

Retorne resposta curta (máx 3 linhas) pro iMessage:
```
📌 {tipo}
→ {destino}
{resumo 1 linha}
```
