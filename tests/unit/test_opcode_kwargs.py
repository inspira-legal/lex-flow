"""Tests for keyword argument binding in the opcode registry."""

import pytest
from lexflow import OpcodeRegistry

pytestmark = pytest.mark.asyncio


@pytest.fixture
def registry():
    reg = OpcodeRegistry()

    @reg.register()
    async def greet(name: str, greeting: str = "Hello", punct: str = "!") -> str:
        return f"{greeting}, {name}{punct}"

    @reg.register()
    async def join_all(*parts: str) -> str:
        return "-".join(parts)

    return reg


async def test_positional_only_call_is_unchanged(registry):
    assert await registry.call("greet", ["Ana"]) == "Hello, Ana!"
    assert await registry.call("greet", ["Ana", "Hi"]) == "Hi, Ana!"


async def test_kwargs_bind_by_name(registry):
    result = await registry.call("greet", [], {"name": "Ana", "greeting": "Hi"})
    assert result == "Hi, Ana!"


async def test_kwargs_skip_optional_parameters(registry):
    """The bug positional binding cannot avoid: filling a later optional only."""
    result = await registry.call("greet", ["Ana"], {"punct": "?"})
    assert result == "Hello, Ana?"


async def test_unknown_kwarg_raises(registry):
    with pytest.raises(ValueError, match="unexpected keyword argument"):
        await registry.call("greet", ["Ana"], {"nome": "Ana"})


async def test_duplicate_argument_raises(registry):
    with pytest.raises(ValueError, match="multiple values"):
        await registry.call("greet", ["Ana"], {"name": "Bia"})


async def test_missing_required_argument_raises(registry):
    with pytest.raises(ValueError, match="requires"):
        await registry.call("greet", [], {"greeting": "Hi"})


async def test_extra_positional_arguments_are_dropped(registry):
    assert await registry.call("greet", ["Ana", "Hi", "!", "extra"]) == "Hi, Ana!"


async def test_variadic_opcode_rejects_kwargs(registry):
    assert await registry.call("join_all", ["a", "b"]) == "a-b"
    with pytest.raises(ValueError, match="variadic"):
        await registry.call("join_all", ["a"], {"parts": "b"})


async def test_privileged_injection_supports_kwargs():
    reg = OpcodeRegistry()

    @reg.register(privileged=True)
    async def needs_engine(x: int, factor: int = 2) -> int:
        pass

    async def impl(x: int, factor: int = 2) -> int:
        return x * factor

    reg.inject("needs_engine", impl)

    assert await reg.call("needs_engine", [5]) == 10
    assert await reg.call("needs_engine", [5], {"factor": 3}) == 15
