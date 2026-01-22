# LexFlow Documentation

Welcome to the LexFlow documentation! This directory contains comprehensive guides for using and understanding LexFlow.

Before you keep reading keep in mind that LexFlow is still in early development and is not yet standardized. It means the language features are going to change and we do not guarantee backwards compatibility so expect braking changes in your workflows as we improve the language.

## Documentation Files

### LexFlow Web (Visual Editor)

**[LexFlow Web](../lexflow-web/README.md)** - Visual workflow editor and execution environment

- [Getting Started](../lexflow-web/docs/GETTING_STARTED.md) - Installation and setup
- [User Guide](../lexflow-web/docs/USER_GUIDE.md) - How to use the visual editor
- [Customization](../lexflow-web/docs/CUSTOMIZATION.md) - Custom backends and providers

### Getting Started

**[GETTING_STARTED.md](GETTING_STARTED.md)** - Installation and first steps

- Installing UV and dependencies
- Setting up your environment
- Running your first workflow
- Common CLI commands
- Development workflow
- Troubleshooting guide

### Core Language

**[GRAMMAR.md](GRAMMAR.md)** - Complete language specification

- Program and workflow structure
- Node types and execution model
- Input type system
- Control flow patterns (if/else, loops, try-catch)
- Variable scoping
- Complete syntax examples

### Feature Guides

**[EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md)** - Exception handling guide

- Try-catch-finally blocks
- Multiple catch handlers
- Exception types and matching
- Throwing exceptions
- Variable scope in catch blocks
- Best practices and patterns
- Complete working examples

**[OPCODE_REFERENCE.md](OPCODE_REFERENCE.md)** - Opcode quick reference

- All 75+ built-in opcodes
- Input/output operations
- Arithmetic, comparison, and logical operators
- Math operations
- String and list operations
- Dictionary and object operations
- AI operations (pydantic-ai integration)
- Exception opcodes
- Type conversions
- Usage examples

## Getting Started

### 0. Installation

Start with [GETTING_STARTED.md](GETTING_STARTED.md) to:

- Install UV and set up your environment
- Install dependencies and activate virtualenv
- Run your first workflow
- Learn common CLI commands

### 1. Learn the Basics

Then read [GRAMMAR.md](GRAMMAR.md) to understand:

- How workflows are structured
- Node chains and execution flow
- The input type system
- Basic control flow

### 2. Add Error Handling

Read [EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md) to learn:

- How to catch and handle exceptions
- Using try-catch-finally blocks
- Creating robust workflows
- Validation with assertions

### 3. Explore Opcodes

Check [OPCODE_REFERENCE.md](OPCODE_REFERENCE.md) for:

- Quick lookup of available operations
- Syntax examples for each opcode
- Understanding opcode parameters

## Quick Examples

### Hello World

```yaml
workflows:
  - name: main
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: print_hello
        inputs: {}

      print_hello:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Hello, World!\n"
```

### With Exception Handling

```yaml
workflows:
  - name: safe_operation
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: try_work
        inputs: {}

      try_work:
        opcode: control_try
        next: done
        inputs:
          TRY:
            branch: do_work
          CATCH1:
            exception_type: null
            var: "error"
            body:
              branch: handle_error

      do_work:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Working...\n"

      handle_error:
        opcode: io_print
        next: null
        inputs:
          STRING:
            variable: error

      done:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Complete!\n"
```

## LexFlow Web

For a visual approach to building workflows, use [LexFlow Web](../lexflow-web/README.md):

```bash
cd lexflow-web
uv run python -m lexflow_web.app
```

Open http://localhost:8000 to access the visual editor with:
- Drag-and-drop node creation
- Live code synchronization
- Real-time execution with streaming output

## Advanced Topics

### Custom Opcodes

You can extend LexFlow with custom opcodes:

```python
from lexflow import opcode


@opcode()
async def my_custom_opcode(x: int, y: int) -> int:
    """My custom operation."""
    return x * y + 42
```

See `example_custom_opcodes.py` for complete examples.

### Multi-File Workflows

Import workflows from other files:

```bash
lexflow main.yaml --include helpers.yaml utils.yaml
```

All workflows from included files become callable.

### Debugging

Use verbose mode for detailed execution info:

```bash
lexflow workflow.yaml --verbose
```

## Example Programs

Check the `programs/` and `examples/` directories for:

- `example_exception_handling.yaml` - Exception handling patterns
- `test_try_catch_*.yaml` - Exception handling tests
- `test_loop_*.yaml` - Loop examples
- `test_conditionals_*.yaml` - Conditional logic
- `example_custom_opcodes.py` - Custom opcode examples

## Architecture

LexFlow uses a clean, layered architecture:

```
Parser → AST → Executor
         ↓
    Opcodes (Plugins)
```

1. **Parser** - Converts JSON/YAML to Abstract Syntax Tree
2. **AST** - Tree-structured representation of workflow
3. **Executor** - Async tree-walk interpreter
4. **Opcodes** - Pluggable operation system

## Contributing

### Adding Documentation

- Keep examples concise and clear
- Include both JSON and YAML versions when helpful
- Add real-world use cases
- Cross-reference between docs

### Documentation Style

- Use clear headers and sections
- Provide code examples for concepts
- Include "what not to do" examples
- Add troubleshooting sections

## Support

For questions, issues, or contributions:

- Talk to me on slack
- Check the documentation
- Look at example programs

