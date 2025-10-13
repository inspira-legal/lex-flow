# Lex Flow Core - Stack-based visual programming workflow interpreter

from .engine import Engine
from .parser import Parser
from .ast import Program, Workflow
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry, default_registry, opcode
from .workflows import WorkflowManager
from .metrics import ExecutionMetrics, NullMetrics
from .opcodes_pydantic_ai import register_pydantic_ai_opcodes
from .opcodes_pygame import register_pygame_opcodes

# Register optional opcode modules
register_pydantic_ai_opcodes()
register_pygame_opcodes()

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
]

__version__ = "0.1.0"
