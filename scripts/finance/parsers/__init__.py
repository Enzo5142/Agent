"""Parsers por origem. Cada módulo exporta detect() e parse()."""
from __future__ import annotations

from typing import Callable
from pathlib import Path

from . import btg_conta, btg_cartao, itau_conta, itau_cartao

from rules import RawTransaction


PARSERS: list[tuple[str, Callable[[Path], bool], Callable[[Path], list[RawTransaction]]]] = [
    ("BTG Cartão", btg_cartao.detect, btg_cartao.parse),
    ("BTG Conta",  btg_conta.detect,  btg_conta.parse),
    ("Itaú Cartão", itau_cartao.detect, itau_cartao.parse),
    ("Itaú Conta",  itau_conta.detect,  itau_conta.parse),
]


def auto_detect(path: Path) -> tuple[str, Callable[[Path], list[RawTransaction]]] | None:
    """Retorna (origem, parse_func) ou None se nenhum parser reconhece o arquivo."""
    for origem, detect, parse in PARSERS:
        try:
            if detect(path):
                return (origem, parse)
        except Exception:
            continue
    return None
