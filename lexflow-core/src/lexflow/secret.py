"""Secret values and how opcodes see them.

A ``Secret`` prints, formats and redacts as ``***``. Each opcode declares a
secret mode that decides what it receives and what its result becomes:

- ``PASS``: arguments and result are untouched; a ``Secret`` stays an object.
- ``REVEAL``: arguments are deep-unwrapped to real values; result untouched.
- ``TAINT`` (default): arguments are deep-unwrapped; when any carried a
  ``Secret``, every ``str`` in the result comes back as a ``Secret``.

The walkers below keep any (sub)container they do not change as the same
object. A container they do change is rebuilt as its base type (``dict``,
``list``, ``tuple``, ``set``, ``frozenset`` or ``SimpleNamespace``), so a
subclass such as ``OrderedDict`` or a namedtuple is not kept then.
"""

from types import SimpleNamespace
from typing import Any, Callable, Iterator, Literal, get_args

SecretMode = Literal["pass", "reveal", "taint"]
SECRET_MODES = get_args(SecretMode)
PASS, REVEAL, TAINT = SECRET_MODES

MASK = "***"

_CONTAINERS = (dict, list, tuple, set, frozenset, SimpleNamespace)
_IMMUTABLES = (tuple, set, frozenset)
_EXCEPTION_MARK = "_lexflow_secret"


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

    def __copy__(self) -> "Secret":
        return self

    def __deepcopy__(self, memo: dict) -> "Secret":
        return self

    def __reduce_ex__(self, protocol: Any):
        raise TypeError("Secret cannot be pickled")

    def __reduce__(self):
        raise TypeError("Secret cannot be pickled")


def mark_secret_exception(exception: BaseException) -> None:
    """Flag an exception whose message may carry a real secret value."""
    try:
        setattr(exception, _EXCEPTION_MARK, True)
    except Exception:
        pass  # never mask the original error


def is_secret_exception(exception: BaseException) -> bool:
    """Whether an exception was raised by an opcode that saw a Secret."""
    return getattr(exception, _EXCEPTION_MARK, False) is True


def _children(value: Any, keys: bool) -> list:
    if isinstance(value, dict):
        return [*value.keys(), *value.values()] if keys else list(value.values())
    if isinstance(value, SimpleNamespace):
        return list(vars(value).values())
    return list(value)


def _containers(value: Any, keys: bool) -> Iterator[tuple[Any, list]]:
    """Yield each container reachable from ``value`` once, with its children."""
    stack, seen = [value], set()
    while stack:
        container = stack.pop()
        if id(container) in seen:
            continue
        seen.add(id(container))
        children = _children(container, keys)
        yield container, children
        stack.extend(c for c in children if isinstance(c, _CONTAINERS))


def contains_secret(value: Any) -> bool:
    """Whether a Secret sits anywhere in dict keys or values, lists, tuples, sets or objects."""
    if isinstance(value, Secret):
        return True
    if not isinstance(value, _CONTAINERS):
        return False
    return any(
        isinstance(child, Secret)
        for _, children in _containers(value, keys=True)
        for child in children
    )


def _walk(value: Any, leaf: Callable[[Any], Any], keys: bool) -> Any:
    """Apply ``leaf`` to every non-container, rebuilding only containers that change.

    Iterative and cycle-safe. Dict keys go through ``leaf`` only when ``keys``.
    """
    if not isinstance(value, _CONTAINERS):
        return leaf(value)

    nodes: dict[int, tuple[Any, list]] = {}
    parents: dict[int, list[int]] = {}
    dirty: set[int] = set()
    for container, children in _containers(value, keys):
        nodes[id(container)] = (container, children)
        for child in children:
            if isinstance(child, _CONTAINERS):
                parents.setdefault(id(child), []).append(id(container))
            elif leaf(child) is not child:
                dirty.add(id(container))

    pending = list(dirty)
    while pending:
        for parent in parents.get(pending.pop(), ()):
            if parent not in dirty:
                dirty.add(parent)
                pending.append(parent)
    if id(value) not in dirty:
        return value

    out: dict[int, Any] = {}

    def get(item: Any) -> Any:
        if isinstance(item, _CONTAINERS):
            return out[id(item)] if id(item) in dirty else item
        return leaf(item)

    # Mutable shells first, so cycles through them resolve
    for key in dirty:
        container = nodes[key][0]
        if isinstance(container, dict):
            out[key] = {}
        elif isinstance(container, list):
            out[key] = []
        elif isinstance(container, SimpleNamespace):
            out[key] = SimpleNamespace()

    # Immutables need their immutable children built first
    for key in dirty:
        stack = [key]
        while stack:
            current = stack[-1]
            if current in out:
                stack.pop()
                continue
            container, children = nodes[current]
            todo = [
                id(c)
                for c in children
                if isinstance(c, _IMMUTABLES) and id(c) in dirty and id(c) not in out
            ]
            if todo:
                stack.extend(todo)
                continue
            stack.pop()
            base = next(t for t in (tuple, frozenset, set) if isinstance(container, t))
            out[current] = base(get(c) for c in children)

    for key in dirty:
        container = nodes[key][0]
        if isinstance(container, dict):
            for k, v in container.items():
                out[key][get(k) if keys else k] = get(v)
        elif isinstance(container, list):
            out[key].extend(get(item) for item in container)
        elif isinstance(container, SimpleNamespace):
            for name, item in vars(container).items():
                setattr(out[key], name, get(item))
    return out[id(value)]


def redact_secrets(value: Any) -> Any:
    """Return the value with every Secret, key or value, replaced by ``***``.

    Never mutates; parts that hold no Secret come back as the same objects.
    """
    return _walk(value, lambda v: MASK if isinstance(v, Secret) else v, keys=True)


def reveal_secrets(value: Any) -> Any:
    """Return the value with every Secret, key or value, replaced by its real value.

    Parts that hold no Secret come back as the same objects, so callers keep
    identity (and in-place mutation) for plain data.
    """
    if not contains_secret(value):
        return value
    return _walk(value, lambda v: v.reveal() if isinstance(v, Secret) else v, keys=True)


def taint(value: Any) -> Any:
    """Return the value with every str turned into a Secret; dict keys stay as they are."""
    return _walk(value, lambda v: Secret(v) if isinstance(v, str) else v, keys=False)
