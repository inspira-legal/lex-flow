from typing import Any, Union
import time
from .ast import Workflow
from .runtime import Runtime
from .executor import Executor, Flow
from .metrics import ExecutionMetrics, NullMetrics


class WorkflowManager:
    """Manage workflow calls and returns."""

    def __init__(
        self,
        workflows: dict[str, Workflow],
        executor: Executor,
        runtime: Runtime,
        metrics: Union[ExecutionMetrics, NullMetrics] = None
    ):
        self.workflows = workflows
        self.executor = executor
        self.runtime = runtime
        self.metrics = metrics if metrics is not None else NullMetrics()

    async def call(self, name: str, args: list[Any]) -> Any:
        """Call a workflow with arguments."""
        start_time = time.perf_counter()

        try:
            if name not in self.workflows:
                raise ValueError(f"Unknown workflow: {name}")

            workflow = self.workflows[name]

            # Initialize with local variables as defaults
            arg_dict = dict(workflow.locals)

            # Override with actual arguments
            for i, param_name in enumerate(workflow.params):
                if i < len(args):
                    arg_dict[param_name] = args[i]

            # Enter workflow scope
            self.runtime.call(name, arg_dict)

            try:
                # Execute workflow body
                flow = await self.executor.exec(workflow.body)

                # Get return value from stack if available
                result = None
                if flow == Flow.RETURN and self.runtime.stack:
                    result = self.runtime.stack[-1]  # Peek, don't pop yet

                # Exit workflow scope
                return_value = self.runtime.ret()

                # If ret() didn't pop, return the result we peeked
                return result if result is not None else return_value

            except Exception as e:
                # Clean up on error
                if self.runtime.frames:
                    self.runtime.ret()
                raise e
        finally:
            duration = time.perf_counter() - start_time
            self.metrics.record("workflow_call", name, duration)