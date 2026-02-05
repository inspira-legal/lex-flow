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
- [📄 HTML Operations](#html-operations) *(requires `lexflow[http]`)*
- [📋 JSON Operations](#json-operations)
- [🎮 Pygame Operations](#pygame-operations) *(requires `lexflow[pygame]`)*
- [🔍 RAG Operations](#rag-operations) *(requires `lexflow[rag]`)*
- [💬 Chat Operations](#chat-operations)
- [💻 CLI Operations](#cli-operations)
- [🐙 GitHub Operations](#github-operations)
- [⚡ Task Operations](#task-operations)
- [📡 Channel Operations](#channel-operations)
- [🔒 Sync Primitives](#sync-primitives)

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

**Returns:** `list`

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

**Returns:** `list`

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

- `obj` (Union, required)
- `key` (str, required)
- `default` (Any, optional, default: `None`)

**Returns:** `Any`

---

### `object_has(obj, key)`

Check if object has property.

**Parameters:**

- `obj` (Union, required)
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

- `obj` (Union, required)
- `key` (str, required)

**Returns:** `Union`

---

### `object_set(obj, key, value)`

Set property value (returns object for chaining).

**Parameters:**

- `obj` (Union, required)
- `key` (str, required)
- `value` (Any, required)

**Returns:** `Union`

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

**Returns:** `list`

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

- `items` (List, required)
- `delay` (float, optional, default: `0`)

**Returns:** `AsyncGenerator`

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

**Returns:** `AsyncGenerator`

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
- `project` (Optional, optional, default: `None`)
- `location` (Optional, optional, default: `None`)

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
- `headers` (Optional, optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict`

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
- `data` (Optional, optional, default: `None`)
- `json` (Optional, optional, default: `None`)
- `headers` (Optional, optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict`

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
- `data` (Optional, optional, default: `None`)
- `json` (Optional, optional, default: `None`)
- `headers` (Optional, optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `Dict`

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
- `headers` (Optional, optional, default: `None`)

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
- `headers` (Optional, optional, default: `None`)

**Returns:** `Dict`

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
- `data` (Optional, optional, default: `None`)
- `json` (Optional, optional, default: `None`)
- `headers` (Optional, optional, default: `None`)

**Returns:** `Dict`

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
- `headers` (Optional, optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `AsyncGenerator`

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
- `headers` (Optional, optional, default: `None`)
- `timeout` (float, optional, default: `30.0`)

**Returns:** `AsyncGenerator`

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
- `default` (Optional, optional, default: `None`)

**Returns:** `Optional`

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

**Returns:** `List`

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

**Returns:** `Optional`

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
- `indent` (Optional, optional, default: `None`)

**Returns:** `str`

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
- `results` (List, required)
- `top_k` (int, optional, default: `10`)
- `text_field` (str, optional, default: `"text"`)
- `alpha` (float, optional, default: `0.5`)

**Returns:** `List`

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

**Returns:** `List`

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

- `texts` (List, required)
- `project` (str, required)
- `location` (str, optional, default: `"us-central1"`)
- `model` (str, optional, default: `"text-embedding-004"`)

**Returns:** `List`

---

### `pdf_extract_pages(file_path)`

Extract text from a PDF file page by page.

Args:
    file_path: Path to the PDF file

Returns:
    List of strings, one per page


**Returns:** `List`

---

### `pdf_extract_pages_from_bytes(data)`

Extract text from PDF bytes page by page.

Args:
    data: PDF content as bytes

Returns:
    List of strings, one per page


**Returns:** `List`

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
- `point_ids` (List, required)

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
- `query_vector` (List, required)
- `limit` (int, optional, default: `5`)

**Returns:** `List`

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
- `vector` (List, required)
- `payload` (Optional, optional, default: `None`)

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
- `point_ids` (List, required)
- `vectors` (List, required)
- `payloads` (Optional, optional, default: `None`)

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

**Returns:** `List`

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

**Returns:** `List`

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

- `pages` (List, required)
- `chunk_size` (int, optional, default: `500`)
- `overlap` (int, optional, default: `50`)

**Returns:** `List`

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

- `pages` (List, required)
- `chunk_size` (int, optional, default: `1000`)
- `overlap` (int, optional, default: `200`)
- `min_chunk_size` (int, optional, default: `100`)

**Returns:** `List`

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

- `history` (List, required)
- `content` (str, required)

**Returns:** `List`

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

- `history` (List, required)
- `role` (str, required)
- `content` (str, required)

**Returns:** `List`

---

### `chat_add_user(history, content)`

Add a user message to chat history.

Args:
    history: The chat history list to modify
    content: The user's message

Returns:
    The updated history


**Parameters:**

- `history` (List, required)
- `content` (str, required)

**Returns:** `List`

---

### `chat_clear(history)`

Clear all messages from chat history.

Args:
    history: The chat history list to clear

Returns:
    The same list, now empty


**Returns:** `List`

---

### `chat_create()`

Create a new empty chat history.

Returns:
    Empty list ready to store chat messages


**Returns:** `List`

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

- `history` (List, required)
- `role` (Optional, optional, default: `None`)

**Returns:** `Optional`

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
- `history` (List, required)
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

**Returns:** `List`

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

**Returns:** `Dict`

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

**Returns:** `Dict`

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

**Returns:** `List`

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
- `timeout` (Optional, optional, default: `None`)

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
- `timeout` (Optional, optional, default: `None`)

**Returns:** `List`

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


**Returns:** `Optional`

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
- `timeout` (Optional, optional, default: `None`)

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
- `timeout` (Optional, optional, default: `None`)

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
- `timeout` (Optional, optional, default: `None`)

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

## Summary

**Total opcodes:** 202

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
| 🤖 AI Operations (Pydantic AI) | 4 | `lexflow[ai]` |
| 🌐 HTTP Operations | 8 | `lexflow[http]` |
| 📄 HTML Operations | 5 | `lexflow[http]` |
| 📋 JSON Operations | 2 | - |
| 🎮 Pygame Operations | 16 | `lexflow[pygame]` |
| 🔍 RAG Operations | 20 | `lexflow[rag]` |
| 💬 Chat Operations | 10 | - |
| 💻 CLI Operations | 10 | - |
| 🐙 GitHub Operations | 7 | - |
| ⚡ Task Operations | 10 | - |
| 📡 Channel Operations | 8 | - |
| 🔒 Sync Primitives | 8 | - |
