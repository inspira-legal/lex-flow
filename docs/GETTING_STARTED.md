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
