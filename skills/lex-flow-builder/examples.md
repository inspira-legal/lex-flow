# LexFlow Workflow Examples

## Template 1: Hello World Básico

```yaml
name: "hello-world"
interface:
  inputs: []
  outputs: []

variables: []

nodes:
  - id: start
    opcode: io_print
    inputs:
      MESSAGE:
        type: literal
        value: "Hello from LexFlow!"
    next: null
```

**Uso**: Workflow mínimo para testar instalação.

---

## Template 2: Input/Output Simples

```yaml
name: "greeter"
interface:
  inputs:
    - name: user_name
      type: string
  outputs:
    - name: greeting
      type: string

variables:
  - name: formatted_greeting
    value: ""

nodes:
  - id: create_greeting
    opcode: string_concat
    inputs:
      STRING1:
        type: literal
        value: "Hello, "
      STRING2:
        type: variable
        value: user_name
    next: add_suffix

  - id: add_suffix
    opcode: string_concat
    inputs:
      STRING1:
        type: variable
        value: formatted_greeting
      STRING2:
        type: literal
        value: "! Welcome to LexFlow."
    next: set_output

  - id: set_output
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "greeting"
      VALUE:
        type: variable
        value: formatted_greeting
    next: print_result

  - id: print_result
    opcode: io_print
    inputs:
      MESSAGE:
        type: variable
        value: formatted_greeting
    next: null
```

**Uso**: Recebe nome do usuário e retorna saudação formatada.

---

## Template 3: Loop Contador

```yaml
name: "counter-loop"
interface:
  inputs:
    - name: max_count
      type: number
  outputs:
    - name: final_count
      type: number

variables:
  - name: counter
    value: 0

nodes:
  - id: start_loop
    opcode: control_repeat
    inputs:
      TIMES:
        type: variable
        value: max_count
    branches:
      BODY: increment_counter
    next: output_result

  - id: increment_counter
    opcode: data_change_variable_by
    inputs:
      VARIABLE:
        type: literal
        value: "counter"
      VALUE:
        type: literal
        value: 1
    next: print_current

  - id: print_current
    opcode: io_print
    inputs:
      MESSAGE:
        type: variable
        value: counter
    next: null  # Retorna ao loop

  - id: output_result
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "final_count"
      VALUE:
        type: variable
        value: counter
    next: null
```

**Uso**: Conta de 1 até N, imprimindo cada número.

---

## Template 4: Condicional If/Else

```yaml
name: "age-classifier"
interface:
  inputs:
    - name: age
      type: number
  outputs:
    - name: classification
      type: string

variables:
  - name: is_adult
    value: false
  - name: result
    value: ""

nodes:
  - id: check_age
    opcode: math_gte
    inputs:
      NUM1:
        type: variable
        value: age
      NUM2:
        type: literal
        value: 18
    next: decide_classification

  - id: decide_classification
    opcode: control_if
    inputs:
      CONDITION:
        type: variable
        value: is_adult
    branches:
      THEN: classify_adult
      ELSE: classify_minor
    next: null

  - id: classify_adult
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "result"
      VALUE:
        type: literal
        value: "Adult"
    next: output_classification

  - id: classify_minor
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "result"
      VALUE:
        type: literal
        value: "Minor"
    next: output_classification

  - id: output_classification
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "classification"
      VALUE:
        type: variable
        value: result
    next: null
```

**Uso**: Classifica idade como "Adult" ou "Minor".

---

## Template 5: Processamento de Lista

```yaml
name: "list-processor"
interface:
  inputs:
    - name: items
      type: array
  outputs:
    - name: processed_count
      type: number

variables:
  - name: item_count
    value: 0
  - name: current_item
    value: null

nodes:
  - id: get_list_length
    opcode: list_length
    inputs:
      LIST:
        type: variable
        value: items
    next: store_count

  - id: store_count
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "item_count"
      VALUE:
        type: computed
        value: previous_result
    next: process_loop

  - id: process_loop
    opcode: control_repeat
    inputs:
      TIMES:
        type: variable
        value: item_count
    branches:
      BODY: get_item
    next: output_count

  - id: get_item
    opcode: list_get
    inputs:
      LIST:
        type: variable
        value: items
      INDEX:
        type: variable
        value: loop_index
    next: print_item

  - id: print_item
    opcode: io_print
    inputs:
      MESSAGE:
        type: variable
        value: current_item
    next: null

  - id: output_count
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "processed_count"
      VALUE:
        type: variable
        value: item_count
    next: null
```

**Uso**: Itera sobre lista e processa cada item.

---

## Template 6: Calculadora Simples

