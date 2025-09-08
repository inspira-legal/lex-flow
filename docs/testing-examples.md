# Testing & Examples

This guide covers testing workflows, creating examples, and validating the interpreter functionality using pytest.

## Testing Framework

Lex Flow uses pytest for comprehensive testing with separate unit and integration test suites.

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_state.py       # WorkflowState and Frame tests
│   ├── test_loader.py      # WorkflowLoader tests
│   ├── test_parser.py      # Parser tests
│   ├── test_engine.py      # Engine tests
│   └── test_opcodes.py     # Opcode system tests
├── integration/             # Full workflow execution tests
│   ├── test_workflow_execution.py
│   ├── simple_hello.json   # Test workflow files
│   ├── test_functions.json
│   └── ...
└── fixtures/               # Test data files
    └── test_document.txt
```

### Running Tests

#### Run All Tests

```bash
uv run pytest
```

#### Run Unit Tests Only

```bash
uv run pytest tests/unit/
```

#### Run Integration Tests Only

```bash
uv run pytest tests/integration/
```

#### Run with Verbose Output

```bash
uv run pytest -v
```

#### Run Specific Test File

```bash
uv run pytest tests/unit/test_state.py -v
```

#### Run Tests Matching Pattern

```bash
uv run pytest -k "test_stack" -v
```

Example output:

```
============================= test session starts ==============================
platform linux -- Python 3.13.7, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/capitani/dev/lex-flow
configfile: pytest.ini
plugins: asyncio-1.1.0
collecting ... collected 59 items

tests/unit/test_state.py::TestWorkflowState::test_stack_operations PASSED
tests/unit/test_loader.py::TestWorkflowLoader::test_load_single_file PASSED
tests/integration/test_workflow_execution.py::TestWorkflowExecution::test_simple_hello_world_execution PASSED

============================== 36 passed, 23 failed in 1.58s ============================
```

## Unit Testing

Unit tests focus on individual components and their behavior in isolation.

### Testing Core Components

#### WorkflowState Tests (`test_state.py`)

```python
def test_stack_operations(workflow_state):
    """Test basic stack operations."""
    workflow_state.push("test_value")
    workflow_state.push(42)

    assert workflow_state.pop() == 42
    assert workflow_state.pop() == "test_value"

def test_call_frame_management(workflow_state):
    """Test call frame push and pop operations."""
    workflow_state.push_frame(return_pc=10, locals={"test": "value"})

    assert len(workflow_state._call_stack) == 1
    frame = workflow_state.peek_frame()
    assert frame._return_pc == 10
```

#### WorkflowLoader Tests (`test_loader.py`)

```python
def test_load_single_file(workflow_loader, temp_workflow_file):
    """Test loading a single workflow file."""
    workflows = workflow_loader.load_files_with_main(temp_workflow_file, [])

    assert len(workflows) == 1
    assert "test_workflow" in workflows

