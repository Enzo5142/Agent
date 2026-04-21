"""Classifica transações por palavra-chave. Fonte: aba 'Instruções Claude' do Excel.

Match case-insensitive, palavra contida na descrição.
Fallback: Outros > Não Identificado (marcado como dúbio).
"""
from __future__ import annotations

import re
from typing import Optional

from rules import (
    ClassifiedTransaction, RawTransaction,
    apply_ana_rules, calc_mesref, detect_fixa_variavel, detect_tipo,
)


# (macro, sub) → lista de substrings que batem. Case-insensitive.
# Ordem importa: primeira que bater vence. Regras mais específicas em cima.
KEYWORD_RULES: list[tuple[str, str, list[str]]] = [
    # ======= MORADIA =======
    ("Moradia", "Aluguel", ["quinto andar", "quintoandar"]),
    ("Moradia", "Energia Elétrica", ["enel", "tupinambaener"]),
    ("Moradia", "Manutenção/Reforma", ["leroy merlin", "n5 movelaria", "karsten"]),

    # ======= ALIMENTAÇÃO =======
    ("Alimentação", "Supermercado", [
        "minuto pa", "pao de acucar", "carrefour", "casotti", "sao jorge",
        "oba hortifruti", "piraja", "quaresmeira", "rede triunfo",
    ]),
    ("Alimentação", "Delivery/iFood", [
        "rappi", "ifood", "moustache beams", "foodmylife", "zé delivery",
        "gjr açaí",
    ]),
    ("Alimentação", "Restaurante", [
        "pizzaria", "sushi", "yosugiru", "nonna", "panini", "telmo", "horse",
        "outback", "steakhouse", "zinin", "jeronimo", "giardino", "mc donald",
        "quinta do conde", "boali", "torino", "pastel ville", "rexpar",
        "50 606 293 leonard",
    ]),

    # ======= TRANSPORTE =======
    ("Transporte", "Uber/99", ["uber", "99pop", "cabify", "urentcar"]),
    ("Transporte", "Combustível", [
        "posto", "shell", "ralpha", "ig recarga", "tag", "conectcar",
        "tagitau", "iupp tag", "shell box",
    ]),
    ("Transporte", "Estacionamento", [
        "west towers", "bsp park", "evspark", "mvb park", "multiplan",
        "datacity", "dca estacionamento",
    ]),
    ("Transporte", "Manutenção Veículo", [
        "borracharia", "alpha center", "frbaterias", "maternidade star",
    ]),

    # ======= SAÚDE =======
    ("Saúde", "Farmácia", ["raia", "drogasil", "drogaria", "granado"]),
    ("Saúde", "Academia", ["totalpass"]),

    # ======= VESTUÁRIO =======
    ("Vestuário", "Roupas", [
        "renner", "calvin", "fila", "youcom", "sephora", "arezzo", "dudalina",
        "jogê", "danki", "brooksfield", "europrestigi", "hope", "vivara",
        "carter", "openbox", "oqvestir", "fratex", "lojas americanas",
        "by mac", "rayban", "magazinelu",
    ]),

    # ======= ASSINATURAS =======
    ("Assinaturas & Serviços", "Streaming (Netflix, Spotify, etc.)", [
        "netflix", "spotify", "hbo max", "youtube", "apple.com/bill", "hbomax",
    ]),
    ("Assinaturas & Serviços", "Telefone/Celular", ["vivo", "claro", "tim "]),
    ("Assinaturas & Serviços", "Armazenamento/Cloud", ["google one", "icloud"]),
    ("Assinaturas & Serviços", "Outros Serviços", [
        "shopify", "melimais", "smartfin", "lavoisier",
    ]),

    # ======= PETS =======
    ("Pets", "Petshop/Banho", [
        "petz", "petlove", "estilo4pet", "espetto carioca", "caopelli",
    ]),
]


def _match(desc_lower: str, keywords: list[str]) -> bool:
    return any(k.lower() in desc_lower for k in keywords)


def _classify_category(desc: str, tipo: str) -> tuple[str, str, bool]:
    """Retorna (macro, sub, dubio). dubio=True se caiu no fallback."""
    desc_lower = desc.lower()

    # Tipo Transferência já veio da regra forte
    if tipo == "Transferência":
        # Pagamento de fatura específico
        if re.search(r"faturaitau|itau\s+mc|fatura.*btg|pgto\s+fatura", desc_lower):
            return ("Transferências", "Transferência entre contas", False)
        # Pix/TED entre contas próprias
        return ("Transferências", "Pix enviado", False)

    # Receita sem regra Ana — provavelmente salário OTM ou pix recebido genérico
    if tipo == "Receita":
        if re.search(r"otm\s+assessor", desc_lower):
            return ("Receita", "Salário", False)
        if re.search(r"rendimento|aplicacao|aplicação|resgate", desc_lower):
            return ("Receita", "Rendimentos", False)
        if _match(desc_lower, ["pix recebido"]):
            return ("Receita", "Pix recebido", False)
        # Fallback receita
        return ("Receita", "Outras Receitas", True)

    # Despesa — itera regras
    for macro, sub, keywords in KEYWORD_RULES:
        if _match(desc_lower, keywords):
            return (macro, sub, False)

    # Fallback despesa
    return ("Outros", "Não Identificado", True)


def classify(tx: RawTransaction) -> ClassifiedTransaction:
    """Recebe uma transação crua, retorna classificada."""
    tipo = detect_tipo(tx)

    # Tenta regra Ana antes do classifier genérico
    ana = apply_ana_rules(tx, tipo)
    if ana:
        macro, sub = ana
        dubio = False
    else:
        macro, sub, dubio = _classify_category(tx.descricao, tipo)

    # Para cartão, vira crédito; pra extrato usa forma_pgto dada pelo parser
    forma = tx.forma_pgto or ("Crédito" if tx.origem.endswith("Cartão") else "Débito")

    return ClassifiedTransaction(
        data=tx.data,
        descricao=tx.descricao,
        valor=tx.valor,
        tipo=tipo,
        categoria_macro=macro,
        categoria_sub=sub,
        forma_pgto=forma,
        origem=tx.origem,
        parcela=tx.parcela,
        fixa_variavel=detect_fixa_variavel(macro, sub),
        mesref=calc_mesref(tx),
        observacao=tx.observacao,
        dubio=dubio,
    )
