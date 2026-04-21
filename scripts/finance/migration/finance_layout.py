#!/usr/bin/env python3
"""Monta o layout da página Finance Hub:
- Callout topo
- Sub-página Dashboard (placeholder com heading + link pras DBs)
- Sub-página Instruções Jarvis (cópia das regras)
- Blocos de navegação
"""
import os
import requests

TOKEN = os.environ["NOTION_TOKEN"]
FH = os.environ["NOTION_FH_PAGE"]
CAT = os.environ["NOTION_FH_CATEGORIAS"]
CTA = os.environ["NOTION_FH_CONTAS"]
TX  = os.environ["NOTION_FH_TRANSACOES"]
OR  = os.environ["NOTION_FH_ORCAMENTO"]
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}


def post(path, body):
    r = requests.post(f"https://api.notion.com/v1{path}", headers=H, json=body, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"{path}: {r.text[:400]}")
    return r.json()


def patch(path, body):
    r = requests.patch(f"https://api.notion.com/v1{path}", headers=H, json=body, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"{path}: {r.text[:400]}")
    return r.json()


def text(content, **ann):
    return {"type": "text", "text": {"content": content}, "annotations": ann}


# ---------------- 1. Sub-página Dashboard ----------------
dash = post("/pages", {
    "parent": {"type": "page_id", "page_id": FH},
    "icon": {"type": "emoji", "emoji": "📊"},
    "properties": {"title": {"title": [{"type": "text", "text": {"content": "Dashboard"}}]}},
})
DASH = dash["id"]
print(f"OK  Dashboard page: {DASH}")

# ---------------- 2. Sub-página Instruções Jarvis ----------------
instr = post("/pages", {
    "parent": {"type": "page_id", "page_id": FH},
    "icon": {"type": "emoji", "emoji": "📖"},
    "properties": {"title": {"title": [{"type": "text", "text": {"content": "Instruções Jarvis"}}]}},
})
INSTR = instr["id"]
print(f"OK  Instruções page: {INSTR}")

# ---------------- 3. Blocos do Finance Hub ----------------
fh_blocks = [
    # Welcome callout
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Central financeira do Enzo & Ana. "}, "annotations": {"bold": True}},
                      {"type": "text", "text": {"content": "Espelha o Excel (Contas Enzo-Ana.xlsx) com as mesmas regras: MesRef de cartão = mês do vencimento, Transferências/Investimentos excluídos do cálculo de gastos reais."}}],
        "icon": {"type": "emoji", "emoji": "💰"},
        "color": "blue_background",
    }},
    {"object": "block", "type": "divider", "divider": {}},

    # Dashboard
    {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "📊 Dashboard"}}],
    }},
    {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "KPIs do mês + gastos por categoria, origem e evolução mensal. Abre em tela cheia."}}],
    }},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "page_id", "page_id": DASH}},

    # Transações
    {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "💳 Transações"}}],
    }},
    {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Todas as transações do ano. Filtre por MesRef no canto superior direito pra ver só o mês corrente."}}],
    }},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": TX}},

    # Orçamento
    {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "🎯 Orçamento"}}],
    }},
    {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Preencha quanto pretende gastar em cada categoria por mês. A coluna Total soma os 12 meses."}}],
    }},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": OR}},

    # Referências
    {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "📂 Referências"}}],
    }},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": CAT}},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": CTA}},

    # Divider + Instruções
    {"object": "block", "type": "divider", "divider": {}},
    {"object": "block", "type": "heading_2", "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "📖 Como usar & regras"}}],
    }},
    {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Regras de classificação, parsing de extratos e edge cases (Transferências, Ana, MesRef de cartão)."}}],
    }},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "page_id", "page_id": INSTR}},
]
patch(f"/blocks/{FH}/children", {"children": fh_blocks})
print(f"OK  Finance Hub layout pronto ({len(fh_blocks)} blocos)")

# ---------------- 4. Conteúdo do Dashboard (placeholder) ----------------
dash_blocks = [
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Dashboard de views filtradas. Crie views da database Transações aqui (gastos por categoria do mês, top 5 gastos, evolução mensal etc). Por limitação da API, views precisam ser criadas manualmente."}}],
        "icon": {"type": "emoji", "emoji": "💡"},
        "color": "yellow_background",
    }},
    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "KPIs do Mês"}}]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": "Renda real = SUM(Valor) WHERE Tipo=Receita AND MesRef=@mês AND Categoria.Macro ≠ Transferências, Investimentos"}},
    ]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": "Gastos reais = SUM(Valor) WHERE Tipo=Despesa AND MesRef=@mês AND Categoria.Macro ≠ Transferências, Investimentos"}},
    ]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
        {"type": "text", "text": {"content": "Saldo = Renda − Gastos. % Poupado = Saldo / Renda."}},
    ]}},
    {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": "Transações do mês corrente"}}]}},
    {"object": "block", "type": "link_to_page", "link_to_page": {"type": "database_id", "database_id": TX}},
]
patch(f"/blocks/{DASH}/children", {"children": dash_blocks})
print(f"OK  Dashboard placeholder ({len(dash_blocks)} blocos)")

