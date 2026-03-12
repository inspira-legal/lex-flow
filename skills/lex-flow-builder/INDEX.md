# lex-flow-builder - Índice de Documentação

Bem-vindo à skill **lex-flow-builder** para Claude Code!

## Navegação Rápida

### Para Começar

| Documento | Descrição | Público |
|-----------|-----------|---------|
| [QUICK_START.md](QUICK_START.md) | Começar em 3 comandos | Todos |
| [INSTALL.md](INSTALL.md) | Guia visual de instalação | Iniciantes |
| [README.md](README.md) | Documentação completa | Desenvolvedores |

### Instalação

| Método | Arquivo | Sistema |
|--------|---------|---------|
| Script automático | [install.sh](install.sh) | Mac/Linux |
| Script automático | [install.bat](install.bat) | Windows |
| Manual | [INSTALL.md](INSTALL.md) | Todos |

### Referências

| Documento | Conteúdo |
|-----------|----------|
| [reference.md](reference.md) | Catálogo completo de opcodes LexFlow |
| [examples.md](examples.md) | Templates prontos de workflows |
| [SKILL.md](SKILL.md) | Definição técnica da skill |

### Compartilhamento

| Documento | Para que serve |
|-----------|----------------|
| [SHARE_MESSAGE.md](SHARE_MESSAGE.md) | Templates para divulgar no time |

---

## Instalação Rápida

### Mac/Linux
```bash
git clone https://github.com/inspira-legal/lex-flow.git
cp -r lex-flow/skills/lex-flow-builder ~/.claude/skills/
# Reiniciar Claude Code
```

### Windows
```cmd
git clone https://github.com/inspira-legal/lex-flow.git
xcopy /E /I lex-flow\skills\lex-flow-builder %USERPROFILE%\.claude\skills\lex-flow-builder
REM Reiniciar Claude Code
```

### Script Automático
```bash
# Mac/Linux
bash install.sh

# Windows
install.bat
```

---

## Como Usar

No Claude Code, digite:

```
"Quero criar um workflow LexFlow para [seu objetivo]"
```

Ou force a ativação:

```
/skill lex-flow-builder
```

---

## Estrutura da Skill

```
lex-flow-builder/
├── INDEX.md           # Este arquivo (navegação)
├── README.md          # Documentação completa
├── QUICK_START.md     # Referência rápida
├── INSTALL.md         # Guia de instalação visual
├── SHARE_MESSAGE.md   # Templates para compartilhar
├── install.sh         # Script de instalação (Mac/Linux)
├── install.bat        # Script de instalação (Windows)
├── SKILL.md           # Definição da skill (OBRIGATÓRIO)
├── reference.md       # Catálogo de opcodes LexFlow
└── examples.md        # Templates de workflows
```

---

## Fluxo de Trabalho

```
1. Usuário descreve objetivo
   ↓
2. Skill faz discovery (perguntas)
   ↓
3. Cria design visual do fluxo
   ↓
4. Implementa YAML completo
   ↓
5. Valida estrutura e opcodes
   ↓
6. Gera documentação
   ↓
7. Fornece instruções de deploy
```

---

## Palavras-chave de Ativação

A skill é ativada automaticamente quando você menciona:

- workflow
- lex-flow / lexflow
- fluxo
- automação
- n8n
- workflow visual

---

## FAQ Rápido

**P: Onde ficam as skills?**
- Mac/Linux: `~/.claude/skills/`
- Windows: `%USERPROFILE%\.claude\skills\`

**P: Preciso instalar dependências?**
- Não! Só o Claude Code.

**P: Como atualizar?**
```bash
cd ~/.claude/skills/lex-flow-builder/
git pull origin main
# Reiniciar Claude Code
```

**P: Como desinstalar?**
```bash
rm -rf ~/.claude/skills/lex-flow-builder/
```

**P: Funciona offline?**
- A skill funciona, mas Claude Code precisa de internet.

---

## Roadmap de Leitura

### Primeira Vez
1. [QUICK_START.md](QUICK_START.md) - 2 min
2. Instalar (script ou manual)
3. Testar: "Quero criar um workflow"

### Aprofundar
1. [README.md](README.md) - 10 min
2. [reference.md](reference.md) - Consulta
3. [examples.md](examples.md) - Templates

### Compartilhar
1. [SHARE_MESSAGE.md](SHARE_MESSAGE.md)
2. Copiar template apropriado
3. Enviar para o time

---

## Links Úteis

- Repositório LexFlow: https://github.com/inspira-legal/lex-flow
- Docs Claude Code: https://code.claude.com/docs/en/quickstart
- Issues/Suporte: [adicionar link]

---

## Versão

**v1.0.0** (2026-03-09)

---

## Licença

[Adicionar licença do projeto]

---

**Dica:** Começe pelo [QUICK_START.md](QUICK_START.md) se for sua primeira vez!
