# LexFlow Reference Guide

## Estrutura de Workflow

### Formato Básico

```yaml
name: "workflow-name"
interface:
  inputs:
    - name: input_name
      type: string | number | boolean | any | array | object
  outputs:
    - name: output_name
      type: string | number | boolean | any | array | object

variables:
  - name: variable_name
    value: initial_value

nodes:
  - id: unique_node_id
    opcode: operation_name
    inputs:
      PARAM_NAME:
        type: literal | variable | computed
        value: value_or_reference
    branches:
      BRANCH_NAME: target_node_id
    next: next_node_id | null
```

## Tipos de Input

### 1. Literal
Valor fixo definido no workflow:
```yaml
inputs:
  MESSAGE:
    type: literal
    value: "Hello World"
```

### 2. Variable
Referência a uma variável do workflow:
```yaml
inputs:
  DATA:
    type: variable
    value: my_variable_name
```

### 3. Computed
Valor calculado (consultar documentação específica):
```yaml
inputs:
  RESULT:
    type: computed
    value: expression_or_function
```

## Catálogo de Opcodes

### I/O Operations

#### `io_input`
Recebe entrada do usuário ou sistema.

**Inputs**:
- `PROMPT` (optional): Mensagem para o usuário
- `DEFAULT` (optional): Valor padrão

**Outputs**: Valor recebido (armazenado em variável)

**Exemplo**:
```yaml
- id: get_input
  opcode: io_input
  inputs:
    PROMPT:
      type: literal
      value: "Digite seu nome:"
  next: process_input
```

#### `io_print`
Imprime mensagem no output.

**Inputs**:
- `MESSAGE`: Texto a ser impresso

**Exemplo**:
```yaml
- id: print_hello
  opcode: io_print
  inputs:
    MESSAGE:
      type: literal
      value: "Hello World"
  next: null
```

#### `io_output`
Define saída do workflow (output final).

**Inputs**:
- `VALUE`: Valor a ser retornado
- `OUTPUT_NAME`: Nome do output (deve corresponder ao interface)

**Exemplo**:
```yaml
- id: set_output
  opcode: io_output
  inputs:
    OUTPUT_NAME:
      type: literal
      value: "result"
    VALUE:
      type: variable
      value: processed_data
  next: null
```

### Control Flow Operations

#### `control_repeat`
Executa um bloco de código N vezes (loop).

**Inputs**:
- `TIMES`: Número de repetições

**Branches**:
- `BODY`: Node inicial do loop

**Exemplo**:
```yaml
- id: loop_10_times
  opcode: control_repeat
  inputs:
    TIMES:
      type: literal
      value: 10
  branches:
    BODY: loop_body_start
  next: after_loop
```

#### `control_if`
Condicional if/then/else.

**Inputs**:
- `CONDITION`: Expressão booleana

**Branches**:
- `THEN`: Node executado se verdadeiro
- `ELSE`: Node executado se falso

**Exemplo**:
```yaml
- id: check_condition
  opcode: control_if
  inputs:
    CONDITION:
      type: variable
      value: is_valid
  branches:
    THEN: success_path
    ELSE: error_path
  next: null
```

#### `control_wait`
Pausa a execução por tempo determinado.

**Inputs**:
- `DURATION`: Tempo em segundos

**Exemplo**:
```yaml
- id: wait_5_seconds
  opcode: control_wait
  inputs:
    DURATION:
      type: literal
      value: 5
  next: continue_flow
```

### Data Operations

#### `data_change_variable_by`
Modifica o valor de uma variável (incremento/decremento).

**Inputs**:
- `VARIABLE`: Nome da variável
- `VALUE`: Valor a adicionar/subtrair

**Exemplo**:
```yaml
- id: increment_counter
  opcode: data_change_variable_by
  inputs:
    VARIABLE:
      type: literal
      value: "counter"
    VALUE:
      type: literal
      value: 1
  next: check_counter
```

#### `data_set_variable`
Define o valor de uma variável.

**Inputs**:
- `VARIABLE`: Nome da variável
- `VALUE`: Novo valor

**Exemplo**:
```yaml
- id: set_status
  opcode: data_set_variable
  inputs:
    VARIABLE:
      type: literal
      value: "status"
    VALUE:
      type: literal
      value: "completed"
  next: finish
```

#### `data_get_variable`
Obtém o valor de uma variável.

**Inputs**:
- `VARIABLE`: Nome da variável

**Outputs**: Valor da variável

**Exemplo**:
```yaml
- id: get_counter
  opcode: data_get_variable
  inputs:
    VARIABLE:
      type: literal
      value: "counter"
  next: use_value
```

### Math Operations

#### `math_add`
Soma dois números.

**Inputs**:
- `NUM1`: Primeiro número
- `NUM2`: Segundo número

**Exemplo**:
```yaml
- id: add_numbers
  opcode: math_add
  inputs:
    NUM1:
      type: literal
      value: 10
    NUM2:
      type: variable
      value: user_input
  next: store_result
```

#### `math_subtract`
Subtrai dois números.

**Inputs**:
- `NUM1`: Número base
- `NUM2`: Número a subtrair

#### `math_multiply`
Multiplica dois números.

**Inputs**:
- `NUM1`: Primeiro fator
- `NUM2`: Segundo fator

#### `math_divide`
Divide dois números.

**Inputs**:
- `NUM1`: Dividendo
- `NUM2`: Divisor

