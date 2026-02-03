# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LexFlow is a stack-based visual programming workflow interpreter written in Python. It parses JSON/YAML workflow definitions into an AST and executes them using an async engine with support for control flow, exception handling, and extensible opcodes.

**Monorepo Structure:**
- `lexflow-core/` - Core engine and runtime
- `lexflow-cli/` - Command-line interface tool
- `lexflow-web/` - Web frontend for visualization and execution
- Root `pyproject.toml` - Combined package configuration

## Developing Workflows and Opcodes

**Documentation References:**
- **Workflow Grammar**: See `docs/GRAMMAR_REFERENCE.md` for the complete workflow syntax and structure
- **Opcode Reference**: See `docs/OPCODE_REFERENCE.md` for all available opcodes and their signatures
- **Core Module Guide**: See `lexflow-core/CLAUDE.md` for architecture, best practices, and common mistakes

**Specialized Agents:**
When developing LexFlow workflows or opcodes, use the specialized Claude Code agents:

- **lexflow-workflow-writer**: Use this agent when creating, writing, or designing LexFlow workflow files. Invoke it for building new workflows, converting logic into LexFlow format, or structuring workflow systems with helper workflows.

- **lexflow-opcode-developer**: Use this agent when creating, modifying, or reviewing LexFlow opcodes. Invoke it for developing new opcode libraries, adding opcodes to existing libraries, or reviewing opcode implementations.

These agents have specialized knowledge of LexFlow conventions and will produce well-structured, idiomatic code.

## Coding Style Guidelines

**Core Principle: KEEP IT SIMPLE**

This codebase is intentionally simple and easy to understand. Do NOT over-engineer it.

### Style Rules

1. **Keep Comments Concise**
   - Avoid over-documenting
   - Only comment when code intent isn't obvious
   - Prefer clear variable/function names over comments

2. **Imports Always at Top Level**
   - No lazy imports inside functions (except rare circular dependency cases)
   - Group stdlib, third-party, local imports

3. **Function Design**
   - Single Responsibility Principle
   - Keep functions simple and focused
   - If a function does multiple things, split it

4. **Formatting**
   - Run `uv run ruff format` regularly
   - Let ruff handle all formatting decisions
   - Don't fight the formatter

5. **No Over-Engineering**
   - Solve today's problem, not tomorrow's
   - No premature abstractions
   - No unnecessary complexity
   - Three strikes rule: wait until you need something 3 times before abstracting

### Examples

❌ **Bad** (over-documented, complex):
```python
def process_data(data):
    """Process the data by doing various transformations.

    This function takes data and processes it through multiple
    steps including validation, transformation, and formatting.

    Args:
        data: The input data to process

    Returns:
        The processed and formatted data
    """
    # First validate the data
    if not data:
        raise ValueError("Data cannot be empty")

    # Then transform it
    result = transform(data)

    # Finally format it
    return format(result)
```

✅ **Good** (simple, clear):
```python
def process_data(data):
    """Process and format data."""
    if not data:
        raise ValueError("Data cannot be empty")
    return format(transform(data))
```

❌ **Bad** (lazy import):
```python
def some_function():
    from typing import Dict  # Don't do this
    result: Dict = {}
```

✅ **Good** (top-level import):
```python
from typing import Dict

def some_function():
    result: Dict = {}
```

❌ **Bad** (over-engineered):
```python
class DataProcessorFactory:
    """Factory for creating data processors."""

    @staticmethod
    def create_processor(processor_type: str):
        if processor_type == "json":
            return JSONProcessor()
        elif processor_type == "yaml":
            return YAMLProcessor()
```

✅ **Good** (simple):
```python
def parse_data(data: str, format: str):
    """Parse data in given format."""
    if format == "json":
        return json.loads(data)
    elif format == "yaml":
        return yaml.safe_load(data)
```

## Development Commands

### Setup
```bash
# Install in development mode with all dependencies
uv sync --all-extras
```

### Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests

# Run single test file
pytest tests/unit/test_output_capture.py

# Run with verbose output
pytest -v

# Run tests from root (pytest uses pythonpath from pytest.ini)
pytest
```

### Code Quality
```bash
# Format code with ruff (run regularly!)
uv run ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Documentation Generation
```bash
# Generate opcode reference from code docstrings
lexflow docs generate                           # Generate to docs/OPCODE_REFERENCE.md
lexflow docs generate -o custom/path.md         # Custom output path
lexflow docs generate --stdout                  # Print to stdout
```

