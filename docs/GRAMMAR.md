# LexFlow Grammar Specification

This document defines the complete grammar for the LexFlow visual programming language.

## Overview

LexFlow is a JSON/YAML-based visual programming language designed for AI workflows. Programs consist of workflows containing interconnected nodes that form execution chains, similar to Scratch but with async-native execution.

## Core Concepts

### Programs

A LexFlow program is the top-level structure containing one or more workflows.

```json
{
  "workflows": [
    /* array of workflow definitions */
  ],
  "globals": {
    /* optional global state */
  },
  "metadata": {
    /* optional program metadata */
  }
}
```

### Workflows

Workflows are the primary unit of organization, similar to functions in traditional programming.

```json
{
  "name": "workflow_name",
  "interface": {
    "inputs": ["param1", "param2"],
    "outputs": ["result"]
  },
  "variables": {
    "variable_name": default_value,
    "counter": 0
  },
  "nodes": { /* node definitions */ },
  "comments": { /* optional documentation */ }
}
```

**Key Points:**

- Each workflow must have a unique `name`
- The `interface` defines parameters and return values
- Variables use names directly for better readability
- Every workflow must contain exactly one `workflow_start` node

### Nodes

Nodes represent operations in the visual programming environment. There are two types:

#### Statement Nodes (Standard)

Execute actions and chain to the next node:

```json
{
  "node_id": {
    "opcode": "io_print",
    "next": "next_node_id",
    "inputs": {
      "STRING": { "literal": "Hello, World!\n" }
    }
  }
}
```

#### Reporter Nodes (Expressions)

Act as expressions, returning values to the stack:

```json
{
  "reporter_id": {
    "opcode": "operator_add",
    "inputs": {
      "OPERAND1": { "variable": "x" },
      "OPERAND2": { "literal": 5 }
    },
    "isReporter": true
  }
}
```

**Node Properties:**

- `opcode` (required): The operation to perform
- `next` (optional): ID of the next node in the execution chain
- `inputs` (optional): Dictionary of input parameters
- `parent` (optional): ID of parent node for nested structures
- `fields` (optional): Additional metadata
- `isReporter` (optional): Boolean indicating if this is a reporter node

## Input Type System

LexFlow uses an object-based encoding system for node inputs:

```json
{
  "inputs": {
    "PARAM_NAME": {"type_key": value}
  }
}
```

### Input Types

| Type Key        | Description                            | Example                       |
| --------------- | -------------------------------------- | ----------------------------- |
| `literal`       | Direct value (string, number, boolean) | `{"literal": "Hello"}`        |
| `node`          | Reference to a reporter node           | `{"node": "calculator"}`      |
| `variable`      | Reference to a variable by name        | `{"variable": "counter"}`     |
| `branch`        | Reference to a node chain              | `{"branch": "loop_body"}`     |
| `workflow_call` | Call to another workflow               | `{"workflow_call": "helper"}` |

### Examples

```json
{
  "inputs": {
    "STRING": { "literal": "Hello World" }, // Literal string
    "NUMBER": { "literal": 42 }, // Literal number
    "COUNTER": { "variable": "counter" }, // Variable reference
    "RESULT": { "node": "calculator_node" }, // Reporter node reference
    "LOOP_BODY": { "branch": "loop_start" }, // Branch to node chain
    "HELPER": { "workflow_call": "helper_workflow" } // Workflow call
  }
}
```

## Variable System

Variables are defined at the workflow level using direct name-value pairs:

```json
{
  "variables": {
    "variable_name": default_value,
    "counter": 0,
    "message": ""
  }
}
```

**Scoping Rules:**

- Each workflow has its own variable space
- Variables are referenced by name
- Workflow calls create new variable scopes
- Local variables shadow parent workflow variables

**Usage:**

- To reference a variable name as a literal: `{"literal": "variable_name"}`
- To reference a variable's value: `{"variable": "variable_name"}`

## Control Flow Patterns

### Sequential Execution

Nodes chain together using the `next` property:

