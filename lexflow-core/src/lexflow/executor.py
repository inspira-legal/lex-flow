from enum import auto, Enum
from typing import Optional
import asyncio
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
    Statement,
)
from .opcodes import OpcodeRegistry


class Flow(Enum):
    """Control flow signals."""

    NEXT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()


class Executor:
    """Execute statements."""

    def __init__(self, runtime: Runtime, evaluator: Evaluator):
        self.rt = runtime
        self.ev = evaluator
        self.opcodes: OpcodeRegistry  # Set by the Engine to avoid circular dependency

    async def exec(self, stmt: Statement) -> Flow:
        """Execute statement using pattern matching."""
        match stmt:
            case Assign(name=n, value=v):
                self.rt.scope[n] = await self.ev.eval(v)
                return Flow.NEXT

            case Block(stmts=stmts):
                for s in stmts:
                    flow = await self.exec(s)
                    if flow != Flow.NEXT:
                        return flow
                return Flow.NEXT

            case If(cond=c, then=t, else_=e):
                if await self.ev.eval(c):
                    return await self.exec(t)
                elif e:
                    return await self.exec(e)
                return Flow.NEXT

            case While(cond=c, body=b):
                while await self.ev.eval(c):
                    flow = await self.exec(b)
                    if flow == Flow.BREAK:
                        break
                    elif flow == Flow.RETURN:
                        return flow
                return Flow.NEXT

            case For(var_name=var, start=s, end=e, step=step, body=b):
                start_val = int(await self.ev.eval(s))
                end_val = int(await self.ev.eval(e))
                step_val = int(await self.ev.eval(step)) if step else 1

                for i in range(start_val, end_val, step_val):
                    self.rt.scope[var] = i
                    flow = await self.exec(b)
                    if flow == Flow.BREAK:
                        break
                    elif flow == Flow.CONTINUE:
                        continue
                    elif flow == Flow.RETURN:
                        return flow
                return Flow.NEXT

            case ForEach(var_name=var, iterable=it, body=b):
                iterable_val = await self.ev.eval(it)
                # Support lists, dicts (iterate keys), and other iterables
                if isinstance(iterable_val, dict):
                    iterable_val = iterable_val.keys()

                for item in iterable_val:
                    self.rt.scope[var] = item
                    flow = await self.exec(b)
                    if flow == Flow.BREAK:
                        break
                    elif flow == Flow.CONTINUE:
                        continue
                    elif flow == Flow.RETURN:
                        return flow
                return Flow.NEXT

            case Fork(branches=branches):
                return await self._exec_fork(branches)

            case Return(values=vals):
                # Push all return values to the stack
                for v in vals:
                    self.rt.push(await self.ev.eval(v))
                return Flow.RETURN

            case ExprStmt(expr=e):
                await self.ev.eval(e)
                return Flow.NEXT

            case OpStmt(name=n, args=args):
                arg_vals = [await self.ev.eval(a) for a in args]
                await self.opcodes.call(n, arg_vals)
                return Flow.NEXT

            case Try(body=body, handlers=handlers, finally_=finally_):
                return await self._exec_try(body, handlers, finally_)

            case Throw(value=value):
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
