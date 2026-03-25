---
name: lexflow-deploy
description: Gerencia deploy e versionamento de workflows LexFlow sempre via CLI. Use quando usuário mencionar "deploy", "publicar", "versionar", "rollback", ou quando lexflow-quick terminar de criar workflow
version: 1.0.0
---

# LexFlow Deploy - Gestão Profissional de Workflows

Gerencio deploy, versionamento e ciclo de vida dos seus workflows LexFlow.

## Princípio Fundamental

**SEMPRE uso CLI para deploy. NUNCA uso interface web.**

Por quê?
- ✅ Rastreável (git commit de cada deploy)
- ✅ Automatizável (CI/CD)
- ✅ Versionado (histórico completo)
- ✅ Auditável (quem deployou o quê e quando)
- ✅ Reversível (rollback fácil)

## O Que Faço

### 1. Deploy Automático
Recebo workflow pronto de `lexflow-quick` e:

```
1. Valido sintaxe YAML
2. Crio versão com timestamp (v1.0.0, v1.1.0, ...)
3. Salvo em workflows/production/
4. Deploy via CLI:
   - save_workflow.py → Salva no LexFlow
   - deploy_manual_lexflow.py → Publica
5. Registro no manifesto
6. Retorno URL de acesso
```

**Você nem percebe! É automático.**

### 2. Versionamento Inteligente
Cada mudança gera nova versão:

```
workflows/
├── production/
│   ├── 20260325_094500_slack_notifier_v1.0.0.yaml
│   ├── 20260325_110200_slack_notifier_v1.1.0.yaml  ← Bug fix
│   └── 20260325_150000_slack_notifier_v2.0.0.yaml  ← Nova feature
├── staging/
│   └── 20260325_143000_slack_notifier_v2.0.0-rc1.yaml
└── manifests/
    └── slack_notifier_v2.0.0_manifest.json
```

**Formato de Versão:**
- Major (v2.0.0): Mudanças incompatíveis
- Minor (v1.1.0): Novas funcionalidades compatíveis
- Patch (v1.0.1): Bug fixes

### 3. Rollback Rápido
Problema em produção? Volto para versão anterior:

```
"rollback workflow X para versão 1.0.0"
  ↓
1. Encontro versão no archive
2. Re-deploy via CLI
3. Pronto! Voltou a funcionar
```

### 4. Monitoramento
Acompanho status dos workflows:

```
"status do workflow X"
  ↓
Workflow: slack-notifier
Versão: v1.1.0
Status: ✅ Ativo
Ambiente: production
Deploy: 2026-03-25 10:02:00
Execuções hoje: 42
Erros hoje: 0
URL: https://lexflow.internal.inspira.legal/w/xxx
```

## Ambientes

### Development
- Desenvolvimento ativo
- Mudanças frequentes
- Sem garantia de estabilidade

### Staging
- Testes finais
- Validação antes de produção
- Dados de teste

### Production
- Workflows estáveis
- Versionamento estrito
- Monitoramento ativo

## Como Trabalho

### Ativação Automática
Sou ativado automaticamente por `lexflow-quick` após criar workflow.

**Transparente para você!**

### Ativação Manual
Pode me chamar diretamente:

```
"fazer deploy do workflow slack-notifier"
"versionar workflow para staging"
"rollback workflow X para versão anterior"
"qual o status do workflow Y?"
```

## Comandos CLI Utilizados

### save_workflow.py
Salva workflow no LexFlow:
```bash
python save_workflow.py slack_notifier.yaml
→ Retorna: workflow_id
```

### deploy_manual_lexflow.py
Publica workflow:
```bash
python deploy_manual_lexflow.py {workflow_id}
→ Retorna: URL de acesso
```

### lexflow_client.py
Operações adicionais:
```bash
python lexflow_client.py status {workflow_id}
python lexflow_client.py list
python lexflow_client.py delete {workflow_id}
```

## Manifesto de Deploy

Cada deploy gera manifesto completo:

```json
{
  "workflow_name": "slack-notifier",
  "version": "1.1.0",
  "timestamp": "20260325_110200",
  "environment": "production",
  "deployed_by": "lexflow-quick",
  "source_hash": "a1b2c3d4",
  "opcodes_used": ["http_post", "json_parse", "slack_send"],
  "custom_opcodes": ["slack_send"],
  "deployed_at": "2026-03-25T11:02:00Z",
  "url": "https://lexflow.internal.inspira.legal/w/abc123"
}
```

**Benefícios:**
- Rastreamento completo
- Auditoria facilitada
- Rollback preciso
- Debug simplificado

## Estrutura de Diretórios

```
workflows/
├── development/
│   └── [workflows em desenvolvimento]
├── staging/
│   └── [workflows em teste]
├── production/
│   └── [workflows ativos]
├── archive/
│   └── [versões antigas]
└── manifests/
    └── [metadados de cada deploy]
```

## Boas Práticas

### ✅ Faça
- Teste em staging antes de production
- Mantenha mensagens de commit descritivas
- Revise manifesto antes de deploy crítico
- Monitore logs após deploy

### ❌ Evite
- Deploy direto em production sem staging
- Pular versionamento
- Deletar versões antigas manualmente
- Deploy via web interface

## Rollback Seguro

### Passo a Passo

1. **Identificar Problema**
   ```
   "workflow X está com erro"
   ```

2. **Verificar Versão Atual**
   ```
   status do workflow X
   → v2.0.0
   ```

3. **Identificar Última Versão Boa**
   ```
   listar versões do workflow X
   → v1.1.0 (última estável)
   ```

4. **Rollback**
   ```
   rollback workflow X para v1.1.0
   ```

5. **Verificar**
   ```
   status do workflow X
   → v1.1.0 ✅
   ```

## Integração CI/CD

Pronto para integrar com pipelines:

```yaml
# .github/workflows/deploy.yml
- name: Deploy Workflow
  run: |
    python save_workflow.py ${{ matrix.workflow }}
    python deploy_manual_lexflow.py $WORKFLOW_ID
```

## Arquitetura Técnica

Detalhes de implementação: [modules/README.md](modules/README.md)

Configurações de ambiente: [configs/environments.yaml](configs/environments.yaml)

## Segurança

### Credenciais
- Nunca commitadas no git
- Armazenadas em variáveis de ambiente
- Rotacionadas regularmente

### Validação
- Sintaxe YAML validada
- Opcodes verificados
- Permissões checadas

### Auditoria
- Todo deploy registrado
- Histórico completo mantido
- Logs detalhados

## Restrições

**Não faço:**
- ❌ Deploy via interface web
- ❌ Mudanças sem versionamento
- ❌ Deploy sem validação

**Sempre:**
- ✅ Uso CLI exclusivamente
- ✅ Versiono automaticamente
- ✅ Mantenho histórico completo
- ✅ Valido antes de deployar