The `lexflow docs generate` command introspects the opcode registry and generates `OPCODE_REFERENCE.md` automatically from function signatures and docstrings. Run this after adding or modifying opcodes to keep documentation in sync.

### Running Workflows
```bash
# Execute a workflow file (JSON or YAML)
lexflow examples/basics/hello_world.yaml

# Include external workflow files
lexflow examples/multi_file/main.yaml --include examples/multi_file/helpers.yaml

# Include multiple files
lexflow main.yaml --include helpers.yaml utils.yaml

# Pass input parameters to workflow
lexflow workflow.yaml --input name=Alice --input age=30

# Multiple inputs with type auto-conversion (JSON parsing)
lexflow workflow.yaml --input name=John --input age=25 --input active=true

# Validate without executing
lexflow workflow.yaml --validate-only

# Redirect output to file
lexflow workflow.yaml --output-file output.txt

# Verbose mode (execution details)
lexflow workflow.yaml --verbose

# Combine multiple options
lexflow workflow.yaml --input name=Alice --output-file result.txt --verbose

# Performance metrics
lexflow workflow.yaml --metrics                          # Show performance report
lexflow workflow.yaml --metrics --metrics-top 20         # Show top 20 operations
lexflow workflow.yaml --metrics --metrics-json           # Export as JSON
lexflow workflow.yaml --metrics --metrics-output perf.txt # Save metrics to file
```

## Architecture Overview

### Core Components

**Engine** (`engine.py`) - Main orchestrator that wires together all components:
- Creates Runtime, Evaluator, Executor instances
- Manages OpcodeRegistry and WorkflowManager
- Handles output redirection via `output` parameter
- Entry point: `await engine.run()`

**Parser** (`parser.py`) - Converts JSON/YAML workflows to AST:
- Supports both JSON and YAML formats (auto-detected by extension)
- **File-based parsing**: `parse_file()` for single file, `parse_files()` for multiple files with `--include`
- **Dictionary-based parsing**: `parse_dict()` for single dict, `parse_dicts()` for main + includes (useful for APIs)
- Main workflow must be named "main"
- External workflows can be called from main workflow

**Runtime** (`runtime.py`) - Execution state management:
- Data stack: `runtime.stack` for operand values
- Call stack: `runtime.frames` for workflow calls
- Scope management: Hierarchical variable scopes with parent chain
- Frame operations: `call()` and `ret()` for workflow invocation

**Evaluator** (`evaluator.py`) - Expression evaluation:
- Pattern matches on AST expression nodes (Literal, Variable, Call, Opcode)
- Evaluates expressions to values asynchronously
- Delegates to OpcodeRegistry and WorkflowManager

**Executor** (`executor.py`) - Statement execution:
- Pattern matches on AST statement nodes (Assign, Block, If, While, Return, Try, etc.)
- Returns Flow enum (NEXT, BREAK, CONTINUE, RETURN) for control flow
- Handles try-catch-finally using Python's native exception handling

**AST** (`ast.py`) - Pydantic models for program structure:
- Expressions: Literal, Variable, Call, Opcode
- Statements: Assign, Block, If, While, Return, ExprStmt, OpStmt, Try, Throw
- Top-level: Workflow, Program

**OpcodeRegistry** (`opcodes.py`) - Plugin system for operations:
- 76 built-in opcodes (I/O, arithmetic, comparison, logical, math, string, list, dictionary, object, type conversions, exceptions, AI)
- Decorator-based registration: `@registry.register()`
- Automatic argument unpacking from lists
- Type hints preserved for introspection
- Global singleton registry for easy custom opcode registration
- AI opcodes in separate module (`opcodes_pydantic_ai.py`) for optional pydantic-ai integration

**WorkflowManager** (`workflows.py`) - External workflow calls:
- Manages workflow parameters and local variables
- Handles workflow call frames and returns
- Integrates with Runtime for scope management

### Data Flow

1. **Parse**: JSON/YAML → Parser → AST (Program)
2. **Initialize**: Program → Engine → Runtime + Evaluator + Executor + OpcodeRegistry + WorkflowManager
3. **Execute**: Engine.run() → Executor.exec(main.body) → Statement evaluation
4. **Evaluate**: Expressions evaluated by Evaluator → Values pushed to Runtime.stack
5. **Return**: Final stack value returned as result

