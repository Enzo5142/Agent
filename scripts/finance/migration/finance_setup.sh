#!/bin/bash
# Cria a estrutura correta do Finance Hub no Notion, baseado no Excel do Enzo.
# 1. Página Finance Hub em Pessoal
# 2. DBs: Categorias, Contas, Transações, Orçamento
# 3. Popula Categorias (65 linhas) e Contas (5 linhas)
set -euo pipefail

: "${NOTION_TOKEN:?NOTION_TOKEN não setado}"
PESSOAL="20fcbec3-cd89-4be7-8f43-edd3f55c669d"
VERSION="2022-06-28"  # API estável pra criação
OUT="$HOME/Agent/.notion-dbs.env"

# ---- helper: HTTP ----
api() {
    local method="$1" path="$2" body_file="$3"
    curl -sX "$method" "https://api.notion.com/v1$path" \
        -H "Authorization: Bearer $NOTION_TOKEN" \
        -H "Notion-Version: $VERSION" \
        -H "Content-Type: application/json" \
        ${body_file:+--data-binary @$body_file}
}

# ---- criar página Finance Hub ----
TMP=$(mktemp)
jq -n --arg parent "$PESSOAL" '{
    parent: {type: "page_id", page_id: $parent},
    icon: {type: "emoji", emoji: "💰"},
    properties: {
        title: {
            title: [{type: "text", text: {content: "Finance Hub"}}]
        }
    }
}' > "$TMP"
FH_RESP=$(api POST "/pages" "$TMP")
FH_ID=$(echo "$FH_RESP" | jq -r '.id')
[ "$FH_ID" = "null" ] && { echo "ERRO ao criar Finance Hub:"; echo "$FH_RESP"; exit 1; }
echo "OK  Finance Hub page: $FH_ID"

# ---- DB Categorias ----
jq -n --arg parent "$FH_ID" '{
    parent: {type: "page_id", page_id: $parent},
    icon: {type: "emoji", emoji: "🏷️"},
    title: [{type: "text", text: {content: "Categorias"}}],
    properties: {
        "Nome": {title: {}},
        "Macro": {select: {options: [
            {name: "Moradia", color: "blue"},
            {name: "Alimentação", color: "orange"},
            {name: "Transporte", color: "yellow"},
            {name: "Saúde", color: "pink"},
            {name: "Educação", color: "purple"},
            {name: "Lazer & Entretenimento", color: "red"},
            {name: "Vestuário", color: "brown"},
            {name: "Assinaturas & Serviços", color: "gray"},
            {name: "Pets", color: "green"},
            {name: "Impostos & Taxas", color: "default"},
            {name: "Investimentos", color: "green"},
            {name: "Transferências", color: "gray"},
            {name: "Receita", color: "green"},
            {name: "Outros", color: "brown"},
            {name: "Cuidados Pessoais", color: "pink"},
            {name: "Presentes & Ocasionais", color: "red"}
        ]}},
        "Subcategoria": {rich_text: {}},
        "Ícone": {rich_text: {}},
        "Tipo": {select: {options: [
            {name: "Receita", color: "green"},
            {name: "Despesa", color: "red"},
            {name: "Transferência", color: "gray"}
        ]}}
    }
}' > "$TMP"
CAT_RESP=$(api POST "/databases" "$TMP")
CAT_ID=$(echo "$CAT_RESP" | jq -r '.id')
[ "$CAT_ID" = "null" ] && { echo "ERRO Categorias:"; echo "$CAT_RESP"; exit 1; }
echo "OK  Categorias DB: $CAT_ID"

# ---- DB Contas ----
jq -n --arg parent "$FH_ID" '{
    parent: {type: "page_id", page_id: $parent},
    icon: {type: "emoji", emoji: "🏦"},
    title: [{type: "text", text: {content: "Contas"}}],
    properties: {
        "Nome": {title: {}},
        "Tipo": {select: {options: [
            {name: "Conta Corrente", color: "blue"},
            {name: "Cartão de Crédito", color: "purple"},
            {name: "Carteira Digital", color: "yellow"}
        ]}},
        "Banco": {select: {options: [
            {name: "BTG", color: "orange"},
            {name: "Itaú", color: "red"},
            {name: "Mercado Pago", color: "blue"}
        ]}},
        "Ativa": {checkbox: {}}
    }
}' > "$TMP"
CTA_RESP=$(api POST "/databases" "$TMP")
CTA_ID=$(echo "$CTA_RESP" | jq -r '.id')
[ "$CTA_ID" = "null" ] && { echo "ERRO Contas:"; echo "$CTA_RESP"; exit 1; }
echo "OK  Contas DB: $CTA_ID"

