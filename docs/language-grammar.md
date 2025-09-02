# Lex Flow Language Grammar

Lex Flow uses JSON-based workflow definitions that describe visual programming flows through nodes and connections.

## File Structure

### Top-Level Format

```json
{
  "workflows": [
    {
      "name": "workflow_name",
      "interface": {
        "inputs": ["param1", "param2"],
        "outputs": ["result"]
      },
      "variables": {
        "1": ["var_name", default_value]
      },
      "nodes": {
        "node_id": {
          "opcode": "operation_name",
          "next": "next_node_id",
          "inputs": {
            "PARAM": [input_type, value]
          }
        }
      }
    }
  ]
}
```

## Workflow Structure

### Workflow Definition

```json
{
  "name": "workflow_name",
  "interface": {
    "inputs": ["param1", "param2"],
    "outputs": ["result1", "result2"]
  },
  "variables": {
    "variable_id": ["variable_name", default_value]
  },
  "nodes": {
    "node_id": { /* node definition */ }
  },
  "comments": {
    "node_id": "Optional comment text"
  }
}
```

**Fields:**

- `name` - Unique workflow identifier (required)
- `interface` - Input/output specification (required)
- `variables` - Local variable definitions (optional)
- `nodes` - Node definitions (required)
- `comments` - Documentation for nodes (optional)

### Workflow Interface

```json
{
  "inputs": ["x", "y"], // Parameters this workflow accepts
  "outputs": ["sum", "product"] // Values this workflow returns
}
```

Workflows with inputs can be called from other workflows. Workflows without inputs serve as entry points.

## Node Structure

### Node Definition

```json
{
  "opcode": "operation_name",
  "next": "next_node_id",
  "inputs": {
    "PARAM_NAME": [input_type, value]
  },
  "fields": {
    "optional_field": "value"
  }
}
```

**Fields:**

- `opcode` - Operation to perform (required)
- `next` - Next node to execute (`null` for end nodes)
- `inputs` - Input parameters (optional)
- `fields` - Additional opcode-specific data (optional)

### Node Execution Flow

Nodes execute sequentially following the `next` chain:

```
workflow_start → node_a → node_b → node_c → null (end)
```

## Input Types

Node inputs support three different formats for better readability and developer experience:

### Format 1: Numeric (Legacy)

```json
"PARAM": [1, "Hello World"]       // String literal
"VALUE": [2, "calculation_node"]  // Node reference
"VAR": [3, "1"]                   // Variable reference  
"BRANCH": [4, "if_true_branch"]   // Branch reference
"RESULT": [5, "helper_workflow"]  // Workflow call
```

### Format 2: Keyword Arrays

```json
"PARAM": ["literal", "Hello World"]       // String literal
"VALUE": ["node", "calculation_node"]     // Node reference
"VAR": ["variable", "1"]                  // Variable reference
"BRANCH": ["branch", "if_true_branch"]    // Branch reference
"RESULT": ["workflow_call", "helper_workflow"] // Workflow call
```

### Format 3: Object Notation (Recommended)

```json
"PARAM": {"literal": "Hello World"}       // String literal
"VALUE": {"node": "calculation_node"}     // Node reference
"VAR": {"variable": "1"}                  // Variable reference
"BRANCH": {"branch": "if_true_branch"}    // Branch reference
"RESULT": {"workflow_call": "helper_workflow"} // Workflow call
```

All three formats are equivalent and can be mixed within the same workflow. The object notation is recommended for new workflows as it's more readable and self-documenting.

### Input Type Details

#### Literal Values (Type 1)
Direct values used as-is in the operation:

```json
"STRING": {"literal": "Hello World"}
"NUMBER": {"literal": 42}
"BOOL": {"literal": true}
```

#### Node References (Type 2)
References to other nodes whose output becomes the input value:

```json
"VALUE": {"node": "calculation_node"}
```

The referenced node executes immediately and its result is used as the input value.

#### Variable References (Type 3)
References to variables defined in the workflow's `variables` section:

```json
"VALUE": {"variable": "1"}
```

#### Branch References (Type 4)
Used in control flow operations to specify execution branches:

```json
"TRUE_BRANCH": {"branch": "if_true_branch"}
```

#### Workflow Calls (Type 5)
Calls to other workflows, using their return value as input:

```json
"RESULT": {"workflow_call": "helper_workflow"}
```

## Variables

### Variable Declaration

```json
{
  "variables": {
    "1": ["counter", 0],
    "2": ["message", "Hello"],
    "3": ["result", null]
  }
}
```

Variables are defined as `"id": ["name", default_value]` pairs:

- `id` - Unique identifier for references
- `name` - Human-readable variable name
- `default_value` - Initial value

### Variable Usage

```json
{
  "opcode": "data_set_variable_to",
  "inputs": {
    "VARIABLE": [1, "1"], // Literal ID of variable to set
    "VALUE": [3, "2"] // Value from variable ID "2"
  }
}
```

## Common Patterns

### Entry Point

Every workflow must have a `workflow_start` node:

```json
{
  "start": {
    "opcode": "workflow_start",
    "next": "first_operation",
    "inputs": {}
  }
}
```

### Sequential Operations

```json
{
  "step1": {
    "opcode": "io_print",
    "next": "step2",
    "inputs": {
      "STRING": [1, "Step 1\n"]
    }
  },
  "step2": {
    "opcode": "io_print",
    "next": null,
    "inputs": {
      "STRING": [1, "Step 2\n"]
    }
  }
}
```

### Variable Operations

```json
{
  "set_var": {
    "opcode": "data_set_variable_to",
    "next": "use_var",
    "inputs": {
      "VARIABLE": [1, "1"],
      "VALUE": [1, "Hello World"]
    }
  },
  "use_var": {
    "opcode": "io_print",
    "next": null,
    "inputs": {
      "STRING": [3, "1"] // Use variable value
    }
  }
}
```

### Workflow Calls

```json
{
  "call_helper": {
    "opcode": "workflow_call",
    "next": "use_result",
    "inputs": {
      "WORKFLOW": [1, "add_numbers"],
      "X": [1, 5],
      "Y": [1, 3]
    }
  },
  "use_result": {
    "opcode": "io_print",
    "next": null,
    "inputs": {
      "STRING": [2, "call_helper"] // Use workflow result
    }
  }
}
```

### Return Values

```json
{
  "return_result": {
    "opcode": "workflow_return",
    "next": null,
    "inputs": {
      "VALUE": [3, "result_var"]
    }
  }
}
```

## Complete Examples

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
            "STRING": [1, "Hello, World!\n"]
          }
        }
      }
    }
  ]
}
```

### Calculator with Variables

```json
{
  "workflows": [
    {
      "name": "calculator",
      "interface": {
        "inputs": ["x", "y"],
        "outputs": ["result"]
      },
      "variables": {
        "1": ["x", 0],
        "2": ["y", 0],
        "3": ["result", 0]
      },
      "nodes": {
        "start": {
          "opcode": "workflow_start",
          "next": "calculate",
          "inputs": {}
        },
        "calculate": {
          "opcode": "operator_add",
          "next": "store_result",
          "inputs": {
            "OPERAND1": [3, "1"],
            "OPERAND2": [3, "2"]
          }
        },
        "store_result": {
          "opcode": "data_set_variable_to",
          "next": "return_value",
          "inputs": {
            "VARIABLE": [1, "3"],
            "VALUE": [2, "calculate"]
          }
        },
        "return_value": {
          "opcode": "workflow_return",
          "next": null,
          "inputs": {
            "VALUE": [3, "3"]
          }
        }
      }
    }
  ]
}
```

## Validation Rules

1. **Required workflow_start** - Every workflow must have exactly one `workflow_start` node
2. **Unique node IDs** - Node IDs must be unique within a workflow
3. **Valid next references** - `next` must reference existing nodes or be `null`
4. **Variable ID consistency** - Variable references must match declared variable IDs
5. **Input type validity** - Input types must be 1-5 with appropriate values
6. **Workflow dependencies** - Referenced workflows must exist in loaded files
7. **Interface compliance** - Workflows with inputs must be callable, workflows without inputs are entry points
