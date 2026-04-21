"""Webhook Jarvis - recebe eventos dos Shortcuts iOS e dispara scripts.

Roda no Mac em background. iPhone acessa via Tailscale
(ex: http://enzo-mac.tailnet.ts.net:8787).

Autenticação: token simples no header `X-Jarvis-Token`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse

JARVIS_HOME = Path(os.environ.get("JARVIS_HOME", Path.home() / "Agent"))
JARVIS_TOKEN = os.environ.get("JARVIS_TOKEN", "")
SCRIPTS = JARVIS_HOME / "scripts"

app = FastAPI(title="Jarvis Webhook")


def _auth(token: str | None) -> None:
    if not JARVIS_TOKEN:
        raise HTTPException(500, "JARVIS_TOKEN não configurado no servidor")
    if token != JARVIS_TOKEN:
        raise HTTPException(401, "token inválido")


def _run(script: str, *args: str) -> dict:
    path = SCRIPTS / script
    if not path.exists():
        raise HTTPException(404, f"script {script} não existe")
    proc = subprocess.run(
        ["bash", str(path), *args],
        capture_output=True,
        text=True,
        cwd=JARVIS_HOME,
        timeout=600,
    )
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "code": proc.returncode,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "home": str(JARVIS_HOME)}


@app.post("/capture")
async def capture(
    content: str = Form(...),
    type_: str = Form("text", alias="type"),
    hint: str = Form(""),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    result = _run("capture.sh", type_, content, hint)
    return JSONResponse(result)


@app.post("/voice")
async def voice(
    audio: UploadFile = File(...),
    hint: str = Form(""),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    tmp = Path(tempfile.gettempdir()) / f"jarvis-{uuid.uuid4()}-{audio.filename}"
    with tmp.open("wb") as f:
        shutil.copyfileobj(audio.file, f)
    transcribe = _run("transcribe-voice.sh", str(tmp))
    if not transcribe["ok"]:
        return JSONResponse(transcribe, status_code=500)
    text = transcribe["stdout"]
    result = _run("capture.sh", "voice", text, hint)
    return JSONResponse({"transcription": text, **result})


@app.post("/video")
async def video(
    url: str = Form(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("analyze-video.sh", url))


@app.post("/article")
async def article(
    url: str = Form(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("analyze-article.sh", url))


@app.post("/finance")
async def finance(
    text: str = Form(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("finance-add.sh", text))


@app.post("/finance/upload")
async def finance_upload(
    file: UploadFile = File(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    """Recebe PDF/XLS de extrato ou fatura, salva em finance-inbox/,
    dispara finance-import.sh e retorna resumo.
    """
    _auth(x_jarvis_token)
    inbox = JARVIS_HOME / "finance-inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    # Nome sanitizado, prefixado com uuid curto pra evitar colisão
    safe_name = f"{uuid.uuid4().hex[:8]}-{Path(file.filename or 'upload').name}"
    dest = inbox / safe_name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    # Roda import. Se timeout (600s) ou erro, retorna os logs.
    result = _run("finance-import.sh")
    result["uploaded"] = safe_name
    return JSONResponse(result)


@app.post("/issue")
async def issue(
    repo: str = Form(...),
    idea: str = Form(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("issue-create.sh", repo, idea))


@app.post("/review")
async def review(
    repo: str = Form(...),
    pr: str = Form(...),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("pr-review.sh", repo, pr))


@app.post("/briefing")
async def briefing(x_jarvis_token: str | None = Header(None)) -> JSONResponse:
    _auth(x_jarvis_token)
    return JSONResponse(_run("briefing.sh"))


@app.post("/run")
async def run_script(
    script: str = Form(...),
    args: str = Form(""),
    x_jarvis_token: str | None = Header(None),
) -> JSONResponse:
    """Escape hatch genérico. Args separados por '|'."""
    _auth(x_jarvis_token)
    argv = args.split("|") if args else []
    return JSONResponse(_run(script, *argv))


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("JARVIS_HOST", "0.0.0.0")
    port = int(os.environ.get("JARVIS_PORT", "8787"))
    uvicorn.run(app, host=host, port=port)