### Control Flow Pattern

Statements return `Flow` enum:
- `Flow.NEXT` - Continue to next statement
- `Flow.BREAK` - Break from loop
- `Flow.CONTINUE` - Continue loop
- `Flow.RETURN` - Return from workflow (value on stack)

Exceptions propagate naturally through Python's exception handling.

## Key Concepts

### Workflow Files

**Main Workflow**: Must be named "main" and exists in the primary file. This is the entry point.

**External Workflows**: Other workflows that can be called from main or from each other. Defined in same file or included files.

**Include Mechanism**: `--include` files have ALL their workflows treated as external (including "main" if present).

### Workflow Inputs

Workflows can define input parameters via `interface.inputs` that can be passed at runtime:

**Defining Inputs** (in workflow YAML/JSON):
```yaml
workflows:
  - name: main
    interface:
      inputs: ["name", "age"]  # Parameter names
      outputs: []
    variables:
      name: "Guest"  # Default values
      age: 0
```

**Passing Inputs via API**:
```python
# Parse workflow
parser = Parser()
program = parser.parse_dict(workflow_data)

# Run with inputs
engine = Engine(program)
result = await engine.run(inputs={"name": "Alice", "age": 30})
```

**Passing Inputs via CLI**:
```bash
lexflow workflow.yaml --input name=Alice --input age=30
```

**Input Validation**: Engine validates that input keys match workflow params, raises `ValueError` if invalid keys provided.

**Type Conversion** (CLI only): Values are parsed as JSON when possible:
- `--input age=30` → `{"age": 30}` (int)
- `--input active=true` → `{"active": true}` (bool)
- `--input items='["a","b"]'` → `{"items": ["a", "b"]}` (list)
- `--input name=Alice` → `{"name": "Alice"}` (string, JSON parsing fails)

### Variables

- **Global variables**: Defined in main workflow's `variables` section, copied to `Program.globals`
- **Local variables**: Each workflow has its own `locals` dict with default values
- **Scope chain**: Child scopes inherit from parent scopes via `Scope.parent`
- **Assignment**: `data_set_variable_to` opcode or `Assign` AST node

### Output Redirection

Engine supports output redirection via `output` parameter (accepts any TextIO):
```python
import io
output_buffer = io.StringIO()
engine = Engine(program, output=output_buffer)
await engine.run()
captured = output_buffer.getvalue()
```

See `docs/OPCODE_REFERENCE.md` for usage with FastAPI, testing, logging, streaming.

### Performance Metrics

LexFlow includes a comprehensive metrics collection system for tracking workflow execution performance:

**Enabling Metrics**:
```python
from lexflow import Parser, Engine

parser = Parser()
program = parser.parse_dict(workflow_data)

# Enable metrics (creates ExecutionMetrics instance)
engine = Engine(program, metrics=True)

await engine.run()

# Get formatted report
print(engine.get_metrics_report())

# Get summary
print(engine.get_metrics_summary())

# Export as dictionary or JSON
metrics_data = engine.metrics.to_dict()
metrics_json = engine.metrics.to_json()
```

**Using Custom Metrics Instance**:
```python
from lexflow.metrics import ExecutionMetrics

# Create and configure metrics instance
metrics = ExecutionMetrics()

# Pass to engine
engine = Engine(program, metrics=metrics)
await engine.run()

# Access detailed metrics
opcode_metrics = metrics.get_aggregated("opcode")
stmt_metrics = metrics.get_aggregated("statement")
workflow_metrics = metrics.get_aggregated("workflow_call")

# Get top N slowest operations
top_opcodes = metrics.get_top_operations("opcode", n=10, sort_by="total_time")
```

**Collected Metrics**:
- **Node timing**: Individual workflow nodes by their ID (e.g., "loop", "print_result", "add_sum")
- **Opcode timing**: Individual opcode execution times
- **Statement timing**: Performance of If/While/For/Assign/etc
- **Expression timing**: Literal/Variable/Call/Opcode evaluations
- **Workflow calls**: External workflow invocation timing
- **Aggregated statistics**: count, total_time, min_time, max_time, avg_time

**Node-Level Metrics**: Each node in your workflow is automatically tracked by its ID from the YAML/JSON file. This allows you to see exactly which nodes are slow:

