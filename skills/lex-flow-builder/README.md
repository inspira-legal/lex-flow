# LexFlow Workflow Builder - Claude Code Skill

Skill para criação guiada de workflows LexFlow no Claude Code, desde discovery até deploy.

## O que faz esta skill?

Guia desenvolvedores na criação completa de workflows LexFlow:
- **Discovery**: Coleta requisitos através de perguntas estruturadas
- **Design**: Cria planos visuais do fluxo
- **Implementação**: Gera código YAML válido
- **Validação**: Verifica estrutura e opcodes
- **Documentação**: Cria docs explicativas
- **Deploy**: Fornece instruções de execução

## Instalação

### Pré-requisitos
- Claude Code instalado ([como instalar](https://code.claude.com/docs/en/quickstart))
- Git (para clonar o repositório)

### Passo 1: Clonar a skill

```bash
# Clonar o repositório LexFlow
git clone https://github.com/inspira-legal/lex-flow.git

# Copiar a skill para o diretório do Claude Code
cp -r lex-flow/skills/lex-flow-builder ~/.claude/skills/

# OU criar um link simbólico (recomendado para desenvolvedores):
# ln -s $(pwd)/lex-flow/skills/lex-flow-builder ~/.claude/skills/lex-flow-builder
```

### Passo 2: Verificar estrutura

A estrutura deve ficar assim:

```
~/.claude/skills/lex-flow-builder/
├── README.md          # Este arquivo
├── SKILL.md           # Definição da skill (obrigatório)
├── reference.md       # Catálogo de opcodes
└── examples.md        # Templates de workflows
```

**IMPORTANTE:** O arquivo `SKILL.md` deve ter o frontmatter YAML no início:

```yaml
---
name: lex-flow-builder
description: Guia desenvolvedores na criacao de workflows LexFlow...
---
```

### Passo 3: Verificar instalação

```bash
# Reiniciar Claude Code (se estiver rodando)
# Ctrl+C para parar, depois iniciar novamente

# Ou simplesmente abrir uma nova sessão
claude-code
```

No chat do Claude Code, digite:

```
/skill lex-flow-builder
```

Se a skill estiver instalada corretamente, o Claude responderá iniciando o processo de criação de workflow.

## Como Usar

### Ativação Automática

A skill é ativada automaticamente quando você menciona:
- "criar workflow"
- "lex-flow" / "lexflow"
- "fluxo"
- "automação"
- "n8n"
- "workflow visual"

**Exemplo:**
```
"Quero criar um workflow LexFlow para processar PDFs"
```

### Ativação Manual

```bash
# No chat do Claude Code:
/skill lex-flow-builder
```

### Exemplo Prático

```
User: "Preciso automatizar o envio de emails quando um arquivo CSV for processado"

Claude (usando a skill):
1. Fará perguntas sobre inputs, outputs, condições
2. Criará um design visual do fluxo
3. Implementará o YAML
4. Validará a estrutura
5. Gerará documentação
6. Fornecerá instruções de deploy
```

## Recursos da Skill

### 1. Discovery Guiado
- Perguntas estruturadas sobre requisitos
- Identificação de inputs/outputs
- Mapeamento de integrações

### 2. Design Visual
- Diagrama de fluxo em ASCII
- Identificação de opcodes necessários
- Planejamento de variáveis

### 3. Implementação YAML
- Código completo e válido
- Seguindo padrões LexFlow
- Com comentários explicativos

### 4. Validação
- Checklist de qualidade
- Verificação de opcodes
- Testes de estrutura

### 5. Documentação
- README do workflow
- Instruções de uso
- Exemplos de execução

### 6. Deploy
- CLI, programático ou web editor
- Comandos prontos
- Troubleshooting

## Arquivos de Referência

- **`reference.md`**: Catálogo completo de opcodes disponíveis
- **`examples.md`**: Templates prontos de workflows comuns
- **`SKILL.md`**: Documentação completa da skill

## Troubleshooting

### Skill não aparece
```bash
# Verificar se está no diretório correto
ls ~/.claude/skills/lex-flow-builder/SKILL.md

# Se não existir, reinstalar
cd ~/.claude/skills/
git clone [url-do-repo]
```

### Skill não é ativada
- Reinicie o Claude Code
- Tente ativação manual: `/skill lex-flow-builder`
- Verifique se o SKILL.md tem o frontmatter correto

### Erros de sintaxe
- Certifique-se que o SKILL.md está completo
- Verifique se não há caracteres especiais no nome

## Contribuindo

Encontrou um bug ou quer melhorar a skill?

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/melhoria`
3. Commit suas mudanças: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/melhoria`
5. Abra um Pull Request

## Licença

[Adicionar licença do projeto]

## Links

- Repositório LexFlow: https://github.com/inspira-legal/lex-flow
- Documentação Claude Code: https://code.claude.com/docs/en/quickstart
- Issues/Suporte: [adicionar link]

## Changelog

### v1.0.0 (2026-03-09)
- Release inicial
- Discovery completo
- Design visual
- Implementação YAML
- Validação e documentação
- Instruções de deploy
