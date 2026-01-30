# LexFlow Opcode Reference

Quick reference for all available opcodes in LexFlow.

> **Note:** This file is auto-generated. Run `lexflow docs generate` to update.

## Table of Contents

- [I/O Operations](#i/o-operations)
- [Operators](#operators)
- [Math Operations](#math-operations)
- [String Operations](#string-operations)
- [List Operations](#list-operations)
- [Dictionary Operations](#dictionary-operations)
- [Object Operations](#object-operations)
- [Type Conversions](#type-conversions)
- [Exception Operations](#exception-operations)
- [Assertion Operations](#assertion-operations)
- [Workflow Operations](#workflow-operations)
- [Data Operations](#data-operations)
- [Control Flow](#control-flow)
- [Async Operations](#async-operations)
- [Chat Operations](#chat-operations)
- [GitHub Operations](#github-operations)
- [Task Operations](#task-operations)
- [Other Operations](#other-operations)

## I/O Operations

### `io_input(prompt="")`

Get input from user.

**Returns:** `str`

---

### `io_print(values)`

Print values to stdout.

**Returns:** `NoneType`

---

## Operators

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

## Math Operations

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

## String Operations

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

## List Operations

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

## Dictionary Operations

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

## Object Operations

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

## Type Conversions

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

## Exception Operations

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

## Assertion Operations

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

## Workflow Operations

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

## Data Operations

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

## Control Flow

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

## Async Operations

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

## Chat Operations

### `chat_add_assistant(history, content)`

Add an assistant message to chat history.

Shorthand for chat_add_message(history, "assistant", content).

Args:
    history: The chat history list to modify
    content: The assistant's response

Returns:
    The updated history

Example:
    chat_add_assistant(history, "The weather is sunny!")


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

Example:
    chat_add_message(history, "user", "Hello!")
    chat_add_message(history, "assistant", "Hi there!")


**Parameters:**

- `history` (List, required)
- `role` (str, required)
- `content` (str, required)

**Returns:** `List`

---

### `chat_add_user(history, content)`

Add a user message to chat history.

Shorthand for chat_add_message(history, "user", content).

Args:
    history: The chat history list to modify
    content: The user's message

Returns:
    The updated history

Example:
    chat_add_user(history, "What is the weather today?")


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

Example:
    chat_clear(history)
    # history is now []


**Returns:** `List`

---

### `chat_create()`

Create a new empty chat history.

Returns:
    Empty list ready to store chat messages.

Example:
    history = chat_create()
    # Returns: []


**Returns:** `List`

---

### `chat_format_for_display(history)`

Format chat history as a readable string for display.

Args:
    history: The chat history list

Returns:
    Formatted string with each message on its own line(s)

Example:
    Output:
    User: Hello!
    Assistant: Hi there! How can I help you today?
    User: What is 2+2?
    Assistant: 2+2 equals 4.


**Returns:** `str`

---

### `chat_get_last(history, role=None)`

Get the last message from chat history.

Args:
    history: The chat history list
    role: Optional filter - if specified, get last message with this role

Returns:
    The last message dict, or None if history is empty or no matching message

Example:
    # Get last message of any type
    last = chat_get_last(history)
    # Returns: {"role": "assistant", "content": "..."}

    # Get last user message specifically
    last_user = chat_get_last(history, "user")


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

Example:
    count = chat_length(history)  # Returns: 5


**Returns:** `int`

---

### `chat_to_prompt(history)`

Convert chat history to a single prompt string for AI.

This formats the conversation history in a way that can be passed
as context to an AI agent that doesn't natively support chat history.

Args:
    history: The chat history list

Returns:
    A formatted string containing the conversation context

Example:
    prompt = chat_to_prompt(history)
    # Returns:
    # "Previous conversation:
    # User: Hello!
    # Assistant: Hi there!
    #
    # Continue the conversation."


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
    agent: A pydantic-ai Agent instance (from pydantic_ai_create_agent)
    history: The chat history list (will be modified)
    user_message: The new user message to send

Returns:
    The assistant's response string

Example:
    response = chat_with_agent(agent, history, "What is the capital of France?")
    # history now contains both the user message and assistant response
    # response = "The capital of France is Paris."

Note:
    The agent must be created using pydantic_ai_create_agent opcode.
    This opcode modifies the history in place.


**Parameters:**

- `agent` (Any, required)
- `history` (List, required)
- `user_message` (str, required)

**Returns:** `str`

---

## GitHub Operations

### `github_get_file_content(owner, repo, path, ref="HEAD")`

Get file content from a repository at a specific ref.

    Args:
        owner: Repository owner
        repo: Repository name
        path: File path relative to repo root
        ref: Git reference (branch, tag, or commit SHA). Default: "HEAD"

    Returns:
        File content as a string (UTF-8 decoded)

    Raises:
        RuntimeError: If file not found or gh command fails

    Example:
        content = github_get_file_content("anthropics", "claude-code", "README.md")
        # Returns: "# Claude Code

This project..."

        # Get file from specific branch
        content = github_get_file_content(
            "anthropics", "claude-code", "src/main.py", ref="feature-branch"
        )
    

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

    Raises:
        RuntimeError: If gh command fails

    Example:
        diff = github_get_pr_diff("anthropics", "claude-code", 123)
        # Returns: "diff --git a/file.py b/file.py
..."
    

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
    List of dicts, each containing:
    - path: File path relative to repo root
    - additions: Number of lines added
    - deletions: Number of lines deleted
    - status: Change status (added, modified, removed, renamed)

Raises:
    RuntimeError: If gh command fails

Example:
    files = github_get_pr_files("anthropics", "claude-code", 123)
    # Returns: [
    #     {"path": "src/main.py", "additions": 10, "deletions": 2, "status": "modified"},
    #     {"path": "README.md", "additions": 5, "deletions": 0, "status": "added"}
    # ]


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
    Dict with PR metadata:
    - title: PR title
    - body: PR description/body
    - author: PR author username
    - state: PR state (OPEN, CLOSED, MERGED)
    - base_branch: Target branch
    - head_branch: Source branch
    - url: PR web URL

Raises:
    RuntimeError: If gh command fails (e.g., PR not found, auth issues)

Example:
    pr_info = github_get_pr_info("anthropics", "claude-code", 123)
    # Returns: {
    #     "title": "Add new feature",
    #     "body": "This PR adds...",
    #     "author": "octocat",
    #     "state": "OPEN",
    #     "base_branch": "main",
    #     "head_branch": "feature/new-thing",
    #     "url": "https://github.com/anthropics/claude-code/pull/123"
    # }


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
    Dict with repo metadata:
    - name: Repository name
    - full_name: Full name (owner/repo)
    - description: Repository description
    - default_branch: Default branch name
    - url: Repository web URL
    - is_private: Whether repo is private

Raises:
    RuntimeError: If gh command fails

Example:
    repo_info = github_get_repo_info("anthropics", "claude-code")
    # Returns: {
    #     "name": "claude-code",
    #     "full_name": "anthropics/claude-code",
    #     "description": "Claude Code CLI",
    #     "default_branch": "main",
    #     "url": "https://github.com/anthropics/claude-code",
    #     "is_private": False
    # }


**Parameters:**

- `owner` (str, required)
- `repo` (str, required)

**Returns:** `Dict`

---

### `github_is_available()`

Check if GitHub CLI is available and authenticated.

Returns:
    True if gh CLI is installed and can make API calls, False otherwise

Example:
    if github_is_available():
        pr_info = github_get_pr_info(...)
    else:
        print("GitHub CLI not available")


**Returns:** `bool`

---

### `github_list_pr_comments(owner, repo, pr_number)`

Get all comments on a PR.

This includes both review comments (on specific lines) and issue comments
(general PR discussion).

Args:
    owner: Repository owner
    repo: Repository name
    pr_number: Pull request number

Returns:
    List of comment dicts, each containing:
    - id: Comment ID
    - author: Comment author username
    - body: Comment text
    - created_at: ISO timestamp of when comment was created
    - type: "review" or "issue" indicating comment type

Raises:
    RuntimeError: If gh command fails

Example:
    comments = github_list_pr_comments("anthropics", "claude-code", 123)
    # Returns: [
    #     {
    #         "id": "123456",
    #         "author": "reviewer",
    #         "body": "Looks good!",
    #         "created_at": "2024-01-15T10:30:00Z",
    #         "type": "issue"
    #     }
    # ]


**Parameters:**

- `owner` (str, required)
- `repo` (str, required)
- `pr_number` (int, required)

**Returns:** `List`

---

## Task Operations

### `task_await(task, timeout=None)`

Wait for a background task to complete and get its result.

Args:
    task: LexFlowTask handle from control_spawn
    timeout: Optional timeout in seconds

Returns:
    The task's return value (usually None for spawn tasks)

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
    timeout: Optional timeout in seconds for all tasks combined

Returns:
    List of results in the same order as tasks

Raises:
    asyncio.TimeoutError: If timeout exceeded
    Exception: If any task raised an exception


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
    True if cancel was requested (task may still be running briefly)


**Returns:** `bool`

---

### `task_exception(task)`

Get the exception message from a failed task.

Args:
    task: LexFlowTask handle from control_spawn

Returns:
    Exception message as string, or None if task succeeded or not done


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
    Exception: If the task raised an exception


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

Useful for cooperative multitasking when doing CPU-bound work
in a background task.


**Returns:** `NoneType`

---

## Other Operations

### `channel_close(channel)`

Close a channel.

After closing, no more values can be sent.

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
    Dict with keys:
    - value: The received value (None if nothing received)
    - ok: True if a value was received, False otherwise


**Returns:** `dict`

---

### `clear_line()`

Clear the current terminal line.

**Returns:** `NoneType`

---

### `noop()`

No operation.

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

Example:
    progress_bar(25, 100, "Processing files")
    # Output: Processing files [███████░░░░░░░░░░░░░░░░░░░░░░░] 25%


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

Start an animated spinner. Returns spinner object to control it later.

Args:
    message: Message to display next to spinner

Returns:
    Spinner object (use with spinner_stop, spinner_update)

Example:
    spinner = spinner_start("Fetching data")
    # ... do work ...
    spinner_stop(spinner, "Data loaded!")


**Returns:** `Spinner`

---

### `spinner_stop(spinner, message="", success=True)`

Stop a spinner and show completion message.

Args:
    spinner: Spinner object from spinner_start
    message: Final message to display (empty = use original message + "done")
    success: True for checkmark, False for X mark

Example:
    spinner_stop(spinner, "Loaded 42 items", success=True)


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

### `text_chunk(text, chunk_size=500, overlap=50)`

Split text into overlapping chunks for embedding.

Args:
    text: Text to split into chunks
    chunk_size: Maximum characters per chunk (default: 500)
    overlap: Characters to overlap between chunks (default: 50)

Returns:
    List of text chunks

Example:
    text: "Long document text..."
    chunk_size: 500
    overlap: 50


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
    overlap: Number of sentences to overlap between chunks (default: 1)

Returns:
    List of text chunks split at sentence boundaries

Example:
    text: "First sentence. Second sentence. Third sentence."
    sentences_per_chunk: 2
    overlap: 1


**Parameters:**

- `text` (str, required)
- `sentences_per_chunk` (int, optional, default: `5`)
- `overlap` (int, optional, default: `1`)

**Returns:** `List`

---

## Summary

**Total opcodes:** 149
