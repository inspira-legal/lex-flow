# Opcode Development Guide

Opcodes are the fundamental operations in Lex Flow. This guide covers how to create custom opcodes using the modern parameter annotation system.

## Overview

Opcodes are Python classes that inherit from `BaseOpcode` and implement async operations executed by the interpreter engine. The system provides:

- **Automatic discovery** via `@opcode()` decorator
- **Type-safe parameter resolution** via `@params()` decorator  
- **Stack-based execution model** for consistent interfaces
- **Return type annotations** for documentation and tooling

## Basic Opcode Structure

### Simple Opcode
```python
from core.opcodes import opcode, BaseOpcode, params

@params(
    message={"type": str, "description": "Text to print"}
)
@opcode("io_print") 
class PrintOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        print(params["message"])
        return True  # Continue execution
```

### Modern Pattern with Helper Methods
```python
@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"}
)
@opcode("operator_add")
class AddOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._op_add(**params)
        state.push(result)
        return True

    async def _op_add(self, op1: int, op2: int) -> int:
        return op1 + op2
```

## Decorators

### @opcode(name)
Registers the opcode with the system for automatic discovery.

```python
@opcode("my_operation")       # Register as "my_operation"
@opcode()                     # Register as lowercase class name
class MyOpcode(BaseOpcode):
    pass
```

### @params(**kwargs)
Defines input parameters with type information and automatic resolution.

```python
@params(
    param_name={
        "type": str,                    # Parameter type
        "description": "What it does",  # Documentation  
        "required": True,               # Required parameter (default)
        "default": None                 # Default value if optional
    }
)
```

**Parameter Configuration**:
- `type` - Python type for validation and documentation
- `description` - Human-readable parameter description
- `required` - Whether parameter is required (default: True)
- `default` - Default value for optional parameters

## Parameter Resolution

### Automatic Parameter Resolution
The `resolve_params()` method automatically handles stack-safe parameter extraction:

```python
async def execute(self, state, stmt, engine) -> bool:
    params = self.resolve_params(state, stmt)  # Safe parameter extraction
    # params is now a dict: {"param_name": value, ...}
```

**Stack Safety**: Only pops the exact number of parameters provided in `stmt.inputs`, preventing stack corruption.

### Parameter Order
Parameters are resolved in **reverse declaration order** (LIFO from stack):

```python
@params(
    first={"type": int},
    second={"type": str}  
)
# Stack: [first_value, second_value] (top)
# Resolves: {"first": first_value, "second": second_value}
```

### Manual Stack Operations (Legacy)
For simple opcodes, you can still use manual stack operations:

```python
@opcode("simple_add")
class SimpleAdd(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        op2 = state.pop()  # Second operand (top of stack)
        op1 = state.pop()  # First operand  
        result = op1 + op2
        state.push(result)
        return True
```

## Return Value Handling

### Stack Results
Push results to stack for other operations to consume:

```python
async def execute(self, state, stmt, engine) -> bool:
    # ... computation ...
    state.push(result)
    return True
```

### Multiple Results
Push multiple values for opcodes that return multiple results:

```python
async def execute(self, state, stmt, engine) -> bool:
    quotient, remainder = divmod(dividend, divisor)
    state.push(quotient)
    state.push(remainder)  # Pushed last = top of stack
    return True
```

### Control Flow
Return `False` to stop execution (used in control flow):

```python
@opcode("workflow_return")
class ReturnOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        # Handle return value
        return False  # Stop execution
```

## Type Annotations

### Return Type Documentation
Use Python type annotations on helper methods for documentation:

```python
async def _op_divide(self, dividend: int, divisor: int) -> float:
    if divisor == 0:
        raise ValueError("Division by zero")
    return dividend / divisor
```

### Type Introspection
The system can inspect return types for tooling and documentation:

```python
@classmethod
def get_return_info(cls) -> dict:
    # Automatically extracts type information from method signatures
    # Used by visual editors and documentation generators
```

## Common Patterns

### Mathematical Operations
```python
@params(
    operand1={"type": float, "description": "First number"},
    operand2={"type": float, "description": "Second number"}
)
@opcode("math_multiply")
class MultiplyOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._multiply(**params)
        state.push(result)
        return True
        
    async def _multiply(self, operand1: float, operand2: float) -> float:
        return operand1 * operand2
```

### String Operations
```python
@params(
    text={"type": str, "description": "Text to process"},
    pattern={"type": str, "description": "Pattern to search for"},
    replacement={"type": str, "description": "Replacement text"}
)
@opcode("string_replace")  
class StringReplaceOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._replace(**params)
        state.push(result)
        return True
        
    async def _replace(self, text: str, pattern: str, replacement: str) -> str:
        return text.replace(pattern, replacement)
```

