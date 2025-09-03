# Core Architecture

Lex Flow uses a multi-layered architecture that transforms JSON/YAML workflows into executable programs through preprocessing, parsing, AST generation, and stack-based execution.

## Architecture Overview

```
JSON/YAML Workflow Files
        ↓
    WorkflowLoader    ← Validates and loads files with dependency resolution
        ↓
    Preprocessor      ← Normalizes input formats and validates syntax
        ↓
   Legacy Models      ← Pydantic models for JSON parsing and validation
        ↓
      Parser          ← Transforms to executable format with branch/reporter discovery
        ↓
    AST Models        ← Runtime execution models with Node objects
        ↓
      Engine          ← Stack-based async executor with control flow
        ↓
   WorkflowState      ← Execution context with stack safety and bounds checking
        ↓
     Opcodes          ← Modern @params() validated operations
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

- File existence and JSON/YAML syntax
- Required `workflow_start` nodes (using WORKFLOW_START_OPCODE constant)
- Duplicate workflow names across files
- Missing workflow dependencies
- Proper node structure and connectivity

### 2. Preprocessor (`core/preprocessor.py`)

**Purpose**: Normalizes input formats and provides comprehensive validation.

**Key Features**:

- **Input Type Normalization**: Converts multiple input formats to internal numeric format
- **Format Support**: `{"literal": "value"}`, `["literal", "value"]`, `[1, "value"]`
- **Comprehensive Validation**: Clear error messages with examples for malformed inputs
- **Backward Compatibility**: Maintains support for legacy numeric input types

**Error Handling**: Replaces silent failures with WorkflowValidationError containing helpful suggestions.

### 3. Legacy Models (`core/models.py`)

**Purpose**: Pydantic models for parsing JSON workflow definitions with Python 3.9+ compatibility.

**Key Models**:

```python
# Constants for consistency
WORKFLOW_START_OPCODE = "workflow_start"

class InputTypes(Enum):
    LITERAL = 1
    NODE_REF = 2
    VARIABLE_REF = 3
    BRANCH_REF = 4
    WORKFLOW_CALL = 5

class Workflow(BaseModel):
    name: str
    interface: WorkflowInterface
    variables: dict
    nodes: dict[str, Node]

class Node(BaseModel):
    opcode: str
    next: Union[str, None] = None  # Python 3.9+ compatible
    inputs: Union[dict[str, list], None] = None
    is_reporter: bool = Field(default=False, alias="isReporter")

class Program(BaseModel):
    workflows: list[Workflow]
```

These models handle JSON validation and provide structured access to workflow data.

### 4. Parser (`core/parser.py`)

**Purpose**: Transform legacy models into executable AST format with optimized discovery.

**Key Improvements**:

- **Consolidated Logic**: Eliminated code duplication between `_parse_chain` and `_parse_workflow_chain`
- **Branch Discovery**: Pre-parses all branches at compile-time for performance
- **Reporter Discovery**: Pre-parses all reporter nodes (both explicit and NODE_REF referenced)
- **Node Object Storage**: Stores actual Node objects instead of dictionaries
- **Generic Methods**: Uses shared `_parse_chain_generic` and `_parse_node_generic` methods

**Key Transformations**:

- Converts node chains into linear statement sequences
- Resolves variable references and node dependencies
- Creates callable workflow definitions with local scopes
- Discovers and pre-compiles branches and reporters
- Builds execution-ready AST program with Node objects

**Core Method**:

```python
def parse(self) -> Program:
    # Transform main workflow to statements
    # Parse all imported workflows
    # Discover branches and reporters across all workflows
    # Return AST Program with pre-parsed components
```

### 5. AST Models (`core/ast.py`)

**Purpose**: Runtime execution models optimized for the interpreter with pre-parsed components.

**Key Improvements**:

- **Pre-parsed Branches**: `branches: dict[str, list[Statement]]` for immediate execution
- **Pre-parsed Reporters**: `reporters: dict[str, Statement]` for efficient evaluation
- **Node Object Storage**: Stores actual Node objects instead of dictionaries
- **Pydantic Model Rebuilding**: Proper handling of forward references

**Key Models**:

```python
class Program:
    variables: dict[str, Any]
    workflows: dict[str, WorkflowDef] = {}
    main: StatementList
    node_map: dict[str, Any] = None
    branches: dict[str, list[Statement]] = {}     # Pre-parsed branches
    reporters: dict[str, Statement] = {}          # Pre-parsed reporters

class Statement:
    opcode: str
    inputs: dict[str, Value]
    next: Union["Statement", None] = None

class Value:
    type: ValueType  # LITERAL, VARIABLE, NODE_REF, BRANCH_REF, WORKFLOW_CALL
    data: Any

class WorkflowDef:
    name: str
    inputs: list[str]                    # Parameter names
    outputs: list[str]                   # Return value names
    body: StatementList                  # Executable statements
    variables: dict[str, Any] = {}       # Local variable scope
    nodes: dict[str, "Node"] = {}        # Actual Node objects (not dictionaries)
