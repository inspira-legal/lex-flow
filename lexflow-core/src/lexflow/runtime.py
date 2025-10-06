from typing import Any, Optional, NamedTuple
from .environment import Scope
from .ast import Program


class Frame(NamedTuple):
    """Lightweight call frame."""

    name: str
    return_addr: int
    scope: "Scope"


class Runtime:
    """Simplified runtime state."""

    def __init__(self, program: Program):
        self.program = program
        self.stack = []  # Data stack
        self.frames = []  # Call stack
        self.pc = 0  # Program counter

        # Initialize global scope
        self.scope = Scope()
        for name, value in program.globals.items():
            self.scope[name] = value

    def push(self, value: Any):
        self.stack.append(value)

    def pop(self) -> Any:
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def peek(self) -> Any:
        if not self.stack:
            raise RuntimeError("Stack empty")
        return self.stack[-1]

    # Frame operations - Clean and minimal
    def call(self, func_name: str, args: dict[str, Any]) -> None:
        """Enter a extern workflow."""
        frame = Frame(func_name, self.pc, self.scope)
        self.frames.append(frame)

        # New scope with parent
        self.scope = Scope(parent=self.scope)
        for name, value in args.items():
            self.scope[name] = value

    def ret(self) -> Optional[Any]:
        """Return from a extern workflow."""
        if not self.frames:
            return None  # Returning from main

        frame = self.frames.pop()
        self.scope = frame.scope
        self.pc = frame.return_addr

        # Return value is on stack
        return self.pop() if self.stack else None

    @property
    def finished(self) -> bool:
        """Check if execution is complete."""
        return self.pc >= len(self.program.main.stmts)

    def __repr__(self):
        return (
            f"Runtime(pc={self.pc}, stack={len(self.stack)}, frames={len(self.frames)})"
        )
