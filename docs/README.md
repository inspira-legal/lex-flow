# LexFlow Documentation

Welcome to the LexFlow documentation! This directory contains comprehensive guides for using and understanding LexFlow.

## Documentation Files

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

### 1. Learn the Basics

Start with [GRAMMAR.md](GRAMMAR.md) to understand:

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

## Language Features

### Core Features

✅ Visual node-based workflows
✅ Stack-based execution model
✅ Async-native operation
✅ Variable scoping
✅ Workflow calls (functions)
✅ JSON and YAML support

### Control Flow

✅ Sequential execution
✅ If/else conditionals
✅ While loops
✅ Try-catch-finally
✅ Workflow returns

### Data Types

✅ Numbers (int, float)
✅ Strings
✅ Booleans
✅ Lists
✅ Dictionaries

### Operations

✅ 75+ built-in opcodes
✅ Arithmetic operations
✅ Comparison and logic
✅ String manipulation
✅ List operations
✅ Dictionary operations
✅ Object operations
✅ AI operations (pydantic-ai)
✅ Exception handling
✅ Custom opcode support

## Advanced Topics

### Custom Opcodes

You can extend LexFlow with custom opcodes:

```python
from lexflow.opcodes import OpcodeRegistry

registry = OpcodeRegistry()

@registry.register()
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

- Check the documentation first
- Look at example programs
- Search existing issues
- Create detailed bug reports

## Version History

### Current Version (MVP)

- ✅ Exception handling (try-catch-finally)
- ✅ 75+ built-in opcodes
- ✅ Dictionary and object operations
- ✅ AI integration (Google Vertex AI via pydantic-ai)
- ✅ Workflow input parameters
- ✅ Output redirection and capture
- ✅ Workflow calls on reporter nodes
- ✅ JSON and YAML support
- ✅ Multi-file workflows
- ✅ Async-native execution
- ✅ Type-hinted opcodes with introspection

## License

See the main project LICENSE file.
