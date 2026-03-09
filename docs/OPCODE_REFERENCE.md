# LexFlow Opcode Reference

Quick reference for all available opcodes in LexFlow.

> **Note:** This file is auto-generated. Run `lexflow docs generate` to update.

## Table of Contents

- [📤 I/O Operations](#i/o-operations)
- [⚡ Operators](#operators)
- [🔢 Math Operations](#math-operations)
- [📝 String Operations](#string-operations)
- [📋 List Operations](#list-operations)
- [📖 Dictionary Operations](#dictionary-operations)
- [📦 Object Operations](#object-operations)
- [🔄 Type Conversions](#type-conversions)
- [⚠️ Exception Operations](#exception-operations)
- [✓ Assertion Operations](#assertion-operations)
- [🔗 Workflow Operations](#workflow-operations)
- [📦 Data Operations](#data-operations)
- [↻ Control Flow](#control-flow)
- [⏱ Async Operations](#async-operations)
- [🤖 AI Operations (Pydantic AI)](#ai-operations-pydantic-ai) *(requires `lexflow[ai]`)*
- [🌐 HTTP Operations](#http-operations) *(requires `lexflow[http]`)*
- [📊 Google Sheets Operations](#google-sheets-operations) *(requires `lexflow[sheets]`)*
- [📄 HTML Operations](#html-operations) *(requires `lexflow[http]`)*
- [📋 JSON Operations](#json-operations)
- [hubspot HubSpot Operations](#hubspot-operations) *(requires `lexflow[http]`)*
- [🔍 Web Search](#web-search) *(requires `lexflow[search]`)*
- [clicksign Clicksign Operations](#clicksign-operations) *(requires `lexflow[clicksign]`)*
- [☁️ Cloud Storage](#cloud-storage) *(requires `lexflow[gcs]`)*
- [🎮 Pygame Operations](#pygame-operations) *(requires `lexflow[pygame]`)*
- [receitaws ReceitaWS Operations](#receitaws-operations) *(requires `lexflow[receitaws]`)*
- [🔍 RAG Operations](#rag-operations) *(requires `lexflow[rag]`)*
- [🐘 PgVector Operations](#pgvector-operations) *(requires `lexflow[pgvector]`)*
- [💬 Chat Operations](#chat-operations)
- [💻 CLI Operations](#cli-operations)
- [🐙 GitHub Operations](#github-operations)
- [📨 Pub/Sub](#pub/sub) *(requires `lexflow[pubsub]`)*
- [⚡ Task Operations](#task-operations)
- [📡 Channel Operations](#channel-operations)
- [🔒 Sync Primitives](#sync-primitives)
- [💬 Slack](#slack) *(requires `lexflow[slack]`)*

## 📤 I/O Operations

### `io_input(prompt="")`

Get input from user.

**Returns:** `str`

---

### `io_print(values)`

Print values to stdout.

**Returns:** `NoneType`

---

## ⚡ Operators

### `operator_add(left, right)`

Add two values (numeric or string concatenation).

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `Any`

---

### `operator_and(left, right)`

Logical AND.

**Parameters:**

- `left` (bool, required)
- `right` (bool, required)

**Returns:** `bool`

---

### `operator_divide(left, right)`

Division (true division).

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `Any`

---

### `operator_equals(left, right)`

Check equality (with type coercion for numbers).

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_greater_than(left, right)`

Check if left > right.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_greater_than_or_equals(left, right)`

Check if left >= right.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_less_than(left, right)`

Check if left < right.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_less_than_or_equals(left, right)`

Check if left <= right.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_modulo(left, right)`

Modulo operation (remainder).

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `Any`

---

### `operator_multiply(left, right)`

Multiply two values.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `Any`

---

### `operator_not(value)`

Logical NOT.

**Returns:** `bool`

---

### `operator_not_equals(left, right)`

Check inequality.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `bool`

---

### `operator_or(left, right)`

Logical OR.

**Parameters:**

- `left` (bool, required)
- `right` (bool, required)

**Returns:** `bool`

---

### `operator_subtract(left, right)`

Subtract right from left.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)

**Returns:** `Any`

---

## 🔢 Math Operations

### `math_abs(value)`

Absolute value.

**Returns:** `Any`

---

### `math_ceil(value)`

Ceiling operation.

**Returns:** `int`

---

### `math_floor(value)`

Floor operation.

**Returns:** `int`

---

### `math_pow(base, exponent)`

Power operation.

**Parameters:**

- `base` (Any, required)
- `exponent` (Any, required)

**Returns:** `Any`

---

### `math_random(min_val, max_val)`

Generate random integer between min and max (inclusive).

**Parameters:**

- `min_val` (int, required)
- `max_val` (int, required)

**Returns:** `int`

---

### `math_sqrt(value)`

Square root.

**Returns:** `float`

---

## 📝 String Operations

### `string_contains(text, substring)`

Check if string contains substring.

**Parameters:**

- `text` (str, required)
- `substring` (str, required)

**Returns:** `bool`

---

### `string_ends_with(text, suffix)`

Check if string ends with suffix.

**Parameters:**

- `text` (str, required)
- `suffix` (str, required)

**Returns:** `bool`

---

### `string_index_of(text, substring)`

Find index of substring, returns -1 if not found.

**Parameters:**

- `text` (str, required)
- `substring` (str, required)

**Returns:** `int`

---

### `string_join(items, delimiter="")`

Join list items into string.

**Parameters:**

- `items` (list, required)
- `delimiter` (str, optional, default: `""`)

**Returns:** `str`

---

### `string_length(text)`

Get string length.

**Returns:** `int`

---

### `string_lower(text)`

Convert to lowercase.

**Returns:** `str`

---

### `string_replace(text, old, new)`

Replace all occurrences of old with new.

**Parameters:**

- `text` (str, required)
- `old` (str, required)
- `new` (str, required)

**Returns:** `str`

---

### `string_split(text, delimiter=" ")`

Split string by delimiter.

**Parameters:**

- `text` (str, required)
- `delimiter` (str, optional, default: `" "`)

**Returns:** `list[str]`

---

### `string_starts_with(text, prefix)`

Check if string starts with prefix.

**Parameters:**

- `text` (str, required)
- `prefix` (str, required)

**Returns:** `bool`

---

### `string_substring(text, start, end=None)`

Extract substring from start to end index.

Args:
    text: Source string
    start: Start index (0-based)
    end: End index (exclusive), or None for rest of string

**Parameters:**

- `text` (str, required)
- `start` (int, required)
- `end` (int, optional, default: `None`)

**Returns:** `str`

---

### `string_trim(text)`

Remove leading/trailing whitespace.

**Returns:** `str`

---

### `string_upper(text)`

Convert to uppercase.

**Returns:** `str`

---

## 📋 List Operations

### `list_append(items, value)`

Append value to list (returns new list).

**Parameters:**

- `items` (list, required)
- `value` (Any, required)

**Returns:** `list`

---

### `list_contains(items, value)`

Check if list contains value.

**Parameters:**

- `items` (list, required)
- `value` (Any, required)

**Returns:** `bool`

---

### `list_get(items, index)`

Get item at index.

**Parameters:**

- `items` (list, required)
- `index` (int, required)

**Returns:** `Any`

---

### `list_length(items)`

Get list length.

**Returns:** `int`

---

### `list_range(start, stop=None, step=1)`

Create a range as list.

**Parameters:**

- `start` (int, required)
- `stop` (int, optional, default: `None`)
- `step` (int, optional, default: `1`)

**Returns:** `list[int]`

---

## 📖 Dictionary Operations

### `dict_clear(d)`

Clear all items from dict.

**Returns:** `dict`

---

### `dict_contains(d, key)`

Check if key exists in dict.

**Parameters:**

- `d` (dict, required)
- `key` (Any, required)

**Returns:** `bool`

---

### `dict_copy(d)`

Create a shallow copy of the dict.

**Returns:** `dict`

---

### `dict_create(*args)`

Create dictionary from key-value pair arguments.

**Returns:** `dict`

---

### `dict_from_lists(keys, values)`

Create dict from parallel lists of keys and values.

**Parameters:**

- `keys` (list, required)
- `values` (list, required)

**Returns:** `dict`

---

### `dict_get(d, key, default=None)`

Get value by key with optional default.

**Parameters:**

- `d` (dict, required)
- `key` (Any, required)
- `default` (Any, optional, default: `None`)

**Returns:** `Any`

---

### `dict_is_empty(d)`

Check if dict is empty.

**Returns:** `bool`

---

### `dict_items(d)`

Get list of (key, value) tuples.

**Returns:** `list`

---

### `dict_keys(d)`

Get list of all keys.

**Returns:** `list`

---

### `dict_len(d)`

Get number of items in dict.

**Returns:** `int`

---

### `dict_pop(d, key, default=None)`

Remove and return value by key.

**Parameters:**

- `d` (dict, required)
- `key` (Any, required)
- `default` (Any, optional, default: `None`)

**Returns:** `Any`

---

### `dict_set(d, key, value)`

Set key-value pair (mutates and returns dict for chaining).

**Parameters:**

- `d` (dict, required)
- `key` (Any, required)
- `value` (Any, required)

**Returns:** `dict`

---

### `dict_setdefault(d, key, default=None)`

Set key to default if not present, return value.

**Parameters:**

- `d` (dict, required)
- `key` (Any, required)
- `default` (Any, optional, default: `None`)

**Returns:** `Any`

---

### `dict_update(d, other)`

Update dict with key-value pairs from other dict.

**Parameters:**

- `d` (dict, required)
- `other` (dict, required)

**Returns:** `dict`

---

### `dict_values(d)`

Get list of all values.

**Returns:** `list`

---

## 📦 Object Operations

### `object_create()`

Create empty object (SimpleNamespace).

**Returns:** `SimpleNamespace`

---

### `object_from_dict(d)`

Create object from dictionary.

**Returns:** `SimpleNamespace`

---

### `object_get(obj, key, default=None)`

Get property value with optional default.

**Parameters:**

- `obj` (Union[types.SimpleNamespace, dict], required)
- `key` (str, required)
- `default` (Any, optional, default: `None`)

**Returns:** `Any`

---

### `object_has(obj, key)`

Check if object has property.

**Parameters:**

- `obj` (Union[types.SimpleNamespace, dict], required)
- `key` (str, required)

**Returns:** `bool`

---

### `object_keys(obj)`

Get list of all property names.

**Returns:** `list`

---

### `object_remove(obj, key)`

Remove property (returns object for chaining).

**Parameters:**

- `obj` (Union[types.SimpleNamespace, dict], required)
- `key` (str, required)

**Returns:** `Union[types.SimpleNamespace, dict]`

---

### `object_set(obj, key, value)`

Set property value (returns object for chaining).

**Parameters:**

- `obj` (Union[types.SimpleNamespace, dict], required)
- `key` (str, required)
- `value` (Any, required)

**Returns:** `Union[types.SimpleNamespace, dict]`

---

### `object_to_dict(obj)`

Convert object to dictionary.

**Returns:** `dict`

---

## 🔄 Type Conversions

### `bool(value)`

Convert to boolean.

**Returns:** `bool`

---

### `float(value)`

Convert to float.

**Returns:** `float`

---

### `int(value)`

Convert to integer.

**Returns:** `int`

---

### `len(value)`

Get length of a value.

**Returns:** `int`

---

### `range(*args)`

Create a range as list.

**Returns:** `list[int]`

---

### `str(value)`

Convert to string.

**Returns:** `str`

---

## ⚠️ Exception Operations

### `throw(message)`

Throw a runtime error with message.

**Returns:** `NoneType`

---

### `throw_assertion_error(message)`

Throw an AssertionError.

**Returns:** `NoneType`

---

### `throw_type_error(message)`

Throw a TypeError.

**Returns:** `NoneType`

---

### `throw_value_error(message)`

Throw a ValueError.

**Returns:** `NoneType`

---

## ✓ Assertion Operations

### `assert_equals(left, right, message="Values not equal")`

Assert two values are equal.

**Parameters:**

- `left` (Any, required)
- `right` (Any, required)
- `message` (str, optional, default: `"Values not equal"`)

**Returns:** `NoneType`

---

### `assert_true(condition, message="Assertion failed")`

Assert condition is true, throw AssertionError otherwise.

**Parameters:**

- `condition` (bool, required)
- `message` (str, optional, default: `"Assertion failed"`)

**Returns:** `NoneType`

---

## 🔗 Workflow Operations

### `noop()`

No operation.

**Returns:** `NoneType`

---

### `workflow_call(workflow, *args)`

Call another workflow by name with arguments.

**Parameters:**

- `workflow` (str, required)
- `args` (Any, required)

**Returns:** `Any`

---

### `workflow_return(value=None)`

Return a value from the current workflow.

**Returns:** `NoneType`

---

### `workflow_start()`

Workflow entry point marker (no-op).

**Returns:** `NoneType`

---

## 📦 Data Operations

### `data_get_variable(var_name)`

Get variable value - handled by parser as Variable reference.

**Returns:** `Any`

---

### `data_set_variable_to(variable, value)`

Set variable to a value.

**Parameters:**

- `variable` (str, required)
- `value` (Any, required)

**Returns:** `NoneType`

---

## ↻ Control Flow

### `control_async_foreach(var, iterable, body)`

Async iterate over items in async iterable, binding each to var.

**Parameters:**

- `var` (str, required)
- `iterable` (Any, required)
- `body` (Any, required)

**Returns:** `NoneType`

---

### `control_for(var, start, end, step=1, body=None)`

Loop from start to end with step, binding each value to var.

**Parameters:**

- `var` (str, required)
- `start` (int, required)
- `end` (int, required)
- `step` (int, optional, default: `1`)
- `body` (Any, optional, default: `None`)

**Returns:** `NoneType`

---

### `control_foreach(var, iterable, body)`

Iterate over items in iterable, binding each to var.

**Parameters:**

- `var` (str, required)
- `iterable` (Any, required)
- `body` (Any, required)

**Returns:** `NoneType`

---

### `control_fork(branches)`

Execute multiple branches concurrently.

**Returns:** `NoneType`

---

### `control_if(condition, then_branch)`

Execute branch if condition is true.

**Parameters:**

- `condition` (bool, required)
- `then_branch` (Any, required)

**Returns:** `NoneType`

---

### `control_if_else(condition, then_branch, else_branch)`

Execute then_branch if condition is true, else_branch otherwise.

**Parameters:**

- `condition` (bool, required)
- `then_branch` (Any, required)
- `else_branch` (Any, required)

**Returns:** `NoneType`

---

### `control_spawn(body, var=None)`

Spawn body as a background task, optionally storing handle in var.

**Parameters:**

- `body` (Any, required)
- `var` (str, optional, default: `None`)

**Returns:** `NoneType`

---

### `control_throw(message)`

Throw a runtime error with the given message.

**Returns:** `NoneType`

---

### `control_try(try_body, catch_handlers=None, finally_body=None)`

Execute try_body with exception handling.

**Parameters:**

- `try_body` (Any, required)
- `catch_handlers` (Any, optional, default: `None`)
- `finally_body` (Any, optional, default: `None`)

**Returns:** `NoneType`

---

### `control_while(condition, body)`

Repeat body while condition is true.

**Parameters:**

- `condition` (bool, required)
- `body` (Any, required)

**Returns:** `NoneType`

---

### `control_with(resource, var, body)`

Execute body with resource as async context manager, binding to var.

**Parameters:**

- `resource` (Any, required)
- `var` (str, required)
- `body` (Any, required)

**Returns:** `NoneType`

---

## ⏱ Async Operations

### `async_from_list(items, delay=0)`

Convert a list to an async generator.

Useful for simulating streaming or rate-limited iteration.

Args:
    items: List of items to yield
    delay: Delay in seconds between yielding items

Yields:
    Each item from the list

**Parameters:**

- `items` (List[Any], required)
- `delay` (float, optional, default: `0`)

**Returns:** `AsyncGenerator[Any, NoneType]`

---

### `async_range(start, stop=None, step=1, delay=0)`

Create an async range generator.

Like range() but async, with optional delay between items.
Useful for rate-limited iteration with control_async_foreach.

Args:
    start: Start value (or stop if stop is None)
    stop: Stop value (exclusive)
    step: Step between values (default 1)
    delay: Delay in seconds between yielding values

Yields:
    Integers in the range

**Parameters:**

- `start` (int, required)
- `stop` (int, optional, default: `None`)
- `step` (int, optional, default: `1`)
- `delay` (float, optional, default: `0`)

**Returns:** `AsyncGenerator[int, NoneType]`

---

### `async_timeout(timeout, body, on_timeout=None)`

Execute body with timeout, optionally running on_timeout if exceeded.

**Parameters:**

- `timeout` (float, required)
- `body` (Any, required)
- `on_timeout` (Any, optional, default: `None`)

**Returns:** `NoneType`

---

## 🤖 AI Operations (Pydantic AI)

> **Requires:** `pip install lexflow[ai]`

### `ai_agent_with_tools(agent, messages, tools, output=None, max_tool_calls=10, timeout_seconds=300.0)`

Run an AI agent with access to LexFlow opcodes and workflows as tools.

This opcode enables agentic workflows where the LLM can reason about
and call LexFlow opcodes or workflows to accomplish tasks.

Args:
    agent: Pre-created agent from pydantic_ai_create_agent
    messages: String prompt or list of {role, content} message dicts.
             If string, normalizes to [{role: "user", content: <string>}]
    tools: List of tools the agent is allowed to call. Can be:
           - String: opcode name (e.g., "operator_add")
           - Dict: workflow reference (e.g., {"workflow": "my_workflow"})
    output: Optional schema for structured output: {text: "string", data: {...}}
    max_tool_calls: Maximum number of tool calls allowed (default: 10)
    timeout_seconds: Timeout for entire operation in seconds (default: 300)

Returns:
    Dict with {text: str, data: Any} containing the agent's response

Raises:
    PermissionError: If agent tries to call a tool not in the allowlist
    ValueError: If tools don't exist or messages format is invalid
    TimeoutError: If execution exceeds timeout_seconds
    RuntimeError: If max_tool_calls exceeded, LLM/tool error, or
                 workflow tools used without WorkflowManager context

Example YAML:
    agent_call:
      opcode: ai_agent_with_tools
      isReporter: true
      inputs:
        agent: {variable: "my_agent"}
        messages: {literal: "Calculate 15 * 23"}
        tools:
          literal:
            - operator_multiply
            - operator_add
            - {workflow: "custom_calculation"}
        max_tool_calls: {literal: 5}
        timeout_seconds: {literal: 30}

Note:
    This is a reporter opcode (isReporter: true, no next).
    To avoid re-execution, store the result in a variable immediately.

    Workflow tools require the workflow to be defined in the same file
    or included via --include. The workflow's interface.description
    is used as the tool description for the LLM.

    When tools are provided, the agent is re-created internally.
    Only model, instructions, and system_prompts are preserved from
    the original agent. Other config (result_validators, model_settings,
    etc.) is not carried over.

**Parameters:**

- `agent` (Any, required)
- `messages` (Union[str, List[dict]], required)
- `tools` (List[Union[str, dict]], required)
- `output` (Optional[dict], optional, default: `None`)
- `max_tool_calls` (int, optional, default: `10`)
- `timeout_seconds` (float, optional, default: `300.0`)

**Returns:** `dict`

---

### `pydantic_ai_create_agent(model, instructions="", system_prompt="")`

Create a pydantic_ai Agent.

Args:
    model: Model instance (from pydantic_ai_create_vertex_model)
    instructions: Optional instructions for the agent
    system_prompt: Optional static system prompt

Returns:
    Agent instance ready to use

**Parameters:**

- `model` (Any, required)
- `instructions` (str, optional, default: `""`)
- `system_prompt` (str, optional, default: `""`)

**Returns:** `Any`

---

### `pydantic_ai_create_vertex_model(model_name, project=None, location=None)`

Create a Google Vertex AI model instance.

Args:
    model_name: Model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
    project: Optional GCP project ID (uses default if not specified)
    location: Optional region (e.g., "us-central1")

Returns:
    GoogleModel instance configured for Vertex AI

**Parameters:**

- `model_name` (str, required)
- `project` (Optional[str], optional, default: `None`)
- `location` (Optional[str], optional, default: `None`)

**Returns:** `Any`

---

### `pydantic_ai_run(agent, prompt)`

Run agent asynchronously with a prompt.

Args:
    agent: Agent instance (from pydantic_ai_create_agent)
    prompt: User prompt to send to the agent

Returns:
    String output from the agent

**Parameters:**

- `agent` (Any, required)
- `prompt` (str, required)

**Returns:** `str`

---

### `pydantic_ai_run_sync(agent, prompt)`

Run agent with a prompt (legacy name, actually async).

Args:
    agent: Agent instance (from pydantic_ai_create_agent)
    prompt: User prompt to send to the agent

Returns:
    String output from the agent

**Parameters:**

- `agent` (Any, required)
- `prompt` (str, required)

**Returns:** `str`

---

## 🌐 HTTP Operations

> **Requires:** `pip install lexflow[http]`

### `http_get(url, headers=None, timeout=30.0)`

Perform an HTTP GET request.

Args:
    url: The URL to request
    headers: Optional dictionary of HTTP headers
    timeout: Request timeout in seconds (default: 30.0)

Returns:
    Response dict with keys: status, headers, text, json

**Parameters:**

- `url` (str, required)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict[str, Any]`

---

### `http_post(url, data=None, json=None, headers=None, timeout=30.0)`

Perform an HTTP POST request.

Args:
    url: The URL to request
    data: Form data to send (for form-encoded POST)
    json: JSON data to send (sets Content-Type automatically)
    headers: Optional dictionary of HTTP headers
    timeout: Request timeout in seconds (default: 30.0)

Returns:
    Response dict with keys: status, headers, text, json

**Parameters:**

- `url` (str, required)
- `data` (Optional[Dict[str, Any]], optional, default: `None`)
- `json` (Optional[Dict[str, Any]], optional, default: `None`)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict[str, Any]`

---

### `http_request(method, url, data=None, json=None, headers=None, timeout=30.0)`

Perform a generic HTTP request with any method.

Args:
    method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
    url: The URL to request
    data: Form data to send
    json: JSON data to send (sets Content-Type automatically)
    headers: Optional dictionary of HTTP headers
    timeout: Request timeout in seconds (default: 30.0)

Returns:
    Response dict with keys: status, headers, text, json

**Parameters:**

- `method` (str, required)
- `url` (str, required)
- `data` (Optional[Dict[str, Any]], optional, default: `None`)
- `json` (Optional[Dict[str, Any]], optional, default: `None`)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict[str, Any]`

---

### `http_session_create(timeout=30.0, headers=None)`

Create an HTTP session for reuse with control_with.

Args:
    timeout: Default request timeout in seconds
    headers: Default headers for all requests

Returns:
    HTTPSession object (use with control_with)

**Parameters:**

- `timeout` (float, optional, default: `30.0`)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)

**Returns:** `HTTPSession`

---

### `http_session_get(session, url, headers=None)`

Perform GET request using a session.

Args:
    session: HTTPSession from http_session_create
    url: The URL to request
    headers: Optional additional headers

Returns:
    Response dict (same as http_get)

**Parameters:**

- `session` (HTTPSession, required)
- `url` (str, required)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `http_session_post(session, url, data=None, json=None, headers=None)`

Perform POST request using a session.

Args:
    session: HTTPSession from http_session_create
    url: The URL to request
    data: Form data to send
    json: JSON data to send
    headers: Optional additional headers

Returns:
    Response dict (same as http_post)

**Parameters:**

- `session` (HTTPSession, required)
- `url` (str, required)
- `data` (Optional[Dict[str, Any]], optional, default: `None`)
- `json` (Optional[Dict[str, Any]], optional, default: `None`)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `http_stream_chunks(url, chunk_size=8192, headers=None, timeout=30.0)`

Stream chunks from an HTTP response.

Args:
    url: The URL to request
    chunk_size: Size of each chunk in bytes (default: 8192)
    headers: Optional dictionary of HTTP headers
    timeout: Request timeout in seconds (default: 30.0)

Yields:
    Byte chunks from the response

**Parameters:**

- `url` (str, required)
- `chunk_size` (int, optional, default: `8192`)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `AsyncGenerator[bytes, NoneType]`

---

### `http_stream_lines(url, headers=None, timeout=30.0)`

Stream lines from an HTTP response.

Yields each line as it becomes available. Useful for streaming APIs
like Server-Sent Events or newline-delimited JSON.

Args:
    url: The URL to request
    headers: Optional dictionary of HTTP headers
    timeout: Request timeout in seconds (default: 30.0)

Yields:
    Each line from the response (stripped of newlines)

**Parameters:**

- `url` (str, required)
- `headers` (Optional[Dict[str, str]], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `AsyncGenerator[str, NoneType]`

---

## 📊 Google Sheets Operations

> **Requires:** `pip install lexflow[sheets]`

### `sheets_append(client, spreadsheet_id, range_notation, values, value_input_option="RAW")`

Append rows to a Google Sheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    range_notation: Range to append after (e.g., "Sheet1!A:D")
    values: 2D list of values to append (each inner list is a row)
    value_input_option: "RAW" for raw values, "USER_ENTERED" for formulas

Returns:
    Response dict with updatedCells, updatedRows, updatedRange

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range_notation: "Sheet1!A:C"
    values: [["Alice", 30, "alice@example.com"]]

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `range_notation` (Any, required)
- `values` (Any, required)
- `value_input_option` (Any, optional, default: `"RAW"`)

**Returns:** `Any`

---

### `sheets_clear(client, spreadsheet_id, range_notation)`

Clear values from a Google Sheet range.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    range_notation: Range in A1 notation to clear (e.g., "Sheet1!A1:D10")

Returns:
    Response dict with clearedRange

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range_notation: "Sheet1!A2:D100"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `range_notation` (Any, required)

**Returns:** `Any`

---

### `sheets_create_client(credentials_path=None)`

Create a Google Sheets client for API operations.

Args:
    credentials_path: Path to service account JSON file. If None,
        uses Application Default Credentials (ADC).

Returns:
    SheetsClient object to use with other sheets_* opcodes

Example with Service Account:
    credentials_path: "/path/to/service-account.json"

Example with ADC (after running 'gcloud auth application-default login'):
    # No arguments needed

**Returns:** `Any`

---

### `sheets_create_sheet(client, spreadsheet_id, title)`

Create a new sheet (tab) in a spreadsheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    title: Name for the new sheet

Returns:
    Dict with sheetId and title of the created sheet

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    title: "New Sheet"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `title` (Any, required)

**Returns:** `Any`

---

### `sheets_delete_sheet(client, spreadsheet_id, sheet_id)`

Delete a sheet (tab) from a spreadsheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    sheet_id: The sheet ID to delete (from sheets_list_sheets)

Returns:
    Dict with success status

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    sheet_id: 123456789

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `sheet_id` (Any, required)

**Returns:** `Any`

---

### `sheets_get_column(client, spreadsheet_id, sheet_name, column)`

Read a specific column from a Google Sheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    sheet_name: Name of the sheet (tab)
    column: Column letter (e.g., "A", "B", "AA")

Returns:
    List of values in the column (excluding empty trailing cells)

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    sheet_name: "Sheet1"
    column: "A"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `sheet_name` (Any, required)
- `column` (Any, required)

**Returns:** `Any`

---

### `sheets_get_last_row(client, spreadsheet_id, sheet_name)`

Get the number of the last row with data in a sheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    sheet_name: Name of the sheet (tab)

Returns:
    Last row number with data (0 if sheet is empty)

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    sheet_name: "Sheet1"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `sheet_name` (Any, required)

**Returns:** `Any`

---

### `sheets_get_row(client, spreadsheet_id, sheet_name, row_number)`

Read a specific row from a Google Sheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    sheet_name: Name of the sheet (tab)
    row_number: Row number (1-indexed)

Returns:
    List of values in the row

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    sheet_name: "Sheet1"
    row_number: 5

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `sheet_name` (Any, required)
- `row_number` (Any, required)

**Returns:** `Any`

---

### `sheets_get_values(client, spreadsheet_id, range_notation)`

Read values from a Google Sheet range.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    range_notation: Range in A1 notation (e.g., "Sheet1!A1:D10")

Returns:
    2D list of values (rows x columns). Empty cells are empty strings.

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range_notation: "Sheet1!A1:D10"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `range_notation` (Any, required)

**Returns:** `Any`

---

### `sheets_list_sheets(client, spreadsheet_id)`

List all sheets (tabs) in a spreadsheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)

Returns:
    List of dicts with sheetId, title, index for each sheet

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)

**Returns:** `Any`

---

### `sheets_test_connection(client, spreadsheet_id, range_notation="A1:B2")`

Test connection to a Google Sheet.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    range_notation: Range to test reading (default: "A1:B2")

Returns:
    True if connection successful, raises exception otherwise

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `range_notation` (Any, optional, default: `"A1:B2"`)

**Returns:** `Any`

---

### `sheets_update(client, spreadsheet_id, range_notation, values, value_input_option="RAW")`

Update values in a Google Sheet range.

Args:
    client: SheetsClient from sheets_create_client
    spreadsheet_id: The spreadsheet ID (from URL)
    range_notation: Range in A1 notation (e.g., "Sheet1!A1:D10")
    values: 2D list of values (rows x columns)
    value_input_option: "RAW" for raw values, "USER_ENTERED" for formulas

Returns:
    Response dict with updatedCells, updatedRows, updatedColumns

Example:
    client: { node: create_client }
    spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    range_notation: "Sheet1!A1:C1"
    values: [["Name", "Age", "Email"]]

**Parameters:**

- `client` (Any, required)
- `spreadsheet_id` (Any, required)
- `range_notation` (Any, required)
- `values` (Any, required)
- `value_input_option` (Any, optional, default: `"RAW"`)

**Returns:** `Any`

---

## 📄 HTML Operations

> **Requires:** `pip install lexflow[http]`

### `html_get_attr(element, attr, default=None)`

Get an attribute value from an HTML element.

Args:
    element: BeautifulSoup element
    attr: Attribute name (e.g., "href", "class", "id")
    default: Value to return if attribute not found

Returns:
    Attribute value as string, or default if not found

**Parameters:**

- `element` (Any, required)
- `attr` (str, required)
- `default` (Optional[str], optional, default: `None`)

**Returns:** `Optional[str]`

---

### `html_get_text(element, strip=True)`

Get the text content from an HTML element.

Args:
    element: BeautifulSoup element
    strip: Whether to strip whitespace (default: True)

Returns:
    Text content of the element

**Parameters:**

- `element` (Any, required)
- `strip` (bool, optional, default: `True`)

**Returns:** `str`

---

### `html_parse(html_text)`

Parse an HTML string into a BeautifulSoup object.

Args:
    html_text: HTML content as a string

Returns:
    BeautifulSoup object for use with html_select* opcodes

**Returns:** `Any`

---

### `html_select(soup, selector)`

Select elements matching a CSS selector.

Args:
    soup: BeautifulSoup object or element (from html_parse)
    selector: CSS selector string

Returns:
    List of matching elements (may be empty)

**Parameters:**

- `soup` (Any, required)
- `selector` (str, required)

**Returns:** `List[Any]`

---

### `html_select_one(soup, selector)`

Select the first element matching a CSS selector.

Args:
    soup: BeautifulSoup object or element (from html_parse)
    selector: CSS selector string

Returns:
    First matching element, or None if no match

**Parameters:**

- `soup` (Any, required)
- `selector` (str, required)

**Returns:** `Optional[Any]`

---

## 📋 JSON Operations

### `json_parse(text)`

Parse a JSON string into a Python object.

Args:
    text: JSON string to parse

Returns:
    Parsed Python object (dict, list, str, int, float, bool, or None)

Raises:
    ValueError: If the string is not valid JSON

**Returns:** `Any`

---

### `json_stringify(obj, indent=None)`

Convert a Python object to a JSON string.

Args:
    obj: Python object to serialize
    indent: Number of spaces for indentation (None for compact)

Returns:
    JSON string representation

Raises:
    TypeError: If the object is not JSON serializable

**Parameters:**

- `obj` (Any, required)
- `indent` (Optional[int], optional, default: `None`)

**Returns:** `str`

---

## hubspot HubSpot Operations

> **Requires:** `pip install lexflow[http]`

### `hubspot_associate(client, from_type, from_id, to_type, to_id, association_type=None)`

Create an association between two HubSpot objects.

Args:
    client: HubSpotClient from hubspot_create_client
    from_type: Source object type (contacts, companies, deals, tickets)
    from_id: Source object ID
    to_type: Target object type (contacts, companies, deals, tickets)
    to_id: Target object ID
    association_type: Integer association type ID (HubSpot v4 API).
        If not provided, auto-inferred from object types.
        Common IDs: contacts→companies=1, companies→contacts=2,
        deals→contacts=3, contacts→deals=4, deals→companies=5,
        companies→deals=6, tickets→contacts=15, contacts→tickets=16.
        See: https://developers.hubspot.com/docs/api/crm/associations

Returns:
    Association response object

Example - Associate contact with company (auto-inferred):
    client: { node: create_client }
    from_type: "contacts"
    from_id: "12345"
    to_type: "companies"
    to_id: "67890"

Example - Associate with explicit type ID:
    client: { node: create_client }
    from_type: "deals"
    from_id: "11111"
    to_type: "contacts"
    to_id: "12345"
    association_type: 3

**Parameters:**

- `client` (HubSpotClient, required)
- `from_type` (str, required)
- `from_id` (str, required)
- `to_type` (str, required)
- `to_id` (str, required)
- `association_type` (Optional[int], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_close_client(client)`

Close a HubSpot client and release its resources.

Args:
    client: HubSpotClient to close

Returns:
    True when the client session is closed

**Returns:** `bool`

---

### `hubspot_create_client(access_token)`

Create a HubSpot API client for CRM operations.

Args:
    access_token: HubSpot private app access token

Returns:
    HubSpotClient object to use with other hubspot_* opcodes

Example:
    access_token: "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Returns:** `HubSpotClient`

---

### `hubspot_create_company(client, properties)`

Create a new company in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    properties: Dict of company properties (e.g., name, domain, industry)

Returns:
    Created company object with id, properties, createdAt

Example:
    client: { node: create_client }
    properties:
      name: "Acme Corp"
      domain: "acme.com"
      industry: "Technology"

**Parameters:**

- `client` (HubSpotClient, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `hubspot_create_contact(client, properties)`

Create a new contact in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    properties: Dict of contact properties (e.g., firstname, lastname, email)

Returns:
    Created contact object with id, properties, createdAt

Example:
    client: { node: create_client }
    properties:
      firstname: "John"
      lastname: "Doe"
      email: "john.doe@example.com"

**Parameters:**

- `client` (HubSpotClient, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `hubspot_create_deal(client, properties)`

Create a new deal in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    properties: Dict of deal properties (e.g., dealname, amount, dealstage)

Returns:
    Created deal object with id, properties, createdAt

Example:
    client: { node: create_client }
    properties:
      dealname: "New Business Deal"
      amount: "10000"
      dealstage: "appointmentscheduled"

**Parameters:**

- `client` (HubSpotClient, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `hubspot_delete_contact(client, contact_id)`

Delete a contact from HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    contact_id: The HubSpot contact ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    contact_id: "12345"

**Parameters:**

- `client` (HubSpotClient, required)
- `contact_id` (str, required)

**Returns:** `bool`

---

### `hubspot_get_associations(client, from_type, object_id, to_type)`

Get associated object IDs for a HubSpot object.

Args:
    client: HubSpotClient from hubspot_create_client
    from_type: Source object type (contacts, companies, deals, tickets)
    object_id: Source object ID
    to_type: Target object type (contacts, companies, deals, tickets)

Returns:
    List of associated object IDs as strings

Example - Get contacts associated with a deal:
    client: { node: create_client }
    from_type: "deals"
    object_id: "12345"
    to_type: "contacts"

**Parameters:**

- `client` (HubSpotClient, required)
- `from_type` (str, required)
- `object_id` (str, required)
- `to_type` (str, required)

**Returns:** `List[str]`

---

### `hubspot_get_company(client, company_id, properties=None)`

Get a company by ID from HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    company_id: The HubSpot company ID
    properties: List of property names to return (default: all)

Returns:
    Company object with id, properties, createdAt, updatedAt

Example:
    client: { node: create_client }
    company_id: "67890"
    properties: ["name", "domain", "industry"]

**Parameters:**

- `client` (HubSpotClient, required)
- `company_id` (str, required)
- `properties` (Optional[List[str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_get_contact(client, contact_id, properties=None)`

Get a contact by ID from HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    contact_id: The HubSpot contact ID
    properties: List of property names to return (default: all)

Returns:
    Contact object with id, properties, createdAt, updatedAt

Example:
    client: { node: create_client }
    contact_id: "12345"
    properties: ["firstname", "lastname", "email"]

**Parameters:**

- `client` (HubSpotClient, required)
- `contact_id` (str, required)
- `properties` (Optional[List[str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_get_deal(client, deal_id, properties=None)`

Get a deal by ID from HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    deal_id: The HubSpot deal ID
    properties: List of property names to return (default: all)

Returns:
    Deal object with id, properties, createdAt, updatedAt

Example:
    client: { node: create_client }
    deal_id: "11111"
    properties: ["dealname", "amount", "dealstage"]

**Parameters:**

- `client` (HubSpotClient, required)
- `deal_id` (str, required)
- `properties` (Optional[List[str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_list_properties(client, object_type)`

List all properties for a HubSpot object type.

Args:
    client: HubSpotClient from hubspot_create_client
    object_type: Object type (contacts, companies, deals)

Returns:
    List of property objects with name, label, type, description

Example:
    client: { node: create_client }
    object_type: "contacts"

**Parameters:**

- `client` (HubSpotClient, required)
- `object_type` (str, required)

**Returns:** `List[Dict[str, Any]]`

---

### `hubspot_search_companies(client, filters, properties=None, limit=100)`

Search companies in HubSpot using filters.

Args:
    client: HubSpotClient from hubspot_create_client
    filters: List of filter objects with propertyName, operator, value.
        Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
    properties: List of property names to return
    limit: Maximum number of results (default: 100, max: 100)

Returns:
    Dict with 'results' list and 'total' count

Example:
    client: { node: create_client }
    filters:
      - propertyName: "domain"
        operator: "EQ"
        value: "hubspot.com"
    properties: ["name", "domain", "industry"]
    limit: 10

**Parameters:**

- `client` (HubSpotClient, required)
- `filters` (List[Dict[str, Any]], required)
- `properties` (Optional[List[str]], optional, default: `None`)
- `limit` (int, optional, default: `100`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_search_contacts(client, filters, properties=None, limit=100)`

Search contacts in HubSpot using filters.

Args:
    client: HubSpotClient from hubspot_create_client
    filters: List of filter objects with propertyName, operator, value.
        Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
    properties: List of property names to return
    limit: Maximum number of results (default: 100, max: 100)

Returns:
    Dict with 'results' list and 'total' count

Example:
    client: { node: create_client }
    filters:
      - propertyName: "email"
        operator: "EQ"
        value: "test@example.com"
    properties: ["firstname", "lastname", "email"]
    limit: 10

**Parameters:**

- `client` (HubSpotClient, required)
- `filters` (List[Dict[str, Any]], required)
- `properties` (Optional[List[str]], optional, default: `None`)
- `limit` (int, optional, default: `100`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_search_deals(client, filters, properties=None, limit=100)`

Search deals in HubSpot using filters.

Args:
    client: HubSpotClient from hubspot_create_client
    filters: List of filter objects with propertyName, operator, value.
        Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
    properties: List of property names to return
    limit: Maximum number of results (default: 100, max: 100)

Returns:
    Dict with 'results' list and 'total' count

Example:
    client: { node: create_client }
    filters:
      - propertyName: "dealstage"
        operator: "EQ"
        value: "closedwon"
    properties: ["dealname", "amount", "dealstage"]
    limit: 10

**Parameters:**

- `client` (HubSpotClient, required)
- `filters` (List[Dict[str, Any]], required)
- `properties` (Optional[List[str]], optional, default: `None`)
- `limit` (int, optional, default: `100`)

**Returns:** `Dict[str, Any]`

---

### `hubspot_test_connection(client)`

Test connection to HubSpot API.

Args:
    client: HubSpotClient from hubspot_create_client

Returns:
    True if connection successful, raises exception otherwise

Example:
    client: { node: create_client }

**Returns:** `bool`

---

### `hubspot_update_company(client, company_id, properties)`

Update an existing company in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    company_id: The HubSpot company ID
    properties: Dict of company properties to update

Returns:
    Updated company object

Example:
    client: { node: create_client }
    company_id: "67890"
    properties:
      industry: "Software"
      numberofemployees: "100"

**Parameters:**

- `client` (HubSpotClient, required)
- `company_id` (str, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `hubspot_update_contact(client, contact_id, properties)`

Update an existing contact in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    contact_id: The HubSpot contact ID
    properties: Dict of contact properties to update

Returns:
    Updated contact object

Example:
    client: { node: create_client }
    contact_id: "12345"
    properties:
      firstname: "Jane"
      phone: "+1234567890"

**Parameters:**

- `client` (HubSpotClient, required)
- `contact_id` (str, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `hubspot_update_deal(client, deal_id, properties)`

Update an existing deal in HubSpot.

Args:
    client: HubSpotClient from hubspot_create_client
    deal_id: The HubSpot deal ID
    properties: Dict of deal properties to update

Returns:
    Updated deal object

Example:
    client: { node: create_client }
    deal_id: "11111"
    properties:
      amount: "15000"
      dealstage: "closedwon"

**Parameters:**

- `client` (HubSpotClient, required)
- `deal_id` (str, required)
- `properties` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

## 🔍 Web Search

> **Requires:** `pip install lexflow[search]`

### `web_search(query, client=None, max_results=5, search_depth="basic", include_domains=None, exclude_domains=None, time_range=None)`

Perform a general web search using Tavily API.

Args:
    query: The search query string
    client: TavilyClient from web_search_create_client (optional, falls back to env var)
    max_results: Maximum number of results to return (default: 5)
    search_depth: Search depth - "basic" or "advanced" (default: "basic")
    include_domains: List of domains to include in search (optional)
    exclude_domains: List of domains to exclude from search (optional)
    time_range: Time range filter - "day", "week", "month", or "year" (optional)

Returns:
    Dict with keys:
    - query: The original query string
    - results: List of result dicts with title, url, content, score
    - response_time: Time taken for the search in seconds

Example:
    query: "Python 3.12 new features"
    max_results: 5
    search_depth: "basic"

**Parameters:**

- `query` (str, required)
- `client` (lexflow.opcodes.opcodes_web_search.TavilyClient | None, optional, default: `None`)
- `max_results` (int, optional, default: `5`)
- `search_depth` (str, optional, default: `"basic"`)
- `include_domains` (Optional[List[str]], optional, default: `None`)
- `exclude_domains` (Optional[List[str]], optional, default: `None`)
- `time_range` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `web_search_context(query, client=None, max_results=5, max_tokens=4000)`

Search the web and return context optimized for RAG/agent prompts.

Returns a plain string of search results ready to be injected directly
into LLM prompts via Tavily's get_search_context().

Args:
    query: The search query string
    client: TavilyClient from web_search_create_client (optional, falls back to env var)
    max_results: Maximum number of results to include (default: 5)
    max_tokens: Maximum tokens in the returned context (default: 4000)

Returns:
    A formatted string containing search results optimized for use
    as context in LLM prompts.

Example:
    query: "quantum computing applications 2024"
    max_results: 5
    max_tokens: 4000

**Parameters:**

- `query` (str, required)
- `client` (lexflow.opcodes.opcodes_web_search.TavilyClient | None, optional, default: `None`)
- `max_results` (int, optional, default: `5`)
- `max_tokens` (int, optional, default: `4000`)

**Returns:** `str`

---

### `web_search_create_client(api_key)`

Create a Tavily API client for web search operations.

Args:
    api_key: Tavily API key

Returns:
    TavilyClient instance to pass to other web_search opcodes

Example:
    api_key: "tvly-xxxxxxxxxxxxxxxxxxxxxxxx"

**Returns:** `TavilyClient`

---

### `web_search_news(query, client=None, max_results=5, time_range="week")`

Search for news articles using Tavily API.

This is a specialized search focused on news content with a default
time range of one week for recent news.

Args:
    query: The search query string
    client: TavilyClient from web_search_create_client (optional, falls back to env var)
    max_results: Maximum number of results to return (default: 5)
    time_range: Time range filter - "day", "week", "month", or "year"
               (default: "week")

Returns:
    Dict with keys:
    - query: The original query string
    - results: List of result dicts with title, url, content, score
    - response_time: Time taken for the search in seconds

Example:
    query: "artificial intelligence breakthroughs"
    max_results: 5
    time_range: "week"

**Parameters:**

- `query` (str, required)
- `client` (lexflow.opcodes.opcodes_web_search.TavilyClient | None, optional, default: `None`)
- `max_results` (int, optional, default: `5`)
- `time_range` (str, optional, default: `"week"`)

**Returns:** `Dict[str, Any]`

---

## clicksign Clicksign Operations

> **Requires:** `pip install lexflow[clicksign]`

### `clicksign_activate_envelope(client, envelope_id)`

Activate an envelope to start the signing process.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    Updated envelope object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_add_authentication(client, envelope_id, document_id, signer_id, auth="email")`

Add an authentication requirement to an envelope.

Requires a signer to provide evidence (e.g., email, SMS, selfie)
before signing a document.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    document_id: The document ID
    signer_id: The signer ID
    auth: Authentication type (e.g., "email", "sms", "pix", "selfie",
        "handwritten", "liveness", "official_document", "icpbr_certificate")

Returns:
    Created requirement object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    document_id: "dddddddd-dddd-dddd-dddd-dddddddddddd"
    signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
    auth: "email"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `document_id` (str, required)
- `signer_id` (str, required)
- `auth` (str, optional, default: `"email"`)

**Returns:** `Dict[str, Any]`

---

### `clicksign_add_document_from_template(client, envelope_id, template_id, filename, data)`

Add a document to an envelope using a template.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    template_id: The template ID to use
    filename: Name for the generated document
    data: Template variable data to fill in

Returns:
    Created document object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    template_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    filename: "contract.pdf"
    data:
      name: "John Doe"
      value: "10000"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `template_id` (str, required)
- `filename` (str, required)
- `data` (Dict[str, Any], required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_add_document_from_upload(client, envelope_id, filename, content_base64)`

Add a document to an envelope by uploading base64 content.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    filename: Name for the uploaded document
    content_base64: Base64-encoded file content

Returns:
    Created document object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    filename: "contract.pdf"
    content_base64: "JVBERi0xLjQK..."

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `filename` (str, required)
- `content_base64` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_add_qualification(client, envelope_id, document_id, signer_id, action="agree", role="sign")`

Add a signing qualification requirement to an envelope.

Links a signer to a document with a specific action and role.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    document_id: The document ID
    signer_id: The signer ID
    action: Action type (e.g., "agree", "sign", "approve", "acknowledge")
    role: Signer role (e.g., "sign", "witness", "intervening", "receipt")

Returns:
    Created requirement object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    document_id: "dddddddd-dddd-dddd-dddd-dddddddddddd"
    signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
    action: "agree"
    role: "sign"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `document_id` (str, required)
- `signer_id` (str, required)
- `action` (str, optional, default: `"agree"`)
- `role` (str, optional, default: `"sign"`)

**Returns:** `Dict[str, Any]`

---

### `clicksign_add_signer(client, envelope_id, name, email, phone_number=None, documentation=None, has_documentation=False, birthday=None, refusable=False, group=0, communicate_events=None)`

Add a signer to an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    name: Full name of the signer (must have at least 2 words)
    email: Email address of the signer
    phone_number: Phone number with country code (e.g., "+5511999999999")
    documentation: CPF or CNPJ document number
    has_documentation: Whether the signer has documentation (default: False)
    birthday: Birthday in ISO 8601 format (e.g., "1990-01-15")
    refusable: Whether the signer can refuse to sign (default: False)
    group: Signing group/order (default: 0)
    communicate_events: Event notification config (e.g., {"sign": "email"})

Returns:
    Created signer object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    name: "John Doe"
    email: "john@example.com"
    phone_number: "+5511999999999"
    refusable: true

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `name` (str, required)
- `email` (str, required)
- `phone_number` (Optional[str], optional, default: `None`)
- `documentation` (Optional[str], optional, default: `None`)
- `has_documentation` (bool, optional, default: `False`)
- `birthday` (Optional[str], optional, default: `None`)
- `refusable` (bool, optional, default: `False`)
- `group` (int, optional, default: `0`)
- `communicate_events` (Optional[Dict[str, str]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `clicksign_batch_requirements(client, envelope_id, requirements)`

Create multiple requirements in a single batch request.

Each requirement in the list should contain action, role (or auth),
document_id, and signer_id.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    requirements: List of requirement dicts, each with keys:
        - action: Action type (e.g., "agree", "provide_evidence")
        - document_id: The document ID
        - signer_id: The signer ID
        - role: Signer role (for qualifications)
        - auth: Auth type (for authentications)

Returns:
    Batch creation response (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    requirements:
      - action: "agree"
        role: "sign"
        document_id: "doc-id-1"
        signer_id: "signer-id-1"
      - action: "provide_evidence"
        auth: "email"
        document_id: "doc-id-1"
        signer_id: "signer-id-1"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `requirements` (List[Dict[str, Any]], required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_cancel_envelope(client, envelope_id)`

Cancel an active envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    Updated envelope object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_close_client(client)`

Close a Clicksign client and release its resources.

Args:
    client: ClicksignClient to close

Returns:
    True when the client session is closed

**Returns:** `bool`

---

### `clicksign_create_client(access_token, sandbox=True)`

Create a Clicksign API client for digital signing operations.

Args:
    access_token: Clicksign API access token
    sandbox: Use sandbox environment (default: True)

Returns:
    ClicksignClient object to use with other clicksign_* opcodes

Example:
    access_token: "your-access-token"
    sandbox: true

**Parameters:**

- `access_token` (str, required)
- `sandbox` (bool, optional, default: `True`)

**Returns:** `ClicksignClient`

---

### `clicksign_create_envelope(client, name, locale="pt-BR", auto_close=True, remind_interval="3", block_after_refusal=False, deadline_at=None)`

Create a new signing envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    name: Name of the envelope
    locale: Envelope locale (default: pt-BR)
    auto_close: Auto-close after all signers sign (default: True)
    remind_interval: Reminder interval in days (default: "3")
    block_after_refusal: Block envelope after a signer refuses (default: False)
    deadline_at: Optional deadline in ISO 8601 format

Returns:
    Created envelope object (JSON:API response)

Example:
    client: { node: create_client }
    name: "Contract 2024"
    locale: "pt-BR"
    auto_close: true

**Parameters:**

- `client` (ClicksignClient, required)
- `name` (str, required)
- `locale` (str, optional, default: `"pt-BR"`)
- `auto_close` (bool, optional, default: `True`)
- `remind_interval` (str, optional, default: `"3"`)
- `block_after_refusal` (bool, optional, default: `False`)
- `deadline_at` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `clicksign_create_webhook(client, url, events)`

Create a webhook subscription for envelope events.

Args:
    client: ClicksignClient from clicksign_create_client
    url: URL to receive webhook POST requests
    events: List of event types to subscribe to (e.g.,
        ["envelope.closed", "signer.signed", "envelope.canceled"])

Returns:
    Created webhook object (JSON:API response)

Example:
    client: { node: create_client }
    url: "https://my-app.com/webhooks/clicksign"
    events:
      - "envelope.closed"
      - "signer.signed"

**Parameters:**

- `client` (ClicksignClient, required)
- `url` (str, required)
- `events` (List[str], required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_delete_document(client, envelope_id, document_id)`

Delete a document from an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    document_id: The document ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `document_id` (str, required)

**Returns:** `bool`

---

### `clicksign_delete_envelope(client, envelope_id)`

Delete an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `bool`

---

### `clicksign_delete_requirement(client, envelope_id, requirement_id)`

Delete a requirement from an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    requirement_id: The requirement ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    requirement_id: "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `requirement_id` (str, required)

**Returns:** `bool`

---

### `clicksign_delete_signer(client, envelope_id, signer_id)`

Delete a signer from an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    signer_id: The signer ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `signer_id` (str, required)

**Returns:** `bool`

---

### `clicksign_delete_webhook(client, webhook_id)`

Delete a webhook subscription.

Args:
    client: ClicksignClient from clicksign_create_client
    webhook_id: The webhook ID

Returns:
    True if deletion was successful

Example:
    client: { node: create_client }
    webhook_id: "wwwwwwww-wwww-wwww-wwww-wwwwwwwwwwww"

**Parameters:**

- `client` (ClicksignClient, required)
- `webhook_id` (str, required)

**Returns:** `bool`

---

### `clicksign_get_document(client, envelope_id, document_id)`

Get a document from an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    document_id: The document ID

Returns:
    Document object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `document_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_get_envelope(client, envelope_id)`

Get an envelope by ID.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    Envelope object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_get_signer(client, envelope_id, signer_id)`

Get a signer from an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    signer_id: The signer ID

Returns:
    Signer object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `signer_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_get_template(client, template_id)`

Get a template by ID.

Args:
    client: ClicksignClient from clicksign_create_client
    template_id: The template ID

Returns:
    Template object (JSON:API response)

Example:
    client: { node: create_client }
    template_id: "tttttttt-tttt-tttt-tttt-tttttttttttt"

**Parameters:**

- `client` (ClicksignClient, required)
- `template_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_documents(client, envelope_id)`

List all documents in an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    List of documents (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_envelopes(client, status=None, name=None)`

List envelopes with optional filters.

Args:
    client: ClicksignClient from clicksign_create_client
    status: Filter by status (e.g., "running", "closed", "canceled")
    name: Filter by name

Returns:
    List of envelopes (JSON:API response)

Example:
    client: { node: create_client }
    status: "running"

**Parameters:**

- `client` (ClicksignClient, required)
- `status` (Optional[str], optional, default: `None`)
- `name` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_requirements(client, envelope_id)`

List all requirements in an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    List of requirements (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_signers(client, envelope_id)`

List all signers in an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    List of signers (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_templates(client)`

List all available document templates.

Args:
    client: ClicksignClient from clicksign_create_client

Returns:
    List of templates (JSON:API response)

Example:
    client: { node: create_client }

**Returns:** `Dict[str, Any]`

---

### `clicksign_list_webhooks(client)`

List all webhook subscriptions.

Args:
    client: ClicksignClient from clicksign_create_client

Returns:
    List of webhooks (JSON:API response)

Example:
    client: { node: create_client }

**Returns:** `Dict[str, Any]`

---

### `clicksign_notify_all(client, envelope_id)`

Send notifications to all pending signers in an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID

Returns:
    Notification response (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_notify_signer(client, envelope_id, signer_id)`

Send a notification to a specific signer.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    signer_id: The signer ID to notify

Returns:
    Notification response (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `signer_id` (str, required)

**Returns:** `Dict[str, Any]`

---

### `clicksign_update_document(client, envelope_id, document_id, filename=None)`

Update a document in an envelope.

Args:
    client: ClicksignClient from clicksign_create_client
    envelope_id: The envelope ID
    document_id: The document ID
    filename: New filename for the document

Returns:
    Updated document object (JSON:API response)

Example:
    client: { node: create_client }
    envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
    filename: "updated_contract.pdf"

**Parameters:**

- `client` (ClicksignClient, required)
- `envelope_id` (str, required)
- `document_id` (str, required)
- `filename` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

## ☁️ Cloud Storage

> **Requires:** `pip install lexflow[gcs]`

### `gcs_close_client(client)`

Close the GCS client and release resources.

Args:
    client: GCS client instance to close

Returns:
    True when closed successfully

Example:
    client: { node: my_client }

**Returns:** `bool`

---

### `gcs_copy_object(client, source_bucket, source_object, dest_bucket, dest_object)`

Copy an object within or between GCS buckets.

Args:
    client: GCS client instance (from gcs_create_client)
    source_bucket: Source bucket name
    source_object: Source object name/path
    dest_bucket: Destination bucket name
    dest_object: Destination object name/path

Returns:
    Dictionary with copy operation metadata

Example:
    client: { node: my_client }
    source_bucket: "source-bucket"
    source_object: "path/to/file.pdf"
    dest_bucket: "dest-bucket"
    dest_object: "backup/file.pdf"

**Parameters:**

- `client` (Storage, required)
- `source_bucket` (str, required)
- `source_object` (str, required)
- `dest_bucket` (str, required)
- `dest_object` (str, required)

**Returns:** `GCSObjectMetadata`

---

### `gcs_create_client(service_file=None)`

Create a Google Cloud Storage async client.

Args:
    service_file: Optional path to service account JSON file

Returns:
    Storage client instance

Example:
    service_file: "/path/to/service-account.json"

Authentication:
    Uses Google Cloud authentication in this order:
    1. service_file parameter (if provided)
    2. GOOGLE_APPLICATION_CREDENTIALS environment variable
    3. gcloud auth application-default login
    4. GCE/GKE metadata server (in cloud environments)

**Returns:** `Storage`

---

### `gcs_delete_object(client, bucket_name, object_name)`

Delete an object from GCS.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path of the object to delete

Returns:
    True if deletion was successful

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "path/to/file.pdf"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)

**Returns:** `bool`

---

### `gcs_download_object_as_bytes(client, bucket_name, object_name)`

Download an object from GCS as bytes.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path of the object in the bucket

Returns:
    Object content as bytes

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "path/to/file.pdf"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)

**Returns:** `bytes`

---

### `gcs_download_object_as_string(client, bucket_name, object_name, encoding="utf-8")`

Download an object from GCS as a string.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path of the object in the bucket
    encoding: Text encoding (default: utf-8)

Returns:
    Object content as string

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "path/to/file.txt"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)
- `encoding` (str, optional, default: `"utf-8"`)

**Returns:** `str`

---

### `gcs_get_object_metadata(client, bucket_name, object_name)`

Get metadata for an object in GCS.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path of the object

Returns:
    Dictionary with object metadata including:
    - name: Object name
    - size: Size in bytes
    - contentType: MIME type
    - updated: Last modification timestamp
    - md5Hash: MD5 hash of content

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "path/to/file.pdf"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)

**Returns:** `GCSObjectMetadata`

---

### `gcs_list_objects(client, bucket_name, prefix=None, max_results=None)`

List objects in a GCS bucket.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    prefix: Optional prefix to filter objects
    max_results: Optional maximum number of results

Returns:
    List of object metadata dictionaries

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    prefix: "uploads/"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `prefix` (Optional[str], optional, default: `None`)
- `max_results` (Optional[int], optional, default: `None`)

**Returns:** `list[lexflow.opcodes.opcodes_gcs.GCSObjectMetadata]`

---

### `gcs_object_exists(client, bucket_name, object_name)`

Check if an object exists in a GCS bucket.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path of the object to check

Returns:
    True if object exists, False otherwise

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "path/to/file.pdf"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)

**Returns:** `bool`

---

### `gcs_upload_object_from_bytes(client, bucket_name, object_name, data, content_type=None)`

Upload bytes to an object in GCS.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path for the object in the bucket
    data: Bytes content to upload
    content_type: Optional MIME type (e.g., "application/pdf")

Returns:
    Dictionary with upload metadata

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "uploads/document.pdf"
    data: { variable: pdf_bytes }
    content_type: "application/pdf"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)
- `data` (bytes, required)
- `content_type` (Optional[str], optional, default: `None`)

**Returns:** `GCSObjectMetadata`

---

### `gcs_upload_object_from_string(client, bucket_name, object_name, data, content_type="text/plain", encoding="utf-8")`

Upload a string to an object in GCS.

Args:
    client: GCS client instance (from gcs_create_client)
    bucket_name: Name of the bucket
    object_name: Name/path for the object in the bucket
    data: String content to upload
    content_type: MIME type (default: "text/plain")
    encoding: Text encoding (default: utf-8)

Returns:
    Dictionary with upload metadata

Example:
    client: { node: my_client }
    bucket_name: "my-bucket"
    object_name: "logs/output.txt"
    data: "Hello, World!"

**Parameters:**

- `client` (Storage, required)
- `bucket_name` (str, required)
- `object_name` (str, required)
- `data` (str, required)
- `content_type` (str, optional, default: `"text/plain"`)
- `encoding` (str, optional, default: `"utf-8"`)

**Returns:** `GCSObjectMetadata`

---

## 🎮 Pygame Operations

> **Requires:** `pip install lexflow[pygame]`

### `pygame_create_color(r, g, b)`

Create an RGB color list.

Args:
    r: Red value (0-255)
    g: Green value (0-255)
    b: Blue value (0-255)

Returns:
    List [r, g, b]

**Parameters:**

- `r` (int, required)
- `g` (int, required)
- `b` (int, required)

**Returns:** `list`

---

### `pygame_create_window(width, height, title="LexFlow + Pygame")`

Create a pygame window and return the display surface.

Args:
    width: Window width in pixels
    height: Window height in pixels
    title: Window title

Returns:
    pygame.Surface object representing the display

**Parameters:**

- `width` (int, required)
- `height` (int, required)
- `title` (str, optional, default: `"LexFlow + Pygame"`)

**Returns:** `Any`

---

### `pygame_delay(milliseconds)`

Async delay in milliseconds.

Args:
    milliseconds: Delay duration in milliseconds

**Returns:** `NoneType`

---

### `pygame_draw_circle(screen, x, y, radius, color)`

Draw a filled circle on the screen.

Args:
    screen: The display surface
    x: Center X position
    y: Center Y position
    radius: Circle radius
    color: RGB color as [r, g, b]

**Parameters:**

- `screen` (Any, required)
- `x` (int, required)
- `y` (int, required)
- `radius` (int, required)
- `color` (list, required)

**Returns:** `NoneType`

---

### `pygame_draw_rect(screen, x, y, width, height, color, filled=True)`

Draw a rectangle on the screen.

Args:
    screen: The display surface
    x: X position (left edge)
    y: Y position (top edge)
    width: Rectangle width
    height: Rectangle height
    color: RGB color as [r, g, b]
    filled: If True, fill; if False, draw outline only

**Parameters:**

- `screen` (Any, required)
- `x` (int, required)
- `y` (int, required)
- `width` (int, required)
- `height` (int, required)
- `color` (list, required)
- `filled` (bool, optional, default: `True`)

**Returns:** `NoneType`

---

### `pygame_draw_text(screen, text, x, y, font_size=48, color=None)`

Draw text on the screen.

Args:
    screen: The display surface
    text: Text to render
    x: X position (left edge)
    y: Y position (top edge)
    font_size: Font size in pixels (default: 48)
    color: RGB color as [r, g, b], defaults to white

**Parameters:**

- `screen` (Any, required)
- `text` (str, required)
- `x` (int, required)
- `y` (int, required)
- `font_size` (int, optional, default: `48`)
- `color` (list, optional, default: `None`)

**Returns:** `NoneType`

---

### `pygame_fill_screen(screen, color)`

Fill the entire screen with a color.

Args:
    screen: The display surface
    color: RGB color as [r, g, b] where each value is 0-255

**Parameters:**

- `screen` (Any, required)
- `color` (list, required)

**Returns:** `NoneType`

---

### `pygame_get_key_pressed(key_name)`

Check if a specific key is currently pressed.

Args:
    key_name: Key name (e.g., "up", "down", "left", "right", "space")

Returns:
    True if key is pressed, False otherwise

**Returns:** `bool`

---

### `pygame_get_screen_height(screen)`

Get the height of the screen.

Args:
    screen: The display surface

Returns:
    Height in pixels

**Returns:** `int`

---

### `pygame_get_screen_width(screen)`

Get the width of the screen.

Args:
    screen: The display surface

Returns:
    Width in pixels

**Returns:** `int`

---

### `pygame_get_ticks()`

Get milliseconds since pygame.init() was called.

Returns:
    Milliseconds elapsed since pygame initialization

**Returns:** `int`

---

### `pygame_init()`

Initialize pygame engine.

**Returns:** `NoneType`

---

### `pygame_process_events()`

Process pygame events (keeps window responsive).

**Returns:** `NoneType`

---

### `pygame_quit()`

Quit pygame and close all windows.

**Returns:** `NoneType`

---

### `pygame_should_quit()`

Check if user wants to quit (clicked X button).

Returns:
    True if quit event detected, False otherwise

**Returns:** `bool`

---

### `pygame_update_display()`

Update the display to show all drawn elements.

**Returns:** `NoneType`

---

## receitaws ReceitaWS Operations

> **Requires:** `pip install lexflow[receitaws]`

### `receitaws_consulta_cnpj(cnpj)`

Consulta dados de uma empresa pelo CNPJ na ReceitaWS.

Args:
    cnpj: CNPJ da empresa (aceita formatado ou apenas digitos)

Returns:
    Dict com dados da empresa (nome, fantasia, situacao, etc.)

Raises:
    ValueError: Se o CNPJ nao tiver 14 digitos ou a API retornar erro

Example:
    cnpj: "11.222.333/0001-81"

**Returns:** `Dict[str, Any]`

---

## 🔍 RAG Operations

> **Requires:** `pip install lexflow[rag]`

### `bm25_rerank(query, results, top_k=10, text_field="text", alpha=0.5)`

Rerank search results using BM25 combined with semantic scores.

Combines the original semantic similarity score with BM25 keyword matching
for improved retrieval quality (hybrid search).

Args:
    query: The search query
    results: List of search results with 'payload' containing text and 'score'
    top_k: Number of results to return (default: 10)
    text_field: Field name in payload containing text (default: "text")
    alpha: Weight for semantic score vs BM25 (0=BM25 only, 1=semantic only)

Returns:
    Reranked results with updated 'score' and 'bm25_score' added

**Parameters:**

- `query` (str, required)
- `results` (List[Dict[str, Any]], required)
- `top_k` (int, optional, default: `10`)
- `text_field` (str, optional, default: `"text"`)
- `alpha` (float, optional, default: `0.5`)

**Returns:** `List[Dict[str, Any]]`

---

### `embedding_create(text, project, location="us-central1", model="text-embedding-004")`

Create an embedding vector for a single text.

Args:
    text: Text to embed
    project: Google Cloud project ID
    location: Google Cloud region (default: "us-central1")
    model: Embedding model name (default: "text-embedding-004")

Returns:
    List of floats representing the embedding vector

**Parameters:**

- `text` (str, required)
- `project` (str, required)
- `location` (str, optional, default: `"us-central1"`)
- `model` (str, optional, default: `"text-embedding-004"`)

**Returns:** `List[float]`

---

### `embedding_create_batch(texts, project, location="us-central1", model="text-embedding-004")`

Create embedding vectors for multiple texts (more efficient).

Args:
    texts: List of texts to embed
    project: Google Cloud project ID
    location: Google Cloud region (default: "us-central1")
    model: Embedding model name (default: "text-embedding-004")

Returns:
    List of embedding vectors (each is a list of floats)

**Parameters:**

- `texts` (List[str], required)
- `project` (str, required)
- `location` (str, optional, default: `"us-central1"`)
- `model` (str, optional, default: `"text-embedding-004"`)

**Returns:** `List[List[float]]`

---

### `pdf_extract_pages(file_path)`

Extract text from a PDF file page by page.

Args:
    file_path: Path to the PDF file

Returns:
    List of strings, one per page

**Returns:** `List[str]`

---

### `pdf_extract_pages_from_bytes(data)`

Extract text from PDF bytes page by page.

Args:
    data: PDF content as bytes

Returns:
    List of strings, one per page

**Returns:** `List[str]`

---

### `pdf_extract_text(file_path)`

Extract all text from a PDF file.

Args:
    file_path: Path to the PDF file

Returns:
    Extracted text from all pages concatenated

**Returns:** `str`

---

### `pdf_extract_text_from_bytes(data)`

Extract all text from PDF bytes.

Useful for processing PDFs downloaded from GCS or other sources
without writing to disk.

Args:
    data: PDF content as bytes

Returns:
    Extracted text from all pages concatenated

**Returns:** `str`

---

### `pdf_page_count(file_path)`

Get the number of pages in a PDF file.

Args:
    file_path: Path to the PDF file

Returns:
    Number of pages in the PDF

**Returns:** `int`

---

### `qdrant_collection_exists(client, name)`

Check if a Qdrant collection exists.

Args:
    client: QdrantClient instance
    name: Collection name to check

Returns:
    True if collection exists

**Parameters:**

- `client` (Any, required)
- `name` (str, required)

**Returns:** `bool`

---

### `qdrant_connect(url="http://localhost:6333")`

Create a Qdrant client connection.

Args:
    url: Qdrant server URL (default: "http://localhost:6333")

Returns:
    QdrantClient instance

**Returns:** `Any`

---

### `qdrant_create_collection(client, name, vector_size=768)`

Create a Qdrant collection if it doesn't exist.

Args:
    client: QdrantClient instance
    name: Collection name
    vector_size: Dimension of embedding vectors (default: 768)

Returns:
    True if created, False if already existed

**Parameters:**

- `client` (Any, required)
- `name` (str, required)
- `vector_size` (int, optional, default: `768`)

**Returns:** `bool`

---

### `qdrant_delete(client, collection, point_ids)`

Delete points from a Qdrant collection by IDs.

Args:
    client: QdrantClient instance
    collection: Collection name
    point_ids: List of point IDs to delete

Returns:
    True if deletion was successful

**Parameters:**

- `client` (Any, required)
- `collection` (str, required)
- `point_ids` (List[int], required)

**Returns:** `bool`

---

### `qdrant_delete_collection(client, name)`

Delete a Qdrant collection.

Args:
    client: QdrantClient instance
    name: Collection name to delete

Returns:
    True if deletion was successful

**Parameters:**

- `client` (Any, required)
- `name` (str, required)

**Returns:** `bool`

---

### `qdrant_search(client, collection, query_vector, limit=5)`

Search for similar vectors in a Qdrant collection.

Args:
    client: QdrantClient instance
    collection: Collection name
    query_vector: Embedding vector to search for
    limit: Maximum number of results (default: 5)

Returns:
    List of dicts with keys: id, score, payload

**Parameters:**

- `client` (Any, required)
- `collection` (str, required)
- `query_vector` (List[float], required)
- `limit` (int, optional, default: `5`)

**Returns:** `List[Dict[str, Any]]`

---

### `qdrant_upsert(client, collection, point_id, vector, payload=None)`

Insert or update a single point in a Qdrant collection.

Args:
    client: QdrantClient instance
    collection: Collection name
    point_id: Unique identifier for the point
    vector: Embedding vector
    payload: Optional metadata dict

Returns:
    True if upsert was successful

**Parameters:**

- `client` (Any, required)
- `collection` (str, required)
- `point_id` (int, required)
- `vector` (List[float], required)
- `payload` (Optional[Dict[str, Any]], optional, default: `None`)

**Returns:** `bool`

---

### `qdrant_upsert_batch(client, collection, point_ids, vectors, payloads=None)`

Insert or update multiple points in a Qdrant collection.

Args:
    client: QdrantClient instance
    collection: Collection name
    point_ids: List of unique identifiers
    vectors: List of embedding vectors
    payloads: Optional list of metadata dicts

Returns:
    True if upsert was successful

**Parameters:**

- `client` (Any, required)
- `collection` (str, required)
- `point_ids` (List[int], required)
- `vectors` (List[List[float]], required)
- `payloads` (Optional[List[Dict[str, Any]]], optional, default: `None`)

**Returns:** `bool`

---

### `text_chunk(text, chunk_size=500, overlap=50)`

Split text into overlapping chunks for embedding.

Args:
    text: Text to split into chunks
    chunk_size: Maximum characters per chunk (default: 500)
    overlap: Characters to overlap between chunks (default: 50)

Returns:
    List of text chunks

**Parameters:**

- `text` (str, required)
- `chunk_size` (int, optional, default: `500`)
- `overlap` (int, optional, default: `50`)

**Returns:** `List[str]`

---

### `text_chunk_by_sentences(text, sentences_per_chunk=5, overlap=1)`

Split text into chunks by sentence boundaries.

Args:
    text: Text to split into chunks
    sentences_per_chunk: Number of sentences per chunk (default: 5)
    overlap: Number of sentences to overlap (default: 1)

Returns:
    List of text chunks split at sentence boundaries

**Parameters:**

- `text` (str, required)
- `sentences_per_chunk` (int, optional, default: `5`)
- `overlap` (int, optional, default: `1`)

**Returns:** `List[str]`

---

### `text_chunk_pages(pages, chunk_size=500, overlap=50)`

Split pages into chunks with page and line metadata.

Chunks text while tracking which page(s) and line(s) each chunk spans.

Args:
    pages: List of page texts (from pdf_extract_pages)
    chunk_size: Maximum characters per chunk (default: 500)
    overlap: Characters to overlap between chunks (default: 50)

Returns:
    List of dicts with keys: text, page_start, page_end, line_start, line_end

**Parameters:**

- `pages` (List[str], required)
- `chunk_size` (int, optional, default: `500`)
- `overlap` (int, optional, default: `50`)

**Returns:** `List[Dict[str, Any]]`

---

### `text_chunk_pages_smart(pages, chunk_size=1000, overlap=200, min_chunk_size=100)`

Split pages into chunks at sentence boundaries with page/line metadata.

Like text_chunk_pages but tries to break at sentence endings (., !, ?)
for better semantic coherence.

Args:
    pages: List of page texts (from pdf_extract_pages)
    chunk_size: Target characters per chunk (default: 1000)
    overlap: Target overlap between chunks (default: 200)
    min_chunk_size: Minimum chunk size before forcing a break (default: 100)

Returns:
    List of dicts with keys: text, page_start, page_end, line_start, line_end

**Parameters:**

- `pages` (List[str], required)
- `chunk_size` (int, optional, default: `1000`)
- `overlap` (int, optional, default: `200`)
- `min_chunk_size` (int, optional, default: `100`)

**Returns:** `List[Dict[str, Any]]`

---

## 🐘 PgVector Operations

> **Requires:** `pip install lexflow[pgvector]`

### `pgvector_collection_exists(pool, name)`

Check if a pgvector collection (table) exists.

Args:
    pool: asyncpg.Pool instance
    name: Collection (table) name to check

Returns:
    True if collection exists

**Parameters:**

- `pool` (Any, required)
- `name` (str, required)

**Returns:** `bool`

---

### `pgvector_connect(dsn, min_size=1, max_size=10, ensure_extension=True)`

Create an asyncpg connection pool with pgvector support.

Args:
    dsn: PostgreSQL connection string
    min_size: Minimum pool connections (default: 1)
    max_size: Maximum pool connections (default: 10)
    ensure_extension: Run CREATE EXTENSION IF NOT EXISTS vector (default: True).
        Set to False if the extension is pre-configured or the user lacks privileges.

Returns:
    asyncpg.Pool instance with pgvector type registered

**Parameters:**

- `dsn` (str, required)
- `min_size` (int, optional, default: `1`)
- `max_size` (int, optional, default: `10`)
- `ensure_extension` (bool, optional, default: `True`)

**Returns:** `Any`

---

### `pgvector_create_collection(pool, name, vector_size=768)`

Create a pgvector collection (table) if it doesn't exist.

Creates the pgvector extension and a table with id, embedding, and payload columns.

Args:
    pool: asyncpg.Pool instance
    name: Collection (table) name
    vector_size: Dimension of embedding vectors (default: 768)

Returns:
    True if created, False if already existed

**Parameters:**

- `pool` (Any, required)
- `name` (str, required)
- `vector_size` (int, optional, default: `768`)

**Returns:** `bool`

---

### `pgvector_delete(pool, collection, point_ids)`

Delete points from a pgvector collection by IDs.

Args:
    pool: asyncpg.Pool instance
    collection: Collection (table) name
    point_ids: List of point IDs to delete

Returns:
    True if deletion was successful

**Parameters:**

- `pool` (Any, required)
- `collection` (str, required)
- `point_ids` (List[int], required)

**Returns:** `bool`

---

### `pgvector_delete_collection(pool, name)`

Delete a pgvector collection (table).

Args:
    pool: asyncpg.Pool instance
    name: Collection (table) name to delete

Returns:
    True if deletion was successful

**Parameters:**

- `pool` (Any, required)
- `name` (str, required)

**Returns:** `bool`

---

### `pgvector_disconnect(pool)`

Close a pgvector connection pool.

Args:
    pool: asyncpg.Pool instance to close

Returns:
    True if pool was closed successfully

**Returns:** `bool`

---

### `pgvector_search(pool, collection, query_vector, limit=5)`

Search for similar vectors in a pgvector collection.

Uses cosine distance (<=> operator) for similarity ranking.

Args:
    pool: asyncpg.Pool instance
    collection: Collection (table) name
    query_vector: Embedding vector to search for
    limit: Maximum number of results (default: 5)

Returns:
    List of dicts with keys: id, score, payload

**Parameters:**

- `pool` (Any, required)
- `collection` (str, required)
- `query_vector` (List[float], required)
- `limit` (int, optional, default: `5`)

**Returns:** `List[Dict[str, Any]]`

---

### `pgvector_upsert(pool, collection, point_id, vector, payload=None)`

Insert or update a single vector point in a pgvector collection.

Args:
    pool: asyncpg.Pool instance
    collection: Collection (table) name
    point_id: Unique identifier for the point
    vector: Embedding vector
    payload: Optional metadata dict

Returns:
    True if upsert was successful

**Parameters:**

- `pool` (Any, required)
- `collection` (str, required)
- `point_id` (int, required)
- `vector` (List[float], required)
- `payload` (Optional[Dict[str, Any]], optional, default: `None`)

**Returns:** `bool`

---

### `pgvector_upsert_batch(pool, collection, point_ids, vectors, payloads=None)`

Insert or update multiple vector points in a pgvector collection.

Args:
    pool: asyncpg.Pool instance
    collection: Collection (table) name
    point_ids: List of unique identifiers
    vectors: List of embedding vectors
    payloads: Optional list of metadata dicts

Returns:
    True if upsert was successful

**Parameters:**

- `pool` (Any, required)
- `collection` (str, required)
- `point_ids` (List[int], required)
- `vectors` (List[List[float]], required)
- `payloads` (Optional[List[Dict[str, Any]]], optional, default: `None`)

**Returns:** `bool`

---

## 💬 Chat Operations

### `chat_add_assistant(history, content)`

Add an assistant message to chat history.

Args:
    history: The chat history list to modify
    content: The assistant's response

Returns:
    The updated history

**Parameters:**

- `history` (List[dict], required)
- `content` (str, required)

**Returns:** `List[dict]`

---

### `chat_add_message(history, role, content)`

Add a message to chat history.

Args:
    history: The chat history list to modify
    role: Message role - "user" or "assistant"
    content: The message content

Returns:
    The updated history (same list, modified in place)

Raises:
    ValueError: If role is not "user" or "assistant"

**Parameters:**

- `history` (List[dict], required)
- `role` (str, required)
- `content` (str, required)

**Returns:** `List[dict]`

---

### `chat_add_user(history, content)`

Add a user message to chat history.

Args:
    history: The chat history list to modify
    content: The user's message

Returns:
    The updated history

**Parameters:**

- `history` (List[dict], required)
- `content` (str, required)

**Returns:** `List[dict]`

---

### `chat_clear(history)`

Clear all messages from chat history.

Args:
    history: The chat history list to clear

Returns:
    The same list, now empty

**Returns:** `List[dict]`

---

### `chat_create()`

Create a new empty chat history.

Returns:
    Empty list ready to store chat messages

**Returns:** `List[dict]`

---

### `chat_format_for_display(history)`

Format chat history as a readable string.

Args:
    history: The chat history list

Returns:
    Formatted string with each message on its own line

**Returns:** `str`

---

### `chat_get_last(history, role=None)`

Get the last message from chat history.

Args:
    history: The chat history list
    role: Optional filter - get last message with this role

Returns:
    The last message dict, or None if empty or no match

**Parameters:**

- `history` (List[dict], required)
- `role` (Optional[str], optional, default: `None`)

**Returns:** `Optional[dict]`

---

### `chat_length(history)`

Get the number of messages in chat history.

Args:
    history: The chat history list

Returns:
    Number of messages

**Returns:** `int`

---

### `chat_to_prompt(history)`

Convert chat history to a single prompt string for AI.

Args:
    history: The chat history list

Returns:
    A formatted string containing the conversation context

**Returns:** `str`

---

### `chat_with_agent(agent, history, user_message)`

Send a message to an AI agent with conversation history context.

This opcode:
1. Adds the user message to history
2. Builds a context-aware prompt from history
3. Sends to the agent
4. Adds the response to history
5. Returns the response

Args:
    agent: A pydantic-ai Agent instance
    history: The chat history list (will be modified)
    user_message: The new user message to send

Returns:
    The assistant's response string

**Parameters:**

- `agent` (Any, required)
- `history` (List[dict], required)
- `user_message` (str, required)

**Returns:** `str`

---

## 💻 CLI Operations

### `clear_line()`

Clear the current terminal line.

**Returns:** `NoneType`

---

### `print_error(message)`

Print an error message with red X.

**Returns:** `NoneType`

---

### `print_info(message)`

Print an info message with blue indicator.

**Returns:** `NoneType`

---

### `print_success(message)`

Print a success message with green checkmark.

**Returns:** `NoneType`

---

### `print_warning(message)`

Print a warning message with yellow indicator.

**Returns:** `NoneType`

---

### `progress_bar(current, total, message="", width=30)`

Display/update a progress bar.

Args:
    current: Current progress value
    total: Total/max value
    message: Optional message to show
    width: Bar width in characters (default: 30)

**Parameters:**

- `current` (int, required)
- `total` (int, required)
- `message` (str, optional, default: `""`)
- `width` (int, optional, default: `30`)

**Returns:** `NoneType`

---

### `spinner_fail(spinner, message="Failed")`

Stop a spinner with failure indicator.

Args:
    spinner: Spinner object from spinner_start
    message: Error message to display

**Parameters:**

- `spinner` (Spinner, required)
- `message` (str, optional, default: `"Failed"`)

**Returns:** `NoneType`

---

### `spinner_start(message="Loading")`

Start an animated spinner.

Args:
    message: Message to display next to spinner

Returns:
    Spinner object (use with spinner_stop, spinner_update)

**Returns:** `Spinner`

---

### `spinner_stop(spinner, message="", success=True)`

Stop a spinner and show completion message.

Args:
    spinner: Spinner object from spinner_start
    message: Final message (empty = original message + "done")
    success: True for checkmark, False for X mark

**Parameters:**

- `spinner` (Spinner, required)
- `message` (str, optional, default: `""`)
- `success` (bool, optional, default: `True`)

**Returns:** `NoneType`

---

### `spinner_update(spinner, message)`

Update the message of a running spinner.

Args:
    spinner: Spinner object from spinner_start
    message: New message to display

**Parameters:**

- `spinner` (Spinner, required)
- `message` (str, required)

**Returns:** `NoneType`

---

## 🐙 GitHub Operations

### `github_get_file_content(owner, repo, path, ref="HEAD")`

Get file content from a repository at a specific ref.

Args:
    owner: Repository owner
    repo: Repository name
    path: File path relative to repo root
    ref: Git reference (branch, tag, or commit SHA)

Returns:
    File content as a string (UTF-8 decoded)

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `path` (str, required)
- `ref` (str, optional, default: `"HEAD"`)

**Returns:** `str`

---

### `github_get_pr_diff(owner, repo, pr_number)`

Get the full diff of a PR.

Args:
    owner: Repository owner
    repo: Repository name
    pr_number: Pull request number

Returns:
    The PR diff as a string in unified diff format

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `pr_number` (int, required)

**Returns:** `str`

---

### `github_get_pr_files(owner, repo, pr_number)`

Get list of files changed in a PR.

Args:
    owner: Repository owner
    repo: Repository name
    pr_number: Pull request number

Returns:
    List of dicts with: path, additions, deletions, status

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `pr_number` (int, required)

**Returns:** `List[Dict[str, Any]]`

---

### `github_get_pr_info(owner, repo, pr_number)`

Get PR metadata from GitHub.

Args:
    owner: Repository owner (e.g., "anthropics")
    repo: Repository name (e.g., "lex-flow")
    pr_number: Pull request number

Returns:
    Dict with: title, body, author, state, base_branch, head_branch, url

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `pr_number` (int, required)

**Returns:** `Dict[str, Any]`

---

### `github_get_repo_info(owner, repo)`

Get repository metadata.

Args:
    owner: Repository owner
    repo: Repository name

Returns:
    Dict with: name, full_name, description, default_branch, url, is_private

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)

**Returns:** `Dict[str, Any]`

---

### `github_is_available()`

Check if GitHub CLI is available and authenticated.

Returns:
    True if gh CLI is installed and authenticated

**Returns:** `bool`

---

### `github_list_pr_comments(owner, repo, pr_number)`

Get all comments on a PR.

Args:
    owner: Repository owner
    repo: Repository name
    pr_number: Pull request number

Returns:
    List of comment dicts with: id, author, body, created_at, type

**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `pr_number` (int, required)

**Returns:** `List[Dict[str, Any]]`

---

## 📨 Pub/Sub

> **Requires:** `pip install lexflow[pubsub]`

### `pubsub_ack_message(subscriber, project_id, subscription_id, message)`

Acknowledge a single message received from pubsub_pull_messages.

Args:
    subscriber: Subscriber client instance
    project_id: GCP project ID
    subscription_id: Subscription ID
    message: Message dictionary with ack_id from pubsub_pull_messages

Returns:
    True if acknowledged successfully

Example:
    subscriber: { variable: my_subscriber }
    project_id: "my-gcp-project"
    subscription_id: "my-subscription"
    message: { variable: msg }

**Parameters:**

- `subscriber` (SubscriberClient, required)
- `project_id` (str, required)
- `subscription_id` (str, required)
- `message` (dict, required)

**Returns:** `bool`

---

### `pubsub_acknowledge_messages(subscriber, project_id, subscription_id, ack_ids)`

Acknowledge messages that have been processed.

Args:
    subscriber: Subscriber client instance (from pubsub_create_subscriber)
    project_id: GCP project ID
    subscription_id: Subscription ID (not the full path)
    ack_ids: List of acknowledgment IDs from pulled messages

Returns:
    True if acknowledgment was successful

Example:
    subscriber: { variable: my_subscriber }
    project_id: "my-gcp-project"
    subscription_id: "my-subscription"
    ack_ids: { variable: message_ack_ids }

**Parameters:**

- `subscriber` (SubscriberClient, required)
- `project_id` (str, required)
- `subscription_id` (str, required)
- `ack_ids` (list, required)

**Returns:** `bool`

---

### `pubsub_close_publisher(publisher)`

Close the publisher client and release resources.

Args:
    publisher: Publisher client instance to close

Returns:
    True if closed successfully

Example:
    publisher: { variable: my_publisher }

**Returns:** `bool`

---

### `pubsub_close_subscriber(subscriber)`

Close the subscriber client and release resources.

Args:
    subscriber: Subscriber client instance to close

Returns:
    True if closed successfully

Example:
    subscriber: { variable: my_subscriber }

**Returns:** `bool`

---

### `pubsub_create_publisher()`

Create a Google Cloud Pub/Sub publisher client.

Returns:
    PublisherClient instance

Example:
    (no inputs required)

Authentication:
    Requires Google Cloud authentication via:
    - gcloud auth application-default login
    - Or GOOGLE_APPLICATION_CREDENTIALS environment variable

Note:
    Supports PUBSUB_EMULATOR_HOST environment variable for local testing.
    When set, authentication is automatically skipped.

**Returns:** `PublisherClient`

---

### `pubsub_create_subscriber()`

Create a Google Cloud Pub/Sub subscriber client.

Returns:
    SubscriberClient instance

Example:
    (no inputs required)

Authentication:
    Requires Google Cloud authentication via:
    - gcloud auth application-default login
    - Or GOOGLE_APPLICATION_CREDENTIALS environment variable

Note:
    Supports PUBSUB_EMULATOR_HOST environment variable for local testing.
    When set, authentication is automatically skipped.

**Returns:** `SubscriberClient`

---

### `pubsub_nack_message(subscriber, project_id, subscription_id, message)`

Negative-acknowledge a message (return to queue for redelivery).

Args:
    subscriber: Subscriber client instance
    project_id: GCP project ID
    subscription_id: Subscription ID
    message: Message dictionary with ack_id from pubsub_pull_messages

Returns:
    True if nack'd successfully

Example:
    subscriber: { variable: my_subscriber }
    project_id: "my-gcp-project"
    subscription_id: "my-subscription"
    message: { variable: msg }

**Parameters:**

- `subscriber` (SubscriberClient, required)
- `project_id` (str, required)
- `subscription_id` (str, required)
- `message` (dict, required)

**Returns:** `bool`

---

### `pubsub_publish_batch(publisher, project_id, topic_id, messages)`

Publish multiple messages to a Pub/Sub topic.

Args:
    publisher: Publisher client instance (from pubsub_create_publisher)
    project_id: GCP project ID
    topic_id: Topic ID (not the full path)
    messages: List of message dictionaries, each with:
        - data: Message data as string (required)
        - attributes: Optional dictionary of attributes

Returns:
    List of message IDs for the published messages

Example:
    publisher: { variable: my_publisher }
    project_id: "my-gcp-project"
    topic_id: "my-topic"
    messages:
      - data: "First message"
        attributes: { "index": "1" }
      - data: "Second message"
        attributes: { "index": "2" }

**Parameters:**

- `publisher` (PublisherClient, required)
- `project_id` (str, required)
- `topic_id` (str, required)
- `messages` (list, required)

**Returns:** `list`

---

### `pubsub_publish_message(publisher, project_id, topic_id, data)`

Publish a message to a Pub/Sub topic.

Args:
    publisher: Publisher client instance (from pubsub_create_publisher)
    project_id: GCP project ID
    topic_id: Topic ID (not the full path)
    data: Message data as string

Returns:
    Message ID of the published message

Example:
    publisher: { variable: my_publisher }
    project_id: "my-gcp-project"
    topic_id: "my-topic"
    data: "Hello, Pub/Sub!"

**Parameters:**

- `publisher` (PublisherClient, required)
- `project_id` (str, required)
- `topic_id` (str, required)
- `data` (str, required)

**Returns:** `str`

---

### `pubsub_publish_message_with_attributes(publisher, project_id, topic_id, data, attributes)`

Publish a message with custom attributes to a Pub/Sub topic.

Args:
    publisher: Publisher client instance (from pubsub_create_publisher)
    project_id: GCP project ID
    topic_id: Topic ID (not the full path)
    data: Message data as string
    attributes: Dictionary of custom attributes (string keys and values)

Returns:
    Message ID of the published message

Example:
    publisher: { variable: my_publisher }
    project_id: "my-gcp-project"
    topic_id: "my-topic"
    data: "Hello with attributes!"
    attributes: { "type": "greeting", "priority": "high" }

**Parameters:**

- `publisher` (PublisherClient, required)
- `project_id` (str, required)
- `topic_id` (str, required)
- `data` (str, required)
- `attributes` (dict, required)

**Returns:** `str`

---

### `pubsub_pull_messages(subscriber, project_id, subscription_id, max_messages=10)`

Pull messages from a Pub/Sub subscription.

Args:
    subscriber: Subscriber client instance (from pubsub_create_subscriber)
    project_id: GCP project ID
    subscription_id: Subscription ID (not the full path)
    max_messages: Maximum number of messages to pull (default: 10)

Returns:
    List of message dictionaries with keys:
    - ack_id: Acknowledgment ID (needed for acknowledging)
    - message_id: Message ID
    - data: Message data as string
    - attributes: Message attributes dictionary
    - publish_time: Publish timestamp as ISO string

Example:
    subscriber: { variable: my_subscriber }
    project_id: "my-gcp-project"
    subscription_id: "my-subscription"
    max_messages: 5

**Parameters:**

- `subscriber` (SubscriberClient, required)
- `project_id` (str, required)
- `subscription_id` (str, required)
- `max_messages` (int, optional, default: `10`)

**Returns:** `list`

---

### `pubsub_subscribe_stream(subscriber, project_id, subscription_id, timeout=None, max_messages=None, batch_size=10, min_poll_interval=0.1, max_poll_interval=5.0, max_retries=10)`

Subscribe to a Pub/Sub subscription and stream messages as an async generator.

This opcode returns an async generator that yields messages as they arrive.
Use with control_async_foreach to process messages continuously.

Uses exponential backoff when no messages are available: starts at
min_poll_interval and doubles up to max_poll_interval. Resets to
min_poll_interval when messages are received.

Args:
    subscriber: Subscriber client instance (from pubsub_create_subscriber)
    project_id: GCP project ID
    subscription_id: Subscription ID (not the full path)
    timeout: Optional timeout in seconds. If None, runs indefinitely.
    max_messages: Optional max number of messages to receive before stopping.
    batch_size: Messages to pull per request (default: 10)
    min_poll_interval: Initial/minimum sleep between polls in seconds (default: 0.1)
    max_poll_interval: Maximum sleep during backoff in seconds (default: 5.0)
    max_retries: Maximum consecutive errors before raising (default: 10)

Yields:
    Message dictionaries with keys:
    - ack_id: Acknowledgment ID
    - message_id: Message ID
    - data: Message data as string
    - attributes: Message attributes dictionary
    - publish_time: Publish timestamp as ISO string

Note:
    The subscriber client is NOT closed by this opcode. Use
    pubsub_close_subscriber to clean up after streaming completes.

Example:
    subscriber: { variable: my_subscriber }
    project_id: "my-gcp-project"
    subscription_id: "my-subscription"
    timeout: 60
    max_messages: 100
    batch_size: 20
    min_poll_interval: 0.05
    max_poll_interval: 10.0

Usage in workflow:
    create_subscriber:
      opcode: pubsub_create_subscriber
      isReporter: true

    subscribe:
      opcode: pubsub_subscribe_stream
      isReporter: true
      inputs:
        subscriber: { node: create_subscriber }
        project_id: { variable: project_id }
        subscription_id: { variable: subscription_id }
        timeout: { literal: 30 }
        batch_size: { literal: 20 }

    process_messages:
      opcode: control_async_foreach
      inputs:
        VAR: { literal: "msg" }
        ITERABLE: { node: subscribe }
      branches:
        BODY:
          - handle_message

**Parameters:**

- `subscriber` (SubscriberClient, required)
- `project_id` (str, required)
- `subscription_id` (str, required)
- `timeout` (Optional[float], optional, default: `None`)
- `max_messages` (Optional[int], optional, default: `None`)
- `batch_size` (int, optional, default: `10`)
- `min_poll_interval` (float, optional, default: `0.1`)
- `max_poll_interval` (float, optional, default: `5.0`)
- `max_retries` (int, optional, default: `10`)

**Returns:** `AsyncGenerator[dict, NoneType]`

---

## ⚡ Task Operations

### `task_await(task, timeout=None)`

Wait for a background task to complete and get its result.

Args:
    task: LexFlowTask handle from control_spawn
    timeout: Optional timeout in seconds

Returns:
    The task's return value

Raises:
    asyncio.TimeoutError: If timeout exceeded
    Exception: If the task raised an exception

**Parameters:**

- `task` (Any, required)
- `timeout` (Optional[float], optional, default: `None`)

**Returns:** `Any`

---

### `task_await_all(tasks, timeout=None)`

Wait for multiple tasks to complete.

Args:
    tasks: List of LexFlowTask handles
    timeout: Optional timeout in seconds

Returns:
    List of results in the same order as tasks

**Parameters:**

- `tasks` (List, required)
- `timeout` (Optional[float], optional, default: `None`)

**Returns:** `List[Any]`

---

### `task_cancel(task)`

Request cancellation of a background task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    True if cancel was requested

**Returns:** `bool`

---

### `task_exception(task)`

Get the exception message from a failed task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    Exception message as string, or None if succeeded/not done

**Returns:** `Optional[str]`

---

### `task_id(task)`

Get the ID of a task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    The task's unique ID

**Returns:** `int`

---

### `task_is_done(task)`

Check if a background task has completed.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    True if task is done (completed, cancelled, or failed)

**Returns:** `bool`

---

### `task_name(task)`

Get the name of a task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    The task's name

**Returns:** `str`

---

### `task_result(task)`

Get the result of a completed task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    The task's return value

Raises:
    InvalidStateError: If task is not done

**Returns:** `Any`

---

### `task_sleep(seconds)`

Sleep for the specified number of seconds.

Args:
    seconds: Duration to sleep

**Returns:** `NoneType`

---

### `task_yield()`

Yield control to other tasks momentarily.

**Returns:** `NoneType`

---

## 📡 Channel Operations

### `channel_close(channel)`

Close a channel.

Args:
    channel: The channel to close

**Returns:** `NoneType`

---

### `channel_create(size=0)`

Create a new channel for inter-task communication.

Args:
    size: Buffer size (0 for unbuffered/synchronous)

Returns:
    A new Channel object

**Returns:** `Channel`

---

### `channel_is_closed(channel)`

Check if a channel is closed.

Args:
    channel: The channel to check

Returns:
    True if closed

**Returns:** `bool`

---

### `channel_is_empty(channel)`

Check if a channel buffer is empty.

Args:
    channel: The channel to check

Returns:
    True if empty

**Returns:** `bool`

---

### `channel_len(channel)`

Get the number of items in the channel buffer.

Args:
    channel: The channel to check

Returns:
    Number of items in buffer

**Returns:** `int`

---

### `channel_receive(channel, timeout=None)`

Receive a value from a channel.

Blocks until a value is available.

Args:
    channel: The channel to receive from
    timeout: Optional timeout in seconds

Returns:
    The received value

Raises:
    asyncio.TimeoutError: If timeout exceeded
    RuntimeError: If channel is closed and empty

**Parameters:**

- `channel` (Channel, required)
- `timeout` (Optional[float], optional, default: `None`)

**Returns:** `Any`

---

### `channel_send(channel, value)`

Send a value through a channel.

Blocks if the channel buffer is full.

Args:
    channel: The channel to send to
    value: The value to send

Raises:
    RuntimeError: If the channel is closed

**Parameters:**

- `channel` (Channel, required)
- `value` (Any, required)

**Returns:** `NoneType`

---

### `channel_try_receive(channel)`

Try to receive a value without blocking.

Args:
    channel: The channel to receive from

Returns:
    Dict with keys: value, ok (True if received)

**Returns:** `dict`

---

## 🔒 Sync Primitives

### `sync_event_clear(event)`

Clear an event (reset to unset state).

Args:
    event: The event to clear

**Returns:** `NoneType`

---

### `sync_event_create()`

Create an event for signaling between tasks.

Returns:
    An asyncio.Event

**Returns:** `Event`

---

### `sync_event_is_set(event)`

Check if an event is set.

Args:
    event: The event to check

Returns:
    True if set

**Returns:** `bool`

---

### `sync_event_set(event)`

Set an event (signal waiting tasks).

Args:
    event: The event to set

**Returns:** `NoneType`

---

### `sync_event_wait(event, timeout=None)`

Wait for an event to be set.

Args:
    event: The event to wait for
    timeout: Optional timeout in seconds

Returns:
    True if event was set, False if timeout

**Parameters:**

- `event` (Event, required)
- `timeout` (Optional[float], optional, default: `None`)

**Returns:** `bool`

---

### `sync_semaphore_acquire(semaphore, timeout=None)`

Acquire a semaphore permit.

Args:
    semaphore: The semaphore to acquire
    timeout: Optional timeout in seconds

Returns:
    True if acquired, False if timeout

**Parameters:**

- `semaphore` (Semaphore, required)
- `timeout` (Optional[float], optional, default: `None`)

**Returns:** `bool`

---

### `sync_semaphore_create(permits=1)`

Create a semaphore for limiting concurrent access.

Args:
    permits: Number of permits (1 for mutex)

Returns:
    An asyncio.Semaphore

**Returns:** `Semaphore`

---

### `sync_semaphore_release(semaphore)`

Release a semaphore permit.

Args:
    semaphore: The semaphore to release

**Returns:** `NoneType`

---

## 💬 Slack

> **Requires:** `pip install lexflow[slack]`

### `slack_add_reaction(client, channel, ts, emoji)`

Add a reaction emoji to a message.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the message exists
    ts: Timestamp of the message
    emoji: Emoji name without colons (e.g., "thumbsup")

Returns:
    True if successful

Required scopes: reactions:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `ts` (str, required)
- `emoji` (str, required)

**Returns:** `bool`

---

### `slack_archive_channel(client, channel)`

Archive a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID to archive

Returns:
    True if successful

Required scopes: channels:manage, groups:write (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)

**Returns:** `bool`

---

### `slack_create_channel(client, name, is_private=False)`

Create a new channel.

Args:
    client: Slack client (from slack_create_client)
    name: Channel name (lowercase, no spaces, max 80 chars)
    is_private: Whether to create a private channel (default: False)

Returns:
    Dict with: id, name, is_private, created

Required scopes: channels:manage, groups:write (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `name` (str, required)
- `is_private` (bool, optional, default: `False`)

**Returns:** `Dict[str, Any]`

---

### `slack_create_client(token)`

Create a Slack Web API client.

Args:
    token: Slack Bot Token (xoxb-...) or User Token (xoxp-...)

Returns:
    AsyncWebClient instance for use with other Slack opcodes

Example:
    token: "xoxb-xxxx-xxxx-xxxx"

**Returns:** `AsyncWebClient`

---

### `slack_delete_file(client, file_id)`

Delete a file.

Args:
    client: Slack client (from slack_create_client)
    file_id: File ID to delete

Returns:
    True if successful

Required scopes: files:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `file_id` (str, required)

**Returns:** `bool`

---

### `slack_delete_message(client, channel, ts)`

Delete a message.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the message exists
    ts: Timestamp of the message to delete

Returns:
    Dict with: ok, channel, ts

Required scopes: chat:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `ts` (str, required)

**Returns:** `Dict[str, Any]`

---

### `slack_format_channel_mention(channel_id)`

Format a channel ID as a mention.

Args:
    channel_id: Channel ID (e.g., "C12345678")

Returns:
    Formatted mention string (e.g., "<#C12345678>")

**Returns:** `str`

---

### `slack_format_link(url, text=None)`

Format a URL as a Slack link.

Args:
    url: URL to link to
    text: Optional display text

Returns:
    Formatted link string (e.g., "<https://example.com|Click here>")

**Parameters:**

- `url` (str, required)
- `text` (Optional[str], optional, default: `None`)

**Returns:** `str`

---

### `slack_format_user_mention(user_id)`

Format a user ID as a mention.

Args:
    user_id: User ID (e.g., "U12345678")

Returns:
    Formatted mention string (e.g., "<@U12345678>")

**Returns:** `str`

---

### `slack_get_channel_info(client, channel)`

Get information about a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID

Returns:
    Dict with: id, name, is_private, is_archived, topic, purpose, num_members, created

Required scopes: channels:read, groups:read (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)

**Returns:** `Dict[str, Any]`

---

### `slack_get_channel_members(client, channel, limit=100)`

Get list of members in a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID
    limit: Maximum number of members to return (default: 100)

Returns:
    List of user IDs

Required scopes: channels:read, groups:read (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `limit` (int, optional, default: `100`)

**Returns:** `List[str]`

---

### `slack_get_conversation_history(client, channel, limit=100, oldest=None, latest=None)`

Get conversation history for a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID
    limit: Number of messages to return (default: 100)
    oldest: Optional oldest message timestamp to fetch from
    latest: Optional latest message timestamp to fetch to

Returns:
    List of message dicts with: ts, text, user, thread_ts, reply_count

Required scopes: channels:history, groups:history (for private), mpim:history, im:history

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `limit` (int, optional, default: `100`)
- `oldest` (Optional[str], optional, default: `None`)
- `latest` (Optional[str], optional, default: `None`)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_get_reactions(client, channel, ts)`

Get reactions on a message.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the message exists
    ts: Timestamp of the message

Returns:
    List of reaction dicts with: name, count, users

Required scopes: reactions:read

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `ts` (str, required)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_get_thread_replies(client, channel, thread_ts, limit=100)`

Get replies in a thread.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the thread exists
    thread_ts: Timestamp of the parent message
    limit: Number of replies to return (default: 100)

Returns:
    List of message dicts with: ts, text, user, thread_ts

Required scopes: channels:history, groups:history (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `thread_ts` (str, required)
- `limit` (int, optional, default: `100`)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_get_user_info(client, user)`

Get information about a user.

Args:
    client: Slack client (from slack_create_client)
    user: User ID

Returns:
    Dict with: id, name, real_name, email, title, phone, is_bot, is_admin, tz

Required scopes: users:read, users:read.email (for email)

**Parameters:**

- `client` (AsyncWebClient, required)
- `user` (str, required)

**Returns:** `Dict[str, Any]`

---

### `slack_get_user_presence(client, user)`

Get user's presence status.

Args:
    client: Slack client (from slack_create_client)
    user: User ID

Returns:
    Dict with: presence (active/away), online, auto_away, manual_away

Required scopes: users:read

**Parameters:**

- `client` (AsyncWebClient, required)
- `user` (str, required)

**Returns:** `Dict[str, Any]`

---

### `slack_invite_to_channel(client, channel, users)`

Invite users to a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID
    users: List of user IDs to invite

Returns:
    True if successful

Required scopes: channels:manage, groups:write (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `users` (List[str], required)

**Returns:** `bool`

---

### `slack_leave_channel(client, channel)`

Leave a channel.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID to leave

Returns:
    True if successful

Required scopes: channels:manage, groups:write (for private)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)

**Returns:** `bool`

---

### `slack_list_channels(client, types=None, limit=100, exclude_archived=True)`

List channels in the workspace.

Args:
    client: Slack client (from slack_create_client)
    types: Comma-separated channel types (public_channel, private_channel, mpim, im)
    limit: Maximum number of channels to return (default: 100)
    exclude_archived: Exclude archived channels (default: True)

Returns:
    List of channel dicts with: id, name, is_private, is_archived, num_members

Required scopes: channels:read, groups:read (for private), mpim:read, im:read

**Parameters:**

- `client` (AsyncWebClient, required)
- `types` (Optional[str], optional, default: `None`)
- `limit` (int, optional, default: `100`)
- `exclude_archived` (bool, optional, default: `True`)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_list_files(client, channel=None, user=None, types=None, limit=100)`

List files in the workspace.

Args:
    client: Slack client (from slack_create_client)
    channel: Optional channel ID to filter by
    user: Optional user ID to filter by
    types: Optional comma-separated file types (spaces, snippets, images, etc.)
    limit: Number of files to return (default: 100)

Returns:
    List of file dicts with: id, name, title, filetype, size, user, created

Required scopes: files:read

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (Optional[str], optional, default: `None`)
- `user` (Optional[str], optional, default: `None`)
- `types` (Optional[str], optional, default: `None`)
- `limit` (int, optional, default: `100`)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_list_users(client, limit=100)`

List users in the workspace.

Args:
    client: Slack client (from slack_create_client)
    limit: Maximum number of users to return (default: 100)

Returns:
    List of user dicts with: id, name, real_name, email, is_bot, is_admin

Required scopes: users:read, users:read.email (for email)

**Parameters:**

- `client` (AsyncWebClient, required)
- `limit` (int, optional, default: `100`)

**Returns:** `List[Dict[str, Any]]`

---

### `slack_remove_reaction(client, channel, ts, emoji)`

Remove a reaction emoji from a message.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the message exists
    ts: Timestamp of the message
    emoji: Emoji name without colons (e.g., "thumbsup")

Returns:
    True if successful

Required scopes: reactions:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `ts` (str, required)
- `emoji` (str, required)

**Returns:** `bool`

---

### `slack_schedule_message(client, channel, text, post_at, thread_ts=None)`

Schedule a message for later delivery.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID or channel name
    text: Message text
    post_at: Unix timestamp for when to send the message
    thread_ts: Optional thread timestamp to reply in thread

Returns:
    Dict with: ok, channel, scheduled_message_id, post_at

Required scopes: chat:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `text` (str, required)
- `post_at` (int, required)
- `thread_ts` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `slack_send_blocks(client, channel, blocks, text="", thread_ts=None)`

Send a message with Block Kit blocks.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID or channel name
    blocks: List of Block Kit block objects
    text: Fallback text for notifications (recommended)
    thread_ts: Optional thread timestamp to reply in thread

Returns:
    Dict with: ok, channel, ts, message

Required scopes: chat:write

See: https://api.slack.com/block-kit

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `blocks` (List[Dict[str, Any]], required)
- `text` (str, optional, default: `""`)
- `thread_ts` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `slack_send_message(client, channel, text, thread_ts=None, broadcast=False, unfurl_links=True, unfurl_media=True)`

Send a message to a channel, user, or thread.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID, channel name, or user ID
    text: Message text (supports Slack markdown)
    thread_ts: Optional thread timestamp to reply in thread
    broadcast: Whether to also post to channel when replying in thread (default: False)
    unfurl_links: Whether to unfurl URLs (default: True)
    unfurl_media: Whether to unfurl media (default: True)

Returns:
    Dict with: ok, channel, ts, message

Required scopes: chat:write, chat:write.public (for public channels)

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `text` (str, required)
- `thread_ts` (Optional[str], optional, default: `None`)
- `broadcast` (bool, optional, default: `False`)
- `unfurl_links` (bool, optional, default: `True`)
- `unfurl_media` (bool, optional, default: `True`)

**Returns:** `Dict[str, Any]`

---

### `slack_send_webhook(url, text, blocks=None, username=None, icon_emoji=None, icon_url=None, timeout=30.0)`

Send a message via incoming webhook.

Args:
    url: Incoming webhook URL (must be https://hooks.slack.com/...)
    text: Message text (required, used as fallback)
    blocks: Optional Block Kit blocks
    username: Optional custom username
    icon_emoji: Optional emoji for bot icon (e.g., ":robot_face:")
    icon_url: Optional URL for bot icon
    timeout: Request timeout in seconds (default: 30)

Returns:
    True if successful

Note: Does not require a Slack client, uses webhook directly

**Parameters:**

- `url` (str, required)
- `text` (str, required)
- `blocks` (Optional[List[Dict[str, Any]]], optional, default: `None`)
- `username` (Optional[str], optional, default: `None`)
- `icon_emoji` (Optional[str], optional, default: `None`)
- `icon_url` (Optional[str], optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `bool`

---

### `slack_test_auth(client)`

Test authentication and get bot/user info.

Args:
    client: Slack client (from slack_create_client)

Returns:
    Dict with: ok, url, team, user, team_id, user_id, bot_id

Useful for verifying token validity and getting workspace info.

**Returns:** `Dict[str, Any]`

---

### `slack_update_message(client, channel, ts, text=None, blocks=None)`

Update an existing message.

Args:
    client: Slack client (from slack_create_client)
    channel: Channel ID where the message exists
    ts: Timestamp of the message to update
    text: New message text (optional if blocks provided)
    blocks: New Block Kit blocks (optional)

Returns:
    Dict with: ok, channel, ts, message

Required scopes: chat:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channel` (str, required)
- `ts` (str, required)
- `text` (Optional[str], optional, default: `None`)
- `blocks` (Optional[List[Dict[str, Any]]], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

### `slack_upload_file(client, channels, content, filename, title=None, initial_comment=None)`

Upload a file to channels.

Args:
    client: Slack client (from slack_create_client)
    channels: List of channel IDs to share the file
    content: File content as string
    filename: Name of the file
    title: Optional title for the file
    initial_comment: Optional comment to add with the file

Returns:
    Dict with: id, name, title, url_private, permalink

Required scopes: files:write

**Parameters:**

- `client` (AsyncWebClient, required)
- `channels` (List[str], required)
- `content` (str, required)
- `filename` (str, required)
- `title` (Optional[str], optional, default: `None`)
- `initial_comment` (Optional[str], optional, default: `None`)

**Returns:** `Dict[str, Any]`

---

## Summary

**Total opcodes:** 330

### Categories

| Category | Opcodes | Requires |
|:---------|--------:|:---------|
| 📤 I/O Operations | 2 | - |
| ⚡ Operators | 14 | - |
| 🔢 Math Operations | 6 | - |
| 📝 String Operations | 12 | - |
| 📋 List Operations | 5 | - |
| 📖 Dictionary Operations | 15 | - |
| 📦 Object Operations | 8 | - |
| 🔄 Type Conversions | 6 | - |
| ⚠️ Exception Operations | 4 | - |
| ✓ Assertion Operations | 2 | - |
| 🔗 Workflow Operations | 4 | - |
| 📦 Data Operations | 2 | - |
| ↻ Control Flow | 11 | - |
| ⏱ Async Operations | 3 | - |
| 🤖 AI Operations (Pydantic AI) | 5 | `lexflow[ai]` |
| 🌐 HTTP Operations | 8 | `lexflow[http]` |
| 📊 Google Sheets Operations | 12 | `lexflow[sheets]` |
| 📄 HTML Operations | 5 | `lexflow[http]` |
| 📋 JSON Operations | 2 | - |
| hubspot HubSpot Operations | 19 | `lexflow[http]` |
| 🔍 Web Search | 4 | `lexflow[search]` |
| clicksign Clicksign Operations | 30 | `lexflow[clicksign]` |
| ☁️ Cloud Storage | 11 | `lexflow[gcs]` |
| 🎮 Pygame Operations | 16 | `lexflow[pygame]` |
| receitaws ReceitaWS Operations | 1 | `lexflow[receitaws]` |
| 🔍 RAG Operations | 20 | `lexflow[rag]` |
| 🐘 PgVector Operations | 9 | `lexflow[pgvector]` |
| 💬 Chat Operations | 10 | - |
| 💻 CLI Operations | 10 | - |
| 🐙 GitHub Operations | 7 | - |
| 📨 Pub/Sub | 12 | `lexflow[pubsub]` |
| ⚡ Task Operations | 10 | - |
| 📡 Channel Operations | 8 | - |
| 🔒 Sync Primitives | 8 | - |
| 💬 Slack | 29 | `lexflow[slack]` |
