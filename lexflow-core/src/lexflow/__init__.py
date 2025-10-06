# Lex Flow Core - Stack-based visual programming workflow interpreter

from .engine import Engine
from .parser import Parser
from .ast import Program, Workflow
from .runtime import Runtime
from .evaluator import Evaluator
from .executor import Executor
from .opcodes import OpcodeRegistry, default_registry, opcode
from .workflows import WorkflowManager
from .opcodes_pydantic_ai import register_pydantic_ai_opcodes

register_pydantic_ai_opcodes()

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
]

__version__ = "0.1.0"
