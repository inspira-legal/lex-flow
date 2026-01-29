from enum import auto, Enum
from typing import Optional, Union, TYPE_CHECKING
import asyncio
import time
from .runtime import Runtime
from .evaluator import Evaluator
from .ast import (
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
    Spawn,
    AsyncForEach,
    Timeout,
    With,
    Statement,
)
from .opcodes import OpcodeRegistry
from .metrics import ExecutionMetrics, NullMetrics

if TYPE_CHECKING:
    from .tasks import TaskManager


class Flow(Enum):
    """Control flow signals."""

    NEXT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()


class Executor:
    """Execute statements."""

    def __init__(
        self,
        runtime: Runtime,
        evaluator: Evaluator,
        metrics: Union[ExecutionMetrics, NullMetrics] = None,
    ):
        self.rt = runtime
        self.ev = evaluator
        self.metrics = metrics if metrics is not None else NullMetrics()
        self.opcodes: OpcodeRegistry  # Set by the Engine to avoid circular dependency
        self.tasks: Optional["TaskManager"] = None  # Set by Engine for background tasks

    async def exec(self, stmt: Statement) -> Flow:
        """Execute statement using pattern matching."""
        start_time = time.perf_counter()
        stmt_type = type(stmt).__name__

        # Extract node_id if available (all statements have this field)
        node_id = getattr(stmt, "node_id", None)

        try:
            match stmt:
                case Assign(name=n, value=v):
                    result = await self._exec_assign(n, v)
                    return result

                case Block(stmts=stmts):
                    result = await self._exec_block(stmts)
                    return result

                case If(cond=c, then=t, else_=e):
                    result = await self._exec_if(c, t, e)
                    return result

                case While(cond=c, body=b):
                    result = await self._exec_while(c, b)
                    return result

                case For(var_name=var, start=s, end=e, step=step, body=b):
                    result = await self._exec_for(var, s, e, step, b)
                    return result

                case ForEach(var_name=var, iterable=it, body=b):
                    result = await self._exec_foreach(var, it, b)
                    return result

                case Fork(branches=branches):
                    result = await self._exec_fork(branches)
                    return result

                case Return(values=vals):
                    result = await self._exec_return(vals)
                    return result

                case ExprStmt(expr=e):
                    result = await self._exec_expr_stmt(e)
                    return result

                case OpStmt(name=n, args=args):
                    result = await self._exec_op_stmt(n, args)
                    return result

                case Try(body=body, handlers=handlers, finally_=finally_):
                    result = await self._exec_try(body, handlers, finally_)
                    return result

                case Throw(value=value):
                    result = await self._exec_throw(value)
                    return result

                case Spawn(body=body, var_name=var_name):
                    result = await self._exec_spawn(body, var_name)
                    return result

                case AsyncForEach(var_name=var, iterable=it, body=b):
                    result = await self._exec_async_foreach(var, it, b)
                    return result

                case Timeout(timeout=t, body=b, on_timeout=fallback):
                    result = await self._exec_timeout(t, b, fallback)
                    return result

                case With(resource=res, var_name=var, body=b):
                    result = await self._exec_with(res, var, b)
                    return result
        finally:
            duration = time.perf_counter() - start_time
            self.metrics.record("statement", stmt_type, duration)

            # Also record node-level metrics if node_id is present
            if node_id:
                self.metrics.record("node", node_id, duration)

    async def _exec_assign(self, name: str, value) -> Flow:
        """Execute assignment statement."""
        self.rt.scope[name] = await self.ev.eval(value)
        return Flow.NEXT

    async def _exec_block(self, stmts: list) -> Flow:
        """Execute block statement."""
        for s in stmts:
            flow = await self.exec(s)
            if flow != Flow.NEXT:
                return flow
        return Flow.NEXT

    async def _exec_if(self, cond, then, else_) -> Flow:
        """Execute if statement."""
        if await self.ev.eval(cond):
            return await self.exec(then)
        elif else_:
            return await self.exec(else_)
        return Flow.NEXT

    async def _exec_while(self, cond, body) -> Flow:
        """Execute while statement."""
        while await self.ev.eval(cond):
            flow = await self.exec(body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_for(self, var_name: str, start, end, step, body) -> Flow:
        """Execute for statement."""
        start_val = int(await self.ev.eval(start))
        end_val = int(await self.ev.eval(end))
        step_val = int(await self.ev.eval(step)) if step else 1

        for i in range(start_val, end_val, step_val):
            self.rt.scope[var_name] = i
            flow = await self.exec(body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.CONTINUE:
                continue
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_foreach(self, var_name: str, iterable, body) -> Flow:
        """Execute foreach statement."""
        iterable_val = await self.ev.eval(iterable)
        # Support lists, dicts (iterate keys), and other iterables
        if isinstance(iterable_val, dict):
            iterable_val = iterable_val.keys()

        for item in iterable_val:
            self.rt.scope[var_name] = item
            flow = await self.exec(body)
            if flow == Flow.BREAK:
                break
            elif flow == Flow.CONTINUE:
                continue
            elif flow == Flow.RETURN:
                return flow
        return Flow.NEXT

    async def _exec_return(self, values: list) -> Flow:
        """Execute return statement."""
        # Push all return values to the stack
        for v in values:
            self.rt.push(await self.ev.eval(v))
        return Flow.RETURN

    async def _exec_expr_stmt(self, expr) -> Flow:
        """Execute expression statement."""
        await self.ev.eval(expr)
        return Flow.NEXT

    async def _exec_op_stmt(self, name: str, args: list) -> Flow:
        """Execute opcode statement."""
        arg_vals = [await self.ev.eval(a) for a in args]
        await self.opcodes.call(name, arg_vals)
        return Flow.NEXT

    async def _exec_throw(self, value) -> Flow:
        """Execute throw statement."""
        error_msg = await self.ev.eval(value)
        raise RuntimeError(str(error_msg))

    async def _exec_try(
        self,
        body: Statement,
        handlers: list[Catch],
        finally_: Optional[Statement],
    ) -> Flow:
        """Execute try-catch-finally"""
        try:
            flow = await self.exec(body)
            return flow

        except Exception as e:
            # Find matching handler
            for handler in handlers:
                if self._matches_exception(e, handler.exception_type):
                    # Bind exception message to variable if specified
                    if handler.var_name:
                        self.rt.scope[handler.var_name] = str(e)

                    # Execute handler body
                    return await self.exec(handler.body)

            # No handler matched, re-raise
            raise

        finally:
            # Always execute finally block if present
            if finally_:
                await self.exec(finally_)

    def _matches_exception(
        self, exception: Exception, expected_type: Optional[str]
    ) -> bool:
        """Check if exception matches expected type."""
        if expected_type is None:
            return True  # Catch-all

        # Match by exception class name
        return type(exception).__name__ == expected_type

    async def _exec_fork(self, branches: list[Statement]) -> Flow:
        """Execute multiple branches concurrently using asyncio.gather."""
        if not branches:
            return Flow.NEXT

        # Create tasks for each branch
        tasks = []
        for branch in branches:
            # Each branch gets executed as a coroutine
            tasks.append(self.exec(branch))

        # Execute all branches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results for control flow signals
        for result in results:
            if isinstance(result, Exception):
                # Re-raise the first exception encountered
                raise result
            elif result == Flow.RETURN:
                # If any branch returns, propagate it
                return Flow.RETURN
            elif result == Flow.BREAK:
                # Break doesn't make sense in fork context, treat as NEXT
                pass

        return Flow.NEXT

    async def _exec_spawn(self, body: Statement, var_name: Optional[str]) -> Flow:
        """Spawn a background task.

        The task shares the current scope, enabling variable communication
        between the main workflow and background task.
        """
        if self.tasks is None:
            raise RuntimeError(
                "TaskManager not available. Cannot spawn background tasks."
            )

        # Create coroutine for the background work
        async def background_work():
            # Execute body in shared scope (same scope reference)
            await self.exec(body)

        # Spawn the task
        task_name = var_name or "background"
        lex_task = self.tasks.spawn(background_work(), name=task_name)

        # Store task handle in variable if requested
        if var_name:
            self.rt.scope[var_name] = lex_task

        return Flow.NEXT

    async def _exec_async_foreach(self, var_name: str, iterable, body) -> Flow:
        """Execute async foreach loop over an async iterable."""
        iterable_val = await self.ev.eval(iterable)

        # Check if it's an async iterable
        if hasattr(iterable_val, "__aiter__"):
            async for item in iterable_val:
                self.rt.scope[var_name] = item
                flow = await self.exec(body)
                if flow == Flow.BREAK:
                    break
                elif flow == Flow.CONTINUE:
                    continue
                elif flow == Flow.RETURN:
                    return flow
        else:
            # Fallback to sync iteration for regular iterables
            if isinstance(iterable_val, dict):
                iterable_val = iterable_val.keys()

            for item in iterable_val:
                self.rt.scope[var_name] = item
                flow = await self.exec(body)
                if flow == Flow.BREAK:
                    break
                elif flow == Flow.CONTINUE:
                    continue
                elif flow == Flow.RETURN:
                    return flow

        return Flow.NEXT

    async def _exec_timeout(self, timeout_expr, body, on_timeout) -> Flow:
        """Execute body with a timeout."""
        timeout_secs = float(await self.ev.eval(timeout_expr))

        try:
            return await asyncio.wait_for(self.exec(body), timeout=timeout_secs)
        except asyncio.TimeoutError:
            if on_timeout:
                return await self.exec(on_timeout)
            raise

    async def _exec_with(self, resource_expr, var_name: str, body) -> Flow:
        """Execute body with an async context manager."""
        resource = await self.ev.eval(resource_expr)

        # Enter the context manager
        if hasattr(resource, "__aenter__"):
            value = await resource.__aenter__()
        elif hasattr(resource, "__enter__"):
            value = resource.__enter__()
        else:
            raise TypeError(
                f"Resource {type(resource).__name__} is not a context manager"
            )

        try:
            self.rt.scope[var_name] = value
            return await self.exec(body)
        finally:
            # Exit the context manager
            if hasattr(resource, "__aexit__"):
                await resource.__aexit__(None, None, None)
            elif hasattr(resource, "__exit__"):
                resource.__exit__(None, None, None)
