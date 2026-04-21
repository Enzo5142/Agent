"""Batch insert no Notion com dedup por hash(data+valor+desc50+origem).

Antes de inserir, baixa todas as transações dos MesRefs afetados pra set em memória.
Check de dedup é O(1). Custo: 1 query paginada por MesRef.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from rules import ClassifiedTransaction, hash_key


NOTION_VERSION = "2022-06-28"
MAPS_FILE = Path(os.environ["HOME"]) / "Agent" / ".notion-finance-maps.json"


def _headers():
    return {
        "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _load_maps() -> dict:
    if not MAPS_FILE.exists():
        raise RuntimeError(
            f"Cadê {MAPS_FILE}? Rode finance_populate.py pra gerar."
        )
    return json.loads(MAPS_FILE.read_text())


def fetch_existing_hashes(mesrefs: set[str]) -> set[tuple]:
    """Retorna set de hash_keys das transações já no Notion pros MesRefs dados."""
    db = os.environ["NOTION_FH_TRANSACOES"]
    seen: set[tuple] = set()
    for mesref in mesrefs:
        cursor = None
        while True:
            body = {
                "page_size": 100,
                "filter": {"property": "MesRef", "rich_text": {"equals": mesref}},
            }
            if cursor:
                body["start_cursor"] = cursor
            r = requests.post(
                f"https://api.notion.com/v1/databases/{db}/query",
                headers=_headers(), json=body, timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            for p in data["results"]:
                props = p["properties"]
                # Reconstrói hash key
                desc = "".join(t["plain_text"] for t in props["Descrição"]["title"])
                valor = props["Valor"]["number"] or 0
                data_str = props["Data"]["date"]["start"] if props["Data"]["date"] else ""
                conta_rel = props["Conta"]["relation"]
                # Mapeia conta_id de volta pro nome — fazemos isso em batch antes
                origem_id = conta_rel[0]["id"] if conta_rel else None
                seen.add((data_str, round(valor, 2), desc[:50].lower().strip(), origem_id))
            cursor = data.get("next_cursor")
            if not data.get("has_more"):
                break
    return seen


def _build_body(tx: ClassifiedTransaction, cat_id: str, cta_id: str, db_id: str) -> dict:
    props = {
        "Descrição": {"title": [{"text": {"content": tx.descricao[:2000]}}]},
        "Data": {"date": {"start": tx.data.isoformat()}},
        "Categoria": {"relation": [{"id": cat_id}]},
        "Tipo": {"select": {"name": tx.tipo}},
        "Valor": {"number": float(tx.valor)},
        "Forma Pgto": {"select": {"name": tx.forma_pgto}},
        "Conta": {"relation": [{"id": cta_id}]},
        "Fixa/Variável": {"select": {"name": tx.fixa_variavel}},
        "MesRef": {"rich_text": [{"text": {"content": tx.mesref}}]},
    }
    if tx.parcela:
        props["Parcela"] = {"rich_text": [{"text": {"content": tx.parcela}}]}
    if tx.observacao:
        props["Observações"] = {"rich_text": [{"text": {"content": tx.observacao[:2000]}}]}
    return {"parent": {"database_id": db_id}, "properties": props}


def _post_single(body: dict, max_retries: int = 5) -> tuple[bool, str | None]:
    url = "https://api.notion.com/v1/pages"
    for attempt in range(max_retries):
        r = requests.post(url, headers=_headers(), json=body, timeout=30)
        if r.status_code == 200:
            return (True, None)
        if r.status_code == 429:
            time.sleep(1 + attempt)
            continue
        if r.status_code >= 500:
            time.sleep(0.5 + attempt * 0.5)
            continue
        return (False, r.text[:400])
    return (False, "max retries")


def insert_batch(
    classified: list[ClassifiedTransaction],
    *,
    skip_existing: bool = True,
    max_workers: int = 4,
) -> dict:
    """Insere lista de transações. Retorna dict com contagens.
    {inserted: N, duplicates: N, errors: [(tx, msg), ...]}
    """
    maps = _load_maps()
    cat_map = maps["categorias"]  # "Macro > Sub" → id
    cta_map = maps["contas"]       # "BTG Conta" → id
    db_id = os.environ["NOTION_FH_TRANSACOES"]

    # Valida mapeamento
    missing = set()
    for tx in classified:
        key = f"{tx.categoria_macro} > {tx.categoria_sub}"
        if key not in cat_map:
            missing.add(key)
        if tx.origem not in cta_map:
            missing.add(f"[conta] {tx.origem}")
    if missing:
        raise RuntimeError(f"Mapeamento ausente: {missing}. Popular primeiro.")

    # Dedup: busca existentes
    duplicates = 0
    existing_reduced: set[tuple] = set()
    if skip_existing and classified:
        mesrefs = {tx.mesref for tx in classified}
        existing = fetch_existing_hashes(mesrefs)
        # Reduz existing ao mesmo formato do hash_key gerado abaixo
        # Como existing usa conta_id e hash_key(tx) usa origem (nome),
        # converto aqui: mapeia cta_id → origem, e rebuilda
        id_to_name = {v: k for k, v in cta_map.items()}
        for (data_str, valor, desc50, origem_id) in existing:
            origem_name = id_to_name.get(origem_id, "")
            existing_reduced.add((data_str, valor, desc50, origem_name))

    to_insert: list[ClassifiedTransaction] = []
    for tx in classified:
        h = hash_key(tx)
        if skip_existing and h in existing_reduced:
            duplicates += 1
            continue
        to_insert.append(tx)

    # Insere em paralelo
    inserted = 0
    errors: list[tuple] = []
    def worker(tx):
        key = f"{tx.categoria_macro} > {tx.categoria_sub}"
        body = _build_body(tx, cat_map[key], cta_map[tx.origem], db_id)
        ok, err = _post_single(body)
        return (tx, ok, err)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker, tx) for tx in to_insert]
        for fut in as_completed(futures):
            tx, ok, err = fut.result()
            if ok:
                inserted += 1
            else:
                errors.append((tx, err))

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors,
        "total_input": len(classified),
    }
