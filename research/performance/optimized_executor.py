"""
Optimized executor prototype - demonstrates performance optimizations.

Key optimizations:
1. Conditional metrics (skip time.perf_counter when disabled)
2. Type dispatch instead of pattern matching on Pydantic models

This is a research prototype. See docs/performance/INTERPRETER_OPTIMIZATION.md
for full details on the optimizations and their impact.
"""

from enum import auto, Enum
from typing import Optional, Union
import asyncio
import time

from lexflow.runtime import Runtime
from lexflow.ast import (
    Assign,
    Block,
    If,
    While,
    For,
    ForEach,
    Fork,
    Return,
    ExprStmt,
    OpStmt,
    Try,
    Throw,
    Catch,
    Statement,
)
from lexflow.opcodes import OpcodeRegistry
from lexflow.metrics import ExecutionMetrics, NullMetrics


class Flow(Enum):
    """Control flow signals."""

    NEXT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()


class OptimizedExecutor:
    """
    Optimized statement executor.

    Optimizations applied:
    - Conditional metrics collection (skip perf_counter when disabled)
    - Type-based dispatch instead of pattern matching
    """

    def __init__(
        self,
        runtime: Runtime,
        evaluator,  # Can be original or optimized
        metrics: Union[ExecutionMetrics, NullMetrics] = None,
    ):
        self.rt = runtime
        self.ev = evaluator
        self.metrics = metrics if metrics is not None else NullMetrics()
        self._metrics_enabled = not isinstance(self.metrics, NullMetrics)
        self.opcodes: OpcodeRegistry

        # Pre-compute type dispatch table (faster than pattern matching)
        self._dispatch = {
            Assign: self._exec_assign,
            Block: self._exec_block,
            If: self._exec_if,
            While: self._exec_while,
            For: self._exec_for,
            ForEach: self._exec_foreach,
            Fork: self._exec_fork,
            Return: self._exec_return,
            ExprStmt: self._exec_expr_stmt,
            OpStmt: self._exec_op_stmt,
            Try: self._exec_try,
            Throw: self._exec_throw,
        }

    async def exec(self, stmt: Statement) -> Flow:
        """Execute statement using type dispatch."""
        if self._metrics_enabled:
            start_time = time.perf_counter()
            stmt_type = type(stmt).__name__
            node_id = getattr(stmt, "node_id", None)

        try:
            handler = self._dispatch.get(type(stmt))
            if handler:
                return await handler(stmt)
            raise ValueError(f"Unknown statement type: {type(stmt)}")
        finally:
            if self._metrics_enabled:
                duration = time.perf_counter() - start_time
                self.metrics.record("statement", stmt_type, duration)
                if node_id:
                    self.metrics.record("node", node_id, duration)

    async def _exec_assign(self, stmt: Assign) -> Flow:
        """Execute assignment statement."""
        self.rt.scope[stmt.name] = await self.ev.eval(stmt.value)
        return Flow.NEXT

    async def _exec_block(self, stmt: Block) -> Flow:
        """Execute block statement."""
        for s in stmt.stmts:
            flow = await self.exec(s)
            if flow != Flow.NEXT:
                return flow
        return Flow.NEXT

    async def _exec_if(self, stmt: If) -> Flow:
        """Execute if statement."""
        if await self.ev.eval(stmt.cond):
            return await self.exec(stmt.then)
        elif stmt.else_:
            return await self.exec(stmt.else_)
        return Flow.NEXT

    async def _exec_while(self, stmt: While) -> Flow:
        """Execute while statement."""
        while await self.ev.eval(stmt.cond):
            flow = await self.exec(stmt.body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_for(self, stmt: For) -> Flow:
        """Execute for statement."""
        start_val = int(await self.ev.eval(stmt.start))
        end_val = int(await self.ev.eval(stmt.end))
        step_val = int(await self.ev.eval(stmt.step)) if stmt.step else 1

        for i in range(start_val, end_val, step_val):
            self.rt.scope[stmt.var_name] = i
            flow = await self.exec(stmt.body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.CONTINUE:
                continue
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_foreach(self, stmt: ForEach) -> Flow:
        """Execute foreach statement."""
        iterable_val = await self.ev.eval(stmt.iterable)
        if isinstance(iterable_val, dict):
            iterable_val = iterable_val.keys()

        for item in iterable_val:
            self.rt.scope[stmt.var_name] = item
            flow = await self.exec(stmt.body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.CONTINUE:
                continue
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_return(self, stmt: Return) -> Flow:
        """Execute return statement."""
        for v in stmt.values:
            self.rt.push(await self.ev.eval(v))
        return Flow.RETURN

    async def _exec_expr_stmt(self, stmt: ExprStmt) -> Flow:
        """Execute expression statement."""
        await self.ev.eval(stmt.expr)
        return Flow.NEXT

    async def _exec_op_stmt(self, stmt: OpStmt) -> Flow:
        """Execute opcode statement."""
        arg_vals = [await self.ev.eval(a) for a in stmt.args]
        await self.opcodes.call(stmt.name, arg_vals)
        return Flow.NEXT

    async def _exec_throw(self, stmt: Throw) -> Flow:
        """Execute throw statement."""
        error_msg = await self.ev.eval(stmt.value)
        raise RuntimeError(str(error_msg))

    async def _exec_try(self, stmt: Try) -> Flow:
        """Execute try-catch-finally."""
        try:
            return await self.exec(stmt.body)
        except Exception as e:
            for handler in stmt.handlers:
                if self._matches_exception(e, handler.exception_type):
                    if handler.var_name:
                        self.rt.scope[handler.var_name] = str(e)
                    return await self.exec(handler.body)
            raise
        finally:
            if stmt.finally_:
                await self.exec(stmt.finally_)

    def _matches_exception(
        self, exception: Exception, expected_type: Optional[str]
    ) -> bool:
        """Check if exception matches expected type."""
        if expected_type is None:
            return True
        return type(exception).__name__ == expected_type

    async def _exec_fork(self, stmt: Fork) -> Flow:
        """Execute multiple branches concurrently."""
        if not stmt.branches:
            return Flow.NEXT
        tasks = [self.exec(branch) for branch in stmt.branches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                raise result
            elif result == Flow.RETURN:
                return Flow.RETURN
        return Flow.NEXT
