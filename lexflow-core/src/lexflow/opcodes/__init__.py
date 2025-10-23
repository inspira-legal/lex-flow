from .opcodes import OpcodeRegistry, default_registry, opcode
from .opcodes_pydantic_ai import register_pydantic_ai_opcodes
from .opcodes_pygame import register_pygame_opcodes


# Register optional opcode modules
register_pydantic_ai_opcodes()
register_pygame_opcodes()

__all__ = ["OpcodeRegistry", "default_registry", "opcode"]
