"""Parser do extrato da conta corrente Itaú.

Formato: .pdf. Lib: PyMuPDF (fitz).
Layout típico: linhas tipo 'DD/MM/YYYY DESCRIÇÃO' e o valor na próxima linha.
Pular 'SALDO DO DIA'. Ag 5718, Conta 006665-6.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import fitz  # pymupdf

from rules import RawTransaction


DATE_LINE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})\s+(.+)$")
# Valor Itaú: "1.234,56" ou "-1.234,56" ou "1.234,56 D" (débito)
VALOR_RE = re.compile(r"^-?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s*([DC])?\s*$")


def detect(path: Path) -> bool:
    if path.suffix.lower() != ".pdf":
        return False
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        doc.close()
        low = text.lower()
        # "Itaú" + "extrato" e NÃO "cartão" ou "fatura"
        if "itaú" in low or "itau" in low:
            if "agência" in low or "conta corrente" in low or "5718" in low:
                if "cartão" not in low and "fatura" not in low:
                    return True
    except Exception:
        return False
    return False


def _parse_valor(s: str) -> tuple[float, str] | None:
    """Retorna (valor, tipo_hint) onde tipo_hint é 'Receita' ou 'Despesa'."""
    s = s.strip()
    neg = s.startswith("-")
    if neg:
        s = s[1:].strip()
    m = VALOR_RE.match(s)
    if not m:
        return None
    v_str = m.group(1).replace(".", "").replace(",", ".")
    try:
        v = float(v_str)
    except ValueError:
        return None
    suffix = m.group(2)
    # 'D' = débito = despesa; 'C' = crédito = receita
    if suffix == "D" or neg:
        return (v, "Despesa")
    if suffix == "C":
        return (v, "Receita")
    # Sem sufixo — precisa inferir pelo contexto. Default receita se positivo.
    return (v, "Receita")


def parse(path: Path) -> list[RawTransaction]:
    doc = fitz.open(path)
    full_text = "\n".join(page.get_text() for page in doc)
    doc.close()

    lines = [ln.strip() for ln in full_text.split("\n") if ln.strip()]

    txs: list[RawTransaction] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Pula saldos
        if "SALDO DO DIA" in line.upper() or "SALDO ANTERIOR" in line.upper():
            i += 1
            continue

        m = DATE_LINE_RE.match(line)
        if not m:
            i += 1
            continue

        data = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        desc = m.group(4).strip()

        # Valor pode estar na MESMA linha (raro) ou na próxima
        valor_tuple = None
        # Primeiro tenta extrair no fim da descrição
        tail_match = re.search(r"(-?\s*\d{1,3}(?:\.\d{3})*,\d{2}\s*[DC]?)\s*$", desc)
        if tail_match:
            valor_tuple = _parse_valor(tail_match.group(1))
            if valor_tuple:
                desc = desc[:tail_match.start()].strip()
        # Se não achou, olha próxima linha
        if valor_tuple is None and i + 1 < len(lines):
            nxt = lines[i + 1]
            valor_tuple = _parse_valor(nxt)
            if valor_tuple is not None:
                i += 1  # consumiu a próxima linha

        if valor_tuple is None:
            i += 1
            continue

        valor, tipo_hint = valor_tuple
        if valor == 0:
            i += 1
            continue

        forma = "Pix" if "pix" in desc.lower() else (
            "Transferência" if "ted " in desc.lower() or "tef " in desc.lower() else (
                "Boleto" if "boleto" in desc.lower() else "Débito"
            )
        )
        txs.append(RawTransaction(
            data=data,
            descricao=desc,
            valor=valor,
            origem="Itaú Conta",
            forma_pgto=forma,
            tipo_hint=tipo_hint,
            raw_source=f"{path.name}:l{i+1}",
        ))
        i += 1

    return txs
