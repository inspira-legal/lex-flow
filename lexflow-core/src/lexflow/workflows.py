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
        metrics: Union[ExecutionMetrics, NullMetrics] = None,
    ):
        self.workflows = workflows
        self.executor = executor
        self.runtime = runtime
        self.metrics = metrics if metrics is not None else NullMetrics()

    async def call(
        self, name: str, args: list[Any], kwargs: dict[str, Any] = None
    ) -> Any:
        """Call a workflow with positional and keyword arguments."""
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

            if kwargs:
                arg_dict.update(self._bind_kwargs(workflow, args, kwargs))

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

    @staticmethod
    def _bind_kwargs(
        workflow: Workflow, args: list[Any], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate keyword arguments against a workflow's parameters."""
        unknown = [k for k in kwargs if k not in workflow.params]
        if unknown:
            raise ValueError(
                f"Workflow '{workflow.name}' got unexpected keyword argument(s) "
                f"{', '.join(sorted(unknown))}. Accepts: {', '.join(workflow.params)}"
            )
        duplicated = [p for p in workflow.params[: len(args)] if p in kwargs]
        if duplicated:
            raise ValueError(
                f"Workflow '{workflow.name}' got multiple values for argument(s) "
                f"{', '.join(duplicated)}"
            )
        return kwargs
