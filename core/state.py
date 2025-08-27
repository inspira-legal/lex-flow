from typing import Any
from .models import Workflow, RuntimeNode, RuntimeWorkflow


class Frame:
    _return_node: RuntimeNode
    _pending_input: str
    _locals: dict

    def __init__(self, return_node, pending_input, locals={}) -> None:
        self._return_node = return_node
        self._locals = locals
        self._pending_input = pending_input


class WorkflowState:
    _workflow: RuntimeWorkflow
    _variables: dict[str, Any]
    _data_stack: list = []
    _call_stack: list = []
    _pc: RuntimeNode | None = None

    def __init__(self, workflow: Workflow):
        self._workflow = RuntimeWorkflow(workflow)
        self._variables = workflow.variables.copy()
        self._pc = self._workflow.start_node

    def pop(self) -> Any:
        return self._data_stack.pop()

    def push(self, value: Any):
        return self._data_stack.append(value)

    def peek(self) -> Any:
        return self._data_stack[-1]

    def push_frame(self, return_node: RuntimeNode, locals: dict = None):
        frame = Frame(_return_node=return_node, _locals=locals or {})
        self._call_stack.append(frame)

    def pop_frame(self) -> Frame:
        return self._call_stack.pop()

    def peek_frame(self) -> Frame | None:
        return self._call_stack[-1] if self._call_stack else None

    def is_finished(self) -> bool:
        return self._pc is None and not self._call_stack

    def __len__(self) -> int:
        """len(state) -> number of items in stack"""
        return len(self._data_stack)

    def __bool__(self) -> bool:
        """bool(state) -> True if stack is not empty"""
        return bool(self._data_stack)

    def __iter__(self):
        """Iterate over stack values (bottom to top)."""
        return iter(self._data_stack)

    def __repr__(self):
        """Nice debugging string."""
        return f"WorkflowState(stack={self._data_stack}, pc={self._pc})"
