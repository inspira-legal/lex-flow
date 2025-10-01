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

    async def run(self) -> Any:
        """Run program to completion with optional output redirection."""
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
