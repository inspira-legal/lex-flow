# LexFlow Reference Guide

## Estrutura de Workflow

### Formato Básico

```yaml
workflows:
  - name: "workflow-name"
    interface:
      inputs:
        - name: input_name
          type: string
          required: true
      outputs: []

    variables:
      variable_name: initial_value

    nodes:
      node_id:
        opcode: operation_name
        next: next_node_id
        inputs:
          PARAM_NAME:
            literal: "value"
            # ou
            variable: var_name
            # ou
            node: reporter_node_id
```

## Tipos de Input

### 1. Literal
Valor fixo definido no workflow:
```yaml
inputs:
  STRING:
    literal: "Hello World"
```

### 2. Variable
Referência a uma variável do workflow:
```yaml
inputs:
  value:
    variable: my_variable_name
```

### 3. Node (Reporter)
Referência a outro node que retorna um valor:
```yaml
inputs:
  VALUE:
    node: compute_result
```

## Catálogo de Opcodes

> **Nota**: Esta é uma referência simplificada baseada nos workflows funcionais. Para lista completa, consulte `/docs/OPCODE_REFERENCE.md` no repositório.

### Core Operations

#### `workflow_start`
⚠️ **OBRIGATÓRIO** - Sempre o primeiro node de qualquer workflow.

**Inputs**: `{}` (vazio)

**Exemplo**:
```yaml
start:
  opcode: workflow_start
  next: primeiro_node
  inputs: {}
```

### I/O Operations

#### `io_print`
Imprime valores no output.

**Inputs**:
- `STRING`: Texto ou valor (literal, variable ou node)

**Exemplo**:
```yaml
print_message:
  opcode: io_print
  next: null
  inputs:
    STRING:
      literal: "Hello World"
```

### Operators

#### `operator_add`
Soma dois números OU concatena strings.

**Inputs**:
- `left`: Primeiro valor
- `right`: Segundo valor

**Exemplo**:
```yaml
add_numbers:
  opcode: operator_add
  isReporter: true
  inputs:
    left:
      literal: 10
    right:
      literal: 5
```

#### `operator_equals`, `operator_greater_than`, `operator_less_than`
Operadores de comparação.

**Inputs**: `left`, `right`  
**Returns**: Boolean

### Control Flow

#### `control_foreach`
Itera sobre cada item em uma coleção.

**Inputs**:
- `VAR`: Nome da variável que receberá cada item
- `ITERABLE`: Lista/array para iterar

**Branches**:
- `BODY`: Node inicial do loop

**Exemplo**:
```yaml
iterate_list:
  opcode: control_foreach
  next: after_loop
  inputs:
    VAR:
      literal: "current_item"
    ITERABLE:
      variable: items
    BODY:
      branch: process_item
```

#### `control_for`
Loop com contador (for loop).

**Inputs**:
- `VAR`: Nome da variável do contador
- `START`: Valor inicial
- `END`: Valor final
- `STEP` (opcional): Incremento (padrão: 1)

**Branches**:
- `BODY`: Node inicial do loop

#### `control_if`
Condicional simples (sem else).

**Inputs**:
- `CONDITION`: Expressão booleana (node reporter)

**Branches**:
- `THEN`: Branch executado se verdadeiro (usa `branch:`, não `node:`)

**Exemplo**:
```yaml
check_value:
  opcode: control_if
  next: after_check
  inputs:
    CONDITION:
      node: is_positive
    THEN:
      branch: print_positive

is_positive:
  opcode: operator_greater_than
  isReporter: true
  inputs:
    OPERAND1:
      variable: x
    OPERAND2:
      literal: 0

print_positive:
  opcode: io_print
  next: null
  inputs:
    STRING:
      literal: "Value is positive"
```

#### `control_if_else`
Condicional if/else completo.

**Inputs**:
- `CONDITION`: Expressão booleana

**Branches**:
- `THEN`: Branch executado se verdadeiro
- `ELSE`: Branch executado se falso

### Data Operations

#### `data_set_variable_to`
Define o valor de uma variável.

**Inputs**:
- `VARIABLE`: Nome da variável
- `VALUE`: Novo valor (pode ser literal, variable ou node)

**Exemplo**:
```yaml
set_counter:
  opcode: data_set_variable_to
  next: continue
  inputs:
    VARIABLE:
      literal: "counter"
    VALUE:
      literal: 0
```

### List Operations

#### `list_length`
Retorna o tamanho de uma lista.

**Inputs**:
- `list`: Lista para medir

### Dictionary Operations

#### `dict_create`
Cria um dicionário vazio (ou com argumentos variáveis).

**Inputs**: Vazio `{}` ou `key1`, `value1`, `key2`, `value2`, etc.

**Exemplo**:
```yaml
create_empty:
  opcode: dict_create
  isReporter: true
  inputs: {}
```

#### `dict_from_lists`
Cria dict de listas paralelas de keys e values.

**Inputs**:
- `keys`: Lista de chaves
- `values`: Lista de valores correspondentes

