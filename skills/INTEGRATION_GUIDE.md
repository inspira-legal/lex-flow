# Guia de Integração - Skills LexFlow

## Visão Geral

As 3 skills LexFlow trabalham juntas de forma transparente para criar, estender e deployar workflows automaticamente.

## Arquitetura de Skills

```
┌─────────────────┐
│  lexflow-quick  │  Skill Principal
│  Cria workflows │  - Detecção de padrões
│                 │  - Templates validados
└────────┬────────┘  - Máximo 2 perguntas
         │
         ├─────────→ ┌──────────────────┐
         │           │  lexflow-extend  │  Extensão
         │           │  Cria opcodes    │  - Wrappers
         │           │                  │  - Implementação nativa
         │           └──────────────────┘  - PRs automáticos
         │
         └─────────→ ┌──────────────────┐
                     │  lexflow-deploy  │  Deploy & Gestão
                     │  Deploy via CLI  │  - Versionamento
                     │                  │  - Rollback
                     └──────────────────┘  - Monitoramento
```

## Fluxo de Trabalho

### Cenário 1: Workflow com Opcodes Existentes

```
1. Usuário: "criar workflow para buscar dados da API GitHub"
   ↓
2. lexflow-quick detecta: api_integration
   ↓
3. lexflow-quick valida: ✅ Todos opcodes existem
   ↓
4. lexflow-quick cria: workflow_api_github.yaml
   ↓
5. lexflow-quick → lexflow-deploy
   ↓
6. lexflow-deploy:
   - Versiona (v1.0.0)
   - Deploy via CLI
   - Retorna URL
   ↓
7. ✅ Pronto! URL: https://lexflow.internal/w/abc123
```

**Tempo total:** ~5 segundos
**Perguntas ao usuário:** 1 (URL da API)

### Cenário 2: Workflow Precisa de Novo Opcode

```
1. Usuário: "criar workflow para enviar mensagem no Slack"
   ↓
2. lexflow-quick detecta: notification (Slack)
   ↓
3. lexflow-quick valida: ❌ Opcode slack_send não existe
   ↓
4. lexflow-quick → lexflow-extend (automático)
   context: {missing_opcodes: ["slack_send"]}
   ↓
5. lexflow-extend:
   - Analisa: wrapper de http_post
   - Gera código Python
   - Cria documentação
   - Salva localmente em .lexflow/custom_opcodes/
   - Prepara PR para lexflow-opcodes
   ↓
6. lexflow-extend → lexflow-quick
   context: {opcode_name: "slack_send", local_path: "..."}
   ↓
7. lexflow-quick:
   - Adiciona slack_send à lista de opcodes
   - Cria workflow com novo opcode
   ↓
8. lexflow-quick → lexflow-deploy
   context: {workflow_path: "...", custom_opcodes: ["slack_send"]}
   ↓
9. lexflow-deploy:
   - Versiona (v1.0.0)
   - Deploy via CLI
   - Registra uso de custom opcode no manifesto
   - Retorna URL
   ↓
10. ✅ Pronto! Opcode criado + Workflow deployado
```

**Tempo total:** ~15 segundos
**Perguntas ao usuário:** 2 (webhook URL, canal)

### Cenário 3: Rollback de Versão

```
1. Usuário: "rollback workflow slack-notifier para v1.0.0"
   ↓
2. Claude detecta palavra "rollback" → ativa lexflow-deploy
   ↓
3. lexflow-deploy:
   - Busca v1.0.0 em workflows/archive/
   - Encontra: 20260325_094500_slack_notifier_v1.0.0.yaml
   - Re-deploy via CLI
   - Atualiza manifesto
   ↓
4. ✅ Pronto! Voltou para v1.0.0
```

**Tempo total:** ~3 segundos
**Perguntas ao usuário:** 0

## Protocolo de Comunicação

### Formato de Mensagem

```python
{
    "source": "lexflow-quick",      # Skill origem
    "target": "lexflow-extend",     # Skill destino
    "action": "CREATE_OPCODE",      # Ação a executar
    "context": {                    # Dados contextuais
        "missing_opcodes": ["slack_send"],
        "original_request": "enviar mensagem no Slack"
    },
    "callback": "lexflow-quick"     # Para onde retornar
}
```

### Ações Disponíveis

| Ação | Origem | Destino | Contexto Requerido |
|------|--------|---------|-------------------|
| CREATE_WORKFLOW | user | lexflow-quick | user_input, params |
| CREATE_OPCODE | lexflow-quick | lexflow-extend | missing_opcodes, original_request |
| OPCODE_READY | lexflow-extend | lexflow-quick | opcode_name, local_path |
| DEPLOY | lexflow-quick | lexflow-deploy | workflow_path, environment |
| DEPLOYMENT_COMPLETE | lexflow-deploy | lexflow-quick | workflow_id, version, url |
| ROLLBACK | user | lexflow-deploy | workflow_id, version |
| GET_STATUS | user | lexflow-deploy | workflow_id |

## Detecção Automática de Skills

### Keywords que Ativam lexflow-quick

```
"criar workflow"
"automatizar"
"fluxo"
"integrar"
"processar"
"enviar"
"buscar dados"
"chamar api"
```

### Keywords que Ativam lexflow-extend

```
"criar opcode"
"novo opcode"
"estender lexflow"
"adicionar funcionalidade"
```

### Keywords que Ativam lexflow-deploy

```
"deploy"
"publicar"
"versionar"
"rollback"
"status do workflow"
"listar versões"
```

## Progressive Disclosure

### Nível 1: SKILL.md (Lido pelo Claude)

