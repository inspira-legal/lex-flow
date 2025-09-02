# Core Architecture

Lex Flow uses a multi-layered architecture that transforms JSON workflows into executable programs through parsing, AST generation, and stack-based execution.

## Architecture Overview

```
JSON Workflow Files
        ↓
    WorkflowLoader  ← Validates and loads files
        ↓
   Legacy Models    ← Pydantic models for JSON parsing
        ↓
      Parser        ← Transforms to execution format
        ↓
    AST Models      ← Runtime execution models
        ↓
      Engine        ← Stack-based executor
        ↓
   WorkflowState    ← Execution context and stack
        ↓
     Opcodes        ← Individual operation implementations
```

## Core Components

### 1. WorkflowLoader (`core/loader.py`)

**Purpose**: Load and validate JSON workflow files with dependency resolution.

**Key Methods**:

- `load_files_with_main(main_file, import_files)` - Load main and import files
- `get_main_workflow_from_file(main_file, workflow_name)` - Determine entry point
- `_load_file(file_path)` - Parse individual JSON files
- `_validate_dependencies()` - Check workflow references

**Validation**:

- File existence and JSON syntax
- Required `workflow_start` nodes
- Duplicate workflow names across files
- Missing workflow dependencies

### 2. Legacy Models (`core/models.py`)

**Purpose**: Pydantic models for parsing JSON workflow definitions.

**Key Models**:

```python
class Workflow(BaseModel):
    name: str
    interface: WorkflowInterface
    variables: dict
    nodes: dict[str, Node]

class Node(BaseModel):
    opcode: str
    next: str | None
    inputs: dict[str, list] | None

class Program(BaseModel):
    workflows: list[Workflow]
```

These models handle JSON validation and provide structured access to workflow data.

### 3. Parser (`core/parser.py`)

**Purpose**: Transform legacy models into executable AST format.

**Key Transformations**:

- Converts node chains into linear statement sequences
- Resolves variable references and node dependencies
- Creates callable workflow definitions with local scopes
- Builds execution-ready AST program

**Core Method**:

```python
def parse(self) -> Program:
    # Transform workflows to executable format
    # Build node reference map
    # Create linear statement sequences
    # Return AST Program ready for execution
```

### 4. AST Models (`core/ast.py`)

**Purpose**: Runtime execution models optimized for the interpreter.

**Key Models**:

```python
class Program:
    workflows: Dict[str, WorkflowDef]  # Executable workflows
    node_map: Dict[str, Node]          # Node lookup

class Statement:
    opcode: str
    inputs: Dict[str, Value]
    node_id: Optional[str]

class Value:
    type: ValueType  # LITERAL, VARIABLE, NODE_REF, etc.
    data: Any

class WorkflowDef:
    name: str
    inputs: List[str]     # Parameter names
    outputs: List[str]    # Return value names
    variables: Dict       # Local variable scope
    body: Block           # Executable statements
```

The AST models are designed for efficient execution with direct stack operations.

### 5. Engine (`core/engine.py`)

**Purpose**: Main execution engine with stack-based operation model.

**Key Components**:

```python
class Engine:
    _state: WorkflowState           # Execution context
    _opcode_registry: OpcodeRegistry # Available operations
    _call_stack_trace: List[str]    # For error reporting
```

**Execution Model**:

- **Sequential execution**: Processes statements with program counter
- **Stack-based**: All operations use stack for parameters and results
- **Async support**: Handles async opcodes naturally
- **Call stack management**: Supports nested workflow calls
- **Error context**: Maintains execution context for debugging

**Core Methods**:

- `step()` - Execute single statement, advance program counter
- `_evaluate_input(value)` - Resolve different input types
- `_execute_statement(stmt)` - Execute opcode with stack management
- `_call_workflow(workflow_name)` - Handle workflow calls with scope

### 6. WorkflowState (`core/state.py`)

**Purpose**: Execution context including stack, variables, and program state.

**Key Components**:

```python
class WorkflowState:
    _data_stack: List[Any]          # Main execution stack
    _variables: Dict[str, Tuple]    # Variable storage
    _pc: int                        # Program counter
    _call_frames: List[CallFrame]   # Call stack
    program: Program                # Currently executing program
```

**Stack Operations**:

- `push(value)` - Add value to top of stack
- `pop()` - Remove and return top value
- `peek()` - Look at top value without removing
- `is_finished()` - Check if execution is complete

**Call Frame Management**:

- `push_frame(return_pc, locals)` - Start new call scope
- `pop_frame()` - Return from call scope
- Variable isolation between call frames

### 7. Opcode System (`core/opcodes.py`)

**Purpose**: Plugin architecture for operations with automatic discovery.

**Base Architecture**:

```python
@opcode("operation_name")
class MyOpcode(BaseOpcode):
    async def execute(self, state: WorkflowState, stmt: Statement, engine: Engine) -> bool:
        # Implementation
        return True  # Continue execution
```

**Automatic Discovery**:

- Scans `opcodes/` directory for opcode implementations
- Uses `@opcode()` decorator for registration
- Supports categorized organization (control, data, io, etc.)

## Execution Flow

### 1. Loading Phase

```python
loader = WorkflowLoader()
workflows = loader.load_files_with_main(main_file, import_files)
main_workflow_name = loader.get_main_workflow_from_file(main_file)
```

### 2. Parsing Phase

```python
parser = Parser(main_workflow, list(workflows.values()))
program = parser.parse()  # Convert to AST
```

### 3. Execution Phase

```python
engine = Engine(program)
while not engine._state.is_finished():
    await engine.step()  # Execute one statement
```

### 4. Statement Execution

```python
# For each statement:
1. Evaluate inputs (literals, variables, node refs, workflow calls)
2. Push input values onto stack
3. Execute opcode with stack access
4. Opcode pops inputs, pushes results
5. Advance program counter
```

## Key Design Decisions

### Dual Model Architecture

- **Legacy Models**: Optimized for JSON parsing and validation
- **AST Models**: Optimized for runtime execution
- **Parser Bridge**: Transforms between formats cleanly

### Stack-Based Execution

- **Simplicity**: All opcodes use consistent stack interface
- **Efficiency**: Direct memory operations without parameter passing overhead
- **Composability**: Easy to chain operations and handle complex expressions

### Async-First Design

- All opcode execution is async
- Supports I/O operations, AI calls, and long-running tasks
- Engine naturally handles async without special cases

### Plugin Architecture

- Opcodes are discovered automatically
- Easy to add new operations without core changes
- Categorized organization (control, data, io, ai, etc.)

### Error Context Preservation

- Full call stack tracking
- Variable state snapshots
- Source location mapping for debugging

## Performance Considerations

### Stack Management

- Efficient LIFO operations with Python lists
- Minimal memory allocation during execution
- Direct value passing without serialization

### Variable Scoping

- Local variable dictionaries per call frame
- Copy-on-write semantics for parameter passing
- Automatic cleanup when frames pop

### Node Reference Optimization

- Direct node ID lookup in program node_map
- Cached opcode instances in registry
- Minimal overhead for reporter node execution

## Extension Points

### Custom Opcodes

Add new operations by implementing `BaseOpcode` and using `@opcode()` decorator.

### State Extensions

Extend `WorkflowState` for domain-specific execution context.

### Parser Enhancements

Modify `Parser` to support new language features or optimizations.

### Loader Plugins

Extend `WorkflowLoader` to support additional file formats or validation rules.
