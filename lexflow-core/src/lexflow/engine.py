from .ast import Program
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry, default_registry
from .workflows import WorkflowManager
from .metrics import ExecutionMetrics, NullMetrics
from .tasks import TaskManager
from contextlib import redirect_stdout
from typing import Any, Optional, TextIO, Union


class Engine:
    def __init__(
        self,
        program: Optional[Program] = None,
        output: Optional[TextIO] = None,
        opcodes: Optional[OpcodeRegistry] = None,
        metrics: Optional[Union[ExecutionMetrics, bool]] = None,
    ):
        # Store configuration
        self.output = output
        self._opcodes_registry = opcodes if opcodes is not None else default_registry

        # Metrics collection
        if metrics is True:
            self.metrics: Union[ExecutionMetrics, NullMetrics] = ExecutionMetrics()
        elif isinstance(metrics, ExecutionMetrics):
            self.metrics = metrics
        else:
            self.metrics = NullMetrics()

        # Create components (will be initialized when program is loaded)
        self.program: Optional[Program] = None
        self.runtime: Optional[Runtime] = None
        self.evaluator: Optional[Evaluator] = None
        self.executor: Optional[Executor] = None
        self.opcodes = self._opcodes_registry
        self.workflows: Optional[WorkflowManager] = None
        self.tasks: TaskManager = TaskManager()

        # Load program if provided
        if program is not None:
            self.load_program(program)

    def load_program(self, program: Program) -> None:
        """Load a program into the engine, reinitializing all components.

        Args:
            program: The program to load
        """
        self.program = program

        # Reinitialize runtime with new program state
        self.runtime = Runtime(program)

        # Create evaluator and executor
        self.evaluator = Evaluator(self.runtime, self.metrics)
        self.executor = Executor(self.runtime, self.evaluator, self.metrics)

        # Recreate workflow manager with new externals
        self.workflows = WorkflowManager(
            program.externals, self.executor, self.runtime, self.metrics
        )

        # Wire up dependencies
        self.evaluator.opcodes = self.opcodes
        self.evaluator.workflows = self.workflows
        self.executor.opcodes = self.opcodes
        self.executor.tasks = self.tasks

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
            # Cleanup background tasks
            await self.tasks.cleanup()
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
