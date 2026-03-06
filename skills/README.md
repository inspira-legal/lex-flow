# LexFlow Skills

Skills são assistentes especializados do Claude Code para auxiliar no desenvolvimento de workflows LexFlow. Cada skill fornece expertise em uma área específica, guiando desde a descoberta de requisitos até o deploy.

## 📋 Skills Disponíveis

### lex-flow-builder

**Descrição**: Especialista em criar workflows LexFlow baseado em contexto do usuário. Guia desde discovery de requisitos, design de fluxo, implementação YAML, até validação, documentação e deploy.

**Quando usar**: Ao mencionar "criar workflow", "lex-flow", "fluxo", "automação", "workflow visual" ou pedir para construir processos automatizados.

**Arquivos**:
- `lex-flow-builder.md` - Processo completo de criação de workflows (Discovery → Design → Implementação → Validação → Documentação → Deploy)
- `reference.md` - Catálogo de opcodes e estruturas de workflow
- `examples.md` - 10 templates prontos de workflows comuns

**Tech Stack**:
- Backend: Python (lexflow-core, lexflow-cli)
- Frontend: TypeScript (lexflow-web)
- Formato: YAML/JSON
- Arquitetura: Node-based graph com opcodes

## 🚀 Como Usar

### No Claude Code

1. **Instalação**: Copie a pasta da skill desejada para `~/.claude/skills/`

   ```bash
   cp -r skills/lex-flow-builder ~/.claude/skills/
   ```

2. **Ativação**: A skill é ativada automaticamente quando você menciona os termos-chave no Claude Code

3. **Fluxo de Trabalho**:
   - Descreva sua necessidade
   - A skill fará discovery via perguntas
   - Criará um plano estruturado
   - Apresentará design para aprovação
   - Implementará o YAML
   - Validará e revisará
   - Gerará documentação
   - Entregará com instruções de deploy

### Exemplo de Uso

```
User: "Preciso criar um workflow que busca issues do Jira e gera um relatório"

Claude Code (com skill lex-flow-builder):
- Fará perguntas sobre autenticação, filtros, formato de saída
- Criará um plano com TodoWrite
- Implementará o workflow YAML
- Testará localmente
- Gerará documentação completa
- Fornecerá instruções de deploy
```

## 📚 Estrutura de uma Skill

Cada skill deve conter:

```
skill-name/
├── skill-name.md     # Arquivo principal com processo e instruções
├── reference.md      # Documentação de referência técnica
└── examples.md       # Templates e exemplos prontos
```

### Arquivo Principal (`skill-name.md`)

Deve incluir:
- Frontmatter com metadados (name, description, allowed-tools)
- Processo passo a passo
- Boas práticas
- Quando usar/não usar a skill
- Workflow recomendado

### Arquivo de Referência (`reference.md`)

Contém:
- Documentação técnica detalhada
- APIs, opcodes, sintaxes
- Padrões e estruturas
- Checklist de validação

### Arquivo de Exemplos (`examples.md`)

Inclui:
- Templates prontos para uso
- Casos de uso comuns
- Padrões de composição
- Boas práticas de nomenclatura

## 🛠️ Criando Novas Skills

Para criar uma nova skill para LexFlow:

1. Crie uma pasta em `skills/` com o nome da skill
2. Crie os 3 arquivos principais (main, reference, examples)
3. Defina o frontmatter no arquivo principal:
   ```yaml
   ---
   name: skill-name
   description: Descrição clara da skill e quando usar. (user)
   allowed-tools: [Read, Write, Edit, Bash, ...]
   ---
   ```
4. Documente o processo completo
5. Adicione exemplos práticos
6. Teste a skill em cenários reais

## 🤝 Contribuindo

Para adicionar ou melhorar skills:

1. Crie um branch: `git checkout -b feature/add-your-skill`
2. Adicione a skill em `skills/your-skill/`
3. Atualize este README com a nova skill
4. Crie uma PR com descrição detalhada
5. Inclua exemplos de uso na PR

## 📖 Documentação Adicional

- [LexFlow Core](../lexflow-core/README.md)
- [Grammar Reference](../docs/GRAMMAR_REFERENCE.md)
- [Opcode Reference](../docs/OPCODE_REFERENCE.md)
- [Examples](../examples/)

## 📝 Licença

As skills seguem a mesma licença do projeto LexFlow.