```json
{
  "first": {
    "opcode": "io_print",
    "next": "second",
    "inputs": { "STRING": { "literal": "First\n" } }
  },
  "second": {
    "opcode": "io_print",
    "next": null,
    "inputs": { "STRING": { "literal": "Second\n" } }
  }
}
```

### Conditional (If)

Simple if without else branch:

```json
{
  "check": {
    "opcode": "control_if",
    "inputs": {
      "CONDITION": { "node": "is_valid" },
      "THEN": { "branch": "true_path" }
    }
  },
  "is_valid": {
    "opcode": "operator_equals",
    "inputs": {
      "OPERAND1": { "variable": "x" },
      "OPERAND2": { "literal": 10 }
    },
    "isReporter": true
  }
}
```

### Conditional (If/Else)

If with else branch:

```json
{
  "check": {
    "opcode": "control_if_else",
    "inputs": {
      "CONDITION": { "node": "is_valid" },
      "THEN": { "branch": "true_path" },
      "ELSE": { "branch": "false_path" }
    }
  },
  "is_valid": {
    "opcode": "operator_equals",
    "inputs": {
      "OPERAND1": { "variable": "x" },
      "OPERAND2": { "literal": 10 }
    },
    "isReporter": true
  }
}
```

### While Loop

```json
{
  "loop": {
    "opcode": "control_while",
    "inputs": {
      "CONDITION": { "node": "keep_running" },
      "BODY": { "branch": "loop_body" }
    }
  },
  "keep_running": {
    "opcode": "operator_less_than",
    "inputs": {
      "OPERAND1": { "variable": "counter" },
      "OPERAND2": { "literal": 10 }
    },
    "isReporter": true
  }
}
```

### For Loop

