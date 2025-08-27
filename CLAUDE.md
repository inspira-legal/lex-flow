# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running Commands

### Basic execution
```bash
python main.py -f examples/hello_world.json
```

### Development dependencies
```bash
pip install -r requirements.txt
```

## Architecture Overview

Lex Flow is a JSON-based workflow interpreter that executes visual programming workflows. The system follows a modular opcode architecture:

### Core Components

- **Engine (`core/engine.py`)**: Main execution engine that processes workflow steps using a program counter and call stack
- **Parser (`core/parser.py`)**: Currently minimal, workflows are loaded directly as JSON
- **Models (`core/models.py`)**: Pydantic models defining Program, Workflow, Node, and RuntimeNode structures
- **State Management (`core/state.py`)**: WorkflowState handles execution context, variables, and call stack
- **Opcode System (`core/opcodes.py`)**: Plugin architecture using decorators and automatic discovery

### Opcode Categories

- **Control Flow (`opcodes/control.py`)**: Flow control operations
- **Data Operations (`opcodes/data.py`)**: Variable manipulation  
- **Events (`opcodes/events.py`)**: Event handling (start events, etc.)
- **I/O Operations (`opcodes/io.py`)**: Print and input operations
- **Operators (`opcodes/operators.py`)**: Mathematical and logical operations

### JSON Workflow Format

Workflows are defined in JSON with this structure:
- `workflows[]`: Array of workflow objects
- `workflows[].nodes{}`: Dictionary of node definitions with opcode, inputs, and flow control
- `workflows[].variables{}`: Variable definitions with format `[name, value]`
- Input types: `1` (literal), `2` (node reference), `3` (variable reference)

### Execution Model

The engine uses a step-based execution model:
1. Load workflow JSON into Pydantic models
2. Initialize engine with first workflow 
3. Step through nodes using program counter
4. Handle node references via call stack frames
5. Execute opcodes with automatic plugin discovery

## Testing

The system uses JSON test files in `examples/` directory. Run tests with:
```bash
python main.py -f examples/comprehensive_test.json
```

Available test files demonstrate various opcode functionality including math operations, logic, I/O, and variable manipulation.