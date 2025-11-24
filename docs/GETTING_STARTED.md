# Getting Started with LexFlow

This guide will walk you through installing LexFlow and running your first workflow.

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and environment manager

## Installation

### 1. Install UV

UV is a fast Python package and project manager. Install it using one of the following methods:

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/lex-flow.git
cd lex-flow
```

### 3. Install Dependencies

UV will automatically create a virtual environment and install all dependencies:

```bash
# Install all dependencies (recommended for development)
uv sync --all-extras

# Or install only core dependencies
uv sync

# Or install with specific extras
uv sync --extra ai        # Include AI opcodes (pydantic-ai)
uv sync --extra pygame    # Include pygame opcodes
uv sync --extra file      # Include file processing (PDF)
```

This command will:
- Create a `.venv` directory with a virtual environment
- Install all project dependencies
- Install the lexflow CLI tool
- Set up development tools (pytest, ruff)

### 4. Activate the Virtual Environment

**macOS and Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

**Or use UV's run command (no activation needed):**
```bash
uv run lexflow --help
```

### 5. Verify Installation

Check that the LexFlow CLI is available:

```bash
lexflow
```


## Running Your First Workflow

### Hello World

Create a simple workflow file called `hello.yaml`:

```yaml
workflows:
  - name: main
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: print_hello
        inputs: {}

      print_hello:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Hello, LexFlow!\n"
```

Run the workflow:

```bash
lexflow hello.yaml
```

Output:
```
Hello, LexFlow!
```

### Explore Examples

The repository includes many organized example workflows:

```bash
# List example categories
ls examples/

# Run a simple hello world example
lexflow examples/basics/hello_world.yaml

# Run with verbose output to see execution details
lexflow examples/basics/cli_inputs.yaml --verbose

# Run with inputs
lexflow examples/basics/cli_inputs.yaml --input name=Alice --input age=30

# Explore different categories
lexflow examples/control_flow/loops_for.yaml
lexflow examples/exception_handling/comprehensive_examples.yaml
lexflow examples/data_structures/dictionaries.yaml
```


## Troubleshooting

### Command Not Found: lexflow

If `lexflow` command is not found after installation:

1. Make sure you've activated the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Or use `uv run`:
   ```bash
   uv run lexflow --help
   ```

3. Or install in editable mode:
   ```bash
   uv pip install -e .
   ```

### Import Errors

If you see import errors when running workflows:

1. Ensure all dependencies are installed:
   ```bash
   uv sync --all-extras
   ```

2. Check that you're in the correct directory:
   ```bash
   pwd  # Should be lex-flow root
   ```

3. For AI opcodes, install the AI extra:
   ```bash
   uv sync --extra ai
   ```

### Python Version Issues

LexFlow requires Python 3.10 or higher:

```bash
# Check your Python version
python --version

# UV will use the correct Python version automatically
uv python list
uv python install 3.12  # Install specific version if needed
```

## Program Serialization (v0.2.0+)

LexFlow Programs can be serialized to JSON for caching, persistence, or network transmission. This is useful for API services, databases, and distributed systems.

### Basic Serialization

```python
from lexflow import Parser, Program

# Parse a workflow
parser = Parser()
workflow_data = {
    "workflows": [{
        "name": "main",
        "interface": {"inputs": [], "outputs": []},
        "variables": {"x": 10},
        "nodes": {
            "start": {"opcode": "workflow_start", "next": None, "inputs": {}}
        }
    }]
}
program = parser.parse_dict(workflow_data)

# Serialize to JSON string
program_json = program.model_dump_json()

# Deserialize from JSON string
program2 = Program.model_validate_json(program_json)

# Programs are now identical
assert program2.main.name == program.main.name
```

### Use Cases

**1. Redis Caching:**
```python
import redis
from lexflow import Parser, Program

# Parse and cache
parser = Parser()
program = parser.parse_dict(workflow_data)

redis_client = redis.Redis()
redis_client.set(f"workflow:{id}", program.model_dump_json())

# Retrieve and execute
program_json = redis_client.get(f"workflow:{id}")
program = Program.model_validate_json(program_json)

from lexflow import Engine
engine = Engine(program)
result = await engine.run()
```

**2. Database Storage:**
```python
from sqlalchemy import Column, String, JSON
from lexflow import Program

class WorkflowModel(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True)
    program_data = Column(JSON)  # Store as JSONB in PostgreSQL

# Save
program_dict = program.model_dump(mode='python')
db_workflow = WorkflowModel(id="workflow-123", program_data=program_dict)
session.add(db_workflow)
session.commit()

# Load
db_workflow = session.query(WorkflowModel).get("workflow-123")
program = Program.model_validate(db_workflow.program_data)
```

**3. FastAPI Service:**
```python
from fastapi import FastAPI
from lexflow import Parser, Engine, Program

app = FastAPI()

@app.post("/parse")
async def parse_workflow(workflow_data: dict):
    parser = Parser()
    program = parser.parse_dict(workflow_data)
    # Return serialized program
    return {"program_json": program.model_dump_json()}

@app.post("/execute")
async def execute_workflow(program_json: str, inputs: dict = {}):
    # Deserialize program
    program = Program.model_validate_json(program_json)

    # Execute
    engine = Engine(program)
    result = await engine.run(inputs=inputs)

    return {"result": result}
```

### How It Works

LexFlow uses Pydantic discriminated unions with type discriminators:

```python
# Each AST node has a 'type' field
literal = Literal(value=42)
print(literal.type)  # "Literal"

variable = Variable(name="x")
print(variable.type)  # "Variable"

# JSON includes type information
{"type": "Literal", "value": 42}
{"type": "Variable", "name": "x"}
```

This allows Pydantic to correctly reconstruct the union types (Expression and Statement) when deserializing from JSON.
