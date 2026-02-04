from .opcodes import (
    CategoryInfo,
    OpcodeRegistry,
    default_registry,
    opcode,
    register_category,
)
from .opcodes_http import register_http_opcodes
from .opcodes_pydantic_ai import register_pydantic_ai_opcodes
from .opcodes_pygame import register_pygame_opcodes
from .opcodes_rag import register_rag_opcodes

# Import opcodes that register via @opcode() decorator (no external dependencies)
from . import opcodes_chat  # noqa: F401
from . import opcodes_cli  # noqa: F401
from . import opcodes_github  # noqa: F401
from . import opcodes_tasks  # noqa: F401

# Register optional opcode modules (require external dependencies)
register_http_opcodes()
register_pydantic_ai_opcodes()
register_pygame_opcodes()
register_rag_opcodes()

__all__ = [
    "CategoryInfo",
    "OpcodeRegistry",
    "default_registry",
    "opcode",
    "register_category",
]