Contém:
- Descrição concisa (3-5 linhas)
- Keywords para ativação
- Capacidades principais
- Quando usar outras skills
- Exemplos de uso

**Objetivo:** Claude entende rapidamente quando ativar a skill

### Nível 2: Seções Expandidas no SKILL.md

Contém:
- Como trabalha
- Padrões reconhecidos
- Arquitetura de alto nível
- Integrações

**Objetivo:** Claude entende o fluxo de trabalho

### Nível 3: modules/README.md

Contém:
- Detalhes técnicos de implementação
- Algoritmos usados
- Estruturas de dados
- Troubleshooting

**Objetivo:** Claude resolve problemas técnicos específicos

## Best Practices Implementadas

### ✅ Máximo 2 Perguntas ao Usuário

As skills foram projetadas para fazer no máximo 2 perguntas por workflow:

```python
# Exemplo: Slack notification
questions = [
    "Qual o webhook URL do Slack?",  # Essencial
    "Qual canal notificar?"          # Opcional (tem default)
]
```

### ✅ Templates Pré-Validados

Apenas oferecemos templates com opcodes comprovadamente funcionais:

```python
if not all_opcodes_exist(template):
    delegate_to_extend()  # Cria automaticamente
else:
    create_workflow()     # Usa template direto
```

### ✅ Transparência Total

Sempre informamos o que está acontecendo:

```
"Detectei que você precisa do opcode slack_send."
"Estou criando esse opcode automaticamente..."
"✅ Opcode criado! Continuando com o workflow..."
"✅ Workflow deployado em: [URL]"
```

### ✅ Deploy Sempre via CLI

```python
# ❌ NUNCA
web_deploy(workflow)

# ✅ SEMPRE
cli_deploy(workflow)  # save_workflow.py + deploy_manual_lexflow.py
```

### ✅ Versionamento Semântico

```
v1.0.0 → Primeira versão
v1.1.0 → Adicionou feature X
v1.1.1 → Bug fix
v2.0.0 → Breaking change
```

## Testes de Integração

### Executar Todos os Testes

```bash
uv run python test_skills_integration.py
```

### Testes Individuais

```python
# Teste 1: Workflow simples (opcodes existentes)
test_simple_workflow()

# Teste 2: Workflow com extensão (opcode novo)
test_workflow_with_extension()

# Teste 3: Fluxo completo de integração
test_full_integration_flow()

# Teste 4: Operações de deploy
test_deployment_operations()
```

## Troubleshooting

### Skill não foi ativada

**Problema:** Claude não detectou a keyword

**Solução:** Force ativação
```
Skill: lexflow-quick
```

### Opcode não foi criado

**Problema:** lexflow-extend não foi acionada

**Solução:** Verifique se lexflow-quick delegou corretamente
```python
# Ver logs
logging.debug("Delegation message sent")
```

### Deploy falhou

**Problema:** Scripts CLI não encontrados ou erro de permissão

**Solução:**
1. Verifique se `save_workflow.py` e `deploy_manual_lexflow.py` existem
2. Teste manualmente:
   ```bash
   python save_workflow.py test.yaml
   python deploy_manual_lexflow.py {workflow_id}
   ```

## Estrutura de Arquivos

```
.claude/skills/
├── shared/
│   └── skill_protocol.py              # Protocolo compartilhado
│
├── lexflow-quick/
│   ├── SKILL.md                       # ← Claude lê
│   ├── lexflow_quick.py               # Implementação
│   ├── modules/
│   │   └── README.md                  # Detalhes técnicos
│   └── templates/
│       └── *.yaml                     # Templates validados
│
├── lexflow-extend/
│   ├── SKILL.md                       # ← Claude lê
│   ├── lexflow_extend.py              # Implementação
│   └── modules/
│       └── README.md                  # Detalhes técnicos
│
├── lexflow-deploy/
│   ├── SKILL.md                       # ← Claude lê
│   ├── lexflow_deploy.py              # Implementação
│   └── modules/
│       └── README.md                  # Detalhes técnicos
│
└── INTEGRATION_GUIDE.md               # ← Este arquivo
```

## Métricas de Sucesso

### Performance

- Workflow simples: < 5 segundos
- Workflow com extensão: < 15 segundos
- Rollback: < 3 segundos

### Usabilidade

- Máximo 2 perguntas por workflow
- Taxa de sucesso > 95%
- Zero intervenção manual no deploy

### Qualidade

- 100% dos deploys versionados
- 100% dos deploys via CLI
- Rollback disponível para todas as versões

## Próximos Passos

### Fase 1: Validação (Atual)
- [x] Implementar 3 skills
- [x] Criar protocolo de integração
- [x] Refatorar para best practices
- [ ] Testar com casos reais

### Fase 2: Produção
- [ ] Conectar APIs reais (LexFlow, GitHub)
- [ ] Adicionar autenticação
- [ ] Expandir catálogo de templates
- [ ] Métricas e monitoramento

### Fase 3: Expansão
- [ ] Mais opcodes pré-criados
- [ ] IA para detecção de padrões
- [ ] Otimização de performance
- [ ] Dashboard de workflows

## Contribuindo

Para adicionar novo template:
1. Criar `.yaml` em `lexflow-quick/templates/`
2. Adicionar padrão de detecção
3. Validar opcodes necessários
4. Documentar em README

Para adicionar novo tipo de opcode:
1. Adicionar analyzer em `lexflow-extend.py`
2. Criar template de geração
3. Adicionar testes
4. Documentar casos de uso

## Suporte

- Issues: GitHub Issues do projeto
- Docs: Este arquivo + SKILL.md de cada skill
- Testes: `test_skills_integration.py`