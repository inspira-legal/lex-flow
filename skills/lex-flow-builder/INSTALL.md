# Guia Rápido de Instalação - lex-flow-builder

## Para Usuários Novos (Instalando do Zero)

### 1. Verificar se tem Claude Code instalado

```bash
# Testar se o Claude Code está instalado
claude-code --version
```

Se não estiver instalado: https://code.claude.com/docs/en/quickstart

---

### 2. Instalar a skill

```bash
# OPÇÃO A: Clonar repo e copiar skill
git clone https://github.com/inspira-legal/lex-flow.git
cp -r lex-flow/skills/lex-flow-builder ~/.claude/skills/

# OPÇÃO B: Link simbólico (recomendado para desenvolvedores)
git clone https://github.com/inspira-legal/lex-flow.git
ln -s $(pwd)/lex-flow/skills/lex-flow-builder ~/.claude/skills/lex-flow-builder

# OPÇÃO C: Download manual
# Baixar apenas a pasta skills/lex-flow-builder/ do repo
# e colocar em ~/.claude/skills/lex-flow-builder/
```

---

### 3. Verificar estrutura

```bash
# Ver se os arquivos estão no lugar certo
ls ~/.claude/skills/lex-flow-builder/

# Deve mostrar:
# SKILL.md
# reference.md
# examples.md
# README.md
```

---

### 4. Reiniciar Claude Code

```bash
# Se o Claude Code estiver rodando, fechar e abrir novamente
# Ou simplesmente abrir uma nova sessão
```

---

### 5. Testar a skill

Abra o Claude Code e digite:

```
Quero criar um workflow LexFlow
```

Ou force a ativação:

```
/skill lex-flow-builder
```

---

## Resumo Visual

```
┌─────────────────────────────────────────────────┐
│  1. Ter Claude Code instalado                   │
│     claude-code --version                       │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  2. Clonar skill para ~/.claude/skills/         │
│     cd ~/.claude/skills/                        │
│     git clone [repo] lex-flow-builder           │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  3. Verificar estrutura                         │
│     ls ~/.claude/skills/lex-flow-builder/       │
│     → SKILL.md ✓                                │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  4. Reiniciar Claude Code                       │
│     (fechar e abrir novamente)                  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  5. Testar                                      │
│     "Quero criar um workflow LexFlow"           │
└─────────────────────────────────────────────────┘
```

---

## Troubleshooting Comum

### "Skill não encontrada"

```bash
# Verificar se está no lugar certo
ls -la ~/.claude/skills/lex-flow-builder/SKILL.md

# Se não aparecer, reinstalar
```

### "Claude não responde ao comando"

1. Reinicie o Claude Code completamente
2. Tente ativação manual: `/skill lex-flow-builder`
3. Verifique logs de erro (se houver)

### "Diretório .claude não existe"

```bash
# Criar estrutura manualmente
mkdir -p ~/.claude/skills/
cd ~/.claude/skills/
# Depois clonar a skill
```

---

## FAQ

**P: Preciso instalar Python ou outras dependências?**
R: Não! A skill roda apenas no Claude Code. Python só é necessário para executar os workflows gerados.

**P: A skill funciona em Windows?**
R: Sim! Use o caminho `%USERPROFILE%\.claude\skills\` no Windows.

**P: Posso ter várias versões da skill?**
R: Não recomendado. Mantenha apenas uma versão em `~/.claude/skills/lex-flow-builder/`

**P: Como atualizar a skill?**
R:
```bash
cd ~/.claude/skills/lex-flow-builder/
git pull origin main
# Reiniciar Claude Code
```

**P: A skill funciona offline?**
R: A skill em si funciona, mas o Claude Code precisa de internet para o modelo de IA.

---

## Próximos Passos

Depois de instalar, veja:
- `README.md` - Documentação completa
- `reference.md` - Catálogo de opcodes LexFlow
- `examples.md` - Workflows prontos para usar

## Suporte

- Issues: [adicionar link do GitHub]
- Docs: https://github.com/inspira-legal/lex-flow
- Claude Code: https://code.claude.com/docs/en/quickstart
