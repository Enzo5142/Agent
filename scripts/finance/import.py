"""Orquestrador do importador de extratos.

Uso:
    python scripts/finance/import.py [pasta]

Se pasta omitida, usa ~/Agent/finance-inbox/.
Após processar, move originais pra ~/Agent/finance-archive/<MesRef>/.

Env necessários: NOTION_TOKEN, NOTION_FH_TRANSACOES, etc (ver .notion-dbs.env).
"""
from __future__ import annotations

import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# Garante que /scripts/finance está no path pra resolver imports
sys.path.insert(0, str(Path(__file__).parent))

from parsers import auto_detect
from classifier import classify
from notion_writer import insert_batch


INBOX = Path(os.environ["HOME"]) / "Agent" / "finance-inbox"
ARCHIVE = Path(os.environ["HOME"]) / "Agent" / "finance-archive"


def process_file(path: Path) -> dict:
    detected = auto_detect(path)
    if detected is None:
        return {"path": path, "origem": None, "error": "origem não detectada"}
    origem, parse = detected

    try:
        raw = parse(path)
    except Exception as e:
        return {"path": path, "origem": origem, "error": f"parse: {e}"}

    if not raw:
        return {"path": path, "origem": origem, "error": "zero transações extraídas"}

    classified = [classify(tx) for tx in raw]
    dubios = sum(1 for t in classified if t.dubio)
    mesref_set = {t.mesref for t in classified}
    venc = classified[0].mesref if origem.endswith("Cartão") else None

    return {
        "path": path,
        "origem": origem,
        "raw_count": len(raw),
        "dubios": dubios,
        "mesrefs": sorted(mesref_set),
        "classified": classified,
        "venc": venc,
    }


def main(argv: list[str]) -> int:
    inbox = Path(argv[1]) if len(argv) > 1 else INBOX
    if not inbox.exists():
        inbox.mkdir(parents=True)

    files = sorted([p for p in inbox.iterdir() if p.is_file() and not p.name.startswith(".")])
    if not files:
        print(f"📭 Inbox vazia: {inbox}")
        return 0

    print(f"📥 Escaneando {inbox} ({len(files)} arquivo(s))\n")
    all_classified = []
    results = []

    for idx, path in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] {path.name}")
        res = process_file(path)
        results.append(res)
        if res.get("error"):
            print(f"  ❌ {res['error']}\n")
            continue
        print(f"  origem: {res['origem']}")
        if res["venc"]:
            print(f"  MesRef: {res['venc']}")
        else:
            print(f"  MesRefs: {', '.join(res['mesrefs'])}")
        print(f"  extraídas: {res['raw_count']}")
        auto = res["raw_count"] - res["dubios"]
        print(f"  classificadas automaticamente: {auto}")
        if res["dubios"]:
            print(f"  dúbias (Outros > Não Identificado): {res['dubios']}")
        all_classified.extend(res["classified"])
        print()

    if not all_classified:
        print("⚠️  Nada pra inserir.")
        return 0

    print(f"📤 Inserindo {len(all_classified)} transações no Notion (com dedup)…")
    result = insert_batch(all_classified)
    print(f"  ✅ Inseridas: {result['inserted']}")
    if result['duplicates']:
        print(f"  ♻️  Duplicadas (ignoradas): {result['duplicates']}")
    if result['errors']:
        print(f"  ❌ Erros: {len(result['errors'])}")
        for tx, err in result['errors'][:3]:
            print(f"     {tx.descricao[:60]}: {err[:80]}")

    # Arquiva por MesRef (usa o primeiro MesRef do resultado)
    # Se import teve múltiplos meses, coloca na pasta do mais frequente
    print()
    archive_count = 0
    for res in results:
        if res.get("error"):
            continue
        # pega o MesRef mais comum no arquivo
        mesref_count = defaultdict(int)
        for t in res["classified"]:
            mesref_count[t.mesref] += 1
        target_mesref = max(mesref_count, key=mesref_count.get)
        dest_dir = ARCHIVE / target_mesref
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / res["path"].name
        shutil.move(str(res["path"]), str(dest))
        archive_count += 1
    if archive_count:
        print(f"📦 Arquivados {archive_count} arquivo(s) em {ARCHIVE}/")

    # Resumo final
    total_dubios = sum(1 for t in all_classified if t.dubio)
    if total_dubios:
        print()
        print(f"🔗 {total_dubios} transações dúbias marcadas como 'Outros > Não Identificado'.")
        print("   Abre o Notion e filtra Subcategoria = 'Não Identificado' pra revisar.")

    return 0 if not result['errors'] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
