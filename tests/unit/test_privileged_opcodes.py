"""Tests for the privileged opcode injection system."""

import pytest
from lexflow.opcodes import OpcodeRegistry

pytestmark = pytest.mark.asyncio


class TestPrivilegedOpcodes:
    """Tests for privileged opcode registration and injection."""

    async def test_privileged_opcode_without_injection_raises_error(self):
        """Calling a privileged opcode without injection raises RuntimeError."""
        registry = OpcodeRegistry()

        @registry.register(privileged=True)
        async def my_privileged_op() -> str:
            pass

        with pytest.raises(RuntimeError, match="Privileged opcode.*requires injection"):
            await registry.call("my_privileged_op", [])

    async def test_inject_non_privileged_opcode_raises_error(self):
        """Injecting into a non-privileged opcode raises ValueError."""
        registry = OpcodeRegistry()

        with pytest.raises(ValueError, match="not privileged"):
            registry.inject("operator_add", lambda: "test")

    async def test_inject_unknown_opcode_raises_error(self):
        """Injecting into an unknown opcode raises ValueError."""
        registry = OpcodeRegistry()

        with pytest.raises(ValueError, match="Unknown opcode"):
            registry.inject("nonexistent_opcode", lambda: "test")

    async def test_injected_implementation_is_called(self):
        """Injected implementation is called instead of placeholder."""
        registry = OpcodeRegistry()

        @registry.register(privileged=True)
        async def my_privileged_op(x: int) -> int:
            pass  # Placeholder

        async def actual_impl(x: int) -> int:
            return x * 2

        registry.inject("my_privileged_op", actual_impl)
        result = await registry.call("my_privileged_op", [5])
        assert result == 10

    async def test_clear_injection_restores_error(self):
        """After clearing injection, opcode raises error again."""
        registry = OpcodeRegistry()

        @registry.register(privileged=True)
        async def my_privileged_op() -> str:
            pass

        async def impl():
            return "injected"

        registry.inject("my_privileged_op", impl)
        assert await registry.call("my_privileged_op", []) == "injected"

        registry.clear_injection("my_privileged_op")
        with pytest.raises(RuntimeError, match="requires injection"):
            await registry.call("my_privileged_op", [])

    async def test_is_privileged(self):
        """is_privileged correctly identifies privileged opcodes."""
        registry = OpcodeRegistry()

        @registry.register(privileged=True)
        async def priv_op() -> None:
            pass

        @registry.register()
        async def normal_op() -> None:
            pass

        assert registry.is_privileged("priv_op") is True
        assert registry.is_privileged("normal_op") is False
        assert registry.is_privileged("nonexistent") is False

    async def test_injected_opcode_with_multiple_args(self):
        """Injected implementation handles multiple arguments."""
        registry = OpcodeRegistry()

        @registry.register(privileged=True)
        async def multi_arg_op(a: int, b: str, c: float = 1.5) -> str:
            pass

        async def impl(a: int, b: str, c: float = 1.5) -> str:
            return f"{a}-{b}-{c}"

        registry.inject("multi_arg_op", impl)

        # With all args
        result = await registry.call("multi_arg_op", [1, "test", 2.5])
        assert result == "1-test-2.5"

        # With default arg
        result = await registry.call("multi_arg_op", [1, "test"])
        assert result == "1-test-1.5"

    async def test_introspect_context_is_privileged(self):
        """introspect_context is registered as a privileged opcode."""
        registry = OpcodeRegistry()
        assert registry.is_privileged("introspect_context") is True

    async def test_get_workflow_manager_is_privileged(self):
        """_get_workflow_manager is registered as a privileged opcode."""
        registry = OpcodeRegistry()
        assert registry.is_privileged("_get_workflow_manager") is True

    async def test_privileged_opcode_listed_in_opcodes(self):
        """Privileged opcodes appear in list_opcodes."""
        registry = OpcodeRegistry()
        opcodes = registry.list_opcodes()
        assert "introspect_context" in opcodes
        # Private opcodes (prefixed with _) are hidden by default
        assert "_get_workflow_manager" not in opcodes
        # But visible with include_private=True
        all_opcodes = registry.list_opcodes(include_private=True)
        assert "_get_workflow_manager" in all_opcodes

    async def test_privileged_opcode_has_interface(self):
        """Privileged opcodes have proper interfaces for documentation."""
        registry = OpcodeRegistry()
        interface = registry.get_interface("introspect_context")
        assert interface["name"] == "introspect_context"
        assert interface["return_type"] == "dict"
        assert "doc" in interface
