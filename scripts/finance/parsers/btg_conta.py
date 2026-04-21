"""Parser do extrato da conta corrente BTG.

Formato: .xls (Excel 97), sem senha. Lib: xlrd.
Colunas (1-indexed / 0-indexed):
  B=1 Data/hora
  C=2 Categoria
  D=3 Transação (tipo)
  G=6 Descrição
  K=10 Valor (negativo = despesa, positivo = receita)

Pular linhas com 'Saldo Diário'.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import xlrd

from rules import RawTransaction


SALDO_PATTERN = re.compile(r"saldo\s+di[aá]rio", re.I)


def detect(path: Path) -> bool:
    if path.suffix.lower() != ".xls":
        return False
    # Assinatura OLE2: D0 CF 11 E0 A1 B1 1A E1
    with open(path, "rb") as f:
        head = f.read(8)
    if head[:4] != b"\xd0\xcf\x11\xe0":
        return False
    # Abre e procura header BTG
    try:
        wb = xlrd.open_workbook(path)
        s = wb.sheet_by_index(0)
        for r in range(min(20, s.nrows)):
            row_text = " ".join(str(s.cell_value(r, c)) for c in range(s.ncols)).lower()
            if "btg" in row_text or "ag 20" in row_text or "211156" in row_text:
                return True
    except Exception:
        return False
    return False


def _parse_date(raw, datemode: int):
    if isinstance(raw, float):
        t = xlrd.xldate_as_tuple(raw, datemode)
        return datetime(*t).date()
    if isinstance(raw, str):
        s = raw.strip()
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S"):
            try:
                return datetime.strptime(s.split()[0], fmt).date()
            except ValueError:
                continue
    return None


def parse(path: Path) -> list[RawTransaction]:
    wb = xlrd.open_workbook(path)
    s = wb.sheet_by_index(0)

    # Acha linha de header (primeira linha que tem "Data" ou "Valor")
    header_row = None
    for r in range(min(30, s.nrows)):
        row_vals = [str(s.cell_value(r, c)).lower() for c in range(s.ncols)]
        if any("data" in v for v in row_vals) and any("valor" in v for v in row_vals):
            header_row = r
            break
    if header_row is None:
        raise RuntimeError(f"Não achei header no BTG Conta {path.name}")

    txs: list[RawTransaction] = []
    for r in range(header_row + 1, s.nrows):
        data_raw = s.cell_value(r, 1)  # B
        cat = str(s.cell_value(r, 2)).strip()  # C
        trans = str(s.cell_value(r, 3)).strip()  # D
        desc = str(s.cell_value(r, 6)).strip()  # G
        val_raw = s.cell_value(r, 10)  # K

        # Pula saldos
        if SALDO_PATTERN.search(desc) or SALDO_PATTERN.search(trans):
            continue
        if not desc and not trans:
            continue

        data = _parse_date(data_raw, wb.datemode)
        if data is None:
            continue

        try:
            valor = float(val_raw)
        except (TypeError, ValueError):
            continue
        if valor == 0:
            continue

        # Forma de pgto pela coluna Transação (ex: "PIX", "TED", "Débito")
        forma = "Pix" if "pix" in trans.lower() else (
            "Transferência" if "ted" in trans.lower() or "transfer" in trans.lower() else (
                "Boleto" if "boleto" in trans.lower() else (
                    "Débito" if "debit" in trans.lower() else "Transferência"
                )
            )
        )

        tipo_hint = "Receita" if valor > 0 else "Despesa"

        # Descrição amigável: usa desc, fallback pro tipo de transação
        full_desc = desc if desc else trans
        txs.append(RawTransaction(
            data=data,
            descricao=full_desc,
            valor=abs(valor),
            origem="BTG Conta",
            forma_pgto=forma,
            tipo_hint=tipo_hint,
            observacao=cat if cat else None,
            raw_source=f"{path.name}:r{r+1}",
        ))
    return txs
