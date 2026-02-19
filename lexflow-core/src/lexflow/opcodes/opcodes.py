from typing import Any, AsyncGenerator, Callable, List, Optional, Union, get_type_hints
from dataclasses import dataclass, field
from functools import wraps
from types import SimpleNamespace
import asyncio
import inspect
import random


@dataclass
class CategoryInfo:
    """Metadata for an opcode category."""

    id: str
    label: str
    prefix: str
    color: str = "#64748B"
    icon: str = "⚡"
    requires: Optional[str] = None  # pip extra required (e.g., "ai", "http")
    order: int = field(default=100)  # display order in docs

    def to_dict(self) -> dict:
        """Convert to dict for grammar.json export."""
        d = {
            "id": self.id,
            "label": self.label,
            "prefix": self.prefix,
            "color": self.color,
            "icon": self.icon,
        }
        if self.requires:
            d["requires"] = self.requires
        return d


class OpcodeRegistry:
    """Registry for opcode functions with automatic registration via decorator."""

    def __init__(self):
        self.opcodes: dict[str, Callable] = {}
        self.signatures: dict[str, inspect.Signature] = {}
        self.categories: dict[str, CategoryInfo] = {}
        self.opcode_categories: dict[str, str] = {}  # opcode_name -> category_id
        self._privileged: set[str] = set()
        self._injected: dict[str, Callable] = {}
        self._register_builtin_categories()
        self._register_builtins()

    def _register_builtin_categories(self):
        """Register built-in categories."""
        builtins = [
            CategoryInfo("io", "I/O Operations", "io_", "#22D3EE", "📤", order=10),
            CategoryInfo(
                "operator", "Operators", "operator_", "#9C27B0", "⚡", order=20
            ),
            CategoryInfo("math", "Math Operations", "math_", "#8B5CF6", "🔢", order=30),
            CategoryInfo(
                "string", "String Operations", "string_", "#F472B6", "📝", order=40
            ),
            CategoryInfo("list", "List Operations", "list_", "#3B82F6", "📋", order=50),
            CategoryInfo(
                "dict", "Dictionary Operations", "dict_", "#F59E0B", "📖", order=60
            ),
            CategoryInfo(
                "object", "Object Operations", "object_", "#10B981", "📦", order=70
            ),
            CategoryInfo(
                "type", "Type Conversions", "type_", "#6B7280", "🔄", order=80
            ),
            CategoryInfo(
                "throw", "Exception Operations", "throw_", "#EF4444", "⚠️", order=90
            ),
            CategoryInfo(
                "assert", "Assertion Operations", "assert_", "#F97316", "✓", order=95
            ),
            CategoryInfo(
                "workflow",
                "Workflow Operations",
                "workflow_",
                "#E91E63",
                "🔗",
                order=100,
            ),
            CategoryInfo(
                "data", "Data Operations", "data_", "#4CAF50", "📦", order=110
            ),
            CategoryInfo(
                "control", "Control Flow", "control_", "#FF9500", "↻", order=120
            ),
            CategoryInfo(
                "async", "Async Operations", "async_", "#06B6D4", "⏱", order=130
            ),
        ]
        for cat in builtins:
            self.categories[cat.id] = cat

    def register_category(
        self,
        id: str,
        label: str,
        prefix: str,
        color: str = "#64748B",
        icon: str = "⚡",
        requires: Optional[str] = None,
        order: int = 200,
    ) -> CategoryInfo:
        """Register a category for opcodes.

        Args:
            id: Unique category identifier (e.g., "pydantic_ai")
            label: Display label (e.g., "AI Operations (Pydantic AI)")
            prefix: Opcode name prefix (e.g., "pydantic_ai_")
            color: Hex color for UI display
            icon: Emoji icon for UI display
            requires: pip extra required (e.g., "ai" for lexflow[ai])
            order: Display order in docs (lower = earlier)

        Returns:
            The registered CategoryInfo
        """
        cat = CategoryInfo(id, label, prefix, color, icon, requires, order)
        self.categories[id] = cat
        return cat

    def get_category(self, opcode_name: str) -> Optional[CategoryInfo]:
        """Get category for an opcode by name."""
        # First check explicit mapping
        if opcode_name in self.opcode_categories:
            cat_id = self.opcode_categories[opcode_name]
            return self.categories.get(cat_id)

        # Fall back to prefix detection
        for cat in self.categories.values():
            if opcode_name.startswith(cat.prefix):
                return cat

        # Special cases for type conversions
        if opcode_name in ("str", "int", "float", "bool", "len", "range"):
            return self.categories.get("type")

        # Special cases for other builtins
        if opcode_name == "noop":
            return self.categories.get("workflow")
        if opcode_name == "throw":
            return self.categories.get("throw")

        return None

    def list_categories(self) -> list[CategoryInfo]:
        """List all registered categories sorted by order."""
        return sorted(self.categories.values(), key=lambda c: (c.order, c.id))

    def register(
        self, name: str = None, *, category: str = None, privileged: bool = False
    ):
        """
        Decorator to register an opcode with automatic argument unpacking.

        Usage:
            @registry.register()
            async def my_opcode(x: int, y: int) -> int:
                return x + y

            @registry.register("custom_name")
            async def another(s: str) -> str:
                return s.upper()

            @registry.register(category="pydantic_ai")
            async def pydantic_ai_run(agent, prompt: str) -> str:
                ...

            @registry.register(privileged=True)
            async def engine_only_op() -> dict:
                pass  # Implementation injected by Engine

        Args:
            name: Custom opcode name (default: function name)
            category: Explicit category ID (default: auto-detect from prefix)
            privileged: If True, opcode requires injection before use
        """

        def decorator(func: Callable) -> Callable:
            # Get opcode name
            opcode_name = name if name else func.__name__

            # Store category mapping if explicit
            if category:
                self.opcode_categories[opcode_name] = category

            # Store original signature for introspection
            sig = inspect.signature(func)
            self.signatures[opcode_name] = sig

            if privileged:
                # Mark as privileged - requires injection before use
                self._privileged.add(opcode_name)

                # Create placeholder that raises if called without injection
                @wraps(func)
                async def placeholder(args: list[Any]) -> Any:
                    raise RuntimeError(
                        f"Privileged opcode '{opcode_name}' requires injection. "
                        f"This opcode must be called within an Engine context."
                    )

                self.opcodes[opcode_name] = placeholder
            else:
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
        # Check for injected implementation first (for privileged opcodes)
        if name in self._injected:
            return await self._injected[name](args)
        return await self.opcodes[name](args)

    def inject(self, name: str, implementation: Callable) -> None:
        """Inject implementation for a privileged opcode.

        Args:
            name: The opcode name to inject implementation for
            implementation: Async function to use as the implementation

        Raises:
            ValueError: If opcode doesn't exist or is not privileged
        """
        if name not in self.opcodes:
            raise ValueError(f"Unknown opcode: {name}")
        if name not in self._privileged:
            raise ValueError(
                f"Opcode '{name}' is not privileged and cannot be injected"
            )

        # Get the signature for argument unpacking
        sig = self.signatures[name]

        # Create wrapper with argument unpacking
        @wraps(implementation)
        async def wrapper(args: list[Any]) -> Any:
            params = list(sig.parameters.values())
            if params and params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
                return await implementation(*args)
            else:
                bound_args = []
                for i, param in enumerate(params):
                    if i < len(args):
                        bound_args.append(args[i])
                    elif param.default != inspect.Parameter.empty:
                        bound_args.append(param.default)
                    else:
                        raise ValueError(
                            f"{name} requires {len(params)} arguments, got {len(args)}"
                        )
                return await implementation(*bound_args)

        self._injected[name] = wrapper

    def clear_injection(self, name: str) -> None:
        """Remove injected implementation for a privileged opcode."""
        self._injected.pop(name, None)

    def is_privileged(self, name: str) -> bool:
        """Check if an opcode is privileged (requires injection)."""
        return name in self._privileged

    @staticmethod
    def _format_type_hint(type_hint: Any) -> str:
        """Format a type hint preserving generic parameters."""
        if getattr(type_hint, "__origin__", None) is not None:
            return str(type_hint).replace("typing.", "")
        if hasattr(type_hint, "__name__"):
            return type_hint.__name__
        return str(type_hint).replace("typing.", "")

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
            type_name = self._format_type_hint(param_type)

            param_info = {
                "name": param_name,
                "type": type_name,
                "required": param.default == inspect.Parameter.empty,
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            params.append(param_info)

        return_type = hints.get("return", Any)
        return_type_name = self._format_type_hint(return_type)

        return {
            "name": name,
            "parameters": params,
            "return_type": return_type_name,
            "doc": inspect.cleandoc(original_func.__doc__)
            if original_func.__doc__
            else None,
        }

    def list_opcodes(self, include_private: bool = False) -> list[str]:
        """List all registered opcodes.

        Args:
            include_private: If True, include opcodes prefixed with '_'.
                            Defaults to False.
        """
        keys = self.opcodes.keys()
        if not include_private:
            keys = [k for k in keys if not k.startswith("_")]
        return sorted(keys)

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

        @self.register()
        async def string_substring(text: str, start: int, end: int = None) -> str:
            """Extract substring from start to end index.

            Args:
                text: Source string
                start: Start index (0-based)
                end: End index (exclusive), or None for rest of string
            """
            if end is None:
                return str(text)[int(start) :]
            return str(text)[int(start) : int(end)]

        @self.register()
        async def string_index_of(text: str, substring: str) -> int:
            """Find index of substring, returns -1 if not found."""
            return str(text).find(substring)

        @self.register()
        async def string_starts_with(text: str, prefix: str) -> bool:
            """Check if string starts with prefix."""
            return str(text).startswith(prefix)

        @self.register()
        async def string_ends_with(text: str, suffix: str) -> bool:
            """Check if string ends with suffix."""
            return str(text).endswith(suffix)

        @self.register()
        async def string_format(template: str, *values) -> str:
            """Format string with positional placeholders ({0}, {1}, ...)."""
            return template.format(*values)

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

        @self.register()
        async def list_pluck(items: list, key: str) -> list:
            """Extract a field from each dict in a list."""
            return [item[key] for item in items]

        @self.register()
        async def list_enumerate(items: list, start: int = 0) -> list:
            """Create index-value pairs from a list."""
            return [[i, item] for i, item in enumerate(items, start=int(start))]

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
        # These opcodes exist for introspection/documentation purposes.
        # Actual execution is handled by the parser and executor, not opcode dispatch.

        @self.register()
        async def data_get_variable(var_name: str) -> Any:
            """Get variable value - handled by parser as Variable reference."""
            raise NotImplementedError(
                "data_get_variable should be handled by parser as Variable"
            )

        @self.register()
        async def data_set_variable_to(variable: str, value: Any) -> None:
            """Set variable to a value."""
            raise NotImplementedError(
                "data_set_variable_to should be handled by parser"
            )

        @self.register()
        async def workflow_return(value: Any = None) -> None:
            """Return a value from the current workflow."""
            raise NotImplementedError("workflow_return should be handled by parser")

        # ============ Control Flow (handled by parser/executor) ============
        @self.register()
        async def control_if(condition: bool, then_branch: Any) -> None:
            """Execute branch if condition is true."""
            raise NotImplementedError("control_if should be handled by parser")

        @self.register()
        async def control_if_else(
            condition: bool, then_branch: Any, else_branch: Any
        ) -> None:
            """Execute then_branch if condition is true, else_branch otherwise."""
            raise NotImplementedError("control_if_else should be handled by parser")

        @self.register()
        async def control_while(condition: bool, body: Any) -> None:
            """Repeat body while condition is true."""
            raise NotImplementedError("control_while should be handled by parser")

        @self.register()
        async def control_for(
            var: str, start: int, end: int, step: int = 1, body: Any = None
        ) -> None:
            """Loop from start to end with step, binding each value to var."""
            raise NotImplementedError("control_for should be handled by parser")

        @self.register()
        async def control_foreach(var: str, iterable: Any, body: Any) -> None:
            """Iterate over items in iterable, binding each to var."""
            raise NotImplementedError("control_foreach should be handled by parser")

        @self.register()
        async def control_fork(*branches: Any) -> None:
            """Execute multiple branches concurrently."""
            raise NotImplementedError("control_fork should be handled by parser")

        @self.register()
        async def control_try(
            try_body: Any, catch_handlers: Any = None, finally_body: Any = None
        ) -> None:
            """Execute try_body with exception handling."""
            raise NotImplementedError("control_try should be handled by parser")

        @self.register()
        async def control_throw(message: str) -> None:
            """Throw a runtime error with the given message."""
            raise NotImplementedError("control_throw should be handled by parser")

        @self.register()
        async def workflow_call(workflow: str, *args: Any) -> Any:
            """Call another workflow by name with arguments."""
            raise NotImplementedError("workflow_call should be handled by parser")

        # ============ Async Control Flow (handled by parser/executor) ============
        @self.register()
        async def control_spawn(body: Any, var: str = None) -> None:
            """Spawn body as a background task, optionally storing handle in var."""
            raise NotImplementedError("control_spawn should be handled by parser")

        @self.register()
        async def control_async_foreach(var: str, iterable: Any, body: Any) -> None:
            """Async iterate over items in async iterable, binding each to var."""
            raise NotImplementedError(
                "control_async_foreach should be handled by parser"
            )

        @self.register()
        async def async_timeout(
            timeout: float, body: Any, on_timeout: Any = None
        ) -> None:
            """Execute body with timeout, optionally running on_timeout if exceeded."""
            raise NotImplementedError("async_timeout should be handled by parser")

        @self.register()
        async def control_with(resource: Any, var: str, body: Any) -> None:
            """Execute body with resource as async context manager, binding to var."""
            raise NotImplementedError("control_with should be handled by parser")

        # ============ Async Utility Operations ============
        @self.register()
        async def async_range(
            start: int, stop: int = None, step: int = 1, delay: float = 0
        ) -> AsyncGenerator[int, None]:
            """Create an async range generator.

            Like range() but async, with optional delay between items.
            Useful for rate-limited iteration with control_async_foreach.

            Args:
                start: Start value (or stop if stop is None)
                stop: Stop value (exclusive)
                step: Step between values (default 1)
                delay: Delay in seconds between yielding values

            Yields:
                Integers in the range
            """
            if stop is None:
                stop = start
                start = 0

            async def gen():
                i = start
                while (step > 0 and i < stop) or (step < 0 and i > stop):
                    yield i
                    i += step
                    if delay > 0:
                        await asyncio.sleep(delay)

            return gen()

        @self.register()
        async def async_from_list(
            items: List[Any], delay: float = 0
        ) -> AsyncGenerator[Any, None]:
            """Convert a list to an async generator.

            Useful for simulating streaming or rate-limited iteration.

            Args:
                items: List of items to yield
                delay: Delay in seconds between yielding items

            Yields:
                Each item from the list
            """

            async def gen():
                for item in items:
                    yield item
                    if delay > 0:
                        await asyncio.sleep(delay)

            return gen()

        # ============ Privileged Introspection Operations ============
        # These opcodes require injection by the Engine to access internal state.

        @self.register(privileged=True)
        async def introspect_context() -> dict:
            """Get execution context including program, workflows, and opcodes.

            Returns a dictionary with:
            - program: Program metadata (globals, main workflow, externals)
            - workflows: Available workflow definitions
            - opcodes: List of registered opcode names

            Note: This is a privileged opcode - implementation is injected by Engine.
            """
            pass  # Implementation injected by Engine

        @self.register(privileged=True)
        async def _get_workflow_manager() -> Any:
            """Get the WorkflowManager instance for workflow execution.

            This is an internal privileged opcode used by ai_agent_with_tools
            to access workflows as tools. Not intended for direct use.

            Note: This is a privileged opcode - implementation is injected by Engine.
            """
            pass  # Implementation injected by Engine


# Default global registry instance
default_registry = OpcodeRegistry()


def opcode(name: str = None, *, category: str = None):
    """Convenience decorator for registering opcodes to the default global registry.

    Usage:
        @opcode()
        async def fibonacci(n: int) -> int:
            return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)

        @opcode(category="my_category")
        async def my_category_op(x: int) -> int:
            return x * 2
    """
    return default_registry.register(name, category=category)


def register_category(
    id: str,
    label: str,
    prefix: str,
    color: str = "#64748B",
    icon: str = "⚡",
    requires: Optional[str] = None,
    order: int = 200,
) -> CategoryInfo:
    """Register a category to the default global registry.

    Usage:
        from lexflow.opcodes import register_category, opcode

        register_category(
            id="my_lib",
            label="My Library",
            prefix="my_lib_",
            color="#10B981",
            icon="🚀",
            requires="mylib",  # pip extra
        )

        @opcode()
        async def my_lib_do_thing(x: int) -> int:
            return x * 2
    """
    return default_registry.register_category(
        id, label, prefix, color, icon, requires, order
    )
