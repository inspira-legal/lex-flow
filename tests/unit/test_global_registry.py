"""Tests for global opcode registry functionality."""

import io
import pytest
from lexflow import Parser, Engine, opcode, default_registry, OpcodeRegistry

pytestmark = pytest.mark.asyncio


# Register a custom opcode using the simple pattern
@opcode()
async def multiply_by_100(x: int) -> int:
    """Custom opcode that multiplies by 100."""
    return x * 100


@opcode("custom_named_op")
async def custom_named_op(text: str) -> str:
    """Custom opcode with custom name."""
    return f"Custom: {text}"


async def test_global_registry_simple():
    """Test that globally registered opcodes work with engines."""
    # Create a workflow that uses the custom opcode
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "use_custom",
                        "inputs": {}
                    },
                    "use_custom": {
                        "opcode": "multiply_by_100",
                        "next": "print_result",
                        "inputs": {
                            "x": {"literal": 5}
                        }
                    },
                    "print_result": {
                        "opcode": "io_print",
                        "next": None,
                        "inputs": {
                            "STRING": {"node": "use_custom"}
                        }
                    }
                }
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run engine - should use globally registered opcode
    result = await engine.run()

    # Verify output
    captured = output_buffer.getvalue()
    assert "500" in captured


async def test_global_registry_with_custom_name():
    """Test globally registered opcode with custom name."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "use_custom",
                        "inputs": {}
                    },
                    "use_custom": {
                        "opcode": "custom_named_op",
                        "next": "print_result",
                        "inputs": {
                            "text": {"literal": "Hello"}
                        }
                    },
                    "print_result": {
                        "opcode": "io_print",
                        "next": None,
                        "inputs": {
                            "STRING": {"node": "use_custom"}
                        }
                    }
                }
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    result = await engine.run()

    captured = output_buffer.getvalue()
    assert "Custom: Hello" in captured


async def test_custom_registry_isolation():
    """Test that custom registries don't include global opcodes."""
    # Create a custom registry
    custom_registry = OpcodeRegistry()

    # Register a custom opcode on this registry
    @custom_registry.register()
    async def isolated_op(x: int) -> int:
        return x * 200

    # Custom registry should have the custom opcode
    result = await custom_registry.call("isolated_op", [5])
    assert result == 1000

    # But should NOT have globally registered opcodes
    with pytest.raises(ValueError, match="Unknown opcode: multiply_by_100"):
        await custom_registry.call("multiply_by_100", [5])


async def test_engine_uses_default_registry():
    """Test that engines use default registry by default."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": None,
                        "inputs": {}
                    }
                }
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    # Create engine without specifying registry
    engine = Engine(program)

    # Should use default_registry
    assert engine.opcodes is default_registry


async def test_engine_with_custom_registry():
    """Test that engines can use custom registries."""
    custom_registry = OpcodeRegistry()

    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": None,
                        "inputs": {}
                    }
                }
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    # Create engine with custom registry
    engine = Engine(program, opcodes=custom_registry)

    # Should use the custom registry
    assert engine.opcodes is custom_registry
    assert engine.opcodes is not default_registry


async def test_multiple_engines_share_global_registry():
    """Test that multiple engines share the same global registry."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": None,
                        "inputs": {}
                    }
                }
            }
        ]
    }

    parser = Parser()
    program1 = parser.parse_dict(workflow)
    program2 = parser.parse_dict(workflow)

    engine1 = Engine(program1)
    engine2 = Engine(program2)

    # Both should use the same default_registry
    assert engine1.opcodes is engine2.opcodes
    assert engine1.opcodes is default_registry
