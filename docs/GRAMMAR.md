# LexFlow Grammar Specification

This document defines the complete grammar for the LexFlow visual programming language.

## Overview

LexFlow is a JSON/YAML-based visual programming language designed for AI workflows. Programs consist of workflows containing interconnected nodes that form execution chains, similar to Scratch but with async-native execution.

## Core Concepts

### Programs

A LexFlow program is the top-level structure containing one or more workflows.

```json
{
  "workflows": [ /* array of workflow definitions */ ],
  "globals": { /* optional global state */ },
  "metadata": { /* optional program metadata */ }
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
      "STRING": {"literal": "Hello, World!\n"}
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
      "OPERAND1": {"variable": "x"},
      "OPERAND2": {"literal": 5}
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

| Type Key | Description | Example |
|----------|-------------|---------|
| `literal` | Direct value (string, number, boolean) | `{"literal": "Hello"}` |
| `node` | Reference to a reporter node | `{"node": "calculator"}` |
| `variable` | Reference to a variable by name | `{"variable": "counter"}` |
| `branch` | Reference to a node chain | `{"branch": "loop_body"}` |
| `workflow_call` | Call to another workflow | `{"workflow_call": "helper"}` |

### Examples

```json
{
  "inputs": {
    "STRING": {"literal": "Hello World"},           // Literal string
    "NUMBER": {"literal": 42},                      // Literal number
    "COUNTER": {"variable": "counter"},             // Variable reference
    "RESULT": {"node": "calculator_node"},          // Reporter node reference
    "LOOP_BODY": {"branch": "loop_start"},          // Branch to node chain
    "HELPER": {"workflow_call": "helper_workflow"}  // Workflow call
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
    "inputs": { "STRING": {"literal": "First\n"} }
  },
  "second": {
    "opcode": "io_print",
    "next": null,
    "inputs": { "STRING": {"literal": "Second\n"} }
  }
}
```

### Conditional (If/Else)

```json
{
  "check": {
    "opcode": "control_if_else",
    "inputs": {
      "CONDITION": {"node": "is_valid"},
      "BRANCH1": {"branch": "true_path"},
      "BRANCH2": {"branch": "false_path"}
    }
  },
  "is_valid": {
    "opcode": "operator_equals",
    "inputs": {
      "OPERAND1": {"variable": "x"},
      "OPERAND2": {"literal": 10}
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
      "CONDITION": {"node": "keep_running"},
      "SUBSTACK": {"branch": "loop_body"}
    }
  },
  "keep_running": {
    "opcode": "operator_less_than",
    "inputs": {
      "OPERAND1": {"variable": "counter"},
      "OPERAND2": {"literal": 10}
    },
    "isReporter": true
  }
}
```

### Workflow Calls and Returns

```json
{
  "call_helper": {
    "opcode": "workflow_call",
    "next": "process_result",
    "inputs": {
      "WORKFLOW": {"literal": "helper_function"},
      "ARG1": {"variable": "x"},
      "ARG2": {"literal": 42}
    }
  }
}
```

```json
{
  "return_value": {
    "opcode": "workflow_return",
    "inputs": {
      "VALUE": {"node": "result_calculator"}
    }
  }
}
```

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
            "STRING": {"literal": "Hello, World!\n"}
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
            "OPERAND1": {"variable": "x"},
            "OPERAND2": {"variable": "y"}
          }
        },
        "return_result": {
          "opcode": "workflow_return",
          "inputs": {
            "VALUE": {"node": "calculate"}
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