# ---------------- 5. Conteúdo de Instruções Jarvis ----------------
instr_blocks = [
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Regras espelhadas da aba 'Instruções Claude' do Excel. Fonte da verdade para o Jarvis processar extratos."}}],
        "icon": {"type": "emoji", "emoji": "📖"},
        "color": "blue_background",
    }},
    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "1. Contas e origens"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "BTG Conta — .xls (Excel 97). Parser: xlrd. Colunas B=data/hora, C=categoria, D=transação, G=descrição, K=valor. Pular 'Saldo Diário'."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "BTG Cartão — .xlsx criptografado. Senha = CPF 50784024898. Agile Encryption AES-128-CBC SHA1. Sheet 'Titular'. Compras em B(data), C(desc), E(valor), F(tipo), H(cartão)."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Itaú Conta — .pdf. PyMuPDF. Padrão DD/MM/YYYY DESCRIÇÃO na linha, valor na linha seguinte. Pular 'SALDO DO DIA'. Ag 5718, Conta 006665-6."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Itaú Cartão — .pdf. 3 cartões: Platinum 4345, Platinum 6313, Black 4111 (+ adicionais 7091, 8412). Layout 2 colunas: word-level, separar x<340 (esq) e x>=340 (dir). Parar em 'próximas faturas'."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Mercado Pago — formato ainda não definido. Aguarda primeiro extrato."}}]}},

    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "2. Regra crítica: MesRef"}}]}},
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "EXTRATO (BTG Conta, Itaú Conta, Mercado Pago):"}, "annotations": {"bold": True}},
                      {"type": "text", "text": {"content": " MesRef = mês da DATA DA TRANSAÇÃO."}}],
        "icon": {"type": "emoji", "emoji": "⚠️"},
        "color": "yellow_background",
    }},
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "CARTÃO (BTG Cartão, Itaú Cartão):"}, "annotations": {"bold": True}},
                      {"type": "text", "text": {"content": " MesRef = mês da FATURA (vencimento), NÃO a data da compra. Ex: compra 15/07/2025 parcela 6/12 com fatura vencendo Jan/2026 → MesRef = 2026-01."}}],
        "icon": {"type": "emoji", "emoji": "⚠️"},
        "color": "red_background",
    }},

    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "3. Transferências e dupla contagem"}}]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Enzo tem 3 bancos (BTG, Itaú, Mercado Pago). Pix/TED entre eles aparece como despesa em um e receita no outro. Para não inflar gastos e renda:"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Categorizar como 'Transferências' todo pagamento de fatura, Pix/TED entre contas próprias, e TED com descrição '208.0001.ENZO B P'."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Categorizar como 'Investimentos > Aporte em Investimentos' todo aporte."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Dashboard exclui Transferências e Investimentos do cálculo de Renda Real e Gastos Reais."}}]}},
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Pix PARA Ana Laura / Ana Flávia ≠ transferência!"}, "annotations": {"bold": True}},
                      {"type": "text", "text": {"content": " É gasto real do casal. Classificar como 'Outros > Pix p/ Ana (gasto casal)'."}}],
        "icon": {"type": "emoji", "emoji": "👩"},
        "color": "pink_background",
    }},
    {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Pix DE Ana Laura / Ana Flávia = RENDA."}, "annotations": {"bold": True}},
                      {"type": "text", "text": {"content": " Classificar como 'Receita > Salário' (não 'Pix recebido'). É salário da esposa, renda do casal."}}],
        "icon": {"type": "emoji", "emoji": "💵"},
        "color": "green_background",
    }},

    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "4. Classificação por palavra-chave"}}]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Lógica replicada do Excel. Match case-insensitive no texto da descrição."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Supermercado: minuto pa, pao de acucar, carrefour, casotti, sao jorge, oba hortifruti, piraja, quaresmeira, rede triunfo"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Restaurante: pizzaria, sushi, yosugiru, nonna, panini, telmo, horse, outback, steakhouse, zinin, jeronimo, giardino, mc donald, boali, torino"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Delivery: rappi, ifood, moustache beams, foodmylife, zé delivery, gjr açaí"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Uber/99: uber, 99pop, cabify, urentcar"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Combustível: posto, shell, ralpha, ig recarga, tag, conectcar, shell box"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Moradia > Aluguel (Fixa): quinto andar, quintoandar"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Moradia > Energia (Fixa): enel, tupinambaener"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Assinaturas (Fixa): netflix, spotify, hbo max, youtube, apple, vivo, claro, google one, shopify, melimais, smartfin"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Pets: petz, petlove, estilo4pet, espetto carioca, caopelli"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Saúde > Farmácia: raia, drogasil, drogaria, granado"}}]}},

    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "5. Processo mensal"}}]}},
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Enzo envia novos extratos/faturas via iPhone (Shortcut) ou pasta. Jarvis:"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Identifica origem pelo conteúdo/filename."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Aplica parser específico da seção 1."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Classifica por palavra-chave (seção 4). Fallback: 'Outros > Não Identificado'."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Calcula MesRef correto (seção 2)."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Dedup por hash (data + valor + desc_first50 + origem)."}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Insere em lote na database Transações. Reporta total + transações dúbias pra revisão."}}]}},

    {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "6. Dados do usuário"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Enzo Barros Pruano — CPF 507.840.248-98"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "BTG: Ag 20, Conta 211156-5"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Itaú: Ag 5718, Conta 006665-6"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Salário: ~R$ 10.300/mês via 'Otm Assessor De Investimentos Ltda'"}}]}},
    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Esposa: Ana Laura Estevam Pimenta / Ana Flávia Estevam Pimenta (o Excel usa ambos nomes)"}}]}},
]

# Notion limita a 100 blocks por request. Envio em batches.
CHUNK = 80
for i in range(0, len(instr_blocks), CHUNK):
    patch(f"/blocks/{INSTR}/children", {"children": instr_blocks[i:i+CHUNK]})
print(f"OK  Instruções page ({len(instr_blocks)} blocos)")

print(f"\n✅ Layout completo.")
print(f"Finance Hub:  https://notion.so/{FH.replace('-','')}")
print(f"Dashboard:    https://notion.so/{DASH.replace('-','')}")
print(f"Instruções:   https://notion.so/{INSTR.replace('-','')}")
