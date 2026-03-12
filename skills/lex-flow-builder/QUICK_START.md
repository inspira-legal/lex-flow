# Quick Start - lex-flow-builder

## Instalação em 3 comandos

```bash
# 1. Clonar o repositório LexFlow
git clone https://github.com/inspira-legal/lex-flow.git

# 2. Copiar a skill
cp -r lex-flow/skills/lex-flow-builder ~/.claude/skills/

# 3. Reiniciar Claude Code
```

## Usar em 1 frase

No Claude Code, digite:

```
"Quero criar um workflow LexFlow para [seu objetivo]"
```

Pronto!

---

## Comandos Úteis

```bash
# Ver se está instalada
ls ~/.claude/skills/lex-flow-builder/SKILL.md

# Atualizar
cd ~/.claude/skills/lex-flow-builder && git pull

# Forçar ativação
# No chat do Claude Code:
/skill lex-flow-builder
```

---

## Palavras que ativam automaticamente

- workflow
- lex-flow / lexflow
- fluxo
- automação
- n8n

---

## Exemplo

```
User: "Preciso processar CSVs e enviar emails"

Claude: [Ativa a skill automaticamente]
- Faz perguntas de discovery
- Cria design visual
- Implementa YAML
- Gera documentação
- Fornece instruções de deploy
```

---

## Links

- Docs completos: `README.md`
- Instalação detalhada: `INSTALL.md`
- Opcodes LexFlow: `reference.md`
- Templates: `examples.md`

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Skill não encontrada | `ls ~/.claude/skills/lex-flow-builder/` |
| Não ativa | Reinicie Claude Code |
| Erro de sintaxe | Verifique `SKILL.md` existe |

---

**Dúvidas?** Leia o `README.md` completo ou abra um issue no repo.
