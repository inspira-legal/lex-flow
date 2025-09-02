from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, Any, get_type_hints
from dataclasses import dataclass
from enum import Enum
import importlib
import pkgutil


class OpcodeNotFoundError(Exception):
    pass


class ParamDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass
class ParamInfo:
    name: str
    type: type
    direction: ParamDirection
    description: str = ""
    required: bool = True
    default: Any = None


class BaseOpcode(ABC):
    _param_definitions: Dict[str, ParamInfo] = {}

    @abstractmethod
    async def execute(self, state, stmt, engine) -> bool:
        pass

    def resolve_params(self, state, stmt) -> Dict[str, Any]:
        params = {}
        input_params = [
            p
            for p in self._param_definitions.values()
            if p.direction == ParamDirection.INPUT
        ]

        provided_count = len(stmt.inputs)
        provided_params = input_params[:provided_count]

        for param in reversed(provided_params):
            params[param.name] = state.pop()

        for param in input_params[provided_count:]:
            if param.required and param.default is None:
                raise ValueError(
                    f"Required parameter '{param.name}' not provided"
                )
            else:
                params[param.name] = param.default

        return params

    @classmethod
    def get_param_info(cls) -> Dict[str, ParamInfo]:
        return getattr(cls, "_param_definitions", {})

    @classmethod
    def get_return_info(cls) -> dict:
        hints = get_type_hints(cls.execute)
        return_hint = hints.get("return", None)

        if return_hint is None or return_hint is bool:
            return {"type": None, "description": "No stack output"}

        if hasattr(return_hint, "__origin__") and return_hint.__origin__ is tuple:
            return {
                "type": "tuple",
                "element_types": list(return_hint.__args__),
                "count": len(return_hint.__args__),
                "description": f"Pushes {len(return_hint.__args__)} values to stack",
            }

        return {
            "type": return_hint,
            "count": 1,
            "description": f"Pushes {return_hint.__name__} to stack",
        }

    @classmethod
    def get_interface(cls) -> dict:
        return {
            "inputs": cls.get_param_info(),
            "outputs": cls.get_return_info(),
            "opcode_name": getattr(cls, "_opcode_name", cls.__name__.lower()),
        }


def params(**kwargs):
    def decorator(cls):
        cls._param_definitions = {}
        for name, config in kwargs.items():
            if isinstance(config, dict):
                cls._param_definitions[name] = ParamInfo(
                    name=name,
                    type=config.get("type", Any),
                    direction=ParamDirection(config.get("direction", "input")),
                    description=config.get("description", ""),
                    required=config.get("required", True),
                    default=config.get("default", None),
                )
        return cls

    return decorator


def opcode(name: Optional[str] = None):
    def decorator(cls: Type[BaseOpcode]) -> Type[BaseOpcode]:
        opcode_name = name if name is not None else cls.__name__.lower()
        cls._opcode_name = opcode_name
        OpcodeRegistry.register(opcode_name, cls)
        return cls

    return decorator


class ControlFlow:
    CONTINUE = "continue"
    REPEAT = "repeat"
    HALT = "halt"


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