```

The AST models are designed for efficient execution with direct stack operations and eliminate runtime parsing overhead.

### 6. Engine (`core/engine.py`)

**Purpose**: Main execution engine with stack-based operation model and return-based control flow.

**Key Improvements**:

- **Return-based Control Flow**: Eliminated dangerous PC manipulation in opcodes
- **Pre-parsed Branch Execution**: Uses pre-compiled branches for performance
- **Pre-parsed Reporter Execution**: Uses pre-compiled reporters without parsing overhead
- **Simplified Workflow Calls**: Uses stored Node objects directly (no manual reconstruction)
- **Consistent Control Flow**: All control operations use ControlFlow constants

**Key Components**:

```python
class Engine:
    _state: WorkflowState           # Execution context with stack safety
    _opcode_registry: OpcodeRegistry # Available operations with discovery
    _call_stack_trace: List[str]    # For error reporting
    _current_workflow: str          # Current workflow context
    _current_node_id: str           # Current node for debugging
```

**Execution Model**:

- **Sequential execution**: Processes statements with program counter
- **Stack-based**: All operations use stack for parameters and results
- **Async support**: Handles async opcodes naturally
- **Return-based control**: Opcodes return control flow instructions instead of manipulating PC
- **Pre-parsed optimization**: Branches and reporters executed without runtime parsing
- **Call stack management**: Supports nested workflow calls with proper scoping
- **Error context**: Maintains execution context for debugging

**Core Methods**:

- `step()` - Execute single statement, handle control flow returns
- `_evaluate_input(value)` - Resolve different input types (LITERAL, VARIABLE, NODE_REF, etc.)
- `_execute_statement(stmt)` - Execute opcode with stack management and control flow
- `_execute_branch_from_node(node_id)` - Execute pre-parsed branch statements
- `_execute_reporter(node_id)` - Execute pre-parsed reporter without parsing
- `_call_workflow(workflow_name)` - Handle workflow calls using stored Node objects

### 7. WorkflowState (`core/state.py`)

**Purpose**: Execution context with comprehensive stack safety and bounds checking.

**Key Improvements**:

- **Stack Safety**: Comprehensive bounds checking with clear error messages
- **PC Validation**: Prevents program counter from going out of bounds
- **Call Stack Safety**: Prevents underflow with descriptive error context
- **Python 3.9+ Compatibility**: Uses `Union[Frame, None]` syntax

**Key Components**:

```python
class WorkflowState:
    _data_stack: list = []              # Main execution stack with safety checks
    _variables: dict[str, Any]          # Variable storage
    _pc: int = 0                        # Program counter with bounds validation
    _call_stack: list = []              # Call stack with underflow protection
    program: Program                    # Currently executing program
```

**Stack Operations with Safety**:

- `push(value)` - Add value to top of stack
- `pop()` - Remove and return top value (raises RuntimeError if empty)
- `peek()` - Look at top value without removing (raises RuntimeError if empty)
- `is_finished()` - Check if execution is complete
- `current_statement()` - Get current statement with bounds checking

**Call Frame Management with Safety**:

- `push_frame(return_pc, locals)` - Start new call scope
- `pop_frame()` - Return from call scope (raises RuntimeError if empty)
- `peek_frame()` - Look at current frame without removing
- Variable isolation between call frames with proper cleanup

### 8. Opcode System (`core/opcodes.py`)

**Purpose**: Modern plugin architecture with parameter validation and enhanced error handling.

**Key Improvements**:

- **Modern @params() System**: Type-safe parameter validation with descriptions
- **Enhanced Error Handling**: Improved discovery with strict mode and helpful suggestions
- **Parameter Introspection**: Opcodes can expose their interface programmatically
- **Early Validation**: Parameters validated at resolution, not during execution

**Modern Architecture**:

```python
@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"}
)
@opcode("operation_name")
class MyOpcode(BaseOpcode):
    async def execute(self, state: WorkflowState, stmt: Statement, engine: Engine) -> bool:
        params = self.resolve_params(state, stmt)  # Type-safe parameter resolution
        result = await self._op_logic(params["op1"], params["op2"])
        state.push(result)
        return True  # Continue execution

    async def _op_logic(self, op1: int, op2: int):
        # Business logic separated from parameter handling
        return op1 + op2
```

**Enhanced Discovery**:

- Scans `opcodes/` directory for opcode implementations
- Enhanced error handling with suggestions for import failures
- Optional strict mode for development environments
- Supports categorized organization (control, data, io, ai, etc.)

**Migration Status**: 16/18 opcodes (89%) migrated to modern @params() system. Only variable-length parameter opcodes (StrFormat, WorkflowCallOpcode) remain using manual handling.

## Execution Flow

### 1. Loading Phase

```python
loader = WorkflowLoader()
workflows = loader.load_files_with_main(main_file, import_files)
main_workflow_name = loader.get_main_workflow_from_file(main_file)
main_workflow = workflows[main_workflow_name]
```

### 2. Preprocessing Phase

```python
preprocessor = WorkflowPreprocessor()
processed_data = preprocessor.preprocess_workflow(workflow_data)
# Normalizes input formats and validates syntax with clear errors
```

### 3. Parsing Phase

```python
parser = Parser(main_workflow, list(workflows.values()))
program = parser.parse()  # Convert to AST with pre-parsed branches/reporters
```

### 4. Execution Phase

```python
engine = Engine(program)
while not engine._state.is_finished():
    await engine.step()  # Execute one statement with control flow handling
```

### 5. Modern Statement Execution

```python
# For each statement:
1. Evaluate inputs (literals, variables, node refs, branch refs, workflow calls)
2. Modern opcodes: Use resolve_params() for type-safe parameter validation
3. Legacy opcodes: Push input values onto stack (only StrFormat, WorkflowCallOpcode)
4. Execute opcode with stack access and business logic separation
5. Handle control flow returns (CONTINUE, REPEAT, HALT)
6. Advance program counter based on control flow result
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