def test_load_invalid_json_raises(workflow_loader, tmp_path):
    """Test that loading invalid JSON raises JSONParseError."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text('{"invalid": json}')

    with pytest.raises(JSONParseError):
        workflow_loader.load_files_with_main(json_file, [])
```

#### Opcode Tests (`test_opcodes.py`)

```python
def test_params_decorator_creates_param_definitions():
    """Test that @params decorator creates parameter definitions."""
    param_info = TestOpcode.get_param_info()

    assert "value1" in param_info
    assert param_info["value1"].type == int
    assert param_info["value1"].description == "First value"

@pytest.mark.asyncio
async def test_opcode_execution(workflow_state):
    """Test executing opcode with parameters."""
    workflow_state.push("world")
    workflow_state.push(123)

    stmt = Statement(opcode="test_opcode", inputs={"value1": None, "value2": None})

    opcode = TestOpcode()
    result = await opcode.execute(workflow_state, stmt, None)

    assert result is True
    assert workflow_state.pop() == "123-world"
```

## Integration Testing

Integration tests verify full workflow execution from loading to completion.

### Workflow Execution Tests

#### Basic Workflow Test

```python
@pytest.mark.asyncio
async def test_simple_hello_world_execution(integration_path):
    """Test execution of simple hello world workflow."""
    workflow_file = integration_path / "simple_hello.json"

    # Load workflow
    loader = WorkflowLoader()
    workflows = loader.load_files_with_main(workflow_file, [])
    main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
    main_workflow = workflows[main_workflow_name]

    # Parse to AST
    parser = Parser(main_workflow, list(workflows.values()))
    program = parser.parse()

    # Execute with output capture
    engine = Engine(program)
    output = StringIO()

    with redirect_stdout(output):
        step_count = 0
        while not engine._state.is_finished() and step_count < 10:
            await engine.step()
            step_count += 1

    result_output = output.getvalue()
    assert "Hello, World!" in result_output
    assert step_count > 0
```

#### Multi-File Workflow Test

```python
@pytest.mark.asyncio
async def test_multi_file_execution(tmp_path):
    """Test execution of multi-file workflow project."""
    # Create main workflow file
    main_data = {
        "workflows": [{
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {"1": ["result", 0]},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "call_helper", "inputs": {}},
                "call_helper": {
                    "opcode": "workflow_call",
                    "next": "print_result",
                    "inputs": {"WORKFLOW": [1, "helper"], "VALUE": [1, 42]}
                }
            }
        }]
    }

    # Test execution...
```

### Test Fixtures

Common test fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def workflow_state(simple_ast_program) -> WorkflowState:
    """WorkflowState instance for testing."""
    return WorkflowState(simple_ast_program)

@pytest.fixture
def temp_workflow_file(tmp_path, sample_workflow_data) -> Path:
    """Create a temporary workflow file for testing."""
    workflow_file = tmp_path / "test_workflow.json"
    workflow_file.write_text(json.dumps(sample_workflow_data, indent=2))
    return workflow_file
```

### Test Categories

#### Basic Operations

- **simple_hello.json** - Basic print operation
- **test_simple_file_load.json** - File operations
- **test_file_content.json** - File content processing

#### Control Flow

- **test_simple_if_else.json** - Conditional execution
- **test_simple_while.json** - Loop operations

#### Functions/Workflows

- **test_functions.json** - Workflow calls and returns
- **test_function_as_input.json** - Workflows as parameters
- **test_optional_return.json** - Optional return values

#### Data Operations

- Variable manipulation
- Data transformations
- Stack operations

### Excluded Tests

Some tests are excluded from automatic runs:

```python
test_files = [f for f in os.listdir(tests_dir)
              if f.endswith(".json")
              and f not in ["expected_outputs.json", "guessing_game.json"]]
```

Interactive tests like `guessing_game.json` require user input and can't run automatically.

## Example Workflows

### Hello World

**File**: `examples/hello_world.json`

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": { "inputs": [], "outputs": [] },
      "variables": {},
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "print_hello",
          "inputs": {}
        },
        "print_hello": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [1, "Hello, World!\n"]
          }
        }
      }
    }
  ]
}
```

**Run**:

```bash
uv run lexflow examples/hello_world.json
```

### Calculator with Variables

**File**: `examples/calculator.json`

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": { "inputs": [], "outputs": [] },
      "variables": {
        "1": ["x", 0],
        "2": ["y", 0],
        "3": ["result", 0]
      },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "set_x",
          "inputs": {}
        },
        "set_x": {
          "opcode": "data_set_variable_to",
          "next": "set_y",
          "inputs": {
            "VARIABLE": [1, "1"],
            "VALUE": [1, 15]
          }
        },
        "set_y": {
          "opcode": "data_set_variable_to",
          "next": "add",
          "inputs": {
            "VARIABLE": [1, "2"],
            "VALUE": [1, 25]
          }
        },
        "add": {
          "opcode": "operator_add",
          "next": "store_result",
          "inputs": {
            "OPERAND1": [3, "1"],
            "OPERAND2": [3, "2"]
          }
        },
        "store_result": {
          "opcode": "data_set_variable_to",
          "next": "print_result",
          "inputs": {
            "VARIABLE": [1, "3"],
            "VALUE": [2, "add"]
          }
        },
        "print_result": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [3, "3"]
          }
        }
      }
    }
  ]
}
```

### Multi-File Project

**File**: `examples/main.json`

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": { "inputs": [], "outputs": [] },
      "variables": {
        "1": ["a", 0],
        "2": ["b", 0]
      },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "set_values",
          "inputs": {}
        },
        "set_values": {
          "opcode": "data_set_variable_to",
          "next": "set_b",
          "inputs": {
            "VARIABLE": [1, "1"],
            "VALUE": [1, 8]
          }
        },
        "set_b": {
          "opcode": "data_set_variable_to",
          "next": "call_math",
          "inputs": {
            "VARIABLE": [1, "2"],
            "VALUE": [1, 3]
          }
        },
        "call_math": {
          "opcode": "workflow_call",
          "next": "print_result",
          "inputs": {
            "WORKFLOW": [1, "add_multiply"],
            "X": [3, "1"],
            "Y": [3, "2"]
          }
        },
        "print_result": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [2, "call_math"]
          }
        }
      }
    }
  ]
}
```

**File**: `examples/math_utils.json`

```json
{
  "workflows": [
    {
      "name": "add_multiply",
      "interface": {
        "inputs": ["x", "y"],
        "outputs": ["result"]
      },
      "variables": {
        "1": ["x", 0],
        "2": ["y", 0],
        "3": ["sum", 0],
        "4": ["product", 0]
      },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "add",
          "inputs": {}
        },
        "add": {
          "opcode": "operator_add",
          "next": "multiply",
          "inputs": {
            "OPERAND1": [3, "1"],
            "OPERAND2": [3, "2"]
          }
        },
        "multiply": {
          "opcode": "operator_multiply",
          "next": "return_result",
          "inputs": {
            "OPERAND1": [2, "add"],
            "OPERAND2": [1, 2]
          }
        },
        "return_result": {
          "opcode": "workflow_return",
          "next": null,
          "inputs": {
            "VALUE": [2, "multiply"]
          }
        }
      }
    }
  ]
}
```

**Run**:

```bash
uv run lexflow examples/main.json -I examples/math_utils.json
```

### Control Flow Example

**File**: `examples/conditional.json`

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": { "inputs": [], "outputs": [] },
      "variables": { "1": ["number", 42] },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "check_positive",
          "inputs": {}
        },
        "check_positive": {
          "opcode": "operator_greater_than",
          "next": "branch",
          "inputs": {
            "OPERAND1": [3, "1"],
            "OPERAND2": [1, 0]
          }
        },
        "branch": {
          "opcode": "control_if_else",
          "next": null,
          "inputs": {
            "CONDITION": [2, "check_positive"],
            "TRUE_BRANCH": [4, "positive_msg"],
            "FALSE_BRANCH": [4, "negative_msg"]
          }
        },
        "positive_msg": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [1, "Number is positive!\n"]
          }
        },
        "negative_msg": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [1, "Number is not positive!\n"]
          }
        }
      }
    }
  ]
}
```

## Debugging Workflows

### Debug Mode

Use `--debug` for step-by-step execution:

```bash
uv run lexflow examples/calculator.json --debug
[INFO] Debug mode enabled. Press Enter to step, 'q' to quit.
Step [0] completed. Continue? (Enter/q):
# Press Enter to continue step by step
```

### Verbose Mode

Use `--verbose` for detailed execution information:

```bash
uv run lexflow examples/main.json -I examples/math_utils.json --verbose
[INFO] Loading main file: main.json
[INFO] Loading 1 import file(s)
[INFO] Main file workflows:
  main() from main.json
[INFO] Imported workflows:
  add_multiply(x, y) -> (result) from math_utils.json
[SUCCESS] Loaded 2 workflow(s)
[INFO] Executing workflow: main
[INFO] Starting execution...
22
[SUCCESS] Workflow completed in 6 steps
```

### Validation Mode

Use `--validate-only` to check workflows without execution:

```bash
uv run lexflow examples/calculator.json --validate-only
[INFO] Loading workflow file: calculator.json
[SUCCESS] Loaded 1 workflow(s)
[SUCCESS] All workflows are valid!
```

## Best Practices

### Test Design

1. **Test one feature per file** - Keep tests focused
2. **Use descriptive names** - Make test purpose clear
3. **Include edge cases** - Test error conditions and boundaries
4. **Keep outputs deterministic** - Avoid random values or timestamps
5. **Document test purpose** - Add comments explaining what's being tested

### Example Creation

1. **Start simple** - Build complexity gradually
2. **Show real use cases** - Examples should solve actual problems
3. **Include comments** - JSON doesn't support comments but use descriptive names
4. **Demonstrate patterns** - Show idiomatic workflow structures
5. **Provide multiple approaches** - Show different ways to solve problems

### Development Workflow

1. **Write failing test** - Create test for new functionality first
2. **Implement feature** - Build opcode or modify interpreter
3. **Run tests** - Check that new test passes and old tests still work
4. **Update expected outputs** - If behavior changes intentionally
5. **Create examples** - Show how to use new functionality

### Test Development Workflow

#### 1. Write Unit Tests First

```python
def test_new_opcode_functionality():
    """Test new opcode behavior."""
    # Arrange
    opcode = NewOpcode()
    workflow_state = create_test_state()

    # Act
    result = await opcode.execute(workflow_state, test_stmt, engine)

    # Assert
    assert result is True
    assert workflow_state.pop() == expected_value
```

#### 2. Add Integration Tests

Create test workflow files in `tests/integration/` to verify end-to-end behavior.

#### 3. Run Tests During Development

```bash
# Run specific test while developing
uv run pytest tests/unit/test_new_feature.py::test_specific_case -v

# Run tests on file change (with pytest-watch)
ptw tests/unit/test_new_feature.py

# Run tests with coverage
uv run pytest --cov=lexflow tests/
```

### Test Configuration

The `pytest.ini` file configures test discovery and execution:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

asyncio_mode = auto

addopts = -v --tb=short --strict-markers

markers =
    unit: Unit tests for individual components
    integration: Integration tests for full workflow execution
    slow: Tests that take longer to run
```

### Continuous Testing

```bash
# Run all tests
uv run pytest

# Run only fast unit tests during development
uv run pytest tests/unit/ -m "not slow"

# Run integration tests for CI/CD
uv run pytest tests/integration/ --maxfail=1

# Generate test coverage report
uv run pytest --cov=lexflow --cov-report=html
```

## Advanced Testing Patterns

### Parametrized Tests

```python
@pytest.mark.parametrize("input_value,expected", [
    (5, 10),
    (-3, -6),
    (0, 0)
])
def test_double_function(input_value, expected):
    result = double(input_value)
    assert result == expected
```

### Mock Testing for External Dependencies

```python
from unittest.mock import Mock, patch

@patch('lexflow.core.engine.Engine._call_workflow')
async def test_workflow_call_with_mock(mock_call):
    mock_call.return_value = "mocked_result"

    engine = Engine(program)
    result = await engine._call_workflow("test_workflow")

    assert result == "mocked_result"
    mock_call.assert_called_once_with("test_workflow")
```

### Error Condition Testing

```python
def test_invalid_opcode_raises_error():
    """Test that invalid opcodes raise appropriate errors."""
    with pytest.raises(RuntimeError) as exc_info:
        engine.execute_invalid_opcode()

    assert "Unknown opcode" in str(exc_info.value)
    assert exc_info.value.opcode == "invalid_opcode"
```

This pytest-based testing framework provides comprehensive coverage of both individual components and full workflow execution, making it easy to develop new features while maintaining system reliability.
