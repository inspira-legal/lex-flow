from typing import Any
from .runtime import Runtime
from .ast import Expression, Literal, Call, Opcode, Variable

# ruff: noqa


class Evaluator:
    """Evaluate expressions to values."""

    def __init__(self, runtime: Runtime):
        self.rt = runtime

        self.unops = {
            "-": lambda x: -int(x),
            "not": lambda x: not self._truthy(x),
        }

    async def eval(self, expr: Expression) -> Any:
        """Evaluate expression using pattern matching."""
        match expr:
            case Literal(value=v):
                return v

            case Variable(name=n):
                return self.rt.scope[n]

            case Call(name=n, args=args):
                arg_vals = [await self.eval(a) for a in args]
                return await self.functions.call(n, arg_vals)

            case Opcode(name=n, args=args):
                arg_vals = [await self.eval(a) for a in args]
                return await self.opcodes.call(n, arg_vals)
