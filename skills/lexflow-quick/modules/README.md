# LexFlow Quick - Módulos Técnicos

## Arquitetura Interna

Este documento detalha a implementação técnica da skill `lexflow-quick`.

## Componentes Principais

### 1. Pattern Detector (`pattern_detector.py`)

Responsável por identificar o tipo de workflow baseado no input do usuário.

**Padrões Suportados:**

| Padrão | Keywords | Template | Opcodes Requeridos |
|--------|----------|----------|-------------------|
| notification | slack, teams, email, notificar | notification.yaml | slack_send, teams_send, email_send |
| api_integration | api, rest, endpoint, webhook | api_fetcher.yaml | http_get, http_post, json_parse |
| data_processing | csv, json, xml, processar | csv_processor.yaml | csv_parse, json_parse, xml_parse |
| web_scraper | scraping, extrair, html | web_scraper.yaml | http_get, html_parse, html_select |

**Algoritmo de Detecção:**

```python
1. Normaliza input (lowercase, remove acentos)
2. Tokeniza em palavras-chave
3. Compara com padrões conhecidos
4. Retorna template com maior score de match
5. Se nenhum match > 70%, retorna None
```

### 2. Template Validator (`template_validator.py`)

Valida se um template pode ser usado verificando disponibilidade de opcodes.

**Fluxo de Validação:**

```
1. Carrega lista de opcodes nativos do LexFlow
2. Para cada opcode no template:
   - Verifica se existe nativamente
   - Se não existe, marca como "requires_extension"
3. Retorna:
   - valid: boolean
   - missing_opcodes: list
   - requires_extension: boolean
```

**Opcodes Nativos Conhecidos:**

- I/O: `io_print`, `io_input`, `io_read_file`, `io_write_file`
- HTTP: `http_get`, `http_post`, `http_put`, `http_delete`
- Data: `json_parse`, `json_stringify`, `csv_parse`, `csv_write`
- HTML: `html_parse`, `html_select`, `html_get_text`
- Collections: `list_foreach`, `list_map`, `list_filter`, `dict_get`, `dict_set`
- Control Flow: `control_if_else`, `control_foreach`, `control_while`
- System: `bash_run`, `python_eval`

### 3. Workflow Generator (`workflow_generator.py`)

Gera workflows YAML baseado em templates e parâmetros do usuário.

**Processo de Geração:**

```
1. Carrega template base (.yaml)
2. Aplica parâmetros do usuário:
   - Substitui variáveis
   - Adiciona inputs/outputs
   - Configura nodes específicos
3. Valida estrutura YAML
4. Salva arquivo com timestamp
5. Retorna path do arquivo gerado
```

**Estrutura de Template:**

```yaml
workflows:
  - name: main
    interface:
      inputs: [...]   # Definido pelo template
      outputs: [...]  # Definido pelo template
    variables:
      # Valores padrão + substituídos pelos do usuário
    nodes:
      # Sequência de operações do template
```

## Integração com Outras Skills

### Delegação para lexflow-extend

Quando um opcode não existe:

```python
# 1. Template requer opcode 'slack_send'
validation = validator.validate_template("notification")
# validation = {valid: False, missing: ['slack_send']}

# 2. Cria mensagem para lexflow-extend
message = {
    "target": "lexflow-extend",
    "action": "CREATE_OPCODE",
    "context": {
        "missing_opcodes": ["slack_send"],
        "original_request": user_input
    }
}

# 3. Aguarda resposta com opcode criado
response = await send_to_skill(message)

# 4. Adiciona opcode temporariamente à lista
opcodes.append(response.opcode_name)

# 5. Continua criação do workflow
```

### Handoff para lexflow-deploy

Após criar workflow:

```python
# 1. Workflow criado com sucesso
workflow_path = generator.create_workflow(template, params)

# 2. Envia para deploy
message = {
    "target": "lexflow-deploy",
    "action": "DEPLOY",
    "context": {
        "workflow_path": workflow_path,
        "environment": "production"
    }
}

# 3. lexflow-deploy assume responsabilidade
response = await send_to_skill(message)

# 4. Retorna resultado ao usuário
return response.url
```

## Protocolo de Comunicação

### Formato de Mensagem

```python
class SkillMessage:
    source: str          # Skill origem
    target: str          # Skill destino
    action: SkillAction  # Ação a executar
    context: dict        # Dados contextuais
    callback: str        # Skill para resposta
```

### Ações Suportadas

| Ação | Descrição | Context Required |
|------|-----------|------------------|
| CREATE_WORKFLOW | Criar novo workflow | user_input, params |
| VALIDATE_TEMPLATE | Validar template | template_name |
| DELEGATE_EXTENSION | Delegar criação de opcode | missing_opcodes |

## Configuração

### Adicionando Novo Template

1. Criar arquivo em `templates/novo_template.yaml`
2. Adicionar padrão em `pattern_detector.py`:
   ```python
   "novo_template": {
       "triggers": ["palavra", "chave"],
       "opcodes": ["opcode1", "opcode2"],
       "validated": True
   }
   ```
3. Validar opcodes existem ou marcar `validated: False`

### Customizando Detecção

Edite `pattern_detector.py` para ajustar:
- Threshold de similaridade (padrão: 70%)
- Pesos de palavras-chave
- Sinônimos reconhecidos

## Testes

Execute testes unitários:

```bash
uv run pytest tests/test_lexflow_quick.py -v
```

Execute teste de integração completo:

```bash
uv run python test_skills_integration.py
```

## Logging & Debug

Habilite logs detalhados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Logs incluem:
- Detecção de padrões
- Validação de opcodes
- Geração de workflows
- Comunicação entre skills

## Performance

### Métricas Alvo

- Detecção de padrão: < 100ms
- Validação de template: < 50ms
- Geração de workflow: < 200ms
- Tempo total (sem extensão): < 500ms

### Otimizações Implementadas

- Cache de opcodes nativos
- Templates pré-carregados em memória
- Validação paralela de múltiplos opcodes

## Troubleshooting

### Problema: Padrão não detectado

**Solução:** Adicione keywords ao detector ou force template:
```python
create_workflow(template_name="api_fetcher", params={...})
```

### Problema: Opcode não encontrado

**Resposta:** Automática - delega para lexflow-extend

### Problema: Workflow inválido

**Causa:** Template corrupto ou parâmetros incorretos
**Solução:** Valide template YAML manualmente