from typing import Any, Union
import time
from .runtime import Runtime
from .ast import Expression, Literal, Call, Opcode, Variable
from .opcodes import OpcodeRegistry
from .metrics import ExecutionMetrics, NullMetrics

# ruff: noqa


class Evaluator:
    """Evaluate expressions to values."""

    def __init__(
        self, runtime: Runtime, metrics: Union[ExecutionMetrics, NullMetrics] = None
    ):
        from .workflows import WorkflowManager

        self.rt = runtime
        self.metrics = metrics if metrics is not None else NullMetrics()
        self.opcodes: OpcodeRegistry  # Set by the Engine to avoid circular dependency
        self.workflows: (
            WorkflowManager  # Set by the Engine to avoid circular dependency
        )

    async def eval(self, expr: Expression) -> Any:
        """Evaluate expression using pattern matching."""
        start_time = time.perf_counter()
        expr_type = type(expr).__name__

        try:
            match expr:
                case Literal(value=v):
                    return v

                case Variable(name=n):
                    return self.rt.scope[n]

                case Call(name=n, args=args):
                    arg_vals = [await self.eval(a) for a in args]
                    # Workflow calls are measured separately in WorkflowManager
                    return await self.workflows.call(n, arg_vals)

                case Opcode(name=n, args=args):
                    arg_vals = [await self.eval(a) for a in args]
                    # Measure opcode execution separately
                    opcode_start = time.perf_counter()
                    result = await self.opcodes.call(n, arg_vals)
                    opcode_duration = time.perf_counter() - opcode_start
                    self.metrics.record("opcode", n, opcode_duration)
                    return result
        finally:
            duration = time.perf_counter() - start_time
            self.metrics.record("expression", expr_type, duration)
