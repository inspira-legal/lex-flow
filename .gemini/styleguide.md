# LexFlow — Code Review Style Guide

You are reviewing Pull Requests for **LexFlow**, a stack-based workflow interpreter used as a **library** in production by other repositories. Bugs here propagate to all consumers. Be rigorous but constructive.

## Review Instructions

- Comment with severity: **HIGH**, **MEDIUM**, or **LOW**.
- HIGH = functional breakage, broken contracts, missing tests, backward-incompatible changes without proper versioning.
- MEDIUM = architecture/pattern deviations that create tech debt, missing consistency with repo conventions.
- LOW = nits, minor consistency improvements, suggestions.
- Reference the rule ID (e.g., H3, M1) when commenting.
- Be concrete: say what is wrong and what to do instead. Do not rewrite entire files.
- Comments are non-blocking suggestions, not approvals/rejections.

## Comment Format

Use this format for each finding:

```
**[SEVERITY]** Rule <ID> — <Short description>

<What was found in the diff.>

**Suggestion:** <Concrete action to fix.>
```

At the end of the review, add a summary:

```
## Review Summary

| Severity | Count |
|----------|-------|
| HIGH | N |
| MEDIUM | N |
| LOW | N |

**Top actions:**
1. <Most important action>
2. <Second most important action>
```

---

## Project Context

LexFlow is a monorepo with three packages:
- **lexflow-core** — Core execution engine (parser, AST, evaluator, runtime, opcodes). This is the library consumed by other repos.
- **lexflow-cli** — Command-line interface.
- **lexflow-web** — Visual editor (React/TypeScript frontend) + FastAPI backend. APIs here are for dev/test only.

Architecture: `YAML/JSON Input -> Parser -> AST -> Engine/Evaluator/Executor -> Opcodes -> Output`

The public API is minimal (only 3 exports from `lexflow-core/src/lexflow/__init__.py`):
```python
from .opcodes.opcodes import opcode, default_registry, OpcodeRegistry
```

---

## Quick Reference — All Rules by Severity

### HIGH

| ID | Rule |
|----|------|
| H1 | Commit messages MUST follow Conventional Commits with scope: `<type>(<scope>): <desc>` |
| H2 | New code MUST include tests: happy path + main error paths / corner cases |
| H3 | Opcodes MUST be `async def`, fully typed, with docstring, using `@opcode()` |
| H4 | Existing opcode signatures MUST NOT change without a major version bump |
| H5 | Removing or renaming a registered opcode is a BREAKING CHANGE |
| H6 | New optional parameters on existing opcodes MUST have default values |
| H7 | Changes to `__init__.py` exports require `BREAKING CHANGE` in commit footer |
| H8 | Before modifying AST/Parser/Executor, confirm the feature cannot be an opcode |
| H9 | Core MUST NOT add application concerns (scheduling, persistence, orchestration) |
| H10 | New mandatory dependencies on core require strong justification |

### MEDIUM

| ID | Rule |
|----|------|
| M1 | Optional dependencies MUST follow the graceful degradation pattern |
| M2 | Pydantic v2 only — no v1 compatibility patterns |
| M3 | FastAPI app uses factory pattern (`create_app()`) |
| M4 | Thread-safe state MUST use `ContextVar`, not global variables |
| M5 | Ruff is mandatory — do not disable or bypass pre-commit hooks |
| M6 | Async tests use `pytestmark = pytest.mark.asyncio` with 10s timeout |
| M7 | Core MUST NOT assume a specific deployment environment |
| M8 | New core modules must follow existing single-responsibility separation |
| M9 | Imports from internal modules have no stability guarantee |
| M10 | POST endpoints return errors in body (`success=False`); GET endpoints use `HTTPException` |

### LOW

| ID | Rule |
|----|------|
| L1 | Tests for optional-dep opcodes should verify graceful degradation |
| L2 | Manual post-construction dependency wiring in Engine is the accepted pattern |
| L3 | `ParseError` is an internal detail — the public contract raises `ValueError` |
| L4 | Ruff uses default configuration — do not add custom rules without prior discussion |
| L5 | APIs in this repo are for dev/test only — endpoint security is not in scope |

---

## HIGH Severity Rules

### H1 — Conventional Commits

Commit messages MUST follow: `<type>(<scope>): <description>`

Valid types: `feat`, `fix`, `docs`, `chore`, `style`, `test`
Valid scopes: `core`, `web`, `cli`, `ai`, `examples`

