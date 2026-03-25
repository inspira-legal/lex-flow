# 🔧 Guia de Manutenção - lex-flow-builder Skill

Este documento explica como manter a skill **lex-flow-builder** sempre atualizada com os opcodes mais recentes do LexFlow.

---

## 📋 Problema

O LexFlow adiciona novos opcodes frequentemente. A skill tem um catálogo em `reference.md` que pode ficar desatualizado.

**Riscos da desatualização:**
- ❌ Skill sugere soluções complexas quando opcode simples já existe
- ❌ Usuários implementam manualmente algo que já tem opcode pronto
- ❌ Redundância e perda de produtividade

---

## ✅ Solução: Hierarquia de Consulta

### 1. **Fonte de Verdade** (Source of Truth)

```
/docs/OPCODE_REFERENCE.md
```

Este arquivo é **gerado automaticamente** do código e está sempre atualizado.

### 2. **Resumo na Skill**

```
/skills/lex-flow-builder/reference.md
```

Contém apenas os opcodes **mais comuns e essenciais**.

**Princípio:** Skill SEMPRE consulta o oficial primeiro, reference.md é fallback.

---

## 🔄 Processo de Sincronização

### Automático (Recomendado)

A cada push em `docs/OPCODE_REFERENCE.md`:

1. **GitHub Action** executa: `.github/workflows/sync-skill-opcodes.yml`
2. **Script Python** compara: `sync_opcodes.py --check-only`
3. **Se há novos opcodes:**
   - Cria/atualiza Issue no GitHub
   - Lista opcodes por categoria (essencial/útil/especializado)
   - Notifica mantenedores

### Manual

```bash
# 1. Ir para o diretório da skill
cd skills/lex-flow-builder

# 2. Executar script de verificação
python sync_opcodes.py

# 3. Revisar output:
#    ⚠️  ESSENCIAIS (devem ser adicionados)
#    💡 ÚTEIS (bom adicionar)
#    🔧 ESPECIALIZADOS (opcional)

# 4. Para cada opcode essencial, adicionar em reference.md
```

---

## 📝 Como Adicionar Novo Opcode

### Passo 1: Verificar detalhes no oficial

```bash
# Buscar opcode no arquivo oficial
grep -A 30 "### \`opcode_name" ../../docs/OPCODE_REFERENCE.md
```

### Passo 2: Avaliar se deve adicionar

✅ **ADICIONE se:**
- Muito usado em workflows comuns
- Essencial para casos de uso frequentes
- Sintaxe complexa que precisa de exemplo

❌ **NÃO adicione se:**
- Muito específico/raramente usado
- Experimental ou em beta
- Já tem exemplo similar documentado

### Passo 3: Adicionar em reference.md

Siga o formato padrão:

```markdown
#### `opcode_name`
Breve descrição do que faz.

**Inputs**:
- `param1` (tipo, required/optional) - Descrição
- `param2` (tipo, optional, default: valor) - Descrição

**Returns**: Tipo de retorno

**Exemplo**:
\`\`\`yaml
node_name:
  opcode: opcode_name
  isReporter: true  # Se retorna valor
  inputs:
    param1:
      literal: "valor"
    param2:
      variable: var_name
\`\`\`
```

### Passo 4: Atualizar data de sincronização

No final de `reference.md`:

```markdown
**ÚLTIMA SINCRONIZAÇÃO**: 2025-03-10 (baseado em commit abc123)
```

### Passo 5: Commit e PR

```bash
git add reference.md
git commit -m "feat(skill): add opcode_name to lex-flow-builder reference"
git push origin feature/update-skill-opcodes
```

---

## 🎯 Estratégia de Priorização

### Categoria: ESSENCIAL ⚠️

Adicionar **imediatamente** ao reference.md:

- `workflow_*` - Controle de workflow
- `io_*` - Input/Output básico
- `operator_*` - Operadores matemáticos/lógicos
- `control_*` - Controle de fluxo (if, loop)
- `data_*` - Manipulação de dados
- `dict_*` - Operações com dicionários
- `list_*` - Operações com listas
- `http_*` - Requisições HTTP

### Categoria: ÚTIL 💡

Adicionar **conforme demanda**:

