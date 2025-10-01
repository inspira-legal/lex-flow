from .ast import Program
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry
from .workflows import WorkflowManager
from contextlib import redirect_stdout
from typing import Any, Optional, TextIO


class Engine:
    """Simple, clean engine."""

    def __init__(self, program: Program, output: Optional[TextIO] = None):
        self.program = program
        self.runtime = Runtime(program)
        self.output = output

        # Create components
        self.evaluator = Evaluator(self.runtime)
        self.executor = Executor(self.runtime, self.evaluator)

        # Plugin systems
        self.opcodes = OpcodeRegistry()
        self.workflows = WorkflowManager(program.externals, self.executor, self.runtime)

        # Wire up dependencies
        self.evaluator.opcodes = self.opcodes
        self.evaluator.functions = self.workflows
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
        """Internal execution logic."""
        # Execute main workflow body
        await self.executor.exec(self.program.main.body)

        # Return final stack value
        return self.runtime.pop() if self.runtime.stack else None
