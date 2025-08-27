from abc import ABC, abstractmethod
from typing import Dict, Type, Optional
import importlib
import pkgutil


class OpcodeNotFoundError(Exception):
    pass


class BaseOpcode(ABC):
    @abstractmethod
    async def execute(self, state, stmt, engine) -> bool:
        pass


def opcode(name: Optional[str] = None):
    def decorator(cls: Type[BaseOpcode]) -> Type[BaseOpcode]:
        opcode_name = name if name is not None else cls.__name__.lower()
        OpcodeRegistry.register(opcode_name, cls)
        return cls

    return decorator


class OpcodeRegistry:
    _opcodes: Dict[str, Type[BaseOpcode]] = {}

    @classmethod
    def register(cls, name: str, opcode_class: Type[BaseOpcode]) -> None:
        cls._opcodes[name] = opcode_class

    @classmethod
    def get(cls, name: str) -> Type[BaseOpcode]:
        if name not in cls._opcodes:
            raise OpcodeNotFoundError(f"Unknown opcode: '{name}'")
        return cls._opcodes[name]

    @classmethod
    def list_opcodes(cls) -> Dict[str, Type[BaseOpcode]]:
        return cls._opcodes.copy()

    @classmethod
    def clear(cls) -> None:
        cls._opcodes.clear()

    @classmethod
    def discover_opcodes(cls, package_name: str = "opcodes") -> None:
        try:
            package = importlib.import_module(package_name)

            for importer, modname, ispkg in pkgutil.iter_modules(
                package.__path__, package.__name__ + "."
            ):
                if not ispkg:
                    try:
                        importlib.import_module(modname)
                    except ImportError as e:
                        print(f"Warning: Could not import opcode module {modname}: {e}")
        except ImportError as e:
            print(f"Warning: Could not import opcodes package {package_name}: {e}")

    @classmethod
    def has_opcode(cls, name: str) -> bool:
        return name in cls._opcodes
