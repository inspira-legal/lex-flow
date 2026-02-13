# Code Review Guide — LexFlow

## Purpose

This guide defines the review rules for Pull Requests in the LexFlow repository. Its goals are:

1. **Protect the core** — LexFlow is a library used in production by other repositories. Bugs here propagate to all consumers.
2. **Maintain consistency** — enforce the patterns and conventions established in the codebase.
3. **Enable automation** — rules are structured so a CI bot can comment on PRs (non-blocking) referencing specific sections.

Severity levels:
- **HIGH** — Functional breakage, broken contracts, missing tests for critical paths, backward-incompatible changes without proper versioning.
- **MEDIUM** — Architecture/pattern deviations that create tech debt, missing consistency with repo conventions.
- **LOW** — Nits, minor consistency improvements, suggestions.

---

## How to Use Before Opening a PR

Before submitting a PR, verify:

1. `uv run pytest` passes (unit + integration).
2. Pre-commit hooks pass (`ruff-format` + `ruff --fix`).
3. Commit messages follow Conventional Commits: `<type>(<scope>): <description>`.
4. New code includes tests (happy path + main error/corner cases).
5. No breaking changes without `BREAKING CHANGE` in commit footer.
6. If adding a new opcode: async, typed, with docstring, using `@opcode()`.
7. If adding optional dependencies: follow the graceful degradation pattern.
8. If modifying AST/Parser/Executor: confirm it cannot be solved as an opcode first.

---

## Checklist by Severity

### HIGH

