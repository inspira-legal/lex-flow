# LexFlow Web User Guide

This guide explains how to use the LexFlow Web visual editor to create, edit, and execute workflows.

## Interface Overview

The LexFlow Web interface consists of five main areas:

```
┌─────────────────────────────────────────────────────────────┐
│                        Toolbar                               │
├──────────┬────────────────────────────┬────────────┬────────┤
│          │                            │            │        │
│  Opcode  │         Canvas             │   Node     │  Code  │
│  Palette │    (Visual Editor)         │  Editor    │ Editor │
│          │                            │            │        │
├──────────┴────────────────────────────┴────────────┴────────┤
│                    Execution Panel                           │
└─────────────────────────────────────────────────────────────┘
```

### Canvas

The central workspace where your workflow is visualized as connected blocks.

- **Pan**: Click and drag on empty space
- **Zoom**: Scroll wheel or pinch gesture
- **Select node**: Click on a node
- **Multi-select**: Ctrl+Click (not yet implemented)

### Opcode Palette

The left sidebar showing all available operations organized by category:

- **Control Flow** (orange) - if, loops, try-catch, fork
- **Data** (green) - variables, lists, dictionaries
- **I/O** (cyan) - print, input
- **Operators** (purple) - math, comparison, string operations
- **Workflow** (magenta) - workflow calls, returns

### Node Editor

When a node is selected, the right panel shows:

- Node ID and opcode
- Input fields for each parameter
- Connection status

### Code Editor

Toggle the code editor to view and edit the raw YAML/JSON:

- Changes sync bidirectionally with the canvas
- Syntax highlighting for YAML
- Error highlighting for invalid syntax

### Execution Panel

The bottom panel for running workflows:

- **Run** button to execute
- Real-time streaming output
- Final result display
- Error messages

## Creating Workflows

### Adding Nodes

**Drag from Palette:**
1. Find the opcode in the palette
2. Drag it onto the canvas
3. Drop to create an orphan node

**Quick Add (coming soon):**
- Right-click on canvas → Add Node

### Connecting Nodes

Nodes have connection ports:

- **Top port** (input): Receives flow from previous node
- **Bottom port** (output): Sends flow to next node
- **Branch ports**: For control flow (if/else, loops, try-catch)

**To connect two nodes:**
1. Click the output port of the source node
2. Drag to the input port of the target node
3. Release to create the connection

**To disconnect:**
- Click on a connection line and press Delete
- Or drag the output port to empty space

### Configuring Nodes

**Select a node** to open the Node Editor panel:

1. **Node ID**: Unique identifier (editable)
2. **Inputs**: Configure each parameter

**Input Types:**

| Type | Description | Example |
|------|-------------|---------|
| Literal | Direct value | `42`, `"hello"`, `true` |
| Variable | Reference to variable | `my_var` |
| Reporter | Output from another node | Click "Use Reporter" |

### Working with Branches

Control flow nodes (if, loops, try-catch) have branch connections:

**If/Else:**
- THEN branch: Executes when condition is true
- ELSE branch: Executes when condition is false

**Loops:**
- BODY branch: The loop body, executed repeatedly

**Try-Catch:**
- TRY branch: Code to attempt
- CATCH branches: Exception handlers
- FINALLY branch: Always executes

To connect a branch:
1. Click the branch port (labeled THEN, ELSE, BODY, etc.)
2. Drag to the first node of the branch
3. Release to connect

### Using Reporter Nodes

Reporter nodes (oval-shaped) return values that can be used as inputs:

1. Create a reporter node (operators, data access)
2. In another node's input, click "Use Reporter"
3. Click the reporter node to link it

