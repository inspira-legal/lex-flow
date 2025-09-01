import pytest
from core.opcodes import BaseOpcode, params, OpcodeRegistry


@params(
    value1={"type": int, "description": "First value"},
    value2={"type": str, "description": "Second value"},
)
class TestOpcode(BaseOpcode):
    """Test opcode for parameter testing."""

    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        state.push(f"{params['value1']}-{params['value2']}")
        return True


class TestBaseOpcode:
    """Essential tests for opcode parameter system."""

    def test_params_decorator_creates_param_definitions(self):
        """Test that @params decorator creates parameter definitions."""
        param_info = TestOpcode.get_param_info()

        assert len(param_info) == 2
        assert "value1" in param_info
        assert "value2" in param_info

        # Check value1 parameter
        value1_param = param_info["value1"]
        assert value1_param.name == "value1"
        assert value1_param.type == int  # noqa
        assert value1_param.description == "First value"
        assert value1_param.required is True

    def test_get_interface(self):
        """Test getting complete opcode interface."""
        interface = TestOpcode.get_interface()

        assert "inputs" in interface
        assert "outputs" in interface
        assert "opcode_name" in interface

        # Check inputs
        inputs = interface["inputs"]
        assert "value1" in inputs
        assert "value2" in inputs


class TestOpcodeRegistry:
    """Test opcode registry functionality."""

    def test_opcode_registry_singleton(self):
        """Test that OpcodeRegistry behaves like a singleton."""
        from core.opcodes import OpcodeRegistry

        registry1 = OpcodeRegistry()
        registry2 = OpcodeRegistry()

        # Both should access the same class-level _opcodes dict
        assert registry1._opcodes is registry2._opcodes

    def test_register_and_get_opcode(self):
        """Test registering and retrieving opcodes."""
        from core.opcodes import opcode

        @opcode("test_register")
        class TestRegisterOpcode(BaseOpcode):
            async def execute(self, state, stmt, engine):
                return True

        registry = OpcodeRegistry()

        # Should be registered
        assert registry.has_opcode("test_register")

        # Should be able to retrieve
        opcode_class = registry.get("test_register")
        assert opcode_class == TestRegisterOpcode

    def test_has_opcode(self):
        """Test checking if opcode exists."""
        registry = OpcodeRegistry()

        # Should not have random opcode
        assert not registry.has_opcode("nonexistent_opcode")

        # Should have registered opcodes after discovery
        registry.discover_opcodes("opcodes")
        assert registry.has_opcode("io_print")  # Should exist

    def test_get_nonexistent_opcode_raises(self):
        """Test that getting non-existent opcode raises error."""
        from core.opcodes import OpcodeNotFoundError

        registry = OpcodeRegistry()

        with pytest.raises(OpcodeNotFoundError):
            registry.get("definitely_nonexistent_opcode")

