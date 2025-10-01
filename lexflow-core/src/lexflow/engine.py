from .ast import Program
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry
from .workflows import WorkflowManager
from typing import Any


class Engine:
    """Simple, clean engine."""

    def __init__(self, program: Program):
        self.program = program
        self.runtime = Runtime(program)

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
        """Run program to completion."""
        # Execute main workflow body
        await self.executor.exec(self.program.main.body)

        # Return final stack value
        return self.runtime.pop() if self.runtime.stack else None
