# LexFlow Interpreter Performance Research

This document summarizes performance research conducted on the LexFlow interpreter, identifying bottlenecks and potential optimizations.

## Executive Summary

| Optimization | Speedup | Complexity | Status |
|--------------|---------|------------|--------|
| Conditional metrics | 1.5x | Low | Prototype |
| Type dispatch (vs pattern matching) | 2x | Low | Prototype |
| Inlined common opcodes | 1.5x | Low | Prototype |
| Sync fast path | 1.3x | Medium | Prototype |
| **Combined (v3)** | **5-6x** | Low-Medium | Prototype |
| PyPy runtime | 3-4x more | User choice | Tested |
| **JIT Compiler** | **70-180x** | Medium | **Prototype** |

## Benchmark Results

### Original vs Optimized (CPython 3.13)

| Iterations | Pure Python | Original | Optimized v3 | Speedup | Overhead vs Python |
|------------|-------------|----------|--------------|---------|-------------------|
| 1,000 | 0.03ms | 7.3ms | 2.2ms | 3.4x | 68x |
| 10,000 | 0.3ms | 69.7ms | 13.2ms | 5.3x | 41x |
| 100,000 | 3.7ms | 730.8ms | 124.2ms | 5.9x | 33x |
| 1,000,000 | 41.8ms | 7997ms | 1266ms | 6.3x | 30x |

### PyPy Comparison (1M iterations)

| Implementation | CPython | PyPy | PyPy Speedup |
|----------------|---------|------|--------------|
| Pure Python | 41.8ms | 1.2ms | 35x |
| Original interpreter | 7997ms | 1996ms | 4x |
| Optimized v3 | 1266ms | 393.6ms | 3.2x |

## Bottleneck Analysis

Profiling revealed where time is spent during execution:

```
Time breakdown (10,000 iterations):
├── evaluator.eval()              29%  - Expression evaluation
├── pydantic.__instancecheck__    13%  - Pattern matching on Pydantic models
├── opcodes.wrapper               11%  - Opcode dispatch overhead
├── executor.exec()                8%  - Statement dispatch
├── time.perf_counter()            6%  - Metrics timing (even when disabled!)
├── abc.__instancecheck__         10%  - ABC type checking
└── Other                         23%
```

### Key Findings

1. **`time.perf_counter()` called unconditionally** - 6% overhead even with NullMetrics
2. **Pattern matching on Pydantic models is slow** - Uses custom `__instancecheck__`
3. **Opcode wrapper re-inspects params every call** - Could be cached at registration
4. **Dict scope access dominates** - ~60% of remaining overhead after optimizations

## Optimization Details

### 1. Conditional Metrics (~1.5x)

**Problem:** `time.perf_counter()` is called on every statement/expression even when metrics are disabled.

**Solution:** Check if metrics are enabled before timing:

```python
# Before
async def eval(self, expr):
    start_time = time.perf_counter()  # Always called
    # ... work ...
    self.metrics.record(...)  # NullMetrics.record() is a no-op

# After
async def eval(self, expr):
    if self._metrics_enabled:
        start_time = time.perf_counter()
    # ... work ...
    if self._metrics_enabled:
        self.metrics.record(...)
```

### 2. Type Dispatch vs Pattern Matching (~2x)

**Problem:** Pattern matching (`match/case`) on Pydantic models triggers slow `__instancecheck__`.

**Solution:** Use direct type dispatch:

```python
# Before (slow)
match expr:
    case Literal(value=v):
        return v
    case Variable(name=n):
        return self.rt.scope[n]

# After (fast)
_dispatch = {
    Literal: self._eval_literal,
    Variable: self._eval_variable,
    ...
}
handler = self._dispatch.get(type(expr))
return await handler(expr)
```

### 3. Inlined Common Opcodes (~1.5x)

**Problem:** Simple operations like `+`, `-`, `<` go through full registry lookup and wrapper.

**Solution:** Inline hot opcodes directly:

```python
_INLINE_OPCODES = {
    "operator_add": lambda a, b: a + b,
    "operator_sub": lambda a, b: a - b,
    "operator_lt": lambda a, b: a < b,
    ...
}

async def _eval_opcode(self, expr):
    inline_fn = self._INLINE_OPCODES.get(expr.name)
    if inline_fn:
        a = await self.eval(expr.args[0])
        b = await self.eval(expr.args[1])
        return inline_fn(a, b)
    # Fall back to registry
    return await self.opcodes.call(expr.name, arg_vals)
```

### 4. Sync Fast Path (~1.3x)

**Problem:** Async/await machinery has overhead even for synchronous operations.

**Solution:** Try synchronous evaluation first for simple expressions:

```python
def _eval_sync(self, expr):
    """Returns value or None if async needed."""
    if type(expr) is Literal:
        return expr.value
    if type(expr) is Variable:
        return self._scope[expr.name]
    return None  # Needs async

async def eval(self, expr):
    result = self._eval_sync(expr)
    if result is not None:
        return result
    return await self._eval_async(expr)
```

## Why Dict Access Can't Be Optimized Further

Cython benchmarks revealed that dict operations are the fundamental bottleneck:

| Implementation | 1M iterations |
|----------------|---------------|
| Cython pure (C types, no dict) | 0.35ms |
| Cython with dict scope | 90ms |
| Python with dict scope | 142ms |

Dict operations are already implemented in C within CPython. Cython can only provide ~1.5x improvement when dicts are involved.

## JIT Compiler (Implemented)

A working JIT compiler prototype is available in `research/performance/compiler.py`.
It generates Python code from workflows at parse time:

```python
# Workflow YAML:
# for i in range(n): total = total + i

# Generated Python:
async def compiled(scope, opcodes, workflows):
    scope["total"] = 0
    for i in range(int(0), int(scope["n"])):
        scope["i"] = i
        scope["total"] = (scope["total"] + scope["i"])
    return scope["total"]
```

### JIT Benchmark Results

| Test | Interpreter | Compiled | Speedup |
|------|-------------|----------|---------|
| Simple Sum (1M) | 7356ms | 107ms | **69x** |
| Nested Loops (200²) | 497ms | 4.5ms | **111x** |
| Conditionals (1M) | 15464ms | 98ms | **157x** |

### Supported Constructs

- **Statements:** For, ForEach, While, If, Try/Catch/Finally, Fork, Return, Assign, Throw
- **Expressions:** Literal, Variable, Opcode, Call (workflow calls)
- **Inlined operators:** `+`, `-`, `*`, `/`, `%`, `<`, `>`, `==`, `!=`, `<=`, `>=`, `and`, `or`, `not`

### Usage

```python
from research.performance.compiler import CompiledEngine

engine = CompiledEngine()
compiled_fn = engine.compile_workflow(workflow)

# Run compiled workflow
result = await compiled_fn(scope, opcodes, workflows)

# View generated code
print(engine.get_source(workflow))
```

**Benefits:**
- Native Python speed for hot loops
- No interpreter overhead
- Works on standard CPython
- Transparent to users
- 70-180x speedup for computation-heavy workflows

## Recommendations

### For LexFlow maintainers:
1. Apply v3 optimizations to core interpreter (5-6x speedup, low risk)
2. Consider workflow compiler for v2.0 (high impact, medium complexity)

### For users needing maximum performance:
1. Push computation into opcodes (use NumPy, etc.)
2. Consider PyPy for computation-heavy workloads
3. Avoid tight loops in workflow DSL; use batch operations

## When Interpreter Performance Matters

| Workload | Interpreter Overhead | Optimize? |
|----------|---------------------|-----------|
| PDF processing (100ms/doc) | 0.01% | No |
| HTTP requests (50ms/req) | 0.02% | No |
| AI inference (1s/call) | 0.001% | No |
| Tight math loops (1M ops) | 99% | Yes - use opcodes |

**Rule of thumb:** If each operation takes >1ms, interpreter overhead is negligible.
