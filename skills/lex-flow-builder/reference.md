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

#### `control_if_else`
Condicional if/else completo.

**Inputs**:
- `CONDITION`: Expressão booleana

**Branches**:
- `THEN`: Node executado se verdadeiro
- `ELSE`: Node executado se falso

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
Cria um dicionário.

**Inputs**: `key1`, `value1`, `key2`, `value2`, etc.

#### `dict_get`
Obtém valor de uma chave.

**Inputs**:
- `dict`: Dicionário
- `key`: Chave a buscar

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

#### `http_post`
Faz requisição HTTP POST.

**Inputs**:
- `url`: URL do endpoint
- `json` (opcional): Payload JSON
- `headers` (opcional): Headers HTTP

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

## Recursos Adicionais

- **Repositório**: https://github.com/inspira-legal/lex-flow
- **Opcode Reference oficial**: `/docs/OPCODE_REFERENCE.md`
- **Grammar Reference**: `/docs/GRAMMAR_REFERENCE.md`
- **Exemplos**: `/examples` no repo

---

**NOTA**: Para lista completa e atualizada de opcodes, consulte `/docs/OPCODE_REFERENCE.md` no repositório oficial.
