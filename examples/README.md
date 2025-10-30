# LexFlow Examples

This directory contains organized examples demonstrating LexFlow's features and capabilities.

## Directory Structure

### 📚 basics/
Fundamental examples to get started with LexFlow.

- `hello_world.yaml` / `hello_world.json` - Simple "Hello, World!" program
- `cli_inputs.yaml` - Using command-line inputs with workflows

**Run examples:**
```bash
lexflow examples/basics/hello_world.yaml
lexflow examples/basics/cli_inputs.yaml --input name=Alice --input age=30
```

### 🔀 control_flow/
Examples demonstrating conditional logic and loops.

- `conditionals.yaml` - If/else statements
- `loops_for.yaml` - For loops with range
- `loops_foreach.yaml` - ForEach loops over collections
- `loops_while.json` - While loops

**Run examples:**
```bash
lexflow examples/control_flow/conditionals.yaml
lexflow examples/control_flow/loops_for.yaml
```

### ⚠️ exception_handling/
Exception handling patterns and best practices.

- `comprehensive_examples.yaml` - Complete guide with multiple patterns
- `basic_try_catch.yaml` - Simple try-catch blocks
- `multiple_handlers.yaml` - Multiple exception types
- `finally_blocks.yaml` - Try-catch-finally patterns
- `catch_variables.yaml` - Binding exception messages to variables
- `catch_variables_advanced.yaml` - Advanced variable binding
- `throwing_errors.yaml` - Throwing custom errors

**Run examples:**
```bash
lexflow examples/exception_handling/comprehensive_examples.yaml
lexflow examples/exception_handling/basic_try_catch.yaml
```

### 📦 data_structures/
Working with dictionaries, objects, and lists.

- `dictionaries.yaml` - Dictionary operations (create, get, set, update)
- `objects.yaml` - Object operations (get, set, has, remove)
- `dicts_and_objects.yaml` - Simple examples of both

**Run examples:**
```bash
lexflow examples/data_structures/dictionaries.yaml
lexflow examples/data_structures/objects.yaml
```

### 📂 multi_file/
Multi-file workflow organization.

- `main.yaml` - Main workflow that calls external workflows
- `helpers.yaml` - Helper workflows
- `more_helpers.json` - Additional helpers

**Run example:**
```bash
lexflow examples/multi_file/main.yaml --include examples/multi_file/helpers.yaml examples/multi_file/more_helpers.json
```

### 🔌 integrations/
Integration examples for extending LexFlow.

#### integrations/pydantic_ai/
AI integration using pydantic-ai with Google Vertex AI.

- `vertex_ai_example.yaml` - Complete AI workflow example

**Requirements:**
```bash
uv sync --extra ai
gcloud auth application-default login
```

**Run example:**
```bash
lexflow examples/integrations/pydantic_ai/vertex_ai_example.yaml
```

#### integrations/pygame/
Pygame integration for game development and graphics.

- `hello.yaml` - Simple pygame window
- `simple.yaml` - Basic pygame workflow
- `wave_animation.yaml` - Animated wave pattern
- `custom_opcodes.py` - Custom pygame opcodes
- `run_hello.py` - Python runner for hello example
- `run_wave.py` - Python runner for wave animation

**Requirements:**
```bash
uv sync --extra pygame
```

**Run examples:**
```bash
python examples/integrations/pygame/run_hello.py
python examples/integrations/pygame/run_wave.py
```

#### integrations/custom_opcodes/
Examples of extending LexFlow with custom operations.

- `basics.py` - Creating custom opcodes
- `metrics_usage.py` - Using the metrics system

**Run examples:**
```bash
python examples/integrations/custom_opcodes/basics.py
python examples/integrations/custom_opcodes/metrics_usage.py
```

## Quick Start

### 1. Start Simple
```bash
lexflow examples/basics/hello_world.yaml
```

### 2. Try Inputs
```bash
lexflow examples/basics/cli_inputs.yaml --input name=YourName --input age=25
```

### 3. Explore Control Flow
```bash
lexflow examples/control_flow/loops_for.yaml
```

### 4. Learn Exception Handling
```bash
lexflow examples/exception_handling/comprehensive_examples.yaml
```

### 5. Work with Data
```bash
lexflow examples/data_structures/dictionaries.yaml
```

## Learning Path

1. **Basics** → Start here to understand workflow structure
2. **Control Flow** → Learn conditional logic and loops
3. **Data Structures** → Work with collections
4. **Exception Handling** → Build robust workflows
5. **Multi-File** → Organize large projects
6. **Integrations** → Extend LexFlow with custom features

## Tips

- Use `--verbose` flag to see execution details
- Use `--validate-only` to check syntax without running
- Use `--metrics` to see performance statistics
- Check `docs/` for detailed language documentation

## More Resources

- [Getting Started Guide](../docs/GETTING_STARTED.md) - Installation and setup
- [Grammar Reference](../docs/GRAMMAR.md) - Complete language specification
- [Opcode Reference](../docs/OPCODE_REFERENCE.md) - All available operations
- [Exception Handling Guide](../docs/EXCEPTION_HANDLING.md) - Detailed exception patterns

---

**Note:** Test-focused files have been moved to `tests/integration/` to keep examples clean and user-focused.
