"""Regras de classificação fina — MesRef, Tipo, Ana Laura, Transferências.

Espelha a lógica da aba 'Instruções Claude' do Excel do Enzo.
Fonte da verdade: página 'Instruções Jarvis' no Notion.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


ENZO_NAME_PATTERNS = [
    re.compile(r"enzo\s+barros\s+pruano", re.I),
    re.compile(r"208\.0001\.enzo\s+b\s+p", re.I),
]
ANA_LAURA_PATTERNS = [re.compile(r"ana\s+laura\s+estevam\s+pimenta", re.I)]
ANA_FLAVIA_PATTERNS = [re.compile(r"ana\s+fl[áa]via\s+estevam\s+pimenta", re.I)]

# Descrições que indicam pagamento de fatura (= transferência interna)
FATURA_PATTERNS = [
    re.compile(r"faturaitau", re.I),
    re.compile(r"itau\s+mc", re.I),
    re.compile(r"fatura\s+.*btg", re.I),
    re.compile(r"pgto\s+fatura", re.I),
]

# Origens que são cartão de crédito (usam MesRef = vencimento, não data)
CARTAO_ORIGENS = {"BTG Cartão", "Itaú Cartão"}
EXTRATO_ORIGENS = {"BTG Conta", "Itaú Conta", "Mercado Pago"}

# Subcategorias que contam como Renda Real (4 do Excel)
RENDA_REAL_SUBS = {"Salário", "Freelance/Extra", "Rendimentos", "Reembolso"}

# Macros EXCLUÍDAS de Gastos Reais
GASTOS_REAIS_EXCLUI = {"Transferências", "Investimentos"}


@dataclass
class RawTransaction:
    """Transação crua extraída pelo parser, antes de classificar."""
    data: date                   # data da transação (compra ou movimento)
    descricao: str
    valor: float                 # positivo
    origem: str                  # nome exato: BTG Conta, BTG Cartão, etc
    forma_pgto: str              # Débito, Crédito, Pix, Transferência, Boleto, Dinheiro
    parcela: Optional[str] = None  # "3/12" ou None
    vencimento: Optional[date] = None  # só pra cartão; None pra extrato
    tipo_hint: Optional[str] = None  # "Receita" ou "Despesa" se o extrato já deu pista
    observacao: Optional[str] = None  # info do cartão, etc
    raw_source: Optional[str] = None  # filename ou linha original pra debug


@dataclass
class ClassifiedTransaction:
    """Transação depois de classificada — pronta pra inserir no Notion."""
    data: date
    descricao: str
    valor: float
    tipo: str                    # Receita / Despesa / Transferência
    categoria_macro: str
    categoria_sub: str
    forma_pgto: str
    origem: str
    parcela: Optional[str]
    fixa_variavel: str           # Fixa / Variável
    mesref: str                  # "2026-04"
    observacao: Optional[str]
    dubio: bool = False          # True se caiu em "Outros > Não Identificado"


def calc_mesref(tx: RawTransaction) -> str:
    """Regra crítica do Excel:
    - extrato → mês da data da transação
    - cartão → mês do vencimento da fatura (NÃO da compra!)
    """
    if tx.origem in CARTAO_ORIGENS:
        if tx.vencimento is None:
            raise ValueError(f"Cartão sem vencimento: {tx!r}")
        return f"{tx.vencimento.year:04d}-{tx.vencimento.month:02d}"
    return f"{tx.data.year:04d}-{tx.data.month:02d}"


def detect_tipo(tx: RawTransaction) -> str:
    """Retorna 'Receita' | 'Despesa' | 'Transferência' baseado na descrição.
    Usa tipo_hint do parser se disponível, mas pode sobrescrever por regras fortes.
    """
    desc = tx.descricao.lower()

    # Regras fortes que sobrescrevem tudo:
    # Pagamento de fatura = Transferência (sai da conta pra "pagar" o cartão)
    if any(p.search(desc) for p in FATURA_PATTERNS):
        return "Transferência"

    # Pix/TED entre contas próprias do Enzo = Transferência
    if any(p.search(desc) for p in ENZO_NAME_PATTERNS):
        return "Transferência"

    # Usa o hint do parser (extrato geralmente marca débito/crédito = despesa/receita)
    if tx.tipo_hint in ("Receita", "Despesa"):
        return tx.tipo_hint

    # Default: cartão = despesa (raramente tem estorno); extrato sem hint = despesa
    return "Despesa"


def _is_ana_laura(desc: str) -> bool:
    return any(p.search(desc) for p in ANA_LAURA_PATTERNS)


def _is_ana_flavia(desc: str) -> bool:
    return any(p.search(desc) for p in ANA_FLAVIA_PATTERNS)


def _is_pix_recebido(desc: str) -> bool:
    return bool(re.search(r"pix\s+recebido", desc, re.I))


def _is_pix_enviado(desc: str) -> bool:
    return bool(re.search(r"pix\s+(enviado|por)", desc, re.I))


def apply_ana_rules(tx: RawTransaction, tipo: str) -> Optional[tuple[str, str]]:
    """Se a transação envolve Ana Laura ou Ana Flávia, retorna (macro, sub).
    Caso contrário retorna None e deixa o classifier seguir o fluxo normal.
    """
    desc = tx.descricao

    # Pix recebido de qualquer Ana → Salário (renda nova)
    if _is_pix_recebido(desc) and (_is_ana_laura(desc) or _is_ana_flavia(desc)):
        return ("Receita", "Salário")

    # Pix enviado pra Ana Laura (esposa) → Outros > Pix p/ Ana (gasto casal)
    if _is_pix_enviado(desc) and _is_ana_laura(desc):
        return ("Outros", "Pix p/ Ana (gasto casal)")

    # Pix enviado pra Ana Flávia (irmã, NÃO esposa) → fluxo normal
    # (classifier decide pela palavra-chave / contexto)

    return None


def detect_fixa_variavel(macro: str, sub: str) -> str:
    """Regra do Excel: Fixa = aluguel, condomínio, internet, assinaturas, plano.
    Variável = resto.
    """
    fixa_macros = {"Moradia", "Assinaturas & Serviços"}
    fixa_subs = {
        "Aluguel", "Condomínio", "IPTU", "Energia Elétrica", "Água", "Gás",
        "Internet", "Plano de Saúde", "Mensalidade Escolar",
        "Streaming (Netflix, Spotify, etc.)", "Telefone/Celular",
        "Armazenamento/Cloud", "Outros Serviços",
    }
    if macro in fixa_macros or sub in fixa_subs:
        return "Fixa"
    return "Variável"


def parse_parcela(desc: str) -> Optional[str]:
    """Extrai 'N/M' da descrição se existir (ex: 'AIRBNB HMMMX 04/05' → '04/05')."""
    m = re.search(r"\b(\d{1,2})\s*/\s*(\d{1,2})\b", desc)
    if m:
        n, tot = int(m.group(1)), int(m.group(2))
        if 1 <= n <= tot <= 99:
            return f"{n:02d}/{tot:02d}"
    return None


def is_renda_real(tipo: str, sub: str) -> bool:
    return tipo == "Receita" and sub in RENDA_REAL_SUBS


def is_gasto_real(tipo: str, macro: str) -> bool:
    return tipo == "Despesa" and macro not in GASTOS_REAIS_EXCLUI


def hash_key(tx: RawTransaction | ClassifiedTransaction) -> tuple:
    """Chave de dedup: mesma combinação = mesma transação.
    Evita re-importar arquivo e duplicar linhas.
    """
    data = tx.data
    return (
        data.isoformat(),
        round(tx.valor, 2),
        tx.descricao[:50].lower().strip(),
        tx.origem,
    )
