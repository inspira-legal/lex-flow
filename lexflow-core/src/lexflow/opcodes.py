from typing import Any, Callable, get_type_hints
from functools import wraps
import inspect
import random


class OpcodeRegistry:
    """Registry for opcode functions with automatic registration via decorator."""

    def __init__(self):
        self.opcodes: dict[str, Callable] = {}
        self.signatures: dict[str, inspect.Signature] = {}
        self._register_builtins()

    def register(self, name: str = None):
        """
        Decorator to register an opcode with automatic argument unpacking.

        Usage:
            @registry.register()
            async def my_opcode(x: int, y: int) -> int:
                return x + y

            @registry.register("custom_name")
            async def another(s: str) -> str:
                return s.upper()
        """

        def decorator(func: Callable) -> Callable:
            # Get opcode name
            opcode_name = name if name else func.__name__

            # Store original signature for introspection
            sig = inspect.signature(func)
            self.signatures[opcode_name] = sig

            # wrapper that handles list unpacking
            @wraps(func)
            async def wrapper(args: list[Any]) -> Any:
                # Get parameter information
                params = list(sig.parameters.values())

                # Handle different parameter patterns
                if params and params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
                    # Function accepts *args
                    return await func(*args)
                else:
                    # Fixed parameters - unpack what we have
                    # Handle optional parameters with defaults
                    bound_args = []
                    for i, param in enumerate(params):
                        if i < len(args):
                            bound_args.append(args[i])
                        elif param.default != inspect.Parameter.empty:
                            bound_args.append(param.default)
                        else:
                            raise ValueError(
                                f"{opcode_name} requires {len(params)} arguments, got {len(args)}"
                            )

                    return await func(*bound_args)

            # Store the wrapper
            self.opcodes[opcode_name] = wrapper

            # Return original function (so it can still be called directly if needed)
            return func

        return decorator

    async def call(self, name: str, args: list[Any]) -> Any:
        """Call an opcode with arguments."""
        if name not in self.opcodes:
            raise ValueError(f"Unknown opcode: {name}")
        return await self.opcodes[name](args)

    def get_interface(self, name: str) -> dict:
        """Get the interface of an opcode from its signature."""
        if name not in self.signatures:
            return {"error": f"No signature for {name}"}

        sig = self.signatures[name]

        # Get the original function (unwrap from the wrapper)
        func = self.opcodes[name]
        original_func = func.__wrapped__ if hasattr(func, "__wrapped__") else func

        try:
            hints = get_type_hints(original_func)
        except:  # noqa
            hints = {}

        params = []
        for param_name, param in sig.parameters.items():
            param_type = hints.get(param_name, Any)
            type_name = (
                param_type.__name__
                if hasattr(param_type, "__name__")
                else str(param_type)
            )

            param_info = {
                "name": param_name,
                "type": type_name,
                "required": param.default == inspect.Parameter.empty,
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            params.append(param_info)

        return_type = hints.get("return", Any)
        return_type_name = (
            return_type.__name__
            if hasattr(return_type, "__name__")
            else str(return_type)
        )

        return {
            "name": name,
            "parameters": params,
            "return_type": return_type_name,
            "doc": original_func.__doc__,
        }

    def list_opcodes(self) -> list[str]:
        """List all registered opcodes."""
        return sorted(self.opcodes.keys())

    def _register_builtins(self):
        """Register built-in opcodes using the decorator pattern."""

        # ============ IO Operations ============
        @self.register()
        async def io_print(*values: Any) -> None:
            """Print values to stdout."""
            print(*values, end="")

        @self.register()
        async def io_input(prompt: str = "") -> str:
            """Get input from user."""
            return input(prompt)

        # ============ Arithmetic Operators ============
        @self.register()
        async def operator_add(left: Any, right: Any) -> Any:
            """Add two values (numeric or string concatenation)."""
            try:
                return int(left) + int(right)
            except (ValueError, TypeError):
                return str(left) + str(right)

        @self.register()
        async def operator_subtract(left: int, right: int) -> int:
            """Subtract right from left."""
            return int(left) - int(right)

        @self.register()
        async def operator_multiply(left: int, right: int) -> int:
            """Multiply two values."""
            return int(left) * int(right)

        @self.register()
        async def operator_divide(left: int, right: int) -> int:
            """Integer division."""
            return int(left) // int(right)

        @self.register()
        async def operator_modulo(left: int, right: int) -> int:
            """Modulo operation (remainder)."""
            return int(left) % int(right)

        # ============ Comparison Operators ============
        @self.register()
        async def operator_equals(left: Any, right: Any) -> bool:
            """Check equality (with type coercion for numbers)."""
            try:
                return int(left) == int(right)
            except (ValueError, TypeError):
                return left == right

        @self.register()
        async def operator_not_equals(left: Any, right: Any) -> bool:
            """Check inequality."""
            try:
                return int(left) != int(right)
            except (ValueError, TypeError):
                return left != right

        @self.register()
        async def operator_less_than(left: int, right: int) -> bool:
            """Check if left < right."""
            return int(left) < int(right)

        @self.register()
        async def operator_greater_than(left: int, right: int) -> bool:
            """Check if left > right."""
            return int(left) > int(right)

        @self.register()
        async def operator_less_than_or_equals(left: int, right: int) -> bool:
            """Check if left <= right."""
            return int(left) <= int(right)

        @self.register()
        async def operator_greater_than_or_equals(left: int, right: int) -> bool:
            """Check if left >= right."""
            return int(left) >= int(right)

        # ============ Logical Operators ============
        @self.register()
        async def operator_and(left: bool, right: bool) -> bool:
            """Logical AND."""
            return bool(left) and bool(right)

        @self.register()
        async def operator_or(left: bool, right: bool) -> bool:
            """Logical OR."""
            return bool(left) or bool(right)

        @self.register()
        async def operator_not(value: bool) -> bool:
            """Logical NOT."""
            return not bool(value)

        # ============ Math Operations ============
        @self.register()
        async def math_random(min_val: int, max_val: int) -> int:
            """Generate random integer between min and max (inclusive)."""
            return random.randint(int(min_val), int(max_val))

        @self.register()
        async def math_abs(value: int) -> int:
            """Absolute value."""
            return abs(int(value))

        @self.register()
        async def math_pow(base: int, exponent: int) -> int:
            """Power operation."""
            return int(base) ** int(exponent)

        @self.register()
        async def math_sqrt(value: float) -> float:
            """Square root."""
            import math

            return math.sqrt(float(value))

        @self.register()
        async def math_floor(value: float) -> int:
            """Floor operation."""
            import math

            return math.floor(float(value))

        @self.register()
        async def math_ceil(value: float) -> int:
            """Ceiling operation."""
            import math

            return math.ceil(float(value))

        # ============ String Operations ============
        @self.register()
        async def string_length(text: str) -> int:
            """Get string length."""
            return len(str(text))

        @self.register()
        async def string_upper(text: str) -> str:
            """Convert to uppercase."""
            return str(text).upper()

        @self.register()
        async def string_lower(text: str) -> str:
            """Convert to lowercase."""
            return str(text).lower()

        @self.register()
        async def string_trim(text: str) -> str:
            """Remove leading/trailing whitespace."""
            return str(text).strip()

        @self.register()
        async def string_split(text: str, delimiter: str = " ") -> list[str]:
            """Split string by delimiter."""
            return str(text).split(delimiter)

        @self.register()
        async def string_join(items: list, delimiter: str = "") -> str:
            """Join list items into string."""
            return delimiter.join(str(item) for item in items)

        @self.register()
        async def string_contains(text: str, substring: str) -> bool:
            """Check if string contains substring."""
            return substring in str(text)

        @self.register()
        async def string_replace(text: str, old: str, new: str) -> str:
            """Replace all occurrences of old with new."""
            return str(text).replace(old, new)

        # ============ List Operations ============
        @self.register()
        async def list_length(items: list) -> int:
            """Get list length."""
            return len(items)

        @self.register()
        async def list_get(items: list, index: int) -> Any:
            """Get item at index."""
            return items[int(index)]

        @self.register()
        async def list_append(items: list, value: Any) -> list:
            """Append value to list (returns new list)."""
            new_list = items.copy()
            new_list.append(value)
            return new_list

        @self.register()
        async def list_contains(items: list, value: Any) -> bool:
            """Check if list contains value."""
            return value in items

        @self.register()
        async def list_range(start: int, stop: int = None, step: int = 1) -> list[int]:
            """Create a range as list."""
            if stop is None:
                return list(range(int(start)))
            return list(range(int(start), int(stop), int(step)))

        # ============ Type Conversions ============
        @self.register("str")
        async def to_string(value: Any) -> str:
            """Convert to string."""
            return str(value)

        @self.register("int")
        async def to_integer(value: Any) -> int:
            """Convert to integer."""
            return int(value)

        @self.register("float")
        async def to_float(value: Any) -> float:
            """Convert to float."""
            return float(value)

        @self.register("bool")
        async def to_boolean(value: Any) -> bool:
            """Convert to boolean."""
            return bool(value)

        @self.register("len")
        async def builtin_len(value: Any) -> int:
            """Get length of a value."""
            return len(value)

        @self.register("range")
        async def builtin_range(*args: int) -> list[int]:
            """Create a range as list."""
            return list(range(*[int(a) for a in args]))

        # ============ Workflow Operations ============
        @self.register()
        async def workflow_start() -> None:
            """Workflow entry point marker (no-op)."""
            pass

        @self.register()
        async def noop() -> None:
            """No operation."""
            pass

        # ============ Special Operations (handled by parser) ============
        @self.register()
        async def data_get_variable(var_name: str) -> None:
            """Get variable value - should be handled by parser as Variable reference."""
            raise NotImplementedError(
                "data_get_variable should be handled by parser as Variable"
            )

        @self.register()
        async def data_set_variable_to(var_name: str, value: Any) -> None:
            """Set variable - handled specially by parser/executor."""
            raise NotImplementedError(
                "data_set_variable_to should be handled by parser"
            )

        @self.register()
        async def workflow_return(value: Any = None) -> None:
            """Return from workflow - handled by Return statement."""
            raise NotImplementedError("workflow_return should be handled by parser")