Breaking changes MUST include `BREAKING CHANGE:` in the commit footer. Semantic-release depends on this format for automated versioning.

Flag commits like `updated stuff`, `fix bug`, or missing scope.

### H2 — Tests Required for New Code

Every PR with new code MUST include tests covering:
1. Happy path — the feature works with valid inputs.
2. Main error paths — invalid input, missing dependencies, timeouts.
3. Main corner cases — edge values, empty inputs, boundary conditions.

There is no minimum coverage percentage, but qualitative coverage is mandatory. If a PR adds a new opcode or module without corresponding test files, flag it as HIGH.

Tests should follow these established patterns:

**Async tests** — use module-level marker:
```python
import pytest
from lexflow import default_registry

pytestmark = pytest.mark.asyncio

async def test_my_opcode_happy_path():
    result = await default_registry.call("my_opcode", ["hello", 5])
    assert result == "hello-5"

async def test_my_opcode_missing_param():
    with pytest.raises(TypeError):
        await default_registry.call("my_opcode", [])
```

**Conditional skipping** for optional dependencies:
```python
import importlib

SOME_LIB_AVAILABLE = importlib.util.find_spec("some_lib") is not None

@pytest.mark.skipif(not SOME_LIB_AVAILABLE, reason="some_lib not installed")
class TestSomeOpcode:
    async def test_happy_path(self):
        ...
```

**Mocking pattern** (unittest.mock):
```python
from unittest.mock import AsyncMock, patch

async def test_with_mocked_client():
    with patch.dict("os.environ", {"API_KEY": "test-key"}):
        with patch("lexflow.opcodes.my_module.SomeClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.do_thing = AsyncMock(return_value={"result": "ok"})
            mock_cls.return_value = mock_client

            result = await default_registry.call("my_opcode", ["query"])
            assert result["result"] == "ok"
```

**Class-based test organization** — group related tests:
```python
class TestMyOpcodeHappyPath:
    async def test_basic_usage(self): ...
    async def test_with_optional_param(self): ...

class TestMyOpcodeErrors:
    async def test_invalid_input(self): ...
    async def test_missing_env_var(self): ...
```

Reference: `tests/unit/test_web_search_opcodes.py`

### H3 — Opcode Standards

Every opcode MUST be:
- `async def` (always async)
- Fully type-hinted (all parameters and return type)
- Decorated with `@opcode()` or `@default_registry.register()`
- Documented with a docstring

Good:
```python
@opcode()
async def my_opcode(param1: str, param2: int = 10) -> str:
    """Brief description of what this opcode does."""
    return f"{param1}-{param2}"
```

Bad (flag each violation):
```python
@opcode()
def my_opcode(param1, param2=10):
    return f"{param1}-{param2}"
```

Reference: `lexflow-core/src/lexflow/opcodes/opcodes.py`

### H4 — Opcode Signature Stability

Existing opcode signatures MUST NOT change without a major version bump. Changing parameter names, order, types, or removing parameters of a registered opcode is a breaking change.

If you see a diff that modifies the signature of an existing `@opcode()` function, check that the commit message includes `BREAKING CHANGE:` in the footer.

### H5 — Opcode Removal/Rename

Removing or renaming a registered opcode is a BREAKING CHANGE. The commit MUST include `BREAKING CHANGE:` in the footer.

### H6 — New Optional Parameters Must Have Defaults

When adding new parameters to existing opcodes, they MUST have default values to maintain backward compatibility.

Good: `async def existing_opcode(a: str, new_param: int = 10) -> str:`
Bad: `async def existing_opcode(a: str, new_param: int) -> str:`

### H7 — Public API Exports

Changes to `lexflow-core/src/lexflow/__init__.py` exports require `BREAKING CHANGE` in the commit footer. This file defines the stable public API.

**What constitutes a breaking change:**
- Changing the signature of an existing registered opcode (name, parameter order, parameter types)
- Removing or renaming a registered opcode
- Changing exports in `lexflow-core/src/lexflow/__init__.py`

**Safe changes (non-breaking):**
- Adding new opcodes
- Adding new optional parameters with defaults to existing opcodes
- Adding new internal modules
- Changes to internal module APIs (no stability guarantee per M9)

### H8 — Opcode-First Principle

Before modifying AST, Parser, Evaluator, or Executor, the author must demonstrate the feature cannot be implemented as an opcode. If a PR adds new Statement or Expression types to `ast.py`, ask: "Can this be solved with `@opcode()` instead?"

### H9 — Core Scope Boundary

