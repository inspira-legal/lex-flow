from enum import auto, Enum
from typing import Optional
from .runtime import Runtime
from .evaluator import Evaluator
from .ast import Assign, Block, If, While, Return, ExprStmt, OpStmt, Try, Throw, Catch, Statement


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

            case Return(value=v):
                if v:
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
        """Execute try-catch-finally using Python's native exception handling."""
        try:
            # Execute try body
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
