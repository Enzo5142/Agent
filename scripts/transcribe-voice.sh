#!/bin/bash
# Transcreve áudio via whisper.cpp local.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

AUDIO_PATH="${1:?caminho do audio obrigatório}"
WHISPER_MODEL="${JARVIS_WHISPER_MODEL:-small}"

log "Transcrevendo: $AUDIO_PATH"

# Converte pra wav 16khz mono se necessário
WAV="$JARVIS_TMP/$(basename "$AUDIO_PATH" | sed 's/\.[^.]*$//').wav"
ffmpeg -y -loglevel error -i "$AUDIO_PATH" -ar 16000 -ac 1 "$WAV"

# Whisper CLI (pip install openai-whisper) ou whisper.cpp
# Procura primeiro no venv do webhook (onde install.sh instalou)
VENV_WHISPER="$JARVIS_HOME/webhook/.venv/bin/whisper"
if [ -x "$VENV_WHISPER" ]; then
    # Python 3.13 framework.org não vem com certs de SSL; usa o certifi do venv
    VENV_CERTS="$JARVIS_HOME/webhook/.venv/lib/python3.13/site-packages/certifi/cacert.pem"
    [ -f "$VENV_CERTS" ] && export SSL_CERT_FILE="$VENV_CERTS" REQUESTS_CA_BUNDLE="$VENV_CERTS"
    "$VENV_WHISPER" "$WAV" --model "$WHISPER_MODEL" --language Portuguese \
        --output_format txt --output_dir "$JARVIS_TMP"
    TXT="$JARVIS_TMP/$(basename "$WAV" .wav).txt"
elif command -v whisper >/dev/null 2>&1; then
    whisper "$WAV" --model "$WHISPER_MODEL" --language Portuguese \
        --output_format txt --output_dir "$JARVIS_TMP"
    TXT="$JARVIS_TMP/$(basename "$WAV" .wav).txt"
elif command -v whisper-cpp >/dev/null 2>&1; then
    whisper-cpp -m "$HOME/.whisper.cpp/models/ggml-$WHISPER_MODEL.bin" \
        -l pt -otxt "$WAV"
    TXT="${WAV%.wav}.wav.txt"
else
    echo "Whisper não instalado. Ver SETUP.md." >&2
    exit 1
fi

cat "$TXT"
