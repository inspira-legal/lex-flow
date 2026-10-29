"""Secret values and how opcodes see them.

A ``Secret`` prints, formats and redacts as ``***``. Each opcode declares a
secret mode that decides what it receives and what its result becomes:

- ``PASS``: arguments and result are untouched; a ``Secret`` stays an object.
- ``REVEAL``: arguments are deep-unwrapped to real values; result untouched.
- ``TAINT`` (default): arguments are deep-unwrapped; when any carried a
  ``Secret``, every ``str`` in the result comes back as a ``Secret``.
"""

from types import SimpleNamespace
from typing import Any, Callable, Literal

PASS = "pass"
REVEAL = "reveal"
TAINT = "taint"
SECRET_MODES = (PASS, REVEAL, TAINT)
SecretMode = Literal["pass", "reveal", "taint"]

MASK = "***"


class Secret:
    """An immutable text value that never shows itself."""

    __slots__ = ("_value",)

    def __init__(self, value: "str | Secret"):
        if isinstance(value, Secret):
            value = value.reveal()
        if not isinstance(value, str):
            raise TypeError(f"Secret wraps a str, not {type(value).__name__}")
        object.__setattr__(self, "_value", value)

    def reveal(self) -> str:
        """Return the real value."""
        return self._value

    def __str__(self) -> str:
        return MASK

    def __repr__(self) -> str:
        return MASK

    def __format__(self, format_spec: str) -> str:
        return format(MASK, format_spec)

    def __bool__(self) -> bool:
        return bool(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Secret):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Secret is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Secret is immutable")

    def __reduce__(self):
        return (Secret, (self._value,))


def contains_secret(value: Any) -> bool:
    """Whether a Secret sits anywhere in dict values, lists, tuples, sets or objects."""
    return _contains_secret(value, set())


def _contains_secret(value: Any, seen: set[int]) -> bool:
    if isinstance(value, Secret):
        return True
    if isinstance(value, (dict, list, tuple, set, frozenset, SimpleNamespace)):
        if id(value) in seen:
            return False
        seen.add(id(value))
        items = _children(value)
        return any(_contains_secret(item, seen) for item in items)
    return False


def _children(value: Any):
    if isinstance(value, dict):
        return value.values()
    if isinstance(value, SimpleNamespace):
        return vars(value).values()
    return value


def _rebuild(value: Any, leaf: Callable[[Any], Any], memo: dict[int, Any]) -> Any:
    """Copy containers, applying ``leaf`` to everything else. Keys stay as they are."""
    if id(value) in memo:
        return memo[id(value)]
    if isinstance(value, dict):
        out = memo[id(value)] = {}
        for key, item in value.items():
            out[key] = _rebuild(item, leaf, memo)
        return out
    if isinstance(value, list):
        out = memo[id(value)] = []
        out.extend(_rebuild(item, leaf, memo) for item in value)
        return out
    if isinstance(value, SimpleNamespace):
        out = memo[id(value)] = SimpleNamespace()
        for key, item in vars(value).items():
            setattr(out, key, _rebuild(item, leaf, memo))
        return out
    if isinstance(value, tuple):
        return tuple(_rebuild(item, leaf, memo) for item in value)
    if isinstance(value, (set, frozenset)):
        return type(value)(_rebuild(item, leaf, memo) for item in value)
    return leaf(value)


def redact_secrets(value: Any) -> Any:
    """Return a new structure with every Secret replaced by ``***``; never mutates."""
    return _rebuild(value, lambda v: MASK if isinstance(v, Secret) else v, {})


def reveal_secrets(value: Any) -> Any:
    """Return the value with every Secret replaced by its real value.

    The value itself comes back when it holds no Secret, so callers keep
    identity (and in-place mutation) for plain data.
    """
    if not contains_secret(value):
        return value
    return _rebuild(value, lambda v: v.reveal() if isinstance(v, Secret) else v, {})


def taint(value: Any) -> Any:
    """Return the value with every str turned into a Secret."""
    return _rebuild(value, lambda v: Secret(v) if isinstance(v, str) else v, {})
