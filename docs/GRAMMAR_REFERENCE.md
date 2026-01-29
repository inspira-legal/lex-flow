# LexFlow Grammar Reference

Reference for all LexFlow language constructs (control flow, data operations, etc.).

> **Note:** This file is auto-generated from `grammar.json`. Run `lexflow docs generate --grammar` to update.

**Grammar Version:** 1.0

## Table of Contents

- [Categories](#categories)
- [Control Flow Constructs](#control-flow-constructs)
- [Data Operations](#data-operations)
- [Workflow Operations](#workflow-operations)
- [Colors Reference](#colors-reference)

## Categories

| ID | Label | Prefix | Color | Icon |
|:---|:------|:-------|:------|:-----|
| `control` | Control Flow | `control_` | `#FF9500` | ⟳ |
| `data` | Data | `data_` | `#4CAF50` | 📦 |
| `io` | I/O | `io_` | `#22D3EE` | 📤 |
| `operator` | Operators | `operator_` | `#9C27B0` | ⚡ |
| `list` | Lists | `list_` | `#3B82F6` | 📋 |
| `dict` | Dicts | `dict_` | `#F59E0B` | 📖 |
| `string` | Strings | `string_` | `#F472B6` | 📝 |
| `math` | Math | `math_` | `#8B5CF6` | 🔢 |
| `workflow` | Workflow | `workflow_` | `#E91E63` | 🔗 |
| `async` | Async | `async_` | `#06B6D4` | ⏱ |

## Control Flow Constructs

### `control_if`

**If** - Execute branch if condition is true.

- **AST Class:** `If`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `CONDITION` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `THEN` | Then | `#66BB6A` | Yes |

---

### `control_if_else`

**If-Else** - Execute then-branch if condition is true, else-branch otherwise.

- **AST Class:** `If`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `CONDITION` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `THEN` | Then | `#66BB6A` | Yes |
| `ELSE` | Else | `#EF5350` | Yes |

---

### `control_while`

**While** - Repeat body while condition is true.

- **AST Class:** `While`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `CONDITION` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

### `control_for`

**For** - For loop with counter variable.

- **AST Class:** `For`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VAR` | `variable_name` (-) | Variable | Yes | - |
| `START` | `expression` (int) | Start | Yes | - |
| `END` | `expression` (int) | End | Yes | - |
| `STEP` | `expression` (int) | Step | No | `1` |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

### `control_foreach`

**ForEach** - Iterate over each item in a collection.

- **AST Class:** `ForEach`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VAR` | `variable_name` (-) | Variable | Yes | - |
| `ITERABLE` | `expression` (list) | Iterable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

### `control_fork`

**Fork** - Execute multiple branches concurrently.

- **AST Class:** `Fork`
- **Category:** `control`

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BRANCH1` | Branch 1 | `#9C27B0` | Yes |
| `BRANCH2` | Branch 2 | `#9C27B0` | No |

*This construct supports dynamic branches.*

---

### `control_try`

**Try** - Exception handling with try/catch/finally.

- **AST Class:** `Try`
- **Category:** `control`

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `TRY` | Try | `#3B82F6` | Yes |
| `CATCH1` | Catch | `#F87171` | No |
| `FINALLY` | Finally | `#FACC15` | No |

*This construct supports dynamic branches.*

---

### `control_throw`

**Throw** - Raise an exception with a message.

- **AST Class:** `Throw`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VALUE` | `expression` (string) | Message | Yes | - |

---

### `control_spawn`

**Spawn** - Spawn a background task.

- **AST Class:** `Spawn`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VAR` | `variable_name` (-) | Task Variable | No | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

### `control_async_foreach`

**Async ForEach** - Async iteration over a stream or async iterable.

- **AST Class:** `AsyncForEach`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VAR` | `variable_name` (-) | Variable | Yes | - |
| `ITERABLE` | `expression` (async_iterable) | Async Iterable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

### `async_timeout`

**Timeout** - Execute body with a timeout, with optional fallback.

- **AST Class:** `Timeout`
- **Category:** `async`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `TIMEOUT` | `expression` (float) | Timeout (seconds) | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |
| `ON_TIMEOUT` | On Timeout | `#FACC15` | No |

---

### `control_with`

**With** - Async context manager (with statement).

- **AST Class:** `With`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `RESOURCE` | `expression` (-) | Resource | Yes | - |
| `VAR` | `variable_name` (-) | Variable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `BODY` | Body | `#22D3EE` | Yes |

---

## Data Operations

### `data_set_variable_to`

**Set Variable** - Assign a value to a variable.

- **AST Class:** `Assign`
- **Category:** `data`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VARIABLE` | `variable_name` (-) | Variable | Yes | - |
| `VALUE` | `expression` (-) | Value | Yes | - |

---

## Workflow Operations

### `workflow_return`

**Return** - Return value(s) from workflow.

- **AST Class:** `Return`
- **Category:** `workflow`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `VALUE` | `expression` (-) | Value | No | - |

*This construct supports dynamic inputs (e.g., ARG1, ARG2, ...).*

---

### `workflow_call`

**Call Workflow** - Call another workflow by name.

- **AST Class:** `ExprStmt`
- **Category:** `workflow`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `WORKFLOW` | `variable_name` (-) | Workflow Name | Yes | - |

*This construct supports dynamic inputs (e.g., ARG1, ARG2, ...).*

---

### `workflow_start`

**Start** - Entry point for workflow execution.

- **AST Class:** `None`
- **Category:** `workflow`

---

## Colors Reference

### Branch Colors

| Branch | Color |
|:-------|:------|
| `THEN` | `#34D399` |
| `ELSE` | `#F87171` |
| `BODY` | `#22D3EE` |
| `TRY` | `#3B82F6` |
| `CATCH` | `#F87171` |
| `FINALLY` | `#FACC15` |
| `ON_TIMEOUT` | `#FACC15` |
| `BRANCH` | `#9C27B0` |
| `default` | `#9C27B0` |

### Node Colors

| Node Type | Color |
|:----------|:------|
| `control_flow` | `#FF9500` |
| `data` | `#4CAF50` |
| `io` | `#22D3EE` |
| `operator` | `#9C27B0` |
| `workflow_op` | `#E91E63` |
| `opcode` | `#64748B` |

### Reporter Colors

| Category | Color |
|:---------|:------|
| `data` | `#4CAF50` |
| `operator` | `#9C27B0` |
| `io` | `#22D3EE` |
| `workflow` | `#E91E63` |
| `default` | `#64748B` |

## Summary

- **Categories:** 10
- **Constructs:** 16
- **Control Flow:** 12
- **Data Operations:** 1
- **Workflow Operations:** 3
