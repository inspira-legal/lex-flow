from .ast import Program
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry, default_registry
from .workflows import WorkflowManager
from .metrics import ExecutionMetrics, NullMetrics
from contextlib import redirect_stdout
from typing import Any, Optional, TextIO, Union


class Engine:
    def __init__(
        self,
        program: Program,
        output: Optional[TextIO] = None,
        opcodes: Optional[OpcodeRegistry] = None,
        metrics: Optional[Union[ExecutionMetrics, bool]] = None,
    ):
        self.program = program
        self.runtime = Runtime(program)
        self.output = output

        # Metrics collection
        if metrics is True:
            self.metrics: Union[ExecutionMetrics, NullMetrics] = ExecutionMetrics()
        elif isinstance(metrics, ExecutionMetrics):
            self.metrics = metrics
        else:
            self.metrics = NullMetrics()

        # Create components
        self.evaluator = Evaluator(self.runtime, self.metrics)
        self.executor = Executor(self.runtime, self.evaluator, self.metrics)

        # Plugin systems
        self.opcodes = opcodes if opcodes is not None else default_registry
        self.workflows = WorkflowManager(program.externals, self.executor, self.runtime, self.metrics)

        # Wire up dependencies
        self.evaluator.opcodes = self.opcodes
        self.evaluator.workflows = self.workflows
        self.executor.opcodes = self.opcodes

    async def run(self, inputs: Optional[dict[str, Any]] = None) -> Any:
        """Run program to completion with optional output redirection and inputs.

        Args:
            inputs: Optional dictionary of input parameters for main workflow.
                   Keys must match the main workflow's interface.inputs parameters.

        Returns:
            The final result value from the workflow execution

        Raises:
            ValueError: If input keys don't match main workflow parameters

        Example:
            >>> engine = Engine(program)
            >>> result = await engine.run(inputs={"name": "Alice", "age": 30})
        """
        # Apply inputs to main workflow if provided
        if inputs:
            # Validate that all input keys are valid parameters
            invalid_keys = set(inputs.keys()) - set(self.program.main.params)
            if invalid_keys:
                raise ValueError(
                    f"Invalid input parameters: {invalid_keys}. "
                    f"Main workflow accepts: {self.program.main.params}"
                )

            # Override runtime scope with provided inputs
            for param_name, value in inputs.items():
                self.runtime.scope[param_name] = value

        if self.output:
            with redirect_stdout(self.output):
                return await self._run_internal()
        else:
            return await self._run_internal()

    async def _run_internal(self) -> Any:
        # Start metrics collection
        self.metrics.start_execution()

        try:
            # Execute main workflow body
            await self.executor.exec(self.program.main.body)

            # Return final stack value
            return self.runtime.pop() if self.runtime.stack else None
        finally:
            # End metrics collection
            self.metrics.end_execution()

    def get_metrics_report(self, top_n: int = 10) -> str:
        """Generate formatted metrics report.

        Args:
            top_n: Number of top operations to show per category

        Returns:
            Formatted text report of execution metrics
        """
        return self.metrics.get_report(top_n=top_n)

    def get_metrics_summary(self) -> str:
        """Get brief metrics summary."""
        return self.metrics.get_summary()
