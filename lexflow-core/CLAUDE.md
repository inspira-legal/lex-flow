# LexFlow Core - Claude Code Guidelines

This document provides guidance specific to the `lexflow-core` module.

**Reference Documentation:**
- `docs/GRAMMAR_REFERENCE.md` - Workflow syntax and node structures
- `docs/OPCODE_REFERENCE.md` - All available opcodes and signatures

**Specialized Agents:**
- Use `lexflow-workflow-writer` agent when creating workflow files
- Use `lexflow-opcode-developer` agent when creating or modifying opcodes

## Architecture Overview

LexFlow Core is a stack-based async workflow interpreter (~3,950 lines). The execution pipeline:

```
JSON/YAML → Parser → AST → Engine → Runtime/Executor/Evaluator → Result
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Parser** | `parser.py` | Converts JSON/YAML to AST using grammar-driven handlers |
| **AST** | `ast.py` | Pydantic models for expressions and statements |
| **Engine** | `engine.py` | Orchestrator that wires components together |
| **Runtime** | `runtime.py` | Execution state: stack, scopes, call frames |
| **Executor** | `executor.py` | Statement execution with control flow |
| **Evaluator** | `evaluator.py` | Expression evaluation |
| **Workflows** | `workflows.py` | External workflow call management |
| **Opcodes** | `opcodes/opcodes.py` | Built-in operations and registry |
| **Grammar** | `grammar.json` | Language schema (single source of truth) |

### Component Interactions

```
Engine
  ├── Runtime (stack, scopes, frames)
  ├── Executor → executes statements
  │     └── Evaluator → evaluates expressions
  │           ├── OpcodeRegistry → built-in operations
  │           └── WorkflowManager → external calls
  └── TaskManager → background tasks
```

## Best Practices

### 1. Use Grammar for Language Structures

The `grammar.json` file is the single source of truth for all language constructs. The parser dynamically builds handlers from it.

```python
# GOOD: Query grammar for control flow detection
from lexflow.grammar import is_control_flow_opcode, get_construct

if is_control_flow_opcode(opcode):
    construct = get_construct(opcode)
    branches = construct.get("branches", [])

# BAD: Hardcoding opcode lists
CONTROL_FLOW_OPCODES = ["control_if", "control_while", ...]  # Don't do this
```

When adding new statement types:
1. Add the construct definition to `grammar.json`
2. Parser will automatically recognize it via handlers
3. Add execution logic to `executor.py`

### 2. Opcode Design

#### Regular Opcodes (Default)

Most opcodes should be simple, stateless functions that don't access engine internals.

```python
# GOOD: Pure opcode with clear inputs/outputs
@registry.register()
async def string_reverse(text: str) -> str:
    return text[::-1]

# GOOD: Opcode with optional parameters
@registry.register()
async def string_pad(text: str, width: int, char: str = " ") -> str:
    return text.center(width, char)
```

#### Privileged Opcodes (Engine Access)

When an opcode needs access to engine internals (runtime, workflows, program), use the **privileged opcode** pattern:

```python
# 1. Register with privileged=True (defines interface only)
@registry.register(privileged=True)
async def introspect_context() -> dict:
    """Get execution context including program, workflows, and opcodes."""
    pass  # Placeholder - implementation injected by Engine

# 2. Engine injects the actual implementation
def _setup_privileged_opcodes(self) -> None:
    async def get_context() -> dict:
        return {
            "program": {...},  # Access to self.program
            "workflows": {...},  # Access to self.workflows
            "opcodes": self.opcodes.list_opcodes(),
        }

    self.opcodes.inject("introspect_context", get_context)
```

This pattern:
- Keeps opcode interface definitions separate from engine-dependent implementations
- Prevents opcodes from directly importing/coupling to engine internals
- Makes testing easier (can inject mock implementations)
- Clearly marks which opcodes require engine context

### 3. Pattern Matching in Executor

Use Python's `match/case` for statement execution. Keep each case simple.

```python
# GOOD: Simple, focused case
case If(cond=cond, then_branch=then, else_branch=else_):
    if await self.evaluator.eval(cond):
        return await self.exec(then)
    elif else_:
        return await self.exec(else_)
    return Flow.NEXT
```

### 4. Stack-Based Return Values

Return values travel via the runtime stack.

```python
# In executor:
case Return(value=expr):
    if expr:
        result = await self.evaluator.eval(expr)
        self.runtime.push(result)
    return Flow.RETURN
```

### 5. Async Everything

All execution is async. Never forget `await`.

```python
# GOOD
result = await engine.run()
flow = await executor.exec(stmt)
value = await evaluator.eval(expr)

# BAD - returns coroutine, not result
result = engine.run()
```

## Common Mistakes to Avoid

### Don't Hardcode Language Structures

All node types, opcodes, and branches should come from `grammar.json`.

```python
# BAD: Hardcoded branch names
if node.get("THEN"):
    ...

# GOOD: Use grammar to discover branches
construct = get_construct(opcode)
for branch in construct.get("branches", []):
    branch_name = branch["name"]
```

### Don't Over-Engineer

This codebase prioritizes simplicity. Avoid:

- Abstract base classes when a simple function works
- Factory patterns for single-use cases
- Configuration systems for one setting

```python
# BAD: Over-engineered
class OpcodeExecutorFactory:
    @staticmethod
    def create_executor(opcode_type: str) -> OpcodeExecutor:
        ...

# GOOD: Simple function
async def call_opcode(name: str, args: list) -> Any:
    func = self.opcodes[name]
    return await func(*args)
```

### Don't Over-Document

Code should be self-explanatory. Comments explain "why", not "what".

```python
# BAD: Obvious comment
# Add x and y together
result = x + y

# GOOD: Clear code, minimal or no comment
result = x + y
```

### Don't Modify AST Nodes

AST nodes are Pydantic models - treat them as immutable.

```python
# BAD: Mutating AST
stmt.cond = new_condition

# GOOD: Create new node if needed
new_stmt = If(cond=new_condition, then_branch=stmt.then_branch, ...)
```

### Don't Bypass the Scope Chain

Use `runtime.scope` for variable access.

```python
# BAD: Direct scope access
runtime.scope.vars["x"] = 10

# GOOD: Use scope interface
runtime.scope["x"] = 10
```

## Adding New Features

### New Opcode

1. Add to `opcodes/opcodes.py` in `_register_builtins()`
2. Use type hints for auto-documentation
3. Run `lexflow docs generate` to update reference

```python
@self.register()
async def string_trim(text: str) -> str:
    """Remove leading and trailing whitespace."""
    return text.strip()
```

### New Privileged Opcode

1. Register with `privileged=True` in `_register_builtins()`
2. Add injection in `engine.py` `_setup_privileged_opcodes()`

```python
# In opcodes.py
@self.register(privileged=True)
async def my_engine_op() -> dict:
    """Opcode that needs engine access."""
    pass

# In engine.py
def _setup_privileged_opcodes(self):
    async def my_impl():
        return {"data": self.runtime.stack}
    self.opcodes.inject("my_engine_op", my_impl)
```

### New Statement Type

1. Add construct to `grammar.json`
2. Add Pydantic model to `ast.py`
3. Add `model_rebuild()` call at end of `ast.py`
4. Add handler to parser if needed
5. Add case to `executor.exec()`

## Testing

```bash
# Run all tests
pytest

# Run core unit tests only
pytest tests/unit/

# Run with verbose output
pytest -v tests/unit/test_executor.py
```

Test patterns:
- Parse workflow dict → create engine → run → assert result
- Use `OutputCapture` to capture printed output
- Use custom `OpcodeRegistry` to inject test opcodes
