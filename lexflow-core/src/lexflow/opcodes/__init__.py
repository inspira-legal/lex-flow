from .opcodes import (
    CategoryInfo,
    OpcodeRegistry,
    default_registry,
    opcode,
    register_category,
)

# Import core opcodes that register via @opcode() decorator (no external dependencies)
from . import opcodes_chat  # noqa: F401
from . import opcodes_cli  # noqa: F401
from . import opcodes_tasks  # noqa: F401

# Register integration opcodes from lexflow-opcodes package
from lexflow_opcodes import register_all

register_all()

__all__ = [
    "CategoryInfo",
    "OpcodeRegistry",
    "default_registry",
    "opcode",
    "register_category",
]
