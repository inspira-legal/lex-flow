# LexFlow Opcode Reference

Quick reference for all available opcodes in LexFlow.

## I/O Operations

### `io_print(*values)`

Print values to stdout (or configured output buffer).

```yaml
opcode: io_print
inputs:
  STRING: { literal: "Hello World\n" }
```

**Note:** Output can be redirected using the Engine's `output` parameter. See [Output Redirection](#output-redirection) below.

### `io_input(prompt="")`

Get input from user with optional prompt.

```yaml
opcode: io_input
inputs:
  prompt: { literal: "Enter name: " }
```

## Arithmetic Operators

### `operator_add(left, right)`

Add two values (numeric or string concatenation).

### `operator_subtract(left, right)`

Subtract right from left.

### `operator_multiply(left, right)`

Multiply two values.

### `operator_divide(left, right)`

Integer division.

### `operator_modulo(left, right)` ⭐ NEW

Modulo operation (remainder).

```yaml
opcode: operator_modulo
inputs:
  left: { literal: 10 }
  right: { literal: 3 }
# Returns: 1
```

## Comparison Operators

### `operator_equals(left, right)`

Check equality (with type coercion for numbers).

### `operator_not_equals(left, right)`

Check inequality.

### `operator_less_than(left, right)`

Check if left < right.

### `operator_greater_than(left, right)`

Check if left > right.

### `operator_less_than_or_equals(left, right)`

Check if left <= right.

### `operator_greater_than_or_equals(left, right)`

Check if left >= right.

## Logical Operators ⭐ NEW

### `operator_and(left, right)`

Logical AND.

```yaml
opcode: operator_and
inputs:
  left: { literal: true }
  right: { literal: false }
# Returns: false
```

### `operator_or(left, right)`

Logical OR.

### `operator_not(value)`

Logical NOT.

## Math Operations

### `math_random(min_val, max_val)`

Generate random integer between min and max (inclusive).

### `math_abs(value)` ⭐ NEW

Absolute value.

### `math_pow(base, exponent)` ⭐ NEW

Power operation.

```yaml
opcode: math_pow
inputs:
  base: { literal: 2 }
  exponent: { literal: 8 }
# Returns: 256
```

### `math_sqrt(value)` ⭐ NEW

Square root.

### `math_floor(value)` ⭐ NEW

Floor operation.

### `math_ceil(value)` ⭐ NEW

Ceiling operation.

## String Operations ⭐ NEW

### `string_length(text)`

Get string length.

### `string_upper(text)`

Convert to uppercase.

```yaml
opcode: string_upper
inputs:
  text: { variable: my_text }
```

### `string_lower(text)`

Convert to lowercase.

### `string_trim(text)`

Remove leading/trailing whitespace.

### `string_split(text, delimiter=" ")`

Split string by delimiter (default: space).

```yaml
opcode: string_split
inputs:
  text: { literal: "a,b,c" }
  delimiter: { literal: "," }
# Returns: ["a", "b", "c"]
```

### `string_join(items, delimiter="")`

Join list items into string.

### `string_contains(text, substring)`

Check if string contains substring.

### `string_replace(text, old, new)`

Replace all occurrences of old with new.

## List Operations ⭐ NEW

### `list_length(items)`

Get list length.

### `list_get(items, index)`

Get item at index.

### `list_append(items, value)`

Append value to list (returns new list).

### `list_contains(items, value)`

Check if list contains value.

### `list_range(start, stop=None, step=1)`

Create a range as list.

```yaml
opcode: list_range
inputs:
  start: { literal: 1 }
  stop: { literal: 10 }
  step: { literal: 2 }
# Returns: [1, 3, 5, 7, 9]
```

## Type Conversions

### `str(value)`

Convert to string.

### `int(value)`

Convert to integer.

### `float(value)`

Convert to float.

### `bool(value)`

Convert to boolean.

### `len(value)`

Get length of a value.

### `range(*args)`

Create a range as list (variadic).

## Exception Operations ⭐ NEW

### `throw(message)`

Throw a runtime error with custom message.

```yaml
opcode: throw
inputs:
  message: { literal: "Something went wrong" }
```

### `throw_value_error(message)`

Throw a ValueError.

```yaml
opcode: throw_value_error
inputs:
  message: { literal: "Invalid input provided" }
```

### `throw_type_error(message)`

Throw a TypeError.

```yaml
opcode: throw_type_error
inputs:
  message: { literal: "Wrong type used" }
```

### `throw_assertion_error(message)`

