# Lex Flow Documentation

Comprehensive documentation for the Lex Flow visual programming workflow interpreter.

## Quick Start

1. **Install dependencies**: `uv sync`
2. **Run a workflow**: `uv run lexflow tests/integration/simple_hello.json`
3. **Test the system**: `uv run pytest`

## Documentation Index

### For Users & Developers

#### [CLI Usage Guide](docs/cli-usage.md)

How to use the command-line interface to run workflows, import files, and debug execution.

- Basic execution commands
- Import system with `-I` flag and `--import-dir`
- Debug mode and verbose output
- Error handling and validation
- Multi-file project structure

#### [Language Grammar](docs/language-grammar.md)

Complete specification of the JSON workflow format and language features.

- JSON workflow structure
- Node definitions and execution flow
- Input types (literal, variable, node reference, etc.)
- Variable system and scoping
- Workflow interfaces and reusability
- Validation rules and best practices

### For Developers & Contributors

#### [Core Architecture](docs/core-architecture.md)

Deep dive into how the interpreter works internally.

- Multi-layered architecture (Loader → Parser → Engine)
- Dual model system (Legacy + AST models)
- Stack-based execution engine
- WorkflowState and call frame management
- Plugin architecture and extension points

#### [Opcode Development Guide](docs/opcode-development.md)

How to create custom opcodes and extend the interpreter.

- Modern `@params` decorator system with type annotations
- Parameter resolution and stack management
- Helper method patterns
- Return value handling
- File organization and testing
- Interface introspection for tooling

#### [Testing & Examples](docs/testing-examples.md)

Testing framework, example workflows, and debugging techniques.

- Automated test runner and validation
- Creating comprehensive test suites
- Example workflows from simple to complex
- Multi-file project examples
- Debug mode and verbose execution
- Best practices for development

## Architecture Overview

```
CLI Interface (lexflow-cli)
        ↓
WorkflowLoader (loads & validates JSON/YAML with dependency resolution)
        ↓
Preprocessor (normalizes input formats with comprehensive validation)
        ↓
Legacy Models (Pydantic JSON parsing with Python 3.9+ compatibility)
        ↓
Parser (transforms to executable format with branch/reporter discovery)
        ↓
AST Models (runtime execution format with pre-parsed components)
        ↓
Engine (stack-based async executor with return-based control flow)
        ↓
WorkflowState (execution context with stack safety and bounds checking)
        ↓
Opcode Registry (modern @params() validated operations with enhanced discovery)
```

## Key Features

- **JSON/YAML workflows** - Human-readable, tooling-friendly formats
- **Multiple input syntaxes** - Numeric, keyword, and object notation for better readability
- **Stack-based execution** - Efficient, composable operation model with safety checks
- **Async-first design** - Natural support for I/O and long-running tasks
- **Modern plugin architecture** - 89% of opcodes use type-safe @params() validation
- **Multi-file projects** - Import system for modular workflows with dependency resolution
- **Type-safe parameters** - Modern @params() system with introspection and early validation
- **Comprehensive testing** - Automated validation and examples
- **Enhanced error handling** - Clear error messages with examples and suggestions
- **Robust preprocessing** - Input format normalization with validation (replaces silent failures)
- **Performance optimizations** - Pre-parsed branches and reporters eliminate runtime parsing
- **Python 3.9+ compatibility** - Union syntax compatibility for broader deployment
- **Consistent architecture** - Eliminated code duplication and manual node reconstruction

## Common Use Cases

### Simple Script Execution

```bash
uv run lexflow script.json
uv run lexflow workflow.yaml  # YAML supported too
```

### Multi-File Projects

```bash
uv run lexflow main.json -I utils.json helpers.json
uv run lexflow main.yaml --import-dir modules/
```

### Development & Debugging

```bash
uv run lexflow workflow.json --debug --verbose
```

### Validation & Testing

```bash
uv run lexflow workflow.json --validate-only
uv run pytest
```

### Modern Input Syntax Examples

**Legacy Numeric Format:**

```json
"inputs": {
  "STRING": [1, "Hello"],
  "VALUE": [2, "calculate_node"],
  "VAR": [3, "1"]
}
```

**Keyword Array Format:**

```json
"inputs": {
  "STRING": ["literal", "Hello"],
  "VALUE": ["node", "calculate_node"],
  "VAR": ["variable", "1"]
}
```

**Object Format (Recommended):**

```json
"inputs": {
  "STRING": {"literal": "Hello"},
  "VALUE": {"node": "calculate_node"},
  "VAR": {"variable": "1"}
}
```

All formats are equivalent and can be mixed in the same workflow.

## Getting Help

- **CLI Help**: `uv run lexflow --help`
- **Test Examples**: Browse `tests/` directory for working examples
- **Error Messages**: Include contextual suggestions and fixes
- **Verbose Mode**: Use `--verbose` to understand execution flow
- **Debug Mode**: Use `--debug` for step-by-step troubleshooting

## Contributing

1. Read the architecture documentation to understand the system
2. Create tests for new functionality using the testing framework
3. Follow the opcode development guide for adding operations
4. Use the CLI patterns for consistent user experience
5. Update documentation when adding features

The modular architecture makes it easy to extend Lex Flow with new opcodes, file formats, or execution models while maintaining backward compatibility.
