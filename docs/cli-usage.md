# CLI Usage Guide

Lex Flow provides a powerful command-line interface for executing JSON-based visual programming workflows.

## Basic Usage

### Single Workflow File

```bash
python main.py workflow.json
```

### Multi-File Projects

```bash
# Import additional workflow files
python main.py main.json -I utils.json helpers.json

# Import from directory
python main.py main.json --import-dir modules/

# Combined imports
python main.py main.json -I extra.json --import-dir shared/
```

## Command Options

### Required Arguments

- `main_file` - The main workflow file to execute (must contain the entry point workflow)

### Import Options

- `-I, --import FILES...` - Additional workflow files to import
- `--import-dir DIRECTORY` - Directory containing workflow files to import

### Execution Options

- `--workflow NAME` - Specify which workflow to execute (default: 'main' or single workflow)
- `--debug` - Enable step-by-step debugging with user input
- `--verbose` - Show detailed execution information
- `--validate-only` - Validate workflows without executing

## File Structure

### Main vs Import Files

- **Main file**: Contains the workflow you want to execute
- **Import files**: Provide additional workflows that can be called from main

```bash
# main.json contains: main, setup workflows
# utils.json contains: add_numbers, multiply workflows
# helpers.json contains: format_output workflow
python main.py main.json -I utils.json helpers.json --workflow setup
```

### Workflow Selection

The interpreter determines which workflow to execute using this priority:

1. **Explicit selection**: `--workflow NAME`
2. **'main' workflow**: If a workflow named 'main' exists in main file
3. **Single workflow**: If main file contains only one workflow
4. **Error**: If main file has multiple workflows without explicit selection

## Execution Modes

### Normal Execution

```bash
python main.py workflow.json
[INFO] Loading workflow file: workflow.json
[SUCCESS] Loaded 1 workflow(s)
[INFO] Executing workflow: main
[INFO] Starting execution...
Hello, World!
```

### Verbose Mode

```bash
python main.py workflow.json --verbose
[INFO] Loading workflow file: workflow.json
[INFO] Main file workflows:
  main() from workflow.json
[SUCCESS] Loaded 1 workflow(s)
[INFO] Executing workflow: main
[INFO] Starting execution...
Hello, World!
[SUCCESS] Workflow completed in 2 steps
```

### Debug Mode

```bash
python main.py workflow.json --debug
[INFO] Debug mode enabled. Press Enter to step, 'q' to quit.
Step [0] completed. Continue? (Enter/q):
# Press Enter to continue, 'q' to quit
```

### Validation Only

```bash
python main.py workflow.json --validate-only
[INFO] Loading workflow file: workflow.json
[SUCCESS] Loaded 1 workflow(s)
[SUCCESS] All workflows are valid!
```

## Error Handling

The CLI provides detailed error messages with contextual suggestions:

### File Not Found

```bash
python main.py missing.json
[ERROR] JSON Error in missing.json: File not found

Suggestions:
  1. Check for missing commas, quotes, or brackets
  2. Validate JSON syntax using a JSON linter
  3. Ensure all strings are properly quoted
```

### Workflow Dependencies

```bash
[ERROR] Workflow 'missing_workflow' not found (referenced from workflow 'main')

Suggestions:
  1. Check if 'missing_workflow' is defined in any input files
  2. Verify workflow names are spelled correctly
  3. Ensure all required files are included
```

### Invalid JSON

```bash
[ERROR] JSON Error in workflow.json at line 15, column 12: Invalid JSON: Expecting ',' delimiter

Suggestions:
  1. Check for missing commas, quotes, or brackets
  2. Validate JSON syntax using a JSON linter
  3. Ensure all strings are properly quoted
```

## Examples

### Basic Workflow

```bash
# Execute a simple workflow
python main.py tests/simple_hello.json
```

### Multi-Workflow Project

```bash
# Main workflow calls functions from imported files
python main.py main.json -I math_utils.json string_utils.json
```

### Development Workflow

```bash
# Validate before execution
python main.py workflow.json --validate-only

# Debug step-by-step
python main.py workflow.json --debug

# Verbose execution for troubleshooting
python main.py workflow.json --verbose
```

### Directory-Based Projects

```bash
# Import all workflows from modules directory
python main.py app.json --import-dir modules/

# Combined file and directory imports
python main.py app.json -I core.json --import-dir plugins/
```

## Best Practices

1. **Use descriptive file names** - `math_operations.json`, not `utils.json`
2. **Organize by functionality** - Group related workflows in the same file
3. **Keep main files focused** - Main file should contain entry points only
4. **Validate before deploying** - Use `--validate-only` to catch errors early
5. **Use verbose mode for debugging** - Helps understand execution flow
6. **Leverage the import system** - Break large projects into manageable files
