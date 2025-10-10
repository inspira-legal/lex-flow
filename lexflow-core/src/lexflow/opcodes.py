from typing import Any, Callable, Union, get_type_hints
from functools import wraps
from types import SimpleNamespace
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
                return left + right
            except (ValueError, TypeError):
                return str(left) + str(right)

        @self.register()
        async def operator_subtract(left: Any, right: Any) -> Any:
            """Subtract right from left."""
            return left - right

        @self.register()
        async def operator_multiply(left: Any, right: Any) -> Any:
            """Multiply two values."""
            return left * right

        @self.register()
        async def operator_divide(left: Any, right: Any) -> Any:
            """Division (true division)."""
            return left / right

        @self.register()
        async def operator_modulo(left: Any, right: Any) -> Any:
            """Modulo operation (remainder)."""
            return left % right

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
        async def operator_less_than(left: Any, right: Any) -> bool:
            """Check if left < right."""
            return left < right

        @self.register()
        async def operator_greater_than(left: Any, right: Any) -> bool:
            """Check if left > right."""
            return left > right

        @self.register()
        async def operator_less_than_or_equals(left: Any, right: Any) -> bool:
            """Check if left <= right."""
            return left <= right

        @self.register()
        async def operator_greater_than_or_equals(left: Any, right: Any) -> bool:
            """Check if left >= right."""
            return left >= right

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
        async def math_abs(value: Any) -> Any:
            """Absolute value."""
            return abs(value)

        @self.register()
        async def math_pow(base: Any, exponent: Any) -> Any:
            """Power operation."""
            return base**exponent

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

        # ============ Dictionary Operations ============
        @self.register()
        async def dict_create(*args) -> dict:
            """Create dictionary from key-value pair arguments."""
            if not args:
                return {}
            if len(args) % 2 != 0:
                raise ValueError(
                    "dict_create requires even number of arguments (key-value pairs)"
                )

            result = {}
            for i in range(0, len(args), 2):
                result[args[i]] = args[i + 1]
            return result

        @self.register()
        async def dict_from_lists(keys: list, values: list) -> dict:
            """Create dict from parallel lists of keys and values."""
            return dict(zip(keys, values))

        @self.register()
        async def dict_set(d: dict, key: Any, value: Any) -> dict:
            """Set key-value pair (mutates and returns dict for chaining)."""
            d[key] = value
            return d

        @self.register()
        async def dict_get(d: dict, key: Any, default: Any = None) -> Any:
            """Get value by key with optional default."""
            return d.get(key, default)

        @self.register()
        async def dict_pop(d: dict, key: Any, default: Any = None) -> Any:
            """Remove and return value by key."""
            return d.pop(key, default)

        @self.register()
        async def dict_setdefault(d: dict, key: Any, default: Any = None) -> Any:
            """Set key to default if not present, return value."""
            return d.setdefault(key, default)

        @self.register()
        async def dict_update(d: dict, other: dict) -> dict:
            """Update dict with key-value pairs from other dict."""
            d.update(other)
            return d

        @self.register()
        async def dict_clear(d: dict) -> dict:
            """Clear all items from dict."""
            d.clear()
            return d

        @self.register()
        async def dict_copy(d: dict) -> dict:
            """Create a shallow copy of the dict."""
            return d.copy()

        @self.register()
        async def dict_keys(d: dict) -> list:
            """Get list of all keys."""
            return list(d.keys())

        @self.register()
        async def dict_values(d: dict) -> list:
            """Get list of all values."""
            return list(d.values())

        @self.register()
        async def dict_items(d: dict) -> list:
            """Get list of (key, value) tuples."""
            return list(d.items())

        @self.register()
        async def dict_contains(d: dict, key: Any) -> bool:
            """Check if key exists in dict."""
            return key in d

        @self.register()
        async def dict_len(d: dict) -> int:
            """Get number of items in dict."""
            return len(d)

        @self.register()
        async def dict_is_empty(d: dict) -> bool:
            """Check if dict is empty."""
            return len(d) == 0

        # ============ Object Operations ============
        @self.register()
        async def object_create() -> SimpleNamespace:
            """Create empty object (SimpleNamespace)."""
            return SimpleNamespace()

        @self.register()
        async def object_from_dict(d: dict) -> SimpleNamespace:
            """Create object from dictionary."""
            return SimpleNamespace(**d)

        @self.register()
        async def object_get(
            obj: Union[SimpleNamespace, dict], key: str, default: Any = None
        ) -> Any:
            """Get property value with optional default."""
            if isinstance(obj, SimpleNamespace):
                return getattr(obj, key, default)
            elif isinstance(obj, dict):
                return obj.get(key, default)
            else:
                raise TypeError(
                    f"object_get only works with SimpleNamespace or dict, not {type(obj).__name__}"
                )

        @self.register()
        async def object_set(
            obj: Union[SimpleNamespace, dict], key: str, value: Any
        ) -> Union[SimpleNamespace, dict]:
            """Set property value (returns object for chaining)."""
            if isinstance(obj, SimpleNamespace):
                setattr(obj, key, value)
                return obj
            elif isinstance(obj, dict):
                obj[key] = value
                return obj
            else:
                raise TypeError(
                    f"object_set only works with SimpleNamespace or dict, not {type(obj).__name__}"
                )

        @self.register()
        async def object_has(obj: Union[SimpleNamespace, dict], key: str) -> bool:
            """Check if object has property."""
            if isinstance(obj, SimpleNamespace):
                return hasattr(obj, key)
            elif isinstance(obj, dict):
                return key in obj
            else:
                raise TypeError("object_has only works with SimpleNamespace or dict")

        @self.register()
        async def object_remove(
            obj: Union[SimpleNamespace, dict], key: str
        ) -> Union[SimpleNamespace, dict]:
            """Remove property (returns object for chaining)."""
            if isinstance(obj, SimpleNamespace):
                if hasattr(obj, key):
                    delattr(obj, key)
                return obj
            elif isinstance(obj, dict):
                obj.pop(key, None)
                return obj
            else:
                raise TypeError("object_remove only works with SimpleNamespace or dict")

        @self.register()
        async def object_keys(obj: Union[SimpleNamespace, dict]) -> list:
            """Get list of all property names."""
            if isinstance(obj, SimpleNamespace):
                return [k for k in vars(obj).keys() if not k.startswith("_")]
            elif isinstance(obj, dict):
                return list(obj.keys())
            else:
                raise TypeError("object_keys only works with SimpleNamespace or dict")

        @self.register()
        async def object_to_dict(obj: Union[SimpleNamespace, dict]) -> dict:
            """Convert object to dictionary."""
            if isinstance(obj, SimpleNamespace):
                return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
            elif isinstance(obj, dict):
                return obj.copy()
            else:
                raise TypeError(
                    "object_to_dict only works with SimpleNamespace or dict"
                )

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

        # ============ Exception Operations ============
        @self.register()
        async def throw(message: str) -> None:
            """Throw a runtime error with message."""
            raise RuntimeError(message)

        @self.register()
        async def throw_value_error(message: str) -> None:
            """Throw a ValueError."""
            raise ValueError(message)

        @self.register()
        async def throw_type_error(message: str) -> None:
            """Throw a TypeError."""
            raise TypeError(message)

        @self.register()
        async def throw_assertion_error(message: str) -> None:
            """Throw an AssertionError."""
            raise AssertionError(message)

        @self.register()
        async def assert_true(
            condition: bool, message: str = "Assertion failed"
        ) -> None:
            """Assert condition is true, throw AssertionError otherwise."""
            if not bool(condition):
                raise AssertionError(message)

        @self.register()
        async def assert_equals(
            left: Any, right: Any, message: str = "Values not equal"
        ) -> None:
            """Assert two values are equal."""
            if left != right:
                raise AssertionError(f"{message}: {left} != {right}")

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


# Default global registry instance
default_registry = OpcodeRegistry()


def opcode(name: str = None):
    """Convenience decorator for registering opcodes to the default global registry.

    Usage:
        @opcode()
        async def fibonacci(n: int) -> int:
            return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
    """
    return default_registry.register(name)