```yaml
name: "calculator"
interface:
  inputs:
    - name: num1
      type: number
    - name: num2
      type: number
    - name: operation
      type: string
  outputs:
    - name: result
      type: number

variables:
  - name: calculated_result
    value: 0

nodes:
  - id: check_operation
    opcode: string_equals
    inputs:
      STRING1:
        type: variable
        value: operation
      STRING2:
        type: literal
        value: "add"
    next: decide_operation

  - id: decide_operation
    opcode: control_if
    inputs:
      CONDITION:
        type: computed
        value: previous_result
    branches:
      THEN: do_addition
      ELSE: check_subtraction
    next: null

  - id: do_addition
    opcode: math_add
    inputs:
      NUM1:
        type: variable
        value: num1
      NUM2:
        type: variable
        value: num2
    next: store_result

  - id: check_subtraction
    opcode: string_equals
    inputs:
      STRING1:
        type: variable
        value: operation
      STRING2:
        type: literal
        value: "subtract"
    next: decide_subtraction

  - id: decide_subtraction
    opcode: control_if
    inputs:
      CONDITION:
        type: computed
        value: previous_result
    branches:
      THEN: do_subtraction
      ELSE: check_multiplication
    next: null

  - id: do_subtraction
    opcode: math_subtract
    inputs:
      NUM1:
        type: variable
        value: num1
      NUM2:
        type: variable
        value: num2
    next: store_result

  - id: check_multiplication
    opcode: string_equals
    inputs:
      STRING1:
        type: variable
        value: operation
      STRING2:
        type: literal
        value: "multiply"
    next: decide_multiplication

  - id: decide_multiplication
    opcode: control_if
    inputs:
      CONDITION:
        type: computed
        value: previous_result
    branches:
      THEN: do_multiplication
      ELSE: do_division
    next: null

  - id: do_multiplication
    opcode: math_multiply
    inputs:
      NUM1:
        type: variable
        value: num1
      NUM2:
        type: variable
        value: num2
    next: store_result

  - id: do_division
    opcode: math_divide
    inputs:
      NUM1:
        type: variable
        value: num1
      NUM2:
        type: variable
        value: num2
    next: store_result

  - id: store_result
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "calculated_result"
      VALUE:
        type: computed
        value: previous_result
    next: output_result

  - id: output_result
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "result"
      VALUE:
        type: variable
        value: calculated_result
    next: null
```

**Uso**: Calculadora com 4 operações básicas (add, subtract, multiply, divide).

---

## Template 7: Validação com Retry

```yaml
name: "validator-with-retry"
interface:
  inputs:
    - name: value_to_validate
      type: string
  outputs:
    - name: is_valid
      type: boolean
    - name: attempts
      type: number

variables:
  - name: retry_count
    value: 0
  - name: max_retries
    value: 3
  - name: validation_passed
    value: false

nodes:
  - id: start_validation
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "retry_count"
      VALUE:
        type: literal
        value: 0
    next: validation_loop

  - id: validation_loop
    opcode: control_repeat
    inputs:
      TIMES:
        type: variable
        value: max_retries
    branches:
      BODY: perform_validation
    next: output_results

  - id: perform_validation
    opcode: string_length
    inputs:
      STRING:
        type: variable
        value: value_to_validate
    next: check_length

  - id: check_length
    opcode: math_gte
    inputs:
      NUM1:
        type: computed
        value: previous_result
      NUM2:
        type: literal
        value: 5
    next: decide_validity

  - id: decide_validity
    opcode: control_if
    inputs:
      CONDITION:
        type: computed
        value: previous_result
    branches:
      THEN: mark_valid
      ELSE: increment_retry
    next: null

  - id: mark_valid
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "validation_passed"
      VALUE:
        type: literal
        value: true
    next: break_loop

  - id: increment_retry
    opcode: data_change_variable_by
    inputs:
      VARIABLE:
        type: literal
        value: "retry_count"
      VALUE:
        type: literal
        value: 1
    next: print_retry

  - id: print_retry
    opcode: io_print
    inputs:
      MESSAGE:
        type: literal
        value: "Validation failed, retrying..."
    next: null

  - id: break_loop
    opcode: control_break
    inputs: {}
    next: null

  - id: output_results
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "is_valid"
      VALUE:
        type: variable
        value: validation_passed
    next: output_attempts

  - id: output_attempts
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "attempts"
      VALUE:
        type: variable
        value: retry_count
    next: null
```

**Uso**: Valida entrada com até 3 tentativas, retornando status e número de tentativas.

---

## Template 8: API Mock Request

```yaml
name: "api-request-mock"
interface:
  inputs:
    - name: endpoint
      type: string
    - name: method
      type: string
  outputs:
    - name: response
      type: object
    - name: status_code
      type: number

variables:
  - name: request_data
    value: {}
  - name: response_data
    value: {}
  - name: status
    value: 200

nodes:
  - id: prepare_request
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "request_data"
      VALUE:
        type: object
        value:
          url: "{endpoint}"
          method: "{method}"
    next: simulate_request

  - id: simulate_request
    opcode: control_wait
    inputs:
      DURATION:
        type: literal
        value: 1
    next: mock_response

  - id: mock_response
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "response_data"
      VALUE:
        type: object
        value:
          success: true
          data: "Mock response"
          timestamp: "2024-01-01T00:00:00Z"
    next: set_status

  - id: set_status
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "status"
      VALUE:
        type: literal
        value: 200
    next: output_response

  - id: output_response
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "response"
      VALUE:
        type: variable
        value: response_data
    next: output_status

  - id: output_status
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "status_code"
      VALUE:
        type: variable
        value: status
    next: null
```

