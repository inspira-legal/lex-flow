# 🚀 LexFlow Skills para Claude Code

> Skills especializadas para criação, edição e deploy de workflows LexFlow usando Claude Code

## 📦 O que são essas Skills?

Este é um conjunto de 3 skills que transformam Claude Code em uma ferramenta poderosa para automação com LexFlow:

- **lexflow-quick** - Cria e edita workflows rapidamente
- **lexflow-extend** - Cria novos opcodes personalizados
- **lexflow-deploy** - Gerencia deploy, versionamento e rollback

## 🎯 Para quem é?

- **Desenvolvedores** que querem automatizar tarefas sem escrever YAML manualmente
- **Times de DevOps** que precisam criar workflows rapidamente
- **Empresas** que usam LexFlow e querem acelerar desenvolvimento

## ⚡ Instalação Rápida

### Opção 1: Instalação Automática (Recomendado)

```bash
# Clone este repositório
git clone https://github.com/seu-usuario/lexflow-skills
cd lexflow-skills

# Execute o instalador
./install.sh
```

### Opção 2: Instalação Manual

1. **Copie a pasta `.claude/skills`** para seu projeto:
```bash
cp -r .claude/skills /seu/projeto/.claude/skills
```

2. **Verifique a estrutura**:
```
seu-projeto/
└── .claude/
    └── skills/
        ├── lexflow-quick/
        ├── lexflow-extend/
        ├── lexflow-deploy/
        └── shared/
```

3. **Teste a instalação**:
```bash
uv run python test_skills_integration.py
```

## 🔧 Configuração

### 1. Configurar Credenciais LexFlow

Crie um arquivo `.env` na raiz do projeto:

```env
# LexFlow API
LEXFLOW_API_URL=https://api.lexflow.com
LEXFLOW_API_KEY=seu_token_aqui

# GitHub (para PRs de opcodes)
GITHUB_TOKEN=ghp_seu_token_aqui
GITHUB_REPO=seu-org/lexflow-opcodes

# Ambiente padrão
DEFAULT_ENVIRONMENT=production
```

### 2. Configurar Claude Code

As skills são detectadas automaticamente pelo Claude Code. Não precisa configurar nada!

## 💬 Como Usar

### Criando Workflows

Basta falar naturalmente com Claude:

```
"criar workflow para enviar mensagem no Slack"
"automatizar processamento de CSV"
"integrar com API do GitHub"
```

### Editando Workflows

```
"editar workflow slack-notifier para adicionar canal #dev"
"modificar api-fetcher para usar nova URL"
"otimizar csv-processor para rodar mais rápido"
```

### Deploy e Gestão

```
"fazer deploy do workflow"
"rollback para versão 1.0.0"
"qual o status do workflow user-signup?"
```

## 📚 Exemplos Práticos

### Exemplo 1: Notificação Slack

```yaml
Você: criar workflow para notificar equipe no Slack quando build falhar

Claude:
✅ Workflow criado: build-failure-notifier
✅ Opcode slack_send criado automaticamente
✅ Deploy realizado: https://lexflow.com/w/build-failure-notifier
```

### Exemplo 2: Processamento de Dados

```yaml
Você: criar workflow para processar planilha Excel e gerar relatório PDF

Claude:
✅ Workflow criado: excel-to-pdf-reporter
✅ Templates aplicados: csv_parse, pdf_generate
✅ Deploy realizado: https://lexflow.com/w/excel-to-pdf-reporter
```

### Exemplo 3: Integração API

```yaml
Você: editar workflow github-monitor para incluir webhook do Discord

Claude:
✅ Workflow encontrado: github-monitor
✅ Node discord_webhook adicionado
✅ Nova versão v1.2.0 deployada
```

## 🏗️ Arquitetura

```
┌─────────────┐
│   Claude    │ ← Você fala naturalmente
│    Code     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│   lexflow-quick          │ ← Detecta padrão e cria workflow
│   (Criação/Edição)       │
└──────┬───────────────────┘
       │ Precisa opcode?
       ▼
┌──────────────────────────┐
│   lexflow-extend         │ ← Cria opcode automaticamente
│   (Extensão)             │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   lexflow-deploy         │ ← Deploy via CLI
│   (Deploy/Gestão)        │
└──────────────────────────┘
```

## 📊 Capacidades

| Funcionalidade | Status | Descrição |
|---------------|--------|-----------|
| Criar workflows | ✅ | Templates validados para APIs, Slack, CSV, Web |
| Editar workflows | ✅ | Adicionar, remover, modificar elementos |
| Criar opcodes | ✅ | Geração automática de Python + testes |
| Deploy via CLI | ✅ | Sempre via linha de comando |
| Versionamento | ✅ | Semântico automático (v1.0.0) |
| Rollback | ✅ | Voltar para versões anteriores |
| Multi-ambiente | ✅ | Dev, staging, production |

## 🤝 Contribuindo

### Como Adicionar Novo Template

1. Crie o arquivo em `lexflow-quick/templates/seu_template.yaml`
2. Adicione ao dicionário em `lexflow_quick.py`:

```python
"seu_template": {
    "triggers": ["palavra", "chave"],
    "opcodes": ["opcode1", "opcode2"],
    "validated": True,
    "template": "templates/seu_template.yaml"
}
```

### Como Adicionar Novo Opcode

1. Implemente em `lexflow-extend/opcodes/seu_opcode.py`
2. Adicione testes em `lexflow-extend/tests/`
3. Registre em `available_opcodes`

### Enviando PRs

```bash
# Fork o projeto
# Crie sua branch
git checkout -b feature/novo-template

# Commit suas mudanças
git commit -m "feat: adiciona template para integração X"

# Push e abra PR
git push origin feature/novo-template
```

## 🐛 Troubleshooting

### Erro: "Skill not found"

Verifique se a estrutura `.claude/skills/` está correta:
```bash
ls -la .claude/skills/
```

### Erro: "Opcode not available"

O opcode será criado automaticamente. Se falhar:
```bash
# Verifique opcodes customizados
ls .lexflow/custom_opcodes/
```

### Erro: "Deploy failed"

Verifique credenciais:
```bash
# Teste conexão
python test_lexflow_connection.py
```

## 📝 Requisitos

- Claude Code instalado
- Python 3.9+
- uv (gerenciador de pacotes)
- Conta LexFlow (para deploy real)

## 📄 Licença

MIT - Veja [LICENSE](LICENSE) para detalhes

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/lexflow-skills/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/lexflow-skills/discussions)
- **Email**: suporte@seu-dominio.com

## 🌟 Showcase

Empresas usando LexFlow Skills:

- 🏢 **Empresa A** - "Reduziu tempo de criação de workflows em 80%"
- 🏢 **Empresa B** - "Deploy 10x mais rápido"
- 🏢 **Empresa C** - "Zero erros de sintaxe YAML"

## 📈 Roadmap

- [ ] Suporte a mais plataformas (Teams, Discord, Telegram)
- [ ] Templates para ML/AI workflows
- [ ] Interface web para gestão
- [ ] Marketplace de opcodes
- [ ] Integração com CI/CD

## ⭐ Star este projeto!

Se você achou útil, deixe uma ⭐ no GitHub!

---

**Desenvolvido com ❤️ pela comunidade LexFlow**