from .ast import Call, Opcode, OpStmt, Program, walk
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry, default_registry
from .opcodes.opcodes import bind_arguments
from .workflows import WorkflowManager
from .metrics import ExecutionMetrics, NullMetrics
from .tasks import TaskManager
from contextlib import redirect_stdout
from typing import Any, Optional, TextIO, Union


class WorkflowValidationError(ValueError):
    """A program cannot bind its arguments and will fail at runtime.

    A ValueError subclass, so consumers catching ValueError keep working while
    a load-time rejection can be told apart from a runtime one.
    """


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
        # Validate before touching any state, so a rejected program cannot be
        # left behind on the engine
        self._validate_bindings(program)

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

        # Setup privileged opcodes with engine-internal access
        self._setup_privileged_opcodes()

    def _validate_bindings(self, program: Program) -> None:
        """Reject a call whose arguments cannot bind, before anything runs.

        Binding fails with a ValueError at call time, which the workflow's own
        catch would swallow and handle as a domain error. Argument counts and
        names are known statically, so the whole class is decided here.
        """
        workflows = {program.main.name: program.main, **program.externals}

        for workflow in workflows.values():
            for node in walk(workflow.body):
                if isinstance(node, (Opcode, OpStmt)):
                    error = self._opcode_binding_error(node)
                elif isinstance(node, Call):
                    error = self._call_binding_error(node, workflows)
                else:
                    continue

                if error:
                    raise WorkflowValidationError(
                        f"In workflow '{workflow.name}', {error}"
                    )

    def _opcode_binding_error(self, node: Union[Opcode, OpStmt]) -> Optional[str]:
        """Why this opcode call cannot bind, or None when it can."""
        sig = self.opcodes.signatures.get(node.name)
        if sig is None:
            return None  # a custom registry may register it later
        try:
            # The values never reach the opcode; only the shape is checked
            bind_arguments(
                node.name, sig, [None] * len(node.args), dict.fromkeys(node.kwargs)
            )
        except ValueError as e:
            return str(e)
        return None

    def _call_binding_error(self, node: Call, workflows: dict) -> Optional[str]:
        """Why this workflow call cannot bind, or None when it can."""
        target = workflows.get(node.name)
        if target is None:
            return f"calls unknown workflow '{node.name}'"

        unknown = sorted(k for k in node.kwargs if k not in target.params)
        if unknown:
            return (
                f"workflow '{node.name}' got unexpected keyword argument(s) "
                f"{', '.join(unknown)}. Accepts: {', '.join(target.params) or '(none)'}"
            )
        duplicated = [p for p in target.params[: len(node.args)] if p in node.kwargs]
        if duplicated:
            return (
                f"workflow '{node.name}' got multiple values for argument(s) "
                f"{', '.join(duplicated)}"
            )
        return None

    def _setup_privileged_opcodes(self) -> None:
        """Inject implementations for privileged opcodes that need engine access."""

        async def get_context() -> dict:
            return {
                "program": {
                    "globals": dict(self.program.globals),
                    "main": {
                        "name": self.program.main.name,
                        "params": list(self.program.main.params),
                    },
                    "externals": {
                        name: {"name": wf.name, "params": list(wf.params)}
                        for name, wf in self.program.externals.items()
                    },
                },
                "workflows": {
                    name: {
                        "name": wf.name,
                        "params": list(wf.params),
                        "locals": dict(wf.locals),
                    }
                    for name, wf in self.workflows.workflows.items()
                },
                "opcodes": self.opcodes.list_opcodes(),
            }

        async def get_workflow_manager() -> Any:
            return self.workflows

        self.opcodes.inject("introspect_context", get_context)
        self.opcodes.inject("_get_workflow_manager", get_workflow_manager)

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
        if self.program is None:
            raise RuntimeError("No program loaded. Call load_program() first.")

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