### Data Manipulation
```python
@params(
    variable_id={"type": str, "description": "Variable ID to set"},
    value={"type": Any, "description": "Value to store"}
)
@opcode("data_set_variable")
class SetVariableOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt) 
        await self._set_variable(state, **params)
        return True
        
    async def _set_variable(self, state, variable_id: str, value: Any):
        if variable_id in state._variables:
            var_name, _ = state._variables[variable_id]
            state._variables[variable_id] = (var_name, value)
```

### I/O Operations
```python
@params(
    prompt={"type": str, "description": "Input prompt to display"}
)
@opcode("io_input")
class InputOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._get_input(**params)
        state.push(result)
        return True
        
    async def _get_input(self, prompt: str) -> str:
        return input(prompt)
```

### Control Flow
```python  
@params(
    condition={"type": bool, "description": "Condition to evaluate"}
)
@opcode("control_if")
class IfOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        
        if params["condition"]:
            # Execute true branch
            true_branch = stmt.inputs.get("TRUE_BRANCH")
            if true_branch:
                statements = engine._parse_branch_chain(true_branch[1])
                await engine._execute_branch(statements)
        else:
            # Execute false branch  
            false_branch = stmt.inputs.get("FALSE_BRANCH")
            if false_branch:
                statements = engine._parse_branch_chain(false_branch[1])
                await engine._execute_branch(statements)
                
        return True
```

## Advanced Features

### Optional Parameters
```python
@params(
    text={"type": str, "description": "Text to process"},
    encoding={"type": str, "description": "Text encoding", "required": False, "default": "utf-8"}
)
@opcode("text_encode")
class EncodeOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        # params["encoding"] will be "utf-8" if not provided
        result = await self._encode(**params)
        state.push(result)
        return True
```

### Error Handling
```python
@params(
    dividend={"type": float, "description": "Number to divide"},
    divisor={"type": float, "description": "Number to divide by"}
)
@opcode("math_divide")
class DivideOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        try:
            params = self.resolve_params(state, stmt)
            result = await self._divide(**params)
            state.push(result)
            return True
        except Exception as e:
            # Push error information or re-raise
            state.push(f"Error: {e}")
            return True
            
    async def _divide(self, dividend: float, divisor: float) -> float:
        if divisor == 0:
            raise ValueError("Division by zero")
        return dividend / divisor
```

### Accessing Engine Context
```python
@params(
    workflow_name={"type": str, "description": "Workflow to call"}
)
@opcode("workflow_call")
class CallOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await engine._call_workflow(params["workflow_name"])
        if result is not None:
            state.push(result)
        return True
```

## File Organization

Organize opcodes by category in the `opcodes/` directory:

```
opcodes/
├── __init__.py
├── control.py      # if_else, while, for loops
├── data.py         # variable operations, data manipulation  
├── events.py       # workflow_start, triggers
├── functions.py    # workflow_call, workflow_return
├── io.py          # print, input, file operations
├── operators.py   # math, comparison, logical operations
├── ai.py          # AI/LLM integration
└── custom/        # Domain-specific opcodes
    ├── __init__.py
    ├── image.py
    └── network.py
```

## Testing Opcodes

### Unit Testing
```python
import pytest
from core.state import WorkflowState
from core.ast import Statement, Value, ValueType
from opcodes.operators import AddOpcode

@pytest.mark.asyncio
async def test_add_opcode():
    # Setup
    state = MockWorkflowState()
    state.push(5)
    state.push(3)
    
    stmt = Statement(opcode="operator_add", inputs={"op1": None, "op2": None})
    opcode = AddOpcode()
    
    # Execute
    result = await opcode.execute(state, stmt, None)
    
    # Assert
    assert result is True
    assert state.pop() == 8
```

### Integration Testing
Create JSON workflow files that exercise your opcodes and add them to the test suite.

## Interface Introspection

### Getting Opcode Information
```python  
from opcodes.operators import AddOpcode

# Get parameter information
param_info = AddOpcode.get_param_info()
# Returns: {"op1": ParamInfo(...), "op2": ParamInfo(...)}

# Get return information  
return_info = AddOpcode.get_return_info()
# Returns: {"type": int, "count": 1, "description": "..."}

# Get complete interface
interface = AddOpcode.get_interface()
# Returns: {"inputs": {...}, "outputs": {...}, "opcode_name": "operator_add"}
```

This information can be used by visual editors to generate appropriate UI controls and validate connections.

## Best Practices

1. **Use the modern @params pattern** - Provides type safety and documentation
2. **Implement helper methods** - Keep execute() clean, put logic in helper methods  
3. **Add comprehensive descriptions** - Document all parameters clearly
4. **Handle errors gracefully** - Don't crash the interpreter
5. **Follow naming conventions** - Use category_operation format (e.g., "math_add")
6. **Test thoroughly** - Unit test opcodes and integration test workflows
7. **Keep stack operations balanced** - Every pop() should have a corresponding push()
8. **Use type annotations** - Help with tooling and documentation generation