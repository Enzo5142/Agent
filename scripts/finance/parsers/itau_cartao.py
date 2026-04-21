"""Parser da fatura de cartão Itaú.

Formato: .pdf. Lib: PyMuPDF (fitz) word-level extraction.
Layout: 2 colunas (separar por x<340 esq, x>=340 dir).
3 cartões: Platinum 4345, Platinum 6313, Black 4111 + adicionais 7091, 8412.
Parar em 'próximas faturas'.

MesRef = mês do vencimento extraído do cabeçalho 'Vencimento: DD/MM/YYYY'.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import fitz

from rules import RawTransaction


COL_SPLIT_X = 340.0

VENC_RE = re.compile(r"vencimento[^\d]*(\d{2})/(\d{2})/(\d{4})", re.I)
DATE_RE = re.compile(r"^(\d{2})/(\d{2})$")  # DD/MM (ano implícito da fatura)
VALOR_RE = re.compile(r"^-?\s*\d{1,3}(?:\.\d{3})*,\d{2}\s*$")


def detect(path: Path) -> bool:
    if path.suffix.lower() != ".pdf":
        return False
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        doc.close()
        low = text.lower()
        if ("itaú" in low or "itau" in low) and ("cartão" in low or "fatura" in low):
            if "vencimento" in low:
                return True
    except Exception:
        return False
    return False


def _venc_from_doc(doc) -> date | None:
    for page in doc[:2]:
        text = page.get_text()
        m = VENC_RE.search(text)
        if m:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return None


def _words_by_line(page):
    """Agrupa palavras por linha (mesmo Y aproximado). Ordena por X."""
    words = page.get_text("words")  # (x0, y0, x1, y1, word, block, line, word_no)
    if not words:
        return []
    # Agrupa por (block, line)
    lines = {}
    for w in words:
        key = (w[5], w[6])
        lines.setdefault(key, []).append(w)
    # Ordena cada linha por X e retorna lista de (y_top, [words])
    out = []
    for key, ws in lines.items():
        ws.sort(key=lambda w: w[0])
        y = min(w[1] for w in ws)
        out.append((y, ws))
    out.sort(key=lambda r: r[0])
    return out


def _parse_valor(s: str) -> float | None:
    s = s.strip()
    if not VALOR_RE.match(s):
        return None
    neg = s.startswith("-")
    if neg:
        s = s[1:].strip()
    v_str = s.replace(".", "").replace(",", ".")
    try:
        return -float(v_str) if neg else float(v_str)
    except ValueError:
        return None


def _extract_column(lines, left: bool, venc: date):
    """Extrai transações de uma coluna (left=True → x<340, else x>=340).
    Retorna lista de (date, desc, valor).
    Para em 'próximas faturas' ou similar.
    """
    txs = []
    for y, words in lines:
        col_words = [w for w in words if (w[0] < COL_SPLIT_X if left else w[0] >= COL_SPLIT_X)]
        if not col_words:
            continue
        texts = [w[4] for w in col_words]
        line_text = " ".join(texts).strip()
        if not line_text:
            continue
        # Stop words
        if re.search(r"pr[óo]ximas\s+faturas|total\s+da\s+fatura|demonstrativo", line_text, re.I):
            break

        # Espera: DD/MM <desc> R$valor
        # texts[0] = "DD/MM", último = valor
        m = DATE_RE.match(texts[0])
        if not m:
            continue
        dd, mm = int(m.group(1)), int(m.group(2))
        # Ano: se mês <= venc.month → mesmo ano; senão, ano-1
        ano = venc.year if mm <= venc.month else venc.year - 1
        try:
            tx_date = date(ano, mm, dd)
        except ValueError:
            continue
        # Último texto = valor
        valor = _parse_valor(texts[-1])
        if valor is None:
            continue
        desc = " ".join(texts[1:-1]).strip()
        if not desc:
            continue
        txs.append((tx_date, desc, valor))
    return txs


def parse(path: Path) -> list[RawTransaction]:
    doc = fitz.open(path)
    venc = _venc_from_doc(doc)
    if venc is None:
        doc.close()
        raise RuntimeError(f"Não achei vencimento na fatura Itaú Cartão {path.name}")

    raw = []
    for page in doc:
        lines = _words_by_line(page)
        raw.extend(_extract_column(lines, left=True, venc=venc))
        raw.extend(_extract_column(lines, left=False, venc=venc))
    doc.close()

    txs: list[RawTransaction] = []
    for tx_date, desc, valor in raw:
        if valor == 0:
            continue

        parcela = None
        m = re.search(r"\b(\d{1,2})/(\d{1,2})\b", desc)
        if m:
            parcela = f"{int(m.group(1)):02d}/{int(m.group(2)):02d}"

        tipo_hint = "Despesa" if valor > 0 else "Receita"
        txs.append(RawTransaction(
            data=tx_date,
            descricao=desc,
            valor=abs(valor),
            origem="Itaú Cartão",
            forma_pgto="Crédito",
            parcela=parcela,
            vencimento=venc,
            tipo_hint=tipo_hint,
            observacao=f"venc. {venc.strftime('%d/%m/%Y')}",
            raw_source=path.name,
        ))
    return txs