**Exemplo**:
```yaml
create_user:
  opcode: dict_from_lists
  isReporter: true
  inputs:
    keys:
      literal: ["name", "age", "role"]
    values:
      literal: ["Alice", 30, "engineer"]
```

#### `dict_get`
Obtém valor de uma chave.

**Inputs**:
- `d`: Dicionário
- `key`: Chave a buscar
- `default` (opcional): Valor padrão se chave não existir

#### `dict_set`
Define/atualiza valor de uma chave.

**Inputs**:
- `d`: Dicionário
- `key`: Chave
- `value`: Novo valor

**Returns**: Dicionário atualizado

#### `dict_update`
Merge dois dicionários.

**Inputs**:
- `d`: Dicionário base
- `other`: Dicionário a mesclar

**Returns**: Dicionário mesclado

#### `dict_keys`
Retorna lista de todas as chaves.

**Inputs**:
- `d`: Dicionário

**Returns**: Lista de strings

#### `dict_contains`
Verifica se chave existe.

**Inputs**:
- `d`: Dicionário
- `key`: Chave a verificar

**Returns**: Boolean

#### `dict_len`
Retorna número de chaves.

**Inputs**:
- `d`: Dicionário

**Returns**: Integer

#### `dict_copy`
Cria cópia do dicionário.

**Inputs**:
- `d`: Dicionário

**Returns**: Novo dicionário (cópia independente)

### String Operations

#### `str`
Converte valor para string.

**Inputs**:
- `value`: Valor a converter

### HTTP Operations

> Requer: `lexflow[http]`

#### `http_get`
Faz requisição HTTP GET.

**Inputs**:
- `url`: URL do endpoint
- `headers` (opcional): Dicionário de headers
- `timeout` (opcional): Timeout em segundos (padrão: 30.0)

**Returns**: Dict com:
- `status`: Código HTTP (ex: 200, 404)
- `headers`: Headers da resposta
- `text`: Body como string
- `json`: Body parseado (se Content-Type for JSON)

**Exemplo**:
```yaml
fetch_data:
  opcode: http_get
  isReporter: true
  inputs:
    url:
      literal: "https://api.example.com/data"

extract_json:
  opcode: dict_get
  isReporter: true
  inputs:
    d:
      node: fetch_data
    key:
      literal: "json"
```

#### `http_post`
Faz requisição HTTP POST.

**Inputs**:
- `url`: URL do endpoint
- `data` (opcional): Form data (form-encoded POST)
- `json` (opcional): Payload JSON (define Content-Type automaticamente)
- `headers` (opcional): Headers HTTP
- `timeout` (opcional): Timeout em segundos (padrão: 30.0)

**Returns**: Dict com mesma estrutura do `http_get`

**Exemplo**:
```yaml
send_message:
  opcode: http_post
  isReporter: true
  inputs:
    url:
      literal: "https://api.slack.com/api/chat.postMessage"
    json:
      node: payload_dict
    headers:
      node: auth_headers
```

## Reporter Nodes

Nodes com `isReporter: true` retornam valores que podem ser usados por outros nodes:

```yaml
compute:
  opcode: operator_add
  isReporter: true
  inputs:
    left:
      literal: 10
    right:
      literal: 5

use_result:
  opcode: io_print
  next: null
  inputs:
    STRING:
      node: compute  # Usa o resultado de compute (15)
```

## Integrações Customizadas

### Slack (Requer opcodes customizados)

Se os opcodes de Slack estiverem instalados:

#### `slack_create_client`
Cria cliente autenticado do Slack.

**Inputs**:
- `token`: OAuth token (xoxb-... ou xoxp-...)

**Returns**: Cliente Slack

#### `slack_send_message`
Envia mensagem para canal.

**Inputs**:
- `client`: Cliente Slack (node)
- `channel`: Nome do canal ou ID
- `text`: Texto da mensagem

#### `slack_test_auth`
Testa autenticação.

**Inputs**:
- `client`: Cliente Slack

**Returns**: Info do usuário autenticado

**Exemplo completo**:
```yaml
create_client:
  opcode: slack_create_client
  isReporter: true
  inputs:
    token:
      variable: slack_token

send_msg:
  opcode: slack_send_message
  isReporter: true
  inputs:
    client:
      node: create_client
    channel:
      literal: "general"
    text:
      literal: "Hello from LexFlow!"
```

## Recursos Adicionais

- **Repositório**: https://github.com/inspira-legal/lex-flow
- **Opcode Reference oficial**: `/docs/OPCODE_REFERENCE.md`
- **Grammar Reference**: `/docs/GRAMMAR_REFERENCE.md`
- **Exemplos Oficiais**: `/examples` no repo
- **Deploy via API**: Veja scripts Python em `lexflow_client.py`

---

**NOTA**: Para lista completa e atualizada de opcodes, consulte `/docs/OPCODE_REFERENCE.md` no repositório oficial.