- `slack_*` - Integrações Slack
- `google_*` - Google APIs
- `github_*` - GitHub integrações
- `file_*` - Operações com arquivos
- `json_*`, `yaml_*`, `csv_*` - Formatos de dados

### Categoria: ESPECIALIZADO 🔧

Adicionar **apenas se houver uso recorrente**:

- Opcodes muito específicos
- Integrações raras
- Funcionalidades experimentais

---

## 🤖 Automação (GitHub Actions)

### Como funciona:

```yaml
# .github/workflows/sync-skill-opcodes.yml

on:
  push:
    paths:
      - 'docs/OPCODE_REFERENCE.md'  # Trigger quando muda
  schedule:
    - cron: '0 9 * * 1'  # Verifica toda segunda 9h

jobs:
  check-sync:
    - Executa sync_opcodes.py --check-only
    - Se detectar novos opcodes essenciais:
      → Cria Issue no GitHub
      → Lista opcodes a adicionar
      → Notifica mantenedores
```

### Monitorar:

- **Issues com label:** `skill-sync`, `automation`
- **Frequência:** Semanal (segundas 9h) + on-demand (quando OPCODE_REFERENCE muda)

---

## 🔍 Workflow de Uso da Skill

**Como a skill usa o catálogo:**

```
1. Usuário pede funcionalidade
   ↓
2. Skill PRIMEIRO consulta:
   - Repositório local: /docs/OPCODE_REFERENCE.md
   - Ou GitHub: https://github.com/.../OPCODE_REFERENCE.md
   ↓
3. Se encontrar opcode:
   → Usar diretamente
   ↓
4. Se NÃO encontrar:
   → Consultar reference.md (resumo)
   ↓
5. Se ainda não encontrar:
   → Oferecer alternativas (HTTP, combinar opcodes, custom)
```

---

## 📊 Métricas de Qualidade

### Indicadores de saúde da skill:

✅ **Boa sincronização:**
- Opcodes essenciais documentados: 100%
- Última sync há menos de 1 mês
- Zero issues abertas sobre opcodes faltantes

⚠️ **Precisa atenção:**
- Opcodes essenciais faltando: > 10%
- Última sync há mais de 2 meses
- 1+ issues abertas há mais de 1 semana

❌ **Crítico:**
- Opcodes essenciais faltando: > 30%
- Última sync há mais de 6 meses
- Múltiplas issues de opcodes faltantes

### Como verificar:

```bash
# Executar verificação manual
python sync_opcodes.py

# Ver saída:
# ✅ Skill está sincronizada!
# ou
# ⚠️  ESSENCIAIS (devem ser adicionados): X opcodes
```

---

## 🚨 Troubleshooting

### "Script retorna erro ao executar"

```bash
# Verificar se está no diretório correto
pwd  # Deve estar em skills/lex-flow-builder

# Verificar se OPCODE_REFERENCE.md existe
ls -la ../../docs/OPCODE_REFERENCE.md

# Verificar Python
python --version  # 3.11+
```

### "Muitos opcodes novos de uma vez"

Isso pode acontecer após grandes updates do LexFlow:

1. **Avaliar cada categoria separadamente**
2. **Priorizar essenciais primeiro**
3. **Criar PR incremental** (não adicionar tudo de uma vez)
4. **Revisar exemplos** antes de adicionar

### "Não sei se opcode é essencial ou não"

Critérios:

```
ESSENCIAL se:
- É usado em > 50% dos workflows
- Não tem alternativa simples
- Funcionalidade core (I/O, control flow, data)

ÚTIL se:
- Integração comum (Slack, Google)
- Tem alternativa mas opcode é mais simples
- Melhora DX significativamente

ESPECIALIZADO se:
- Caso de uso muito específico
- Integração rara
- Funcionalidade experimental
```

Quando em dúvida: **pergunte ao time ou não adicione ainda**.

---

## 📞 Contato

Para dúvidas sobre manutenção da skill:

- **GitHub Issues**: Tag `@maintainer` em issues com label `skill-sync`
- **Repositório**: https://github.com/inspira-legal/lex-flow
- **Documentação**: `/docs` no repositório

---

**Última atualização**: 2025-03-10
**Mantenedores**: Time Inspira Legal + Claude Code Community
