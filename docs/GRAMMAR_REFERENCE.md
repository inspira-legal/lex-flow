# LexFlow Grammar Reference

Reference for all LexFlow language constructs (control flow, data operations, etc.).

> **Note:** This file is auto-generated from `grammar.json`. Run `lexflow docs generate --grammar` to update.

**Grammar Version:** 1.1

## Table of Contents

- [Categories](#categories)
- [Node Syntax](#node-syntax)
- [Control Flow Constructs](#control-flow-constructs)
- [Data Operations](#data-operations)
- [Workflow Operations](#workflow-operations)
- [Colors Reference](#colors-reference)

## Categories

| ID | Label | Prefix | Color | Icon |
|:---|:------|:-------|:------|:-----|
| `io` | I/O Operations | `io_` | `#22D3EE` | 📤 |
| `operator` | Operators | `operator_` | `#9C27B0` | ⚡ |
| `math` | Math Operations | `math_` | `#8B5CF6` | 🔢 |
| `string` | String Operations | `string_` | `#F472B6` | 📝 |
| `list` | List Operations | `list_` | `#3B82F6` | 📋 |
| `dict` | Dictionary Operations | `dict_` | `#F59E0B` | 📖 |
| `object` | Object Operations | `object_` | `#10B981` | 📦 |
| `type` | Type Conversions | `type_` | `#6B7280` | 🔄 |
| `throw` | Exception Operations | `throw_` | `#EF4444` | ⚠️ |
| `assert` | Assertion Operations | `assert_` | `#F97316` | ✓ |
| `workflow` | Workflow Operations | `workflow_` | `#E91E63` | 🔗 |
| `data` | Data Operations | `data_` | `#4CAF50` | 📦 |
| `control` | Control Flow | `control_` | `#FF9500` | ↻ |
| `async` | Async Operations | `async_` | `#06B6D4` | ⏱ |
| `pydantic_ai` | AI Operations (Pydantic AI) | `pydantic_ai_` | `#10B981` | 🤖 |
| `http` | HTTP Operations | `http_` | `#3B82F6` | 🌐 |
| `sheets` | Google Sheets Operations | `sheets_` | `#34A853` | 📊 |
| `html` | HTML Operations | `html_` | `#E34F26` | 📄 |
| `json` | JSON Operations | `json_` | `#F59E0B` | 📋 |
| `hubspot` | HubSpot Operations | `hubspot_` | `#FF7A59` | hubspot |
| `web_search` | Web Search | `web_search` | `#8B5CF6` | 🔍 |
| `apollo` | Apollo.io | `apollo_` | `#4A90D9` | 🚀 |
| `clicksign` | Clicksign Operations | `clicksign_` | `#4B0082` | clicksign |
| `gcs` | Cloud Storage | `gcs_` | `#4285F4` | ☁️ |
| `receitaws` | ReceitaWS Operations | `receitaws_` | `#009C3B` | receitaws |
| `rag` | RAG Operations | `rag_` | `#8B5CF6` | 🔍 |
| `pgvector` | PgVector Operations | `pgvector_` | `#336791` | 🐘 |
| `chat` | Chat Operations | `chat_` | `#6366F1` | 💬 |
| `cli` | CLI Operations | `cli_` | `#EC4899` | 💻 |
| `github` | GitHub Operations | `github_` | `#24292F` | 🐙 |
| `pubsub` | Pub/Sub | `pubsub_` | `#EA4335` | 📨 |
| `task` | Task Operations | `task_` | `#0EA5E9` | ⚡ |
| `channel` | Channel Operations | `channel_` | `#14B8A6` | 📡 |
| `sync` | Sync Primitives | `sync_` | `#A855F7` | 🔒 |
| `slack` | Slack | `slack_` | `#4A154B` | 💬 |

## Node Syntax

A node passes its arguments with `args` (a positional list), `kwargs`
(a mapping of parameter names), or both:

```yaml
greet:
  opcode: string_join
  args:
    - literal: ["Hello", "World"]
  kwargs:
    delimiter: { literal: " " }
```

Constructs use the slot names in the tables below, all lowercase:

```yaml
gate:
  opcode: control_if_else
  kwargs:
    condition: { node: is_ready }
    then: { branch: run }
    else: { branch: skip }
```

Slots that hold several values are lists: `args` for a fork's branches,
a call's arguments and a return's values, and `catch` for a try's
handlers. `workflow_call` names the callee in `workflow` and passes any
other keyword straight to the workflow's parameters.

### Legacy `inputs`

The older form is a single `inputs` mapping, still accepted and still
parsed exactly as before: for an opcode its keys are labels only and
the order binds, and for a construct the slots are UPPERCASE
(`CONDITION`, `THEN`, `BRANCH1`, `CATCH1`, ...). A node may not carry
both forms. Run `lexflow migrate <path>` to convert.

## Control Flow Constructs

### `control_if`

**If** - Execute branch if condition is true.

- **AST Class:** `If`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `condition` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `then` | Then | `#66BB6A` | Yes |

---

### `control_if_else`

**If-Else** - Execute then-branch if condition is true, else-branch otherwise.

- **AST Class:** `If`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `condition` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `then` | Then | `#66BB6A` | Yes |
| `else` | Else | `#EF5350` | Yes |

---

### `control_while`

**While** - Repeat body while condition is true.

- **AST Class:** `While`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `condition` | `expression` (bool) | Condition | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

### `control_for`

**For** - For loop with counter variable.

- **AST Class:** `For`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `var` | `variable_name` (-) | Variable | Yes | - |
| `start` | `expression` (int) | Start | Yes | - |
| `end` | `expression` (int) | End | Yes | - |
| `step` | `expression` (int) | Step | No | `1` |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

### `control_foreach`

**ForEach** - Iterate over each item in a collection.

- **AST Class:** `ForEach`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `var` | `variable_name` (-) | Variable | Yes | - |
| `iterable` | `expression` (list) | Iterable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

### `control_fork`

**Fork** - Execute multiple branches concurrently.

- **AST Class:** `Fork`
- **Category:** `control`

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `args` | Branches | `#9C27B0` | Yes |

*This construct supports dynamic branches.*

---

### `control_try`

**Try** - Exception handling with try/catch/finally.

- **AST Class:** `Try`
- **Category:** `control`

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `try` | Try | `#3B82F6` | Yes |
| `catch` | Catch | `#F87171` | No |
| `finally` | Finally | `#FACC15` | No |

*This construct supports dynamic branches.*

---

### `control_throw`

**Throw** - Raise an exception with a message.

- **AST Class:** `Throw`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `value` | `expression` (string) | Message | Yes | - |

---

### `control_spawn`

**Spawn** - Spawn a background task.

- **AST Class:** `Spawn`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `var` | `variable_name` (-) | Task Variable | No | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

### `control_async_foreach`

**Async ForEach** - Async iteration over a stream or async iterable.

- **AST Class:** `AsyncForEach`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `var` | `variable_name` (-) | Variable | Yes | - |
| `iterable` | `expression` (async_iterable) | Async Iterable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

### `async_timeout`

**Timeout** - Execute body with a timeout, with optional fallback.

- **AST Class:** `Timeout`
- **Category:** `async`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `timeout` | `expression` (float) | Timeout (seconds) | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |
| `on_timeout` | On Timeout | `#FACC15` | No |

---

### `control_with`

**With** - Async context manager (with statement).

- **AST Class:** `With`
- **Category:** `control`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `resource` | `expression` (-) | Resource | Yes | - |
| `var` | `variable_name` (-) | Variable | Yes | - |

**Branches:**

| Name | Label | Color | Required |
|:-----|:------|:------|:---------|
| `body` | Body | `#22D3EE` | Yes |

---

## Data Operations

### `data_set_variable_to`

**Set Variable** - Assign a value to a variable.

- **AST Class:** `Assign`
- **Category:** `data`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `variable` | `variable_name` (-) | Variable | Yes | - |
| `value` | `expression` (-) | Value | Yes | - |

---

## Workflow Operations

### `workflow_return`

**Return** - Return value(s) from workflow.

- **AST Class:** `Return`
- **Category:** `workflow`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `args` | `expression` (-) | Values | No | - |

*This construct supports dynamic inputs (e.g., ARG1, ARG2, ...).*

---

### `workflow_call`

**Call Workflow** - Call another workflow by name.

- **AST Class:** `ExprStmt`
- **Category:** `workflow`

**Inputs:**

| Name | Type | Label | Required | Default |
|:-----|:-----|:------|:---------|:--------|
| `workflow` | `variable_name` (-) | Workflow Name | Yes | - |

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
| `then` | `#34D399` |
| `else` | `#F87171` |
| `body` | `#22D3EE` |
| `try` | `#3B82F6` |
| `catch` | `#F87171` |
| `finally` | `#FACC15` |
| `on_timeout` | `#FACC15` |
| `args` | `#9C27B0` |
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

- **Categories:** 35
- **Constructs:** 17
- **Control Flow:** 12
- **Data Operations:** 1
- **Workflow Operations:** 3