Example: Using `operator_add` as input to `io_print`:
```yaml
add_numbers:
  opcode: operator_add
  isReporter: true
  inputs:
    A: { literal: 5 }
    B: { literal: 3 }

print_result:
  opcode: io_print
  inputs:
    STRING: { node: add_numbers }  # Uses reporter output
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo |
| `Ctrl+B` | Toggle code editor |
| `Ctrl+E` | Toggle execution panel |
| `Ctrl+P` | Toggle palette |
| `Ctrl+0` | Reset zoom |
| `Delete` / `Backspace` | Delete selected node |
| `Escape` | Close panels / Deselect |

## Executing Workflows

### Running a Workflow

1. Click **Run** in the execution panel (or use the toolbar button)
2. Watch the streaming output in real-time
3. View the final result when complete

### Providing Inputs

If your workflow has input parameters:

1. Click the settings icon next to Run
2. Enter values for each input
3. Click Run

### Viewing Metrics

Enable metrics to see performance data:

1. Check "Include Metrics" before running
2. View timing data for each node after execution

## Working with Variables

### Defining Variables

Variables are defined in the workflow's `variables` section:

1. Open the code editor
2. Add variables under the `variables` key:
   ```yaml
   variables:
     counter: 0
     name: "default"
     items: []
   ```

### Using Variables

In node inputs:
- Select "Variable" as the input type
- Enter the variable name

### Setting Variables

Use the `data_set_variable_to` opcode:

```yaml
set_counter:
  opcode: data_set_variable_to
  inputs:
    NAME: { literal: "counter" }
    VALUE: { literal: 10 }
```

## Examples

### Hello World

```yaml
workflows:
  - name: main
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: hello
        inputs: {}

      hello:
        opcode: io_print
        next: null
        inputs:
          STRING: { literal: "Hello, World!\n" }
```

### Loop with Counter

```yaml
workflows:
  - name: main
    variables:
      sum: 0
    nodes:
      start:
        opcode: workflow_start
        next: loop
        inputs: {}

      loop:
        opcode: control_for
        next: print_result
        inputs:
          VAR: { literal: "i" }
          START: { literal: 0 }
          END: { literal: 10 }
          BODY: { branch: add_to_sum }

      add_to_sum:
        opcode: data_set_variable_to
        next: null
        inputs:
          NAME: { literal: "sum" }
          VALUE: { node: compute_sum }

      compute_sum:
        opcode: operator_add
        isReporter: true
        inputs:
          A: { variable: sum }
          B: { variable: i }

      print_result:
        opcode: io_print
        next: null
        inputs:
          STRING: { node: format_result }

      format_result:
        opcode: operator_format
        isReporter: true
        inputs:
          TEMPLATE: { literal: "Sum: {}\n" }
          ARGS: { node: wrap_sum }

      wrap_sum:
        opcode: list_create
        isReporter: true
        inputs:
          ITEMS: { variable: sum }
```

### Conditional Logic

```yaml
workflows:
  - name: main
    variables:
      age: 25
    nodes:
      start:
        opcode: workflow_start
        next: check_age
        inputs: {}

      check_age:
        opcode: control_if_else
        next: null
        inputs:
          CONDITION: { node: is_adult }
          THEN: { branch: print_adult }
          ELSE: { branch: print_minor }

      is_adult:
        opcode: operator_greater_or_equal
        isReporter: true
        inputs:
          A: { variable: age }
          B: { literal: 18 }

      print_adult:
        opcode: io_print
        next: null
        inputs:
          STRING: { literal: "You are an adult\n" }

      print_minor:
        opcode: io_print
        next: null
        inputs:
          STRING: { literal: "You are a minor\n" }
```

## Tips and Best Practices

### Node Naming

- Use descriptive IDs: `calculate_total` not `node1`
- Keep IDs short but meaningful
- Use snake_case for consistency

### Organizing Workflows

- Start simple, add complexity gradually
- Use sub-workflows for reusable logic
- Keep the main chain linear when possible

### Debugging

1. Add `io_print` nodes to trace values
2. Use the code editor to inspect structure
3. Check the execution panel for errors
4. Use `--verbose` flag when running from CLI

### Performance

- Avoid deep nesting in loops
- Use reporters for computed values
- Enable metrics to identify bottlenecks

## Next Steps

- **[Customization](CUSTOMIZATION.md)** - Custom backends and configuration
- **[LexFlow Grammar](../../docs/GRAMMAR.md)** - Complete language specification
- **[Opcode Reference](../../docs/OPCODE_REFERENCE.md)** - All available opcodes