```python
# Access node-level metrics
node_metrics = engine.metrics.get_aggregated("node")
for node_id, metrics in node_metrics.items():
    print(f"{node_id}: {metrics.total_time:.6f}s ({metrics.count} calls)")

# Output:
# loop: 0.000124s (1 calls)
# loop_body: 0.000025s (5 calls)
# print_result: 0.000032s (1 calls)
```

**Zero Overhead When Disabled**: Metrics are disabled by default (uses `NullMetrics` with no overhead)

**Example Report**:
```
================================================================================
LEXFLOW EXECUTION METRICS REPORT
================================================================================

Total Execution Time: 0.002456 seconds
Total Operations: 42

--------------------------------------------------------------------------------
NODE METRICS
--------------------------------------------------------------------------------
Name                           Count   Total(s)      Avg(s)      Min(s)      Max(s)
--------------------------------------------------------------------------------
loop                               1    0.000124    0.000124    0.000124    0.000124
loop_body                          5    0.000025    0.000005    0.000004    0.000007
print_result                       1    0.000032    0.000032    0.000032    0.000032

--------------------------------------------------------------------------------
OPCODE METRICS
--------------------------------------------------------------------------------
Name                           Count   Total(s)      Avg(s)      Min(s)      Max(s)
--------------------------------------------------------------------------------
operator_add                       5    0.000123    0.000025    0.000020    0.000030
io_print                           3    0.000089    0.000030    0.000028    0.000032
```

### Exception Handling

Uses `control_try` opcode with catch handlers and optional finally:
- Catch handlers can specify exception type (ValueError, TypeError, etc.)
- Variable binding: `var_name` in catch handler binds exception message to variable
- Python exceptions propagate naturally through the async call stack
- See `examples/exception_handling/` for comprehensive examples

### Custom Opcodes

Register custom opcodes using the decorator pattern:
```python
from lexflow.opcodes import OpcodeRegistry

registry = OpcodeRegistry()

@registry.register()
async def my_custom_op(x: int, y: int = 10) -> int:
    """Custom opcode with optional parameter."""
    return x + y

# Wire into engine
engine.opcodes = registry  # Or extend default registry
```

See `examples/integrations/custom_opcodes/basics.py` for complete examples.

## Testing Strategy

- **Unit tests**: Test individual components (opcodes, parser, evaluator, etc.)
- **Integration tests**: Test full workflow execution end-to-end
- Test files located in `tests/` directory
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/` (organized by feature category)
- Educational examples: `examples/` (organized by topic for users)
- Use `pytest -m unit` or `pytest -m integration` to run specific categories
- All tests use `pytest-asyncio` for async support (mode: auto)

## Important Implementation Details

### Async/Await Pattern
All execution is async. Key methods:
- `engine.run()` - Main execution entry point
- `executor.exec(stmt)` - Statement execution
- `evaluator.eval(expr)` - Expression evaluation
- `opcodes.call(name, args)` - Opcode invocation
- `workflows.call(name, args)` - Workflow calls

### Stack-Based Execution
- Expressions push values to stack
- Return statements push return value to stack before returning Flow.RETURN
- Workflow calls pop return value from stack after workflow returns

### Pattern Matching
Heavy use of Python 3.10+ pattern matching (`match/case`) in:
- `evaluator.eval()` for expressions
- `executor.exec()` for statements

### Parser Node Types
JSON/YAML nodes use special input formats:
- `{"literal": value}` - Literal value
- `{"variable": "name"}` - Variable reference
- `{"node": "node_id"}` - Reporter node reference (including workflow calls on reporters)
- `{"branch": "node_id"}` - Branch reference (control flow)
- `{"workflow_call": "name"}` - Workflow call (expression or statement)

### File Format Support
- JSON files: `.json` extension
- YAML files: `.yaml` or `.yml` extension
- Auto-detection: Tries JSON first, falls back to YAML if extension unknown

## AI Integration

LexFlow supports AI operations via pydantic-ai with Google Vertex AI:

**Available AI Opcodes:**
- `pydantic_ai_create_vertex_model(model_name, project=None, location=None)` - Create Vertex AI model
- `pydantic_ai_create_agent(model, instructions='', system_prompt='')` - Create AI agent
- `pydantic_ai_run_sync(agent, prompt)` - Run agent synchronously
- `pydantic_ai_run(agent, prompt)` - Run agent asynchronously

**Installation:**
```bash
pip install lexflow[ai]
gcloud auth application-default login
```

**Example:**
See `examples/integrations/pydantic_ai/vertex_ai_example.yaml` for complete workflow with AI integration.

## Common Patterns

### Parsing Workflows from Dictionaries

For API integrations, parse dictionaries directly instead of using temp files:

```python
from lexflow import Parser, Engine
import json
import yaml

