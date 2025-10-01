from enum import auto, Enum
from .runtime import Runtime
from .evaluator import Evaluator
from .ast import Assign, Block, If, While, Return, ExprStmt, OpStmt, Statement


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
