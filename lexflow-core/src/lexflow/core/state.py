from typing import Any, Union
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
    _data_stack: list
    _call_stack: list
    _pc: int = 0

    def __init__(self, program: Program):
        self.program = program
        self._data_stack = []
        self._call_stack = []
        self._variables = program.variables.copy()
        self._pc = 0

    def pop(self) -> Any:
        if not self._data_stack:
            raise RuntimeError(
                f"Stack underflow - cannot pop from empty stack "
                f"(PC: {self._pc}, stack size: {len(self._data_stack)})"
            )
        return self._data_stack.pop()

    def push(self, value: Any):
        return self._data_stack.append(value)

    def peek(self) -> Any:
        if not self._data_stack:
            raise RuntimeError(
                f"Stack underflow - cannot peek at empty stack "
                f"(PC: {self._pc}, stack size: {len(self._data_stack)})"
            )
        return self._data_stack[-1]

    def push_frame(
        self, return_pc: int, pending_input: str = None, locals: dict = None
    ):
        frame = Frame(return_pc=return_pc, pending_input=pending_input, locals=locals)
        self._call_stack.append(frame)

    def pop_frame(self) -> Frame:
        if not self._call_stack:
            raise RuntimeError(
                f"Call stack underflow - cannot pop frame from empty call stack "
                f"(PC: {self._pc}, call stack depth: {len(self._call_stack)})"
            )
        return self._call_stack.pop()

    def peek_frame(self) -> Union[Frame, None]:
        return self._call_stack[-1] if self._call_stack else None

    def is_finished(self) -> bool:
        return self._pc >= len(self.program.main.statements) and not self._call_stack

    def current_statement(self) -> Statement:
        if self._pc < 0:
            raise RuntimeError(f"Program counter is negative: {self._pc}")
        if self._pc >= len(self.program.main.statements):
            raise RuntimeError(
                f"Program counter {self._pc} is beyond program end "
                f"(program has {len(self.program.main.statements)} statements)"
            )
        return self.program.main.statements[self._pc]

    def __len__(self) -> int:
        return len(self._data_stack)

    def __bool__(self) -> bool:
        return bool(self._data_stack)

    def __iter__(self):
        return iter(self._data_stack)

    def __repr__(self):
        return f"WorkflowState(stack={self._data_stack}, pc={self._pc})"