# Parse JSON workflow
parser = Parser()
workflow_dict = json.loads(json_string)
program = parser.parse_dict(workflow_dict)

# Or parse YAML workflow
workflow_dict = yaml.safe_load(yaml_string)
program = parser.parse_dict(workflow_dict)

# Parse with includes (main + helper workflows)
main_dict = {"workflows": [...]}
helper_dict = {"workflows": [...]}
program = parser.parse_dicts(main_dict, [helper_dict])
```

### Running Workflows with Inputs

Pass input parameters at runtime:

```python
# Define workflow with inputs in interface
workflow_data = {
    "workflows": [{
        "name": "main",
        "interface": {
            "inputs": ["name", "age"],
            "outputs": []
        },
        "variables": {"name": "Guest", "age": 0},
        "nodes": {...}
    }]
}

# Parse and run with inputs
parser = Parser()
program = parser.parse_dict(workflow_data)
engine = Engine(program)

# Inputs override default values from variables
result = await engine.run(inputs={"name": "Alice", "age": 30})

# Invalid inputs raise ValueError
try:
    result = await engine.run(inputs={"invalid_key": "value"})
except ValueError as e:
    print(f"Validation error: {e}")
    # "Invalid input parameters: {'invalid_key'}. Main workflow accepts: ['name', 'age']"
```

### Adding New Opcode

**Simple Pattern (Recommended):**
```python
from lexflow import opcode

@opcode()
async def my_custom_op(x: int, y: int) -> int:
    """My custom operation."""
    return x + y

# Opcode is now available to all engines automatically
```

**Advanced Pattern (Custom Registry):**
```python
from lexflow import OpcodeRegistry, Engine

# Create isolated registry
custom_registry = OpcodeRegistry()

@custom_registry.register()
async def isolated_op(x: int) -> int:
    return x * 100

# Use with engine
engine = Engine(program, opcodes=custom_registry)
```

**Adding Built-in Opcodes:**
1. Add function to `opcodes.py` using `@self.register()` in `_register_builtins()`
2. Use type hints for automatic documentation
3. Run `lexflow docs generate` to update `docs/OPCODE_REFERENCE.md`

### Adding New Statement Type
1. Add Pydantic model to `ast.py`
2. Add case to `executor.exec()` pattern match
3. Update parser to recognize new statement format
4. Add to `Statement` union type

### Debugging Workflows
1. Use `--verbose` flag to see execution details
2. Use `--validate-only` to check parsing without execution
3. Add `io_print` opcodes to inspect values during execution
4. Check `runtime.stack` and `runtime.scope` state

## Release Workflow

This monorepo uses **semantic-release** with independent versioning for each package.

### Tag Format

| Package | Tag Format | Example |
|---------|------------|---------|
| lexflow-core | `core-v{version}` | `core-v1.2.0` |
| lexflow-cli | `cli-v{version}` | `cli-v1.0.0` |
| lexflow-web | `web-v{version}` | `web-v0.5.0` |

### Commit Convention

Use conventional commits to trigger automatic releases:

| Commit Prefix | Version Bump | Example |
|---------------|--------------|---------|
| `feat(core):` | Minor (0.X.0) | `feat(core): add new opcode` |
| `fix(core):` | Patch (0.0.X) | `fix(core): handle edge case` |
| `perf(cli):` | Patch (0.0.X) | `perf(cli): optimize parsing` |
| `feat!:` or `BREAKING CHANGE:` | Major (X.0.0) | `feat!: redesign API` |
| `chore:`, `docs:`, `test:` | No release | `docs: update readme` |

**Scope tags:** Use `(core)`, `(cli)`, or `(web)` to indicate which package the change affects.

### Manual Version Check

To preview what version would be released (dry run):
```bash
cd lexflow-core
pip install python-semantic-release
semantic-release version --dry-run
```

### CI/CD

The `.github/workflows/release.yml` workflow:
1. Detects which packages changed using path filters
2. Runs semantic-release for each changed package
3. Creates version tags and GitHub releases automatically

Releases are triggered on pushes to `main` branch only.