### String Operations

#### `string_concat`
Concatena strings.

**Inputs**:
- `STRING1`: Primeira string
- `STRING2`: Segunda string

**Exemplo**:
```yaml
- id: join_strings
  opcode: string_concat
  inputs:
    STRING1:
      type: literal
      value: "Hello "
    STRING2:
      type: variable
      value: user_name
  next: print_greeting
```

#### `string_length`
Retorna o comprimento de uma string.

**Inputs**:
- `STRING`: String a medir

#### `string_contains`
Verifica se uma string contém outra.

**Inputs**:
- `STRING`: String principal
- `SEARCH`: Texto a buscar

**Outputs**: Boolean (true/false)

### List/Array Operations

#### `list_create`
Cria uma nova lista.

**Inputs**:
- `ITEMS`: Array de valores iniciais (opcional)

#### `list_add`
Adiciona item ao final da lista.

**Inputs**:
- `LIST`: Lista alvo
- `ITEM`: Item a adicionar

#### `list_get`
Obtém item em posição específica.

**Inputs**:
- `LIST`: Lista fonte
- `INDEX`: Posição (0-based)

#### `list_length`
Retorna o tamanho da lista.

**Inputs**:
- `LIST`: Lista a medir

### Custom/Extended Operations

#### `custom_*`
Operações customizadas podem ser adicionadas via extensões.

**Exemplo de uso**:
```yaml
- id: custom_operation
  opcode: custom_send_email
  inputs:
    TO:
      type: variable
      value: recipient_email
    SUBJECT:
      type: literal
      value: "Workflow Notification"
    BODY:
      type: variable
      value: email_content
  next: log_sent
```

## Padrões de Controle de Fluxo

### Sequencial
```yaml
nodes:
  - id: step1
    opcode: io_print
    inputs:
      MESSAGE: {type: literal, value: "Step 1"}
    next: step2

  - id: step2
    opcode: io_print
    inputs:
      MESSAGE: {type: literal, value: "Step 2"}
    next: step3
```

### Condicional
```yaml
nodes:
  - id: check
    opcode: control_if
    inputs:
      CONDITION: {type: variable, value: is_valid}
    branches:
      THEN: valid_path
      ELSE: invalid_path
    next: null

  - id: valid_path
    opcode: io_print
    inputs:
      MESSAGE: {type: literal, value: "Valid!"}
    next: end

  - id: invalid_path
    opcode: io_print
    inputs:
      MESSAGE: {type: literal, value: "Invalid!"}
    next: end
```

### Loop
```yaml
nodes:
  - id: init_counter
    opcode: data_set_variable
    inputs:
      VARIABLE: {type: literal, value: "count"}
      VALUE: {type: literal, value: 0}
    next: loop_start

  - id: loop_start
    opcode: control_repeat
    inputs:
      TIMES: {type: literal, value: 5}
    branches:
      BODY: loop_body
    next: after_loop

  - id: loop_body
    opcode: data_change_variable_by
    inputs:
      VARIABLE: {type: literal, value: "count"}
      VALUE: {type: literal, value: 1}
    next: print_count

  - id: print_count
    opcode: io_print
    inputs:
      MESSAGE: {type: variable, value: count}
    next: null  # Retorna ao loop
```

## Variáveis e Escopo

### Declaração
Todas as variáveis devem ser declaradas no início do workflow:

```yaml
variables:
  - name: counter
    value: 0
  - name: result
    value: null
  - name: items
    value: []
  - name: config
    value: {enabled: true, timeout: 30}
```

### Tipos Suportados
- **Primitivos**: string, number, boolean, null
- **Complexos**: array, object
- **Dinâmicos**: any (tipo inferido em runtime)

## Debugging e Validação

### Checklist de Validação
- [ ] Todos os nodes têm IDs únicos
- [ ] Todos os nodes referenciados em `next` e `branches` existem
- [ ] Todas as variáveis usadas foram declaradas
- [ ] Todos os opcodes existem e têm inputs corretos
- [ ] Interface inputs/outputs correspondem ao uso no workflow
- [ ] Não há loops infinitos sem condição de saída

### Erros Comuns
1. **Node não encontrado**: next aponta para ID inexistente
2. **Variável não declarada**: Uso de variável não listada em `variables`
3. **Opcode inválido**: Opcode não existe no catálogo
4. **Input faltando**: Opcode requer input obrigatório não fornecido
5. **Tipo incompatível**: Valor não corresponde ao tipo esperado

## Extensões e Custom Opcodes

Para adicionar operações customizadas, consulte a documentação de extensões do LexFlow.

**Estrutura básica de custom opcode**:
```python
from lexflow.core import register_opcode

@register_opcode("custom_my_operation")
async def my_operation(inputs, context):
    # Lógica customizada
    param1 = inputs.get("PARAM1")
    result = process(param1)
    return result
```

## Recursos Adicionais

- **Repositório**: https://github.com/inspira-legal/lex-flow
- **Documentação completa**: Clonar repo e acessar `/docs`
- **Opcode Reference oficial**: Ver `/docs/opcodes.md` no repo
- **Grammar Reference**: Ver `/docs/grammar.md` no repo
- **Exemplos**: Ver `/examples` no repo

---

**NOTA**: Esta é uma referência baseada em documentação pública. Para lista completa e atualizada de opcodes, consulte o repositório oficial ou execute `lexflow --list-opcodes`.