| ID | Rule | Section |
|----|------|---------|
| H1 | Commit messages MUST follow Conventional Commits with scope: `<type>(<scope>): <desc>` | [Repo Patterns > Commits](#commits) |
| H2 | New code MUST include tests: happy path + main error paths / corner cases | [Tests](#tests-and-functional-validation) |
| H3 | Opcodes MUST be `async def`, fully typed, with docstring, using `@opcode()` | [Repo Patterns > Opcodes](#opcodes) |
| H4 | Existing opcode signatures MUST NOT change without a major version bump | [Contracts > Backward Compatibility](#backward-compatibility) |
| H5 | Removing or renaming a registered opcode is a BREAKING CHANGE | [Contracts > Backward Compatibility](#backward-compatibility) |
| H6 | New optional parameters on existing opcodes MUST have default values | [Contracts > Backward Compatibility](#backward-compatibility) |
| H7 | Changes to `__init__.py` exports require `BREAKING CHANGE` in commit footer | [Contracts > Backward Compatibility](#backward-compatibility) |
| H8 | Before modifying AST/Parser/Executor, confirm the feature cannot be an opcode | [Core Extension](#what-belongs-in-core) |
| H9 | Core MUST NOT add application concerns (scheduling, persistence, orchestration) | [Core Extension](#what-belongs-in-core) |
| H10 | New mandatory dependencies on core require strong justification | [Core Extension](#what-belongs-in-core) |

### MEDIUM

| ID | Rule | Section |
|----|------|---------|
| M1 | Optional dependencies MUST follow the graceful degradation pattern: `try/except ImportError` + `*_AVAILABLE` flag + `_check_*()` + `register_*_opcodes()` | [Repo Patterns > Dependencies](#optional-dependencies) |
| M2 | Pydantic v2 only — no v1 compatibility patterns | [Repo Patterns > Pydantic](#pydantic) |
| M3 | FastAPI app uses factory pattern (`create_app()`) | [Repo Patterns > FastAPI](#fastapi) |
| M4 | Thread-safe state MUST use `ContextVar`, not global variables | [Repo Patterns > State](#state-management) |
| M5 | Ruff is mandatory — do not disable or bypass pre-commit hooks | [Repo Patterns > Linting](#linting) |
| M6 | Async tests use `pytestmark = pytest.mark.asyncio` with 10s timeout | [Tests](#tests-and-functional-validation) |
| M7 | Core MUST NOT assume a specific deployment environment | [Core Extension](#what-belongs-in-core) |
| M8 | New core modules must follow existing single-responsibility separation | [Core Extension](#what-belongs-in-core) |
| M9 | Imports from internal modules (`from lexflow.parser import ...`) have no stability guarantee | [Contracts > Backward Compatibility](#backward-compatibility) |
| M10 | POST endpoints return errors in body (`success=False`); GET endpoints use `HTTPException` | [Contracts > API](#api-endpoints) |

### LOW

| ID | Rule | Section |
|----|------|---------|
| L1 | Tests for optional-dep opcodes should verify graceful degradation (opcode NOT registered when dep missing) | [Tests](#tests-and-functional-validation) |
| L2 | Manual post-construction dependency wiring in Engine is the accepted pattern for circular imports | [Repo Patterns > Architecture](#architecture) |
| L3 | `ParseError` is an internal detail — the public contract raises `ValueError` | [Exceptions](#exceptions-and-errors) |
| L4 | Ruff uses default configuration — do not add custom rules without prior discussion | [Repo Patterns > Linting](#linting) |
| L5 | APIs in this repo are for dev/test only — endpoint security is not in scope | [Security](#security) |

---

## Repo Patterns

### Commits

**Rule H1** — Conventional Commits with scope.

Format: `<type>(<scope>): <description>`

Valid types: `feat`, `fix`, `docs`, `chore`, `style`, `test`
Valid scopes: `core`, `web`, `cli`, `ai`, `examples`

Breaking changes MUST include `BREAKING CHANGE:` in the commit footer. This triggers a major version bump via semantic-release.

```
# Good
feat(ai): add ai_agent_with_tools opcode for agentic workflows
fix(core): handle empty node list in parser

# Good — breaking change
feat(core): rename default_registry to global_registry

BREAKING CHANGE: default_registry has been renamed to global_registry

# Bad
updated stuff
fix bug
```

### Opcodes

**Rule H3** — Every opcode must be:
- `async def`
- Fully type-hinted (parameters and return)
- Decorated with `@opcode()` or registered via `@default_registry.register()`
- Documented with a docstring

```python
# Good
@opcode()
async def my_opcode(param1: str, param2: int = 10) -> str:
    """Brief description of what this opcode does."""
    return f"{param1}-{param2}"

# Bad — missing async, types, docstring
@opcode()
def my_opcode(param1, param2=10):
    return f"{param1}-{param2}"
```

Reference: `lexflow-core/src/lexflow/opcodes/opcodes.py`

### Optional Dependencies

**Rule M1** — All optional dependency modules MUST follow this exact pattern:

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
    # ... register opcodes
```

Reference files:
- `lexflow-core/src/lexflow/opcodes/opcodes_web_search.py`
- `lexflow-core/src/lexflow/opcodes/opcodes_pydantic_ai.py`
- `lexflow-core/src/lexflow/opcodes/opcodes_http.py`

### Pydantic

**Rule M2** — Pydantic v2 only.

- Use `BaseModel` with `model_config` (not `class Config`)
- Use `Annotated[..., Field(discriminator="type")]` for union types
- Use `model_rebuild()` for self-referencing models
- No `from pydantic.v1 import ...`

Reference: `lexflow-core/src/lexflow/ast.py`

### FastAPI

**Rule M3** — The web package uses a factory pattern.

- App is created via `create_app() -> FastAPI`
- Uvicorn runs with `factory=True`
- Routers are included with appropriate prefixes (`/api` for REST, root for WebSocket)

Reference: `lexflow-web/src/lexflow_web/app.py`

### State Management

**Rule M4** — Thread-safe state uses `ContextVar`.

When state needs to be passed through async execution contexts (e.g., tool call tracking, WebSocket send/receive), use `contextvars.ContextVar` — never module-level globals.

```python
# Good
from contextvars import ContextVar
_my_context: ContextVar[Optional[MyType]] = ContextVar("_my_context", default=None)

# Bad
_global_state: Optional[MyType] = None
```

Reference:
- `lexflow-core/src/lexflow/opcodes/opcodes_pydantic_ai.py` — `_tool_call_context`, `_workflow_manager_context`
- `lexflow-web/src/lexflow_web/opcodes.py` — `web_send`, `web_receive`

### Linting

**Rules M5, L4** — Ruff is mandatory via pre-commit hooks.

- `ruff-format` for formatting
- `ruff check --fix` for linting
- Default configuration (no custom `[tool.ruff]` section)
- Do not bypass pre-commit hooks (`--no-verify`)
- Do not add/remove ruff rules without prior team discussion

Reference: `.pre-commit-config.yaml`

### Architecture

**Rule L2** — The core follows a pipeline architecture:

```
YAML/JSON Input -> Parser -> AST -> Engine/Evaluator/Executor -> Opcodes -> Output
```

Key design decisions:
- **Strategy Pattern** in Parser (priority-ordered handlers)
- **Registry/Plugin Pattern** for opcodes
- **Pattern Matching** (`match/case`) in Evaluator and Executor
- **Null Object Pattern** for metrics (`NullMetrics`)
- **Post-construction dependency wiring** in Engine to avoid circular imports (accepted pattern)

Reference:
- `lexflow-core/src/lexflow/engine.py` — wiring and orchestration
- `lexflow-core/src/lexflow/evaluator.py` — expression evaluation
- `lexflow-core/src/lexflow/executor.py` — statement execution

---

## What Belongs in Core

These rules determine whether a new feature should be added to `lexflow-core` or developed externally.

### Decision Rules

| ID | Rule | Decision Test |
|----|------|---------------|
| H8 | **If it can be an opcode, it MUST be an opcode** | *"Can I solve this with `@opcode()` + optional dep?"* If yes -> opcode. |
| H9 | **Core is a runtime/interpreter** — application concerns stay outside | *"Does this feature make sense without knowing where/when the workflow runs?"* If no -> outside core. |
| H10 | **No new mandatory heavy deps** — use optional dep pattern if external lib needed | *"Do ALL consumers need this dep, even those who don't use the feature?"* If no -> optional. |
| S4 | **AST/Parser/Executor changes are "heart surgery"** — require architectural review | *"Do I need to change the language grammar for this?"* If yes -> architectural review required. |
| M7 | **Core must not assume deployment environment** — no Redis, no DB, no scheduler, no queue | *"Does it work with just `python -c 'from lexflow import ...'`?"* If no -> outside core. |
| M8 | **New modules follow single-responsibility** — one file = one responsibility | *"Does this code belong in an existing file or is it a new responsibility?"* |

### Decision Examples

| Feature | Passes | Fails | Verdict |
|---------|--------|-------|---------|
| Scheduling module | — | H9 (app concern), M7 (assumes scheduler infra) | **Outside core** |
| Multiple start nodes | H9 (execution model) | H8 (can't be opcode) -> triggers S4 | **Core, but needs architectural review** |
| Kafka integration opcode | H8 (is an opcode), H10 (optional dep) | — | **Opcode with optional dep** |
| Workflow persistence/saving | — | H9 (app concern), M7 (assumes storage) | **Outside core** |
| New AST statement type | H9 (language feature) | H8 (can't be opcode) -> triggers S4 | **Core, needs architectural review** |
| Rate limiter | — | H9 (app concern), M7 (assumes infra) | **Outside core** |

---

## Tests and Functional Validation

### Mandatory (HIGH)

**Rule H2** — Every PR with new code MUST include tests covering:

1. **Happy path** — the feature works as expected with valid inputs.
2. **Main error paths** — what happens with invalid input, missing dependencies, timeouts.
3. **Corner cases** — edge values, empty inputs, boundary conditions.

There is no minimum coverage percentage, but qualitative coverage is mandatory.

### Patterns to Follow

**Async tests** (Rule M6):
```python
import pytest

pytestmark = pytest.mark.asyncio

async def test_my_opcode_happy_path():
    result = await default_registry.call("my_opcode", ["hello", 5])
    assert result == "hello-5"

async def test_my_opcode_missing_param():
    with pytest.raises(TypeError):
        await default_registry.call("my_opcode", [])
```

**Conditional skipping for optional deps**:
```python
import importlib

SOME_LIB_AVAILABLE = importlib.util.find_spec("some_lib") is not None

@pytest.mark.skipif(not SOME_LIB_AVAILABLE, reason="some_lib not installed")
class TestSomeOpcode:
    async def test_happy_path(self):
        ...
```

**Graceful degradation tests** (Rule L1):
```python
@pytest.mark.skipif(SOME_LIB_AVAILABLE, reason="Test only when lib is NOT installed")
class TestImportErrorWhenNotInstalled:
    async def test_opcode_not_registered(self):
        assert "some_opcode" not in default_registry._opcodes
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

---

## Contracts

### Backward Compatibility

LexFlow is a library — breaking changes affect all consumers.

| Rule | What constitutes a breaking change |
|------|------------------------------------|
| H4 | Changing the signature of an existing registered opcode (name, parameter order, parameter types) |
| H5 | Removing or renaming a registered opcode |
| H7 | Changing exports in `lexflow-core/src/lexflow/__init__.py` |

**Current public API** (stable):
```python
# lexflow-core/src/lexflow/__init__.py
from .opcodes.opcodes import opcode, default_registry, OpcodeRegistry
```

**Safe changes** (non-breaking):
- Adding new opcodes
- Adding new optional parameters with defaults to existing opcodes (Rule H6)
- Adding new internal modules
- Changes to internal module APIs (Rule M9 — no stability guarantee)

**Breaking changes MUST**:
- Include `BREAKING CHANGE:` in the commit message footer
- This triggers a major version bump via semantic-release

### API Endpoints

**Rule M10** — APIs in this repo are for development/testing only.

- **POST endpoints** (`/api/parse`, `/api/validate`, `/api/execute`): return errors in response body with `success=False` and HTTP 200. The frontend expects consistent JSON.
- **GET endpoints** (`/api/examples/*`): use `HTTPException` with appropriate status codes (404, 400).
- **WebSocket**: errors sent as `{"type": "error", "message": str(e)}`.

This pattern is intentional. Production API error handling is the responsibility of consuming repositories.

Reference: `lexflow-web/src/lexflow_web/api.py`

---

## Exceptions and Errors

**Rule L3** — Exception handling in the core:

- `ParseError` is an **internal** exception in `parser.py`. It is always converted to `ValueError` at the boundary. Consumers should catch `ValueError` for parse errors.
- `RuntimeError` is used for workflow-level errors (e.g., `Throw` statement).
- `PermissionError` is raised when an opcode/workflow is not in the tool allowlist.
- `TimeoutError` for agent execution timeouts.
- `ImportError` with descriptive message for missing optional dependencies.

The core does **not** use `HTTPException` — that is exclusively for the web layer.

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

---

## Observability

The core intentionally does **NOT** include logging (Rule R2). This is a design decision to keep the library clean — consumers configure their own logging.

**What exists**:
- `ExecutionMetrics` — custom performance metrics for workflow execution (node, statement, expression, opcode, workflow_call timings).
- `NullMetrics` — zero-overhead no-op when metrics are disabled.
- CLI `--metrics` flag for performance reports.

**What does NOT belong in core**:
- `import logging` / `structlog` / any log framework
- Request/response logging (consumer responsibility)
- Distributed tracing (consumer responsibility)
- Health check endpoints (consumer responsibility)

Reference: `lexflow-core/src/lexflow/metrics.py`

---

## Security

**Rule L5** — The APIs in this repo are for development/testing only. Endpoint security (auth, CORS, rate limiting) is **not in scope** — that is the responsibility of consuming repositories.

**What IS enforced in core**:
- **Path traversal protection** in the examples endpoint (`api.py:206-209`).
- **Tool allowlist** for AI agents — opcodes/workflows must be explicitly listed to be callable (`opcodes_pydantic_ai.py`).
- **`max_tool_calls` limit** to prevent runaway tool execution.
- **Execution timeout** (`timeout_seconds`) for agent operations.
- **`ContextVar` isolation** prevents cross-request state contamination.

**What to watch in PRs**:
- New endpoints that read files should validate paths against traversal.
- New opcode modules that fetch URLs or read files should consider SSRF/path traversal.
- Environment variables with secrets should never be logged or returned in responses.
- The `.env` file must remain in `.gitignore`.

---

## Repo Examples (Source of Truth)

| Pattern | Reference File |
|---------|---------------|
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
| Semantic release config | `lexflow-core/pyproject.toml` (section `[tool.semantic_release]`) |