# ---- DB Transações (relation → Categorias, Contas) ----
jq -n --arg parent "$FH_ID" --arg cat "$CAT_ID" --arg cta "$CTA_ID" '{
    parent: {type: "page_id", page_id: $parent},
    icon: {type: "emoji", emoji: "💳"},
    title: [{type: "text", text: {content: "Transações"}}],
    properties: {
        "Descrição": {title: {}},
        "Data": {date: {}},
        "Categoria": {relation: {database_id: $cat, single_property: {}}},
        "Tipo": {select: {options: [
            {name: "Receita", color: "green"},
            {name: "Despesa", color: "red"},
            {name: "Transferência", color: "gray"}
        ]}},
        "Valor": {number: {format: "real"}},
        "Forma Pgto": {select: {options: [
            {name: "Débito", color: "blue"},
            {name: "Crédito", color: "purple"},
            {name: "Pix", color: "green"},
            {name: "Transferência", color: "gray"},
            {name: "Boleto", color: "orange"},
            {name: "Dinheiro", color: "brown"}
        ]}},
        "Conta": {relation: {database_id: $cta, single_property: {}}},
        "Parcela": {rich_text: {}},
        "Fixa/Variável": {select: {options: [
            {name: "Fixa", color: "blue"},
            {name: "Variável", color: "yellow"}
        ]}},
        "MesRef": {rich_text: {}},
        "Observações": {rich_text: {}}
    }
}' > "$TMP"
TX_RESP=$(api POST "/databases" "$TMP")
TX_ID=$(echo "$TX_RESP" | jq -r '.id')
[ "$TX_ID" = "null" ] && { echo "ERRO Transações:"; echo "$TX_RESP"; exit 1; }
echo "OK  Transações DB: $TX_ID"

# ---- DB Orçamento (categoria macro x mês) ----
# Usa 12 colunas number + coluna total formula
jq -n --arg parent "$FH_ID" '{
    parent: {type: "page_id", page_id: $parent},
    icon: {type: "emoji", emoji: "🎯"},
    title: [{type: "text", text: {content: "Orçamento"}}],
    properties: {
        "Categoria": {title: {}},
        "Jan": {number: {format: "real"}},
        "Fev": {number: {format: "real"}},
        "Mar": {number: {format: "real"}},
        "Abr": {number: {format: "real"}},
        "Mai": {number: {format: "real"}},
        "Jun": {number: {format: "real"}},
        "Jul": {number: {format: "real"}},
        "Ago": {number: {format: "real"}},
        "Set": {number: {format: "real"}},
        "Out": {number: {format: "real"}},
        "Nov": {number: {format: "real"}},
        "Dez": {number: {format: "real"}},
        "Total": {formula: {expression: "prop(\"Jan\") + prop(\"Fev\") + prop(\"Mar\") + prop(\"Abr\") + prop(\"Mai\") + prop(\"Jun\") + prop(\"Jul\") + prop(\"Ago\") + prop(\"Set\") + prop(\"Out\") + prop(\"Nov\") + prop(\"Dez\")"}}
    }
}' > "$TMP"
OR_RESP=$(api POST "/databases" "$TMP")
OR_ID=$(echo "$OR_RESP" | jq -r '.id')
[ "$OR_ID" = "null" ] && { echo "ERRO Orçamento:"; echo "$OR_RESP"; exit 1; }
echo "OK  Orçamento DB: $OR_ID"

rm -f "$TMP"

# ---- salva IDs ----
cat > "$OUT" <<EOF
# Gerado por finance_setup.sh + jarvis_create_dbs.sh
# IDs das databases do Notion.

# Jarvis (antigo) — mantém
NOTION_DB_PROJECTS=347e3a12-dada-81a9-b0de-d0559be9d697
NOTION_DB_TASKS=347e3a12-dada-81d7-bd0a-dd72c61894af
NOTION_DB_HABITOS=347e3a12-dada-81a9-a6f5-ca436141526e
NOTION_DB_CONSULTAS=347e3a12-dada-816e-bb9b-c0571e3ba578
NOTION_DB_TEAM=347e3a12-dada-8198-bfe7-f6f2cacd2945
NOTION_DB_CRM=347e3a12-dada-81f5-b1c3-f9268c693826

# Finance Hub (novo, estrutura do Excel do Enzo)
NOTION_FH_PAGE=$FH_ID
NOTION_FH_CATEGORIAS=$CAT_ID
NOTION_FH_CONTAS=$CTA_ID
NOTION_FH_TRANSACOES=$TX_ID
NOTION_FH_ORCAMENTO=$OR_ID
EOF
echo
echo "✅ Estrutura criada. IDs em $OUT"
