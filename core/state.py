from typing import Any
from .ast import Program, Statement


class Frame:
    _return_pc: int
    _pending_input: str
    _locals: dict

    def __init__(
        self, return_pc: int, pending_input: str = None, locals: dict = None
    ) -> None:
        self._return_pc = return_pc
        self._locals = locals or {}
        self._pending_input = pending_input


class WorkflowState:
    program: Program
    _variables: dict[str, Any]
    _data_stack: list = []
    _call_stack: list = []
    _pc: int = 0

    def __init__(self, program: Program):
        self.program = program
        self._variables = program.variables.copy()
        self._pc = 0

    def pop(self) -> Any:
        return self._data_stack.pop()

    def push(self, value: Any):
        return self._data_stack.append(value)

    def peek(self) -> Any:
        return self._data_stack[-1]

    def push_frame(
        self, return_pc: int, pending_input: str = None, locals: dict = None
    ):
        frame = Frame(return_pc=return_pc, pending_input=pending_input, locals=locals)
        self._call_stack.append(frame)

    def pop_frame(self) -> Frame:
        return self._call_stack.pop()

    def peek_frame(self) -> Frame | None:
        return self._call_stack[-1] if self._call_stack else None

    def is_finished(self) -> bool:
        return self._pc >= len(self.program.main.statements) and not self._call_stack

    def current_statement(self) -> Statement:
        return self.program.main.statements[self._pc]

    def __len__(self) -> int:
        return len(self._data_stack)

    def __bool__(self) -> bool:
        return bool(self._data_stack)

    def __iter__(self):
        return iter(self._data_stack)

    def __repr__(self):
        return f"WorkflowState(stack={self._data_stack}, pc={self._pc})"
