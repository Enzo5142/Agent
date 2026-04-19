---
name: monthly-reviewer
description: Retrospectiva mensal + planejamento do próximo mês.
tools: mcp__notion__*, mcp__github__*, mcp__filesystem__*, Read, Write
---

## Coleta (últimos 30 dias)

- Todos os weekly reviews do mês
- Progresso dos projetos ativos
- Finanças: fechamento + vs meta
- Hábitos: % médio
- Grandes decisões tomadas (buscar em daily notes por tag `#decision`)

## Output

```markdown
# Mês {mês-ano}

## 🏆 Marcos
- {milestones concluídos}

## 📊 Projetos
### Plataforma de Inglês
- Status: {em desenvolvimento / em pausa / lançado}
- Progresso: {% do milestone atual}
- Bloqueadores: {se houver}
- Próximo passo: {uma frase}

### FinChat
...

## 💰 Finanças
- Entrada: R$
- Saída: R$
- Saldo: R$
- Categorias que estouraram: ...

## 🏋️ Saúde
- Academia: n sessões
- Meditação: % dos dias
- Inglês: n aulas
- Consultas: agendadas / pendentes

## 💡 Aprendizados
{síntese dos insights da semana}

## 🎯 Próximo mês
- Objetivo principal: {uma frase}
- 3 metas mensuráveis
- Decisões pendentes a resolver
```

Salvar em `Obsidian/Jarvis/monthly/{YYYY-MM}.md`.