**Uso**: Simula requisição HTTP com resposta mockada.

---

## Template 9: Data Pipeline

```yaml
name: "data-pipeline"
interface:
  inputs:
    - name: raw_data
      type: array
  outputs:
    - name: processed_data
      type: array
    - name: stats
      type: object

variables:
  - name: cleaned_data
    value: []
  - name: filtered_data
    value: []
  - name: final_data
    value: []
  - name: record_count
    value: 0

nodes:
  - id: stage1_clean
    opcode: custom_clean_data
    inputs:
      DATA:
        type: variable
        value: raw_data
    next: store_cleaned

  - id: store_cleaned
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "cleaned_data"
      VALUE:
        type: computed
        value: previous_result
    next: stage2_filter

  - id: stage2_filter
    opcode: custom_filter_data
    inputs:
      DATA:
        type: variable
        value: cleaned_data
      CRITERIA:
        type: object
        value: {status: "active"}
    next: store_filtered

  - id: store_filtered
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "filtered_data"
      VALUE:
        type: computed
        value: previous_result
    next: stage3_transform

  - id: stage3_transform
    opcode: custom_transform_data
    inputs:
      DATA:
        type: variable
        value: filtered_data
    next: store_final

  - id: store_final
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "final_data"
      VALUE:
        type: computed
        value: previous_result
    next: calculate_stats

  - id: calculate_stats
    opcode: list_length
    inputs:
      LIST:
        type: variable
        value: final_data
    next: store_count

  - id: store_count
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "record_count"
      VALUE:
        type: computed
        value: previous_result
    next: output_data

  - id: output_data
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "processed_data"
      VALUE:
        type: variable
        value: final_data
    next: output_stats

  - id: output_stats
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "stats"
      VALUE:
        type: object
        value:
          total_records: "{record_count}"
          pipeline_stages: 3
    next: null
```

**Uso**: Pipeline de processamento de dados com múltiplas etapas (clean → filter → transform).

---

## Template 10: Error Handling

```yaml
name: "safe-processor"
interface:
  inputs:
    - name: data
      type: any
  outputs:
    - name: result
      type: any
    - name: error
      type: string

variables:
  - name: processing_result
    value: null
  - name: error_message
    value: ""
  - name: has_error
    value: false

nodes:
  - id: try_process
    opcode: control_try
    inputs: {}
    branches:
      TRY: process_data
      CATCH: handle_error
    next: output_results

  - id: process_data
    opcode: custom_risky_operation
    inputs:
      DATA:
        type: variable
        value: data
    next: store_success

  - id: store_success
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "processing_result"
      VALUE:
        type: computed
        value: previous_result
    next: null

  - id: handle_error
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "has_error"
      VALUE:
        type: literal
        value: true
    next: store_error_message

  - id: store_error_message
    opcode: data_set_variable
    inputs:
      VARIABLE:
        type: literal
        value: "error_message"
      VALUE:
        type: computed
        value: error_description
    next: log_error

  - id: log_error
    opcode: io_print
    inputs:
      MESSAGE:
        type: variable
        value: error_message
    next: null

  - id: output_results
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "result"
      VALUE:
        type: variable
        value: processing_result
    next: output_error

  - id: output_error
    opcode: io_output
    inputs:
      OUTPUT_NAME:
        type: literal
        value: "error"
      VALUE:
        type: variable
        value: error_message
    next: null
```

**Uso**: Executa operação com try/catch, capturando erros de forma segura.

---

## Padrões de Composição

### Subworkflows (Modular)

```yaml
name: "main-workflow"
nodes:
  - id: call_subworkflow
    opcode: workflow_execute
    inputs:
      WORKFLOW_NAME:
        type: literal
        value: "helper-workflow"
      INPUTS:
        type: object
        value:
          param1: "value1"
    next: process_subresult
```

### Parallel Execution (se suportado)

```yaml
name: "parallel-tasks"
nodes:
  - id: fork_parallel
    opcode: control_parallel
    branches:
      BRANCH1: task1
      BRANCH2: task2
      BRANCH3: task3
    next: join_results

  - id: join_results
    opcode: data_merge_results
    inputs:
      RESULTS:
        type: array
        value: [task1_result, task2_result, task3_result]
    next: output
```

---

## Boas Práticas de Nomenclatura

```yaml
# IDs descritivos
- id: fetch_user_data          # BOM
- id: node1                     # RUIM

# Variáveis claras
- name: user_authentication_token  # BOM
- name: temp                       # RUIM

# Inputs explícitos
MESSAGE: {type: literal, value: "User logged in"}  # BOM
MSG: {type: literal, value: "ok"}                  # RUIM
```

---

## Como Usar os Templates

1. **Copie o template** mais próximo do seu caso de uso
2. **Adapte os inputs/outputs** conforme necessário
3. **Modifique os nodes** para sua lógica específica
4. **Teste localmente** com lexflow-cli
5. **Itere e refine** baseado nos resultados

Para mais exemplos, visite: https://github.com/inspira-legal/lex-flow/tree/main/examples