# LexFlow

A stack-based visual programming workflow interpreter. Define workflows in YAML/JSON, visualize them in a node-based editor, and execute them with an async Python engine.

## Packages

| Package | Description |
|---------|-------------|
| [lexflow-core](./lexflow-core/) | Core interpreter engine |
| [lexflow-cli](./lexflow-cli/) | Command-line interface |
| [lexflow-web](./lexflow-web/) | Visual editor & web backend |

## Quick Start

### Run a Workflow

```bash
uv tool install lexflow-cli
lexflow examples/basics/hello_world.yaml
```

### Embed the Visual Editor

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-v1.3.1/lexflow-web/frontend/dist/lexflow-editor.css">
<script src="https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-v1.3.1/lexflow-web/frontend/dist/lexflow-editor.umd.js"></script>
<script>
  LexFlowEditor.mount('#editor', { theme: 'dark' });
</script>
```

See [lexflow-web](./lexflow-web/) for full documentation.

### Use as a Library

```python
from lexflow import Parser, Engine

workflow = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: greet
      greet:
        opcode: io_print
        inputs:
          MESSAGE: { literal: "Hello, World!" }
"""

parser = Parser()
program = parser.parse_dict(yaml.safe_load(workflow))
engine = Engine(program)
result = await engine.run()
```

## Example Workflow

```yaml
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      counter: 0
    nodes:
      start:
        next: loop
      loop:
        opcode: control_repeat
        inputs:
          TIMES: { literal: 5 }
        branches:
          BODY: increment
        next: done
      increment:
        opcode: data_change_variable_by
        inputs:
          VARIABLE: { literal: "counter" }
          VALUE: { literal: 1 }
      done:
        opcode: io_print
        inputs:
          MESSAGE: { variable: "counter" }
```

## Documentation

- [Opcode Reference](./docs/OPCODE_REFERENCE.md) - All available operations
- [Grammar Reference](./docs/GRAMMAR_REFERENCE.md) - Workflow syntax
- [Examples](./examples/) - Sample workflows

## Development

```bash
# Install all packages in dev mode
uv sync --all-extras

# Run tests
pytest

# Format code
uv run ruff format .
```
