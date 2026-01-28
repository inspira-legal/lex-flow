"""
Optimized evaluator prototype - demonstrates performance optimizations.

Key optimizations:
1. Conditional metrics (skip time.perf_counter when disabled)
2. Type dispatch instead of pattern matching
3. Inlined common opcodes
4. Sync fast path for simple expressions

This is a research prototype. See docs/performance/INTERPRETER_OPTIMIZATION.md
for full details on the optimizations and their impact.
"""

from typing import Any, Union
import time

from lexflow.runtime import Runtime
from lexflow.ast import Expression, Literal, Call, Opcode, Variable
from lexflow.opcodes import OpcodeRegistry
from lexflow.metrics import ExecutionMetrics, NullMetrics


class OptimizedEvaluator:
    """
    Optimized expression evaluator with ~5-6x speedup over original.

    Optimizations applied:
    - Conditional metrics collection
    - Type-based dispatch instead of pattern matching
    - Inlined common opcodes (add, sub, mul, comparisons)
    - Sync fast path for simple expressions
    """

    # Inline simple opcodes to avoid registry lookup and wrapper overhead
    _INLINE_OPCODES = {
        "operator_add": lambda a, b: a + b,
        "operator_sub": lambda a, b: a - b,
        "operator_mul": lambda a, b: a * b,
        "operator_div": lambda a, b: a / b,
        "operator_mod": lambda a, b: a % b,
        "operator_less_than": lambda a, b: a < b,
        "operator_greater_than": lambda a, b: a > b,
        "operator_equals": lambda a, b: a == b,
        "operator_not_equals": lambda a, b: a != b,
        "operator_less_than_or_equal": lambda a, b: a <= b,
        "operator_greater_than_or_equal": lambda a, b: a >= b,
        "operator_and": lambda a, b: a and b,
        "operator_or": lambda a, b: a or b,
        "operator_not": lambda a: not a,
    }

    def __init__(
        self, runtime: Runtime, metrics: Union[ExecutionMetrics, NullMetrics] = None
    ):
        from lexflow.workflows import WorkflowManager

        self.rt = runtime
        self._scope = runtime.scope  # Direct reference for faster access
        self.metrics = metrics if metrics is not None else NullMetrics()
        self._metrics_enabled = not isinstance(self.metrics, NullMetrics)
        self.opcodes: OpcodeRegistry
        self.workflows: WorkflowManager

    def _eval_sync(self, expr: Expression) -> Any:
        """
        Synchronous evaluation for expressions that don't need async.
        Returns None if the expression requires async evaluation.
        """
        expr_type = type(expr)

        if expr_type is Literal:
            return expr.value

        if expr_type is Variable:
            return self._scope[expr.name]

        if expr_type is Opcode:
            # Check if we can evaluate synchronously (inlined + sync args)
            inline_fn = self._INLINE_OPCODES.get(expr.name)
            if inline_fn:
                args = expr.args
                if len(args) == 2:
                    a = self._eval_sync(args[0])
                    if a is None:
                        return None  # Need async
                    b = self._eval_sync(args[1])
                    if b is None:
                        return None
                    return inline_fn(a, b)
                elif len(args) == 1:
                    a = self._eval_sync(args[0])
                    if a is None:
                        return None
                    return inline_fn(a)

        # Needs async evaluation
        return None

    async def eval(self, expr: Expression) -> Any:
        """Evaluate expression - tries sync first, falls back to async."""
        if not self._metrics_enabled:
            # Try sync path first (fastest)
            result = self._eval_sync(expr)
            if result is not None or type(expr) is Literal:
                # Literal can legitimately return None
                if type(expr) is Literal:
                    return expr.value
                return result
            # Fall back to async
            return await self._eval_async(expr)

        # With metrics - still try sync for the actual computation
        start_time = time.perf_counter()
        expr_type = type(expr).__name__
        try:
            result = self._eval_sync(expr)
            if result is not None or type(expr) is Literal:
                if type(expr) is Literal:
                    return expr.value
                return result
            return await self._eval_async(expr)
        finally:
            duration = time.perf_counter() - start_time
            self.metrics.record("expression", expr_type, duration)

    async def _eval_async(self, expr: Expression) -> Any:
        """Async evaluation for expressions that need it."""
        expr_type = type(expr)

        if expr_type is Literal:
            return expr.value

        if expr_type is Variable:
            return self._scope[expr.name]

        if expr_type is Opcode:
            return await self._eval_opcode(expr)

        if expr_type is Call:
            arg_vals = [await self.eval(a) for a in expr.args]
            return await self.workflows.call(expr.name, arg_vals)

        raise ValueError(f"Unknown expression type: {expr_type}")

    async def _eval_opcode(self, expr: Opcode) -> Any:
        """Evaluate opcode with inlining."""
        name = expr.name
        args = expr.args

        inline_fn = self._INLINE_OPCODES.get(name)
        if inline_fn:
            if len(args) == 2:
                a = await self.eval(args[0])
                b = await self.eval(args[1])
                return inline_fn(a, b)
            elif len(args) == 1:
                a = await self.eval(args[0])
                return inline_fn(a)
            else:
                arg_vals = [await self.eval(a) for a in args]
                return inline_fn(*arg_vals)

        # Registry call for non-inlined opcodes
        arg_vals = [await self.eval(a) for a in args]
        return await self.opcodes.call(name, arg_vals)