Range-based iteration (like Python's `for i in range(...)`):

```json
{
  "loop": {
    "opcode": "control_for",
    "inputs": {
      "VAR": { "literal": "i" },
      "START": { "literal": 0 },
      "END": { "literal": 10 },
      "STEP": { "literal": 1 },
      "BODY": { "branch": "loop_body" }
    }
  }
}
```

**Parameters:**
- `VAR`: Loop variable name (literal string)
- `START`: Starting value (inclusive)
- `END`: Ending value (exclusive)
- `STEP`: Optional step value (default: 1)
- `BODY`: Loop body branch

**Note:** Loop variable persists after loop completion with its last value (Python-like behavior).

### ForEach Loop

Iterate over any iterable (lists, dict keys, etc.):

```json
{
  "loop": {
    "opcode": "control_foreach",
    "inputs": {
      "VAR": { "literal": "item" },
      "ITERABLE": { "variable": "my_list" },
      "BODY": { "branch": "process_item" }
    }
  }
}
```

**Parameters:**
- `VAR`: Variable to bind current item (literal string)
- `ITERABLE`: List, dict, or any iterable
- `BODY`: Loop body branch

**Notes:**
- When iterating over dicts, iterates over keys
- Loop variable persists after loop completion with its last value (Python-like behavior)

### Fork (Concurrent Execution)

Execute multiple branches concurrently:

```json
{
  "parallel": {
    "opcode": "control_fork",
    "inputs": {
      "BRANCH1": { "branch": "task_a" },
      "BRANCH2": { "branch": "task_b" },
      "BRANCH3": { "branch": "task_c" }
    }
  }
}
```

**Parameters:**
- `BRANCH1`, `BRANCH2`, ..., `BRANCHn`: Branches to execute concurrently
- All branches run using `asyncio.gather()`
- If any branch raises an exception, it propagates immediately
- If any branch returns, the fork returns immediately

### Workflow Calls and Returns

```json
{
  "call_helper": {
    "opcode": "workflow_call",
    "next": "process_result",
    "inputs": {
      "WORKFLOW": { "literal": "helper_function" },
      "ARG1": { "variable": "x" },
      "ARG2": { "literal": 42 }
    }
  }
}
```

```json
{
  "return_value": {
    "opcode": "workflow_return",
    "inputs": {
      "VALUE": { "node": "result_calculator" }
    }
  }
}
```

### Exception Handling (Try-Catch-Finally)

LexFlow provides native exception handling using Python's built-in exception system.

#### Basic Try-Catch

```json
{
  "try_divide": {
    "opcode": "control_try",
    "next": "after_try",
    "inputs": {
      "TRY": { "branch": "attempt_operation" },
      "CATCH1": {
        "exception_type": "ZeroDivisionError",
        "var": "error",
        "body": { "branch": "handle_error" }
      }
    }
  }
}
```

#### Multiple Catch Handlers

```json
{
  "multi_catch": {
    "opcode": "control_try",
    "inputs": {
      "TRY": { "branch": "risky_code" },
      "CATCH1": {
        "exception_type": "ValueError",
        "var": "err",
        "body": { "branch": "handle_value_error" }
      },
      "CATCH2": {
        "exception_type": "TypeError",
        "var": "err",
        "body": { "branch": "handle_type_error" }
      },
      "CATCH3": {
        "exception_type": null,
        "var": "err",
        "body": { "branch": "handle_any" }
      }
    }
  }
}
```

#### Try-Finally (Cleanup)

```json
{
  "with_cleanup": {
    "opcode": "control_try",
    "inputs": {
      "TRY": { "branch": "do_work" },
      "FINALLY": { "branch": "cleanup" }
    }
  }
}
```

#### Throwing Exceptions

**Using control_throw statement:**

```json
{
  "throw_error": {
    "opcode": "control_throw",
    "inputs": {
      "VALUE": { "literal": "Custom error message" }
    }
  }
}
```

**Using throw opcodes:**

```json
{
  "throw_specific": {
    "opcode": "throw_value_error",
    "next": "unreachable",
    "inputs": {
      "message": { "literal": "Invalid input" }
    }
  }
}
```

**Exception Variable Scope:**

- Variables set by `var` in catch handlers persist for the entire workflow
- They behave like regular workflow variables
- Can be overwritten by subsequent catch handlers

## Execution Model

### Flow

1. Engine starts with the `workflow_start` node
2. Executes current node's opcode with stack-based parameters
3. Follows `next` reference to continue execution chain
4. Reporter nodes are executed when referenced by other nodes
5. Control flow opcodes can override the `next` chain

### Stack-Based Operations

All opcodes use a data stack for parameter passing:

- Reporter nodes push results onto the stack
- Statement nodes pop parameters from the stack as needed
- This enables expression composition and nested operations

### Async-Native

The entire execution pipeline is async:

- All opcode execution is async by default
- Supports I/O operations without blocking
- Natural integration with AI APIs and external services

## Complete Example

### Simple Hello World

```json
{
  "workflows": [
    {
      "name": "main",
      "interface": {
        "inputs": [],
        "outputs": []
      },
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
            "STRING": { "literal": "Hello, World!\n" }
          }
        }
      }
    }
  ]
}
```

### Function with Return Value

```json
{
  "workflows": [
    {
      "name": "add_numbers",
      "interface": {
        "inputs": ["x", "y"],
        "outputs": ["sum"]
      },
      "variables": {
        "x": 0,
        "y": 0
      },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "calculate",
          "inputs": {}
        },
        "calculate": {
          "opcode": "operator_add",
          "next": "return_result",
          "inputs": {
            "OPERAND1": { "variable": "x" },
            "OPERAND2": { "variable": "y" }
          }
        },
        "return_result": {
          "opcode": "workflow_return",
          "inputs": {
            "VALUE": { "node": "calculate" }
          }
        }
      }
    }
  ]
}
```

## File Format Support

LexFlow supports both JSON and YAML formats:

### JSON

```bash
lexflow workflow.json
```

### YAML

```bash
lexflow workflow.yaml
```

The preprocessor automatically detects the format and normalizes the structure.

## Grammar Validation

The grammar is validated at multiple levels:

1. **Syntax**: JSON/YAML parsing
2. **Structure**: Pydantic model validation
3. **Semantics**: Workflow-level validation (start node, dependencies)
4. **Format**: Input type preprocessing and normalization

Errors at each level provide contextual information to help developers fix issues quickly.
