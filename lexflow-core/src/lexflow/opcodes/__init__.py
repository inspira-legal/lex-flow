"""
LexFlow Opcodes Package

This package contains all the opcode implementations for the LexFlow workflow engine.
The opcodes are automatically discovered by the engine through the @opcode decorator.
"""

# Import all opcode modules to ensure they are registered
from . import ai
from . import control
from . import data
from . import file
from . import io
from . import operators
from . import void
from . import workflows
