# Lex Flow Core - Stack-based visual programming workflow interpreter

from .engine import Engine
from .parser import Parser
from .ast import Program, Workflow
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .workflows import WorkflowManager
from .metrics import ExecutionMetrics, NullMetrics
from .opcodes import default_registry, OpcodeRegistry, opcode
from .grammar import (
    get_grammar,
    get_construct,
    get_category,
    get_control_flow_opcodes,
    get_branch_color,
    get_node_color,
    get_reporter_color,
    is_control_flow_opcode,
)


# Main exports for API users
__all__ = [
    "Engine",
    "Parser",
    "Program",
    "Workflow",
    "Runtime",
    "Evaluator",
    "Executor",
    "OpcodeRegistry",
    "default_registry",
    "opcode",
    "WorkflowManager",
    "ExecutionMetrics",
    "NullMetrics",
    # Grammar module exports
    "get_grammar",
    "get_construct",
    "get_category",
    "get_control_flow_opcodes",
    "get_branch_color",
    "get_node_color",
    "get_reporter_color",
    "is_control_flow_opcode",
]

__version__ = "0.1.0"