The core is a **runtime/interpreter**. Application concerns MUST stay outside:
- Scheduling/cron -> outside core
- Persistence/saving workflows -> outside core
- Orchestration/queueing -> outside core
- Monitoring/alerting -> outside core
- Rate limiting -> outside core

Decision test: *"Does this feature make sense without knowing where/when the workflow runs?"* If no, it does not belong in core.

Apply these decision rules in order:

| ID | Rule | Decision Test |
|----|------|---------------|
| H8 | **If it can be an opcode, it MUST be an opcode** | *"Can I solve this with `@opcode()` + optional dep?"* If yes -> opcode. |
| H9 | **Core is a runtime/interpreter** — application concerns stay outside | *"Does this feature make sense without knowing where/when the workflow runs?"* If no -> outside core. |
| H10 | **No new mandatory heavy deps** — use optional dep pattern if external lib needed | *"Do ALL consumers need this dep, even those who don't use the feature?"* If no -> optional. |
| — | **AST/Parser/Executor changes are "heart surgery"** — require architectural review | *"Do I need to change the language grammar for this?"* If yes -> architectural review required. |
| M7 | **Core must not assume deployment environment** — no Redis, no DB, no scheduler, no queue | *"Does it work with just `python -c 'from lexflow import ...'`?"* If no -> outside core. |
| M8 | **New modules follow single-responsibility** — one file = one responsibility | *"Does this code belong in an existing file or is it a new responsibility?"* |

Use this decision table to evaluate PRs that add new modules or significant functionality:

| Feature | Passes | Fails | Verdict |
|---------|--------|-------|---------|
| Scheduling module | — | H9 (app concern), M7 (assumes scheduler infra) | **Outside core** |
| Multiple start nodes | H9 (execution model) | H8 (can't be opcode) -> triggers architectural review | **Core, but needs architectural review** |
| Kafka integration opcode | H8 (is an opcode), H10 (optional dep) | — | **Opcode with optional dep** |
| Workflow persistence/saving | — | H9 (app concern), M7 (assumes storage) | **Outside core** |
| New AST statement type | H9 (language feature) | H8 (can't be opcode) -> triggers architectural review | **Core, needs architectural review** |
| Rate limiter | — | H9 (app concern), M7 (assumes infra) | **Outside core** |

When a PR touches `ast.py`, `parser.py`, `evaluator.py`, or `executor.py`, it is "heart surgery" on the core. Require the author to justify why it cannot be solved as an opcode (H8).

### H10 — No New Mandatory Dependencies

New mandatory dependencies on `lexflow-core` require strong justification. If a feature needs an external library, it should use the optional dependency pattern (see M1).

Decision test: *"Do ALL consumers need this dependency, even those who don't use this feature?"* If no, it must be optional.

---

## MEDIUM Severity Rules

### M1 — Optional Dependency Pattern

All optional dependency modules MUST follow this exact pattern:

```python
# 1. Try import + availability flag
try:
    from some_lib import SomeClient
    SOME_LIB_AVAILABLE = True
except ImportError:
    SOME_LIB_AVAILABLE = False

# 2. Check helper with install instructions
def _check_some_lib():
    if not SOME_LIB_AVAILABLE:
        raise ImportError(
            "some-lib is required. Install with: uv add 'lexflow[some_extra]'"
        )

# 3. Client/resource getter
def _get_client():
    _check_some_lib()
    api_key = os.environ.get("SOME_API_KEY", "")
    if not api_key:
        raise ValueError("SOME_API_KEY environment variable is required")
    return SomeClient(api_key=api_key)

# 4. Registration function with early return
def register_some_opcodes():
    if not SOME_LIB_AVAILABLE:
        return
    # ... register opcodes here
```

If a PR adds a new optional dependency module and is missing any of these 4 steps, flag it. Reference files that demonstrate the correct pattern:
- `lexflow-core/src/lexflow/opcodes/opcodes_web_search.py`
- `lexflow-core/src/lexflow/opcodes/opcodes_pydantic_ai.py`
- `lexflow-core/src/lexflow/opcodes/opcodes_http.py`

If a PR adds a new optional dependency module that deviates from this pattern, flag it.

### M2 — Pydantic v2 Only

No Pydantic v1 compatibility patterns allowed:
- Use `model_config` dict, not `class Config`
- Use `Annotated[..., Field(discriminator="type")]` for union types
- Use `model_rebuild()` for self-referencing models
- No `from pydantic.v1 import ...`

### M3 — FastAPI Factory Pattern

The web package uses `create_app() -> FastAPI` factory pattern. Uvicorn runs with `factory=True`. Do not instantiate FastAPI at module level.

Reference: `lexflow-web/src/lexflow_web/app.py`

### M4 — ContextVar for Thread-Safe State

When state needs to be passed through async execution contexts, use `contextvars.ContextVar`. Never use module-level global variables for mutable state.

Good: `_my_context: ContextVar[Optional[MyType]] = ContextVar("_my_context", default=None)`
Bad: `_global_state: Optional[MyType] = None` (then mutated at runtime)

### M5 — Ruff is Mandatory

Ruff formatting and linting via pre-commit hooks must not be bypassed. Flag any:
- Use of `--no-verify` on commits
- Disabling of ruff checks via `# noqa` without justification
- Attempts to bypass pre-commit hooks

### M6 — Async Test Convention

All async tests must use `pytestmark = pytest.mark.asyncio` at module level. Test timeout is 10 seconds (configured in `pytest.ini`).

### M7 — No Deployment Environment Assumptions

Core must not assume a specific deployment environment. It must work with just `python -c 'from lexflow import ...'` — no Redis, no database, no scheduler, no message queue required.

If a PR introduces infrastructure dependencies in `lexflow-core`, flag it.

### M8 — Single Responsibility for New Modules

New core modules must follow the existing single-responsibility separation pattern. Each file has one clear responsibility (e.g., `parser.py`, `evaluator.py`, `executor.py`, `runtime.py`). Do not add unrelated functionality to existing modules.

### M9 — Internal Module Stability

Imports from internal modules (`from lexflow.parser import ...`, `from lexflow.engine import ...`) have no stability guarantee. Only exports from `lexflow-core/src/lexflow/__init__.py` are part of the stable public API.

### M10 — API Error Handling Pattern

APIs in this repo are for dev/test only. The established pattern is:
- **POST endpoints** (`/api/parse`, `/api/validate`, `/api/execute`): catch exceptions and return errors in response body with `success=False` and HTTP 200.
- **GET endpoints** (`/api/examples/*`): use `HTTPException` with appropriate status codes (404, 400).
- **WebSocket**: errors sent as `{"type": "error", "message": str(e)}`.

New endpoints should follow this pattern consistently.

---

## LOW Severity Rules

### L1 — Graceful Degradation Tests

Tests for optional-dependency opcodes should include a test that verifies the opcode is NOT registered when the dependency is missing:

```python
@pytest.mark.skipif(LIB_AVAILABLE, reason="Test only when lib is NOT installed")
class TestImportErrorWhenNotInstalled:
    async def test_opcode_not_registered(self):
        assert "my_opcode" not in default_registry._opcodes
```

### L2 — Engine Dependency Wiring

Manual post-construction dependency wiring in `Engine` is the accepted pattern for avoiding circular imports. Do not refactor this into constructor injection without prior discussion.

### L3 — ParseError is Internal

`ParseError` is an internal exception in `parser.py`. The public contract raises `ValueError` at the parser boundary. Do not expose `ParseError` to consumers.

The core uses a specific exception hierarchy — flag PRs that deviate:

| Exception | When to use | Where |
|-----------|-------------|-------|
| `ValueError` | Parse errors (public contract), invalid opcode arguments | Parser boundary, opcodes |
| `RuntimeError` | Workflow-level errors (`Throw` statement), unrecoverable agent errors | Executor, opcodes |
| `PermissionError` | Opcode/workflow not in tool allowlist | AI agent opcodes |
| `TimeoutError` | Agent or operation execution timeout | AI agent opcodes |
| `ImportError` | Missing optional dependency (with install instructions in message) | Optional dep modules |
| `TypeError` | Wrong argument types to opcodes | Opcodes |

The core does **NOT** use `HTTPException` — that is exclusively for the web layer (`lexflow-web`).

Pattern for opcode error handling:
```python
@opcode()
async def my_opcode(value: str) -> str:
    """Process a value."""
    if not value:
        raise ValueError("value cannot be empty")
    return value.upper()
```

Reference:
- `lexflow-core/src/lexflow/parser.py` — `ParseError`, conversion to `ValueError`
- `lexflow-core/src/lexflow/executor.py` — `RuntimeError` for `Throw`
- `lexflow-core/src/lexflow/opcodes/opcodes_pydantic_ai.py` — `PermissionError`, `TimeoutError`

### L4 — Ruff Default Configuration

Ruff uses default configuration (no custom `[tool.ruff]` section in pyproject.toml). Do not add custom rules without prior team discussion.

### L5 — API Security Scope

APIs in this repo are for dev/test only. Endpoint security (auth, CORS, rate limiting) is not in scope for this repository. That is the responsibility of consuming repositories.

---

## Architecture Design Patterns

The core uses these established design patterns. New code should be consistent with them:

- **Strategy Pattern** in Parser — priority-ordered `NodeHandler` subclasses (`ControlFlowHandler`, `DataHandler`, `WorkflowHandler`, `ExceptionHandler`, `DefaultHandler`).
- **Registry/Plugin Pattern** for opcodes — `OpcodeRegistry` with `@opcode()` decorator. This is THE extension mechanism.
- **Pattern Matching** (`match/case`) in Evaluator and Executor for dispatching on AST node types.
- **Null Object Pattern** for metrics — `NullMetrics` provides same interface as `ExecutionMetrics` but does nothing (zero overhead when disabled).
- **Post-construction dependency wiring** in Engine — manual injection after construction to avoid circular imports (accepted pattern, see L2).
- **Context Variable Pattern** — `ContextVar` for thread-safe state passing in async contexts.
- **Factory Pattern** — `create_app()` for FastAPI in web package.

Reference:
- `lexflow-core/src/lexflow/engine.py` — wiring and orchestration
- `lexflow-core/src/lexflow/evaluator.py` — expression evaluation with `match/case`
- `lexflow-core/src/lexflow/executor.py` — statement execution with `match/case`
- `lexflow-core/src/lexflow/parser.py` — strategy pattern with handlers
- `lexflow-core/src/lexflow/metrics.py` — null object pattern

---

## Observability

The core intentionally does NOT include logging (`import logging`, `structlog`, etc.). This is a deliberate design decision to keep the library clean — consumers configure their own logging.

**What exists:**
- `ExecutionMetrics` — custom performance metrics for workflow execution (node, statement, expression, opcode, workflow_call timings).
- `NullMetrics` — zero-overhead no-op when metrics are disabled.
- CLI `--metrics` flag for performance reports.

**What does NOT belong in core:**
- `import logging` / `structlog` / any log framework
- Request/response logging (consumer responsibility)
- Distributed tracing / OpenTelemetry (consumer responsibility)
- Health check endpoints (consumer responsibility)

If a PR adds `import logging` or any log framework to `lexflow-core`, flag it as MEDIUM — this breaks the library's logging-agnostic design. Logging belongs in consuming repositories.

## Security Considerations

**What IS already enforced in core:**
- **Path traversal protection** in the examples endpoint (`api.py:206-209`).
- **Tool allowlist** for AI agents — opcodes/workflows must be explicitly listed to be callable (`opcodes_pydantic_ai.py`).
- **`max_tool_calls` limit** to prevent runaway tool execution.
- **Execution timeout** (`timeout_seconds`) for agent operations.
- **`ContextVar` isolation** prevents cross-request state contamination.

**Flag these in PRs:**
- New endpoints that read files without path traversal validation.
- Opcode modules that fetch URLs or read files without SSRF/path traversal protection.
- Environment variables with secrets being logged or returned in responses.
- `.env` file not in `.gitignore`.
- New opcodes that execute arbitrary code without sandboxing considerations.

## Reference Files (Source of Truth)

When in doubt about patterns, check these canonical files:

| Pattern | Reference |
|---------|-----------|
| Opcode development | `lexflow-core/src/lexflow/opcodes/opcodes_http.py` |
| Optional dependency module | `lexflow-core/src/lexflow/opcodes/opcodes_web_search.py` |
| AST with discriminated unions | `lexflow-core/src/lexflow/ast.py` |
| FastAPI factory pattern | `lexflow-web/src/lexflow_web/app.py` |
| API endpoint patterns | `lexflow-web/src/lexflow_web/api.py` |
| ContextVar usage | `lexflow-core/src/lexflow/opcodes/opcodes_pydantic_ai.py` |
| Unit tests with mocking | `tests/unit/test_web_search_opcodes.py` |
| Integration tests with YAML | `tests/integration/async_features/test_background_tasks.py` |
| Custom metrics | `lexflow-core/src/lexflow/metrics.py` |
| Engine wiring | `lexflow-core/src/lexflow/engine.py` |
| Pre-commit config | `.pre-commit-config.yaml` |
| Semantic release config | `lexflow-core/pyproject.toml` (`[tool.semantic_release]`) |
