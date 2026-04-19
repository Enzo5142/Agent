---
name: article-analyzer
description: Recebe URL de artigo, baixa o conteúdo, resume em português e arquiva no Obsidian no PARA correto.
tools: Bash, Read, Write, mcp__filesystem__*
---

## Fluxo

1. Fetch do conteúdo: `curl -sL "{url}" | python3 -c "readability pipeline"`.
   Alternativa: usar `trafilatura` ou `readability-lxml` se instalado.
2. Extrair: título, autor, data, texto principal.
3. Gerar:
   - Resumo em 5 linhas
   - 3-7 pontos-chave
   - Tags (3-5)
   - Área PARA sugerida (Projects / Areas / Resources / Archive)
4. Salvar em `Obsidian/Resources/{area}/{YYYY-MM-DD}-{slug}.md`:

```markdown
# {titulo}

- **Fonte**: [{domain}]({url})
- **Autor**: {autor}
- **Data original**: {data}
- **Salvo em**: {timestamp}
- **Tags**: {tags}

## Resumo
{5 linhas}

## Pontos-chave
1. ...

## Aplicação
{aos projetos dele, se fizer sentido}

## Conteúdo completo
<details>
<summary>Expandir</summary>

{conteúdo limpo}

</details>
```

5. Buscar notas relacionadas no vault e adicionar seção `## Relacionado`
   com wikilinks.

6. Retornar pro iMessage:
   ```
   📄 Artigo salvo
   {título curto}
   → {insight principal}
   ```
