# Testing & Examples

This guide covers testing workflows, creating examples, and validating the interpreter functionality.

## Testing Framework

Lex Flow includes an integrated testing system that executes JSON workflows and validates their outputs.

### Running Tests

#### Run All Tests
```bash
python run_tests.py
```

Output:
```
Running 8 tests...

✅ simple_hello        - PASS (2 steps)
✅ test_functions      - PASS (4 steps)  
✅ test_simple_if_else - PASS (3 steps)
❌ broken_test         - FAIL (0 steps)
   Error: Unknown opcode 'invalid_operation'

==================================================
Test Results: 7 PASSED, 1 FAILED
```

#### Validate Against Expected Outputs
```bash
python validate_tests.py
```

Output:
```
Validating 8 tests against expected outputs...

✅ simple_hello        - Output matches expected
✅ test_functions      - Output matches expected
❌ test_simple_if_else - Output mismatch
   Expected: 'Number is positive\n'
   Actual:   'Number is negative\n'

==================================================
❌ Some tests FAILED. Check output above.
```

### Test Structure

Tests are JSON workflow files in the `tests/` directory:

```
tests/
├── expected_outputs.json    # Expected output strings
├── simple_hello.json       # Basic "Hello World" test
├── test_functions.json     # Workflow calls and returns
├── test_simple_if_else.json # Control flow
├── test_simple_while.json  # Loops
└── ...
```

#### Test Files
Each test is a complete JSON workflow that exercises specific functionality:

```json
{
  "workflows": [
    {
      "name": "main", 
      "interface": {"inputs": [], "outputs": []},
      "variables": {},
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "test_operation",
          "inputs": {}
        },
        "test_operation": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [1, "Test output\n"]
          }
        }
      }
    }
  ]
}
```

#### Expected Outputs
The `expected_outputs.json` file contains expected output strings for validation:

```json
{
  "simple_hello": "Hello, World!\n",
  "test_functions": "Function result!\n",
  "test_simple_if_else": "Number is positive\n"
}
```

### Creating Tests

#### 1. Write Test Workflow
Create a JSON file in `tests/` that exercises the functionality:

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": {"inputs": [], "outputs": []},
      "variables": {"1": ["result", 0]},
      "nodes": {
        "start": {
          "opcode": "workflow_start", 
          "next": "calculate",
          "inputs": {}
        },
        "calculate": {
          "opcode": "operator_add",
          "next": "print_result", 
          "inputs": {
            "OPERAND1": [1, 10],
            "OPERAND2": [1, 5]
          }
        },
        "print_result": {
          "opcode": "io_print",
          "next": null,
          "inputs": {
            "STRING": [2, "calculate"]
          }
        }
      }
    }
  ]
}
```

#### 2. Run Test to Get Output
```bash
python run_tests.py
```

Check the "DETAILED OUTPUT" section to see what your test produces.

#### 3. Add Expected Output
Add the expected output to `tests/expected_outputs.json`:

```json
{
  "my_new_test": "15\n"
}
```

#### 4. Validate
```bash  
python validate_tests.py
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
      "interface": {"inputs": [], "outputs": []},
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
python main.py examples/hello_world.json
```

### Calculator with Variables
**File**: `examples/calculator.json`
```json
{
  "workflows": [
    {
      "name": "main",
      "interface": {"inputs": [], "outputs": []},
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
      "interface": {"inputs": [], "outputs": []},
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
python main.py examples/main.json -I examples/math_utils.json
```

### Control Flow Example  
**File**: `examples/conditional.json`
```json
{
  "workflows": [
    {
      "name": "main",
      "interface": {"inputs": [], "outputs": []},
      "variables": {"1": ["number", 42]},
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
python main.py examples/calculator.json --debug
[INFO] Debug mode enabled. Press Enter to step, 'q' to quit.
Step [0] completed. Continue? (Enter/q): 
# Press Enter to continue step by step
```

### Verbose Mode
Use `--verbose` for detailed execution information:

```bash
python main.py examples/main.json -I examples/math_utils.json --verbose
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
python main.py examples/calculator.json --validate-only
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

### Continuous Testing
```bash
# Quick validation during development
python validate_tests.py

# Full test run with details
python run_tests.py

# Test specific workflow  
python main.py tests/simple_hello.json --verbose
```

## Advanced Testing

### Performance Testing
Time execution of complex workflows:

```bash
time python main.py examples/complex_workflow.json
```

### Memory Testing
Monitor memory usage during execution of large workflows.

### Integration Testing
Test multi-file projects with complex dependency chains:

```bash
python main.py main.json -I utils.json helpers.json data.json --verbose
```

### Error Testing
Create workflows that intentionally trigger errors to test error handling:

```json
{
  "nodes": {
    "error_node": {
      "opcode": "nonexistent_opcode",
      "inputs": {}
    }
  }
}
```

This comprehensive testing framework ensures the interpreter works correctly and provides examples for learning and development.