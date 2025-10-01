# Exception Handling in LexFlow

## Overview

LexFlow provides native exception handling that leverages Python's built-in try-except-finally mechanism. This gives you robust error handling with minimal complexity while maintaining clean visual workflow design.

## Table of Contents

- [Basic Concepts](#basic-concepts)
- [Try-Catch Syntax](#try-catch-syntax)
- [Exception Types](#exception-types)
- [Catch Handlers](#catch-handlers)
- [Finally Blocks](#finally-blocks)
- [Throwing Exceptions](#throwing-exceptions)
- [Variable Scope](#variable-scope)
- [Best Practices](#best-practices)
- [Complete Examples](#complete-examples)

---

## Basic Concepts

### What is Exception Handling?

Exception handling allows your workflow to gracefully handle errors and unexpected conditions without crashing. When an error occurs, you can:

- Catch the error and recover
- Display a user-friendly message
- Clean up resources (files, connections, etc.)
- Continue execution with fallback logic

### Key Components

1. **Try Block** - Code that might throw an exception
2. **Catch Handlers** - Code that handles specific exceptions
3. **Finally Block** - Code that always runs (cleanup)
4. **Throw Statements** - Explicitly raise exceptions

---

## Try-Catch Syntax

### Basic Structure

```yaml
try_node:
  opcode: control_try
  next: after_try
  inputs:
    TRY:
      branch: risky_operation
    CATCH1:
      exception_type: "ValueError"
      var: "error"
      body:
        branch: handle_error
    FINALLY:
      branch: cleanup
```

### Components Explained

**TRY Input:**

- **Type:** Branch reference
- **Purpose:** Points to the first node of code that might throw an exception
- **Required:** Yes

**CATCH Inputs (CATCH1, CATCH2, etc.):**

- **Type:** Object with three fields
- **Fields:**
  - `exception_type` (optional): String name of exception class (e.g., "ValueError")
  - `var` (optional): Variable name to bind exception message
  - `body` (required): Branch reference to handler code
- **Required:** At least one catch handler

**FINALLY Input:**

- **Type:** Branch reference
- **Purpose:** Code that always executes (even if exception occurs)
- **Required:** No

---

## Exception Types

### Built-in Exception Types

LexFlow supports catching any Python exception by name:

| Exception Type      | When It Occurs         | Example                            |
| ------------------- | ---------------------- | ---------------------------------- |
| `ValueError`        | Invalid value provided | Converting "abc" to integer        |
| `TypeError`         | Wrong type used        | Adding string to number            |
| `ZeroDivisionError` | Division by zero       | `10 / 0`                           |
| `AssertionError`    | Assertion fails        | `assert_true` with false condition |
| `RuntimeError`      | General runtime error  | Generic errors                     |
| `KeyError`          | Missing dictionary key | Accessing non-existent key         |
| `IndexError`        | Invalid list index     | `list[100]` on small list          |
| `AttributeError`    | Missing attribute      | Accessing undefined attribute      |

### Catch-All Handler

Use `exception_type: null` to catch any exception:

```yaml
CATCH1:
  exception_type: null # Catches everything
  var: "error"
  body:
    branch: handle_any_error
```

**Best Practice:** Put catch-all handlers **last** after specific handlers.

---

## Catch Handlers

### Single Handler

Catches one specific exception type:

```yaml
try_node:
  opcode: control_try
  inputs:
    TRY:
      branch: divide
    CATCH1:
      exception_type: "ZeroDivisionError"
      var: "err"
      body:
        branch: handle_division_error
```

### Multiple Handlers

Handlers are checked in order (CATCH1, CATCH2, CATCH3...):

```yaml
try_node:
  opcode: control_try
  inputs:
    TRY:
      branch: risky_code
    CATCH1:
      exception_type: "ValueError"
      var: "err"
      body:
        branch: handle_value_error
    CATCH2:
      exception_type: "TypeError"
      var: "err"
      body:
        branch: handle_type_error
    CATCH3:
      exception_type: null # Catch-all (last)
      var: "err"
      body:
        branch: handle_other
```

**Execution Flow:**

1. Try block executes
2. If exception occurs, check CATCH1
3. If doesn't match, check CATCH2
4. Continue until match found
5. If no match, exception propagates

### Exception Variable Binding

The `var` field creates a variable containing the exception message:

```yaml
CATCH1:
  exception_type: "ValueError"
  var: "error_message" # Variable name
  body:
    branch: handle_error

# In the handler:
print_error:
  opcode: io_print
  inputs:
    STRING:
      variable: error_message # Access the error message
```

**What the variable contains:**

- String representation of the exception message
- Example: `"integer division or modulo by zero"`
- Example: `"invalid literal for int() with base 10: 'abc'"`

---

## Finally Blocks

### Purpose

Finally blocks **always execute**, regardless of:

- Whether an exception occurred
- Whether the exception was caught
- Whether the try block completed successfully

### Common Uses

1. **Resource cleanup:**

```yaml
try_node:
  opcode: control_try
  inputs:
    TRY:
      branch: read_file
    CATCH1:
      exception_type: null
      body:
        branch: handle_error
    FINALLY:
      branch: close_file # Always runs
```

2. **Logging:**

```yaml
FINALLY:
  branch: log_operation # Log success or failure
```

3. **State restoration:**

```yaml
FINALLY:
  branch: restore_state # Reset variables
```

### Try-Finally Without Catch

You can use finally without catch for cleanup only:

```yaml
try_node:
  opcode: control_try
  inputs:
    TRY:
      branch: do_work
    FINALLY:
      branch: cleanup
```

If an exception occurs, it will propagate after the finally block executes.

---

## Throwing Exceptions

### Two Ways to Throw

#### 1. control_throw Statement

For dynamic error messages (uses expression evaluation):

```yaml
throw_node:
  opcode: control_throw
  next: will_not_execute
  inputs:
    VALUE:
      literal: "User authentication failed"
```

Can use expressions:

```yaml
throw_node:
  opcode: control_throw
  inputs:
    VALUE:
      node: build_error_message # Uses reporter node
```

Creates a `RuntimeError` exception.

#### 2. Throw Opcodes

For specific exception types:

**throw** - Generic RuntimeError:

```yaml
throw_node:
  opcode: throw
  inputs:
    message:
      literal: "Something went wrong"
```

**throw_value_error** - ValueError:

```yaml
throw_node:
  opcode: throw_value_error
  inputs:
    message:
      literal: "Invalid input provided"
```

**throw_type_error** - TypeError:

```yaml
throw_node:
  opcode: throw_type_error
  inputs:
    message:
      literal: "Wrong type used"
```

**throw_assertion_error** - AssertionError:

```yaml
throw_node:
  opcode: throw_assertion_error
  inputs:
    message:
      literal: "Assertion failed"
```

### Assertion Opcodes

**assert_true** - Throw if condition is false:

```yaml
validate:
  opcode: assert_true
  inputs:
    condition:
      node: check_valid
    message:
      literal: "Validation failed"
```

**assert_equals** - Throw if values not equal:

```yaml
validate:
  opcode: assert_equals
  inputs:
    left:
      variable: expected
    right:
      variable: actual
    message:
      literal: "Values don't match"
```

---

## Variable Scope

### Lifetime

Exception variables created by `var` in catch handlers:

- ✅ **Created:** When catch block executes
- ✅ **Lifetime:** Entire workflow (not just the catch block)
- ✅ **Deallocated:** When workflow completes

### Scope Example

```yaml
workflows:
  - name: main
    variables: {}
    nodes:
      # First try-catch
      try1:
        opcode: control_try
        inputs:
          CATCH1:
            var: "err" # Creates "err" variable

      # Can still access "err" here!
      print_after_try:
        opcode: io_print
        inputs:
          STRING:
            variable: err # Still works

      # Second try-catch overwrites
      try2:
        opcode: control_try
        inputs:
          CATCH1:
            var: "err" # Overwrites "err"
```

### Best Practices for Scope

1. **Use unique names for different try-catch blocks:**

```yaml
CATCH1:
  var: "parse_error"

# Later...
CATCH1:
  var: "network_error"
```

2. **Or reuse intentionally to overwrite:**

```yaml
CATCH1:
  var: "error"  # General error variable

# Later...
CATCH1:
  var: "error"  # Overwrites previous
```

3. **Document lifetime in comments:**

```yaml
# Note: "err" persists for entire workflow
CATCH1:
  var: "err"
```

---

## Best Practices

### 1. Specific Handlers First

```yaml
# ✅ Good: Specific to general
CATCH1:
  exception_type: "ValueError"
CATCH2:
  exception_type: "TypeError"
CATCH3:
  exception_type: null # Catch-all last
```

```yaml
# ❌ Bad: Catch-all first
CATCH1:
  exception_type: null # Catches everything!
CATCH2:
  exception_type: "ValueError" # Never reached
```

### 2. Always Bind Error Messages

```yaml
# ✅ Good: Can see what went wrong
CATCH1:
  exception_type: "ValueError"
  var: "error_msg"  # Enables debugging

# ❌ Less useful: No error details
CATCH1:
  exception_type: "ValueError"
  # No var field
```

### 3. Use Finally for Cleanup

```yaml
# ✅ Good: Guaranteed cleanup
try_node:
  inputs:
    TRY:
      branch: open_and_process_file
    CATCH1:
      exception_type: null
      body:
        branch: handle_error
    FINALLY:
      branch: close_file # Always closes
```

### 4. Choose Right Throw Method

- **control_throw**: Dynamic messages, expressions
- **throw_value_error**: When you know the type
- **assert_true**: For validation

### 5. Provide Helpful Error Messages

```yaml
# ✅ Good: Clear context
throw_value_error:
  inputs:
    message:
      literal: "User ID must be a positive integer, got: -5"

# ❌ Bad: Vague
throw_value_error:
  inputs:
    message:
      literal: "Invalid input"
```

---

## Complete Examples

### Example 1: Safe Division

```yaml
workflows:
  - name: safe_divide
    variables:
      result: 0
    nodes:
      start:
        opcode: workflow_start
        next: try_divide

      try_divide:
        opcode: control_try
        next: print_result
        inputs:
          TRY:
            branch: attempt_divide
          CATCH1:
            exception_type: "ZeroDivisionError"
            var: "err"
            body:
              branch: use_default

      attempt_divide:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE:
            literal: result
          VALUE:
            node: calc_divide

      calc_divide:
        opcode: operator_divide
        inputs:
          left: { literal: 100 }
          right: { literal: 0 }
        isReporter: true

      use_default:
        opcode: data_set_variable_to
        next: print_error
        inputs:
          VARIABLE:
            literal: result
          VALUE:
            literal: 0

      print_error:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Warning: Division by zero, using default value\n"

      print_result:
        opcode: io_print
        next: null
        inputs:
          STRING:
            variable: result
```

### Example 2: Input Validation

```yaml
workflows:
  - name: validate_input
    variables:
      value: 0
    nodes:
      start:
        opcode: workflow_start
        next: try_validate

      try_validate:
        opcode: control_try
        next: process_valid_input
        inputs:
          TRY:
            branch: check_range
          CATCH1:
            exception_type: "AssertionError"
            var: "validation_error"
            body:
              branch: show_validation_error

      check_range:
        opcode: assert_true
        next: check_positive
        inputs:
          condition:
            node: in_range
          message:
            literal: "Value must be between 1 and 100"

      in_range:
        opcode: operator_and
        inputs:
          left:
            node: greater_than_zero
          right:
            node: less_than_hundred
        isReporter: true

      greater_than_zero:
        opcode: operator_greater_than
        inputs:
          left: { variable: value }
          right: { literal: 0 }
        isReporter: true

      less_than_hundred:
        opcode: operator_less_than
        inputs:
          left: { variable: value }
          right: { literal: 101 }
        isReporter: true
```

### Example 3: Try-Catch-Finally with Cleanup

```yaml
workflows:
  - name: process_file
    variables:
      file_open: false
    nodes:
      start:
        opcode: workflow_start
        next: try_process

      try_process:
        opcode: control_try
        next: print_done
        inputs:
          TRY:
            branch: open_file
          CATCH1:
            exception_type: null
            var: "file_error"
            body:
              branch: handle_file_error
          FINALLY:
            branch: cleanup

      open_file:
        opcode: data_set_variable_to
        next: process_contents
        inputs:
          VARIABLE:
            literal: file_open
          VALUE:
            literal: true

      process_contents:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Processing file...\n"

      handle_file_error:
        opcode: io_print
        next: print_error_msg
        inputs:
          STRING:
            literal: "Error processing file: "

      print_error_msg:
        opcode: io_print
        next: null
        inputs:
          STRING:
            variable: file_error

      cleanup:
        opcode: control_if_else
        inputs:
          CONDITION:
            variable: file_open
          BRANCH1:
            branch: close_file
          BRANCH2:
            branch: skip_close

      close_file:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Closing file...\n"
```

---

## Exception Propagation Through Workflows

### How It Works

Exceptions **automatically propagate** through workflow calls using Python's native exception mechanism. This means you can catch exceptions from called workflows in the calling workflow.

### Example: Basic Propagation

```yaml
workflows:
  - name: main
    nodes:
      try_call:
        opcode: control_try
        inputs:
          TRY:
            branch: call_helper
          CATCH1:
            exception_type: "ValueError"
            var: "err"
            body:
              branch: handle_error

      call_helper:
        opcode: workflow_call
        inputs:
          WORKFLOW:
            literal: helper_that_throws

  - name: helper_that_throws
    nodes:
      throw_error:
        opcode: throw_value_error
        inputs:
          message:
            literal: "Error from helper workflow"
```

**Flow:**

1. Main workflow calls `helper_that_throws`
2. Helper workflow throws ValueError
3. Exception propagates back to main
4. Main's catch handler catches it

### Nested Propagation

Exceptions propagate through multiple levels of workflow calls:

```yaml
main (try-catch)
→ workflow_a
→ workflow_b
→ workflow_c
→ throws exception
← propagates
← propagates
← propagates
→ caught by main
```

### With Parameters

Exception propagation works with parameterized workflows:

```yaml
try_call:
  opcode: control_try
  inputs:
    TRY:
      branch: call_validator
    CATCH1:
      exception_type: "AssertionError"
      var: "err"
      body:
        branch: handle_validation_error

call_validator:
  opcode: workflow_call
  inputs:
    WORKFLOW:
      literal: validate_number
    ARG1:
      variable: user_input # Exception includes parameter context
```

### Benefits

**Clean separation:**

- Helper workflows focus on logic
- Caller handles errors
- No need to return error codes

**Flexible error handling:**

- Catch at any level
- Different handlers for different callers
- Propagate through multiple layers

**Test File:**
See `examples/test_exception_propagation_workflows.yaml` for complete examples.

---

## Common Patterns

### Pattern 1: Retry Logic

```yaml
try_with_retry:
  opcode: control_try
  inputs:
    TRY:
      branch: attempt_operation
    CATCH1:
      exception_type: "ConnectionError"
      var: "err"
      body:
        branch: retry_after_delay
```

### Pattern 2: Error Logging

```yaml
catch_and_log:
  opcode: control_try
  inputs:
    TRY:
      branch: risky_operation
    CATCH1:
      exception_type: null
      var: "error"
      body:
        branch: log_error
    FINALLY:
      branch: log_completion
```

### Pattern 3: Validation Chain

```yaml
validate_all:
  opcode: control_try
  inputs:
    TRY:
      branch: validate_step1
    CATCH1:
      exception_type: "AssertionError"
      var: "validation_msg"
      body:
        branch: show_validation_error
```

---

## Troubleshooting

### Common Issues

**Issue:** Exception not caught

```yaml
# Problem: Wrong exception type
CATCH1:
  exception_type: "ValueError"  # But throws TypeError!

# Solution: Use catch-all or correct type
CATCH1:
  exception_type: "TypeError"  # Matches now
```

**Issue:** Can't access exception variable

```yaml
# Problem: Typo in variable name
CATCH1:
  var: "error_msg"

print_error:
  inputs:
    STRING:
      variable: errormsg # Missing underscore!
```

**Issue:** Finally not executing

```yaml
# If you see this, it's a bug - finally ALWAYS executes
# Check your branch reference is correct
FINALLY:
  branch: cleanup_node # Make sure this node exists
```

---

## Summary

Exception handling in LexFlow provides:

- ✅ Native Python exception support
- ✅ Multiple catch handlers with type matching
- ✅ Catch-all handlers for unknown exceptions
- ✅ Finally blocks for guaranteed cleanup
- ✅ Exception message variable binding
- ✅ Custom throw statements and opcodes
- ✅ Assertion helpers for validation

Use exception handling to build robust workflows that gracefully handle errors and provide great user experience.

For more examples, see:

- `examples/example_exception_handling.yaml` - Comprehensive real-world patterns
- `examples/example_catch_variable.yaml` - Accessing exception variables
- `examples/example_catch_variable_advanced.yaml` - Advanced variable usage
- `examples/test_exception_propagation_workflows.yaml` - Exception propagation through workflow calls
- `examples/test_try_catch_*.yaml` - All exception handling test cases