Throw an AssertionError.

```yaml
opcode: throw_assertion_error
inputs:
  message: { literal: "Assertion failed" }
```

### `assert_true(condition, message="Assertion failed")`

Assert condition is true, throw AssertionError otherwise.

```yaml
opcode: assert_true
inputs:
  condition: { node: check_valid }
  message: { literal: "Validation failed" }
```

### `assert_equals(left, right, message="Values not equal")`

Assert two values are equal.

```yaml
opcode: assert_equals
inputs:
  left: { variable: expected }
  right: { variable: actual }
  message: { literal: "Values don't match" }
```

**Note:** For structured exception handling (try-catch-finally), use `control_try` opcode. See [EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md) for details.

## Workflow Operations

### `workflow_start()`

Workflow entry point marker (no-op).

### `noop()`

No operation.

---

## Legend

⭐ NEW - Opcodes added in recent updates

## Total Count

**52 opcodes** available (32 newly added)

## Usage in Workflows

All opcodes can be used in two ways:

1. **As statements** (OpStmt):

```yaml
node_name:
  opcode: io_print
  next: next_node
  inputs:
    STRING: { literal: "Hello" }
```

2. **As expressions** (reporter nodes):

```yaml
reporter_node:
  opcode: operator_add
  inputs:
    left: { literal: 5 }
    right: { literal: 3 }
  isReporter: true

# Reference in another node:
another_node:
  opcode: io_print
  inputs:
    STRING: { node: reporter_node }
```

## Output Redirection

LexFlow supports redirecting workflow output using Python's built-in `redirect_stdout`. This is useful for capturing output in APIs, tests, or logging.

### Basic Usage

```python
import io
from lexflow import Parser, Engine

# Capture output to string
output_buffer = io.StringIO()
engine = Engine(program, output=output_buffer)
await engine.run()

captured_output = output_buffer.getvalue()
print(f"Captured: {captured_output}")
```

### CLI Usage

```bash
# Redirect to file
lexflow workflow.yaml --output-file output.txt

# Verbose mode still prints to stderr
lexflow workflow.yaml --output-file output.txt --verbose
```

### Use Cases

**1. FastAPI Integration - Capture Output**

```python
from fastapi import FastAPI
import io

@app.post("/run-workflow")
async def run_workflow(workflow_data: dict):
    program = parser.parse(workflow_data)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)
    result = await engine.run()

    return {
        "result": result,
        "output": output_buffer.getvalue()
    }
```

**2. Testing - Assert Output**

```python
import io
import pytest

async def test_hello_world():
    output = io.StringIO()
    engine = Engine(program, output=output)
    await engine.run()

    assert "Hello, World!" in output.getvalue()
```

**3. File Logging**

```python
# Log to file
with open('workflow.log', 'w') as log_file:
    engine = Engine(program, output=log_file)
    await engine.run()
```

**4. Multiple Outputs (Tee)**

```python
from lexflow.output import TeeOutput
import sys

# Write to both stdout and file
with open('workflow.log', 'w') as f:
    tee = TeeOutput(sys.stdout, f)
    engine = Engine(program, output=tee)
    await engine.run()
```

**5. Streaming (WebSocket/SSE)**

```python
from lexflow.output import StreamingOutput

async def send_to_client(line):
    await websocket.send(line)

stream = StreamingOutput(send_to_client)
engine = Engine(program, output=stream)
await engine.run()
stream.flush()
```

**6. Context Manager**

```python
from lexflow.output import OutputCapture

with OutputCapture() as capture:
    engine = Engine(program)
    await engine.run()
    output = capture.get_output()
```

### Output Utilities

**OutputCapture** - Context manager for simple capture:
```python
from lexflow.output import OutputCapture

with OutputCapture() as capture:
    # Your code here
    output = capture.get_output()
```

**TeeOutput** - Write to multiple destinations:
```python
from lexflow.output import TeeOutput

tee = TeeOutput(sys.stdout, file_handle, string_io)
engine = Engine(program, output=tee)
```

**StreamingOutput** - Stream to callback:
```python
from lexflow.output import StreamingOutput

stream = StreamingOutput(callback_function)
engine = Engine(program, output=stream)
```

## Adding Custom Opcodes

See `example_custom_opcodes.py` for complete examples.

```python
from lexflow.opcodes import OpcodeRegistry

registry = OpcodeRegistry()

@registry.register()
async def my_opcode(x: int, y: int = 10) -> int:
    """My custom opcode with optional parameter."""
    return x + y
```
