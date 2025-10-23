"""Tests for Engine.run(inputs=...) functionality."""

import io
import pytest
from lexflow import Parser, Engine

# Enable async test support
pytestmark = pytest.mark.asyncio


# Workflow with inputs that prints a greeting
GREETING_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": ["name", "age"], "outputs": []},
            "variables": {"name": "Guest", "age": 0},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": "print_name",
                    "inputs": {},
                },
                "print_name": {
                    "opcode": "io_print",
                    "next": "print_age",
                    "inputs": {"STRING": {"variable": "name"}},
                },
                "print_age": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"variable": "age"}},
                },
            },
        }
    ]
}


async def test_engine_run_with_inputs():
    """Test running engine with input parameters."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run with inputs
    result = await engine.run(inputs={"name": "Alice", "age": 30})

    # Verify inputs were used
    captured = output_buffer.getvalue()
    assert "Alice" in captured
    assert "30" in captured


async def test_engine_run_without_inputs():
    """Test running engine without inputs (uses defaults)."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run without inputs - should use defaults
    result = await engine.run()

    # Verify defaults were used
    captured = output_buffer.getvalue()
    assert "Guest" in captured
    assert "0" in captured


async def test_engine_run_partial_inputs():
    """Test running with only some inputs (others use defaults)."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run with only name input
    result = await engine.run(inputs={"name": "Bob"})

    # Verify name was overridden but age used default
    captured = output_buffer.getvalue()
    assert "Bob" in captured
    assert "0" in captured  # Default age


async def test_engine_run_invalid_input_key():
    """Test that invalid input keys raise ValueError."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    engine = Engine(program)

    # Try to run with invalid input key
    with pytest.raises(ValueError, match="Invalid input parameters"):
        await engine.run(inputs={"invalid_key": "value"})


async def test_engine_run_multiple_invalid_keys():
    """Test error message with multiple invalid keys."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    engine = Engine(program)

    # Try to run with multiple invalid input keys
    with pytest.raises(ValueError) as exc_info:
        await engine.run(inputs={"name": "Alice", "invalid1": "x", "invalid2": "y"})

    error_msg = str(exc_info.value)
    assert "invalid1" in error_msg
    assert "invalid2" in error_msg
    assert "Main workflow accepts: ['name', 'age']" in error_msg


async def test_engine_run_valid_and_invalid_keys():
    """Test that even one invalid key causes error."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    engine = Engine(program)

    # Mix of valid and invalid keys
    with pytest.raises(ValueError, match="Invalid input parameters"):
        await engine.run(inputs={"name": "Alice", "invalid": "value"})


async def test_engine_run_empty_inputs():
    """Test running with empty inputs dict (should use defaults)."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run with empty inputs dict
    result = await engine.run(inputs={})

    # Should use defaults
    captured = output_buffer.getvalue()
    assert "Guest" in captured
    assert "0" in captured


async def test_engine_run_none_inputs():
    """Test running with inputs=None (should use defaults)."""
    parser = Parser()
    program = parser.parse_dict(GREETING_WORKFLOW)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run with None inputs
    result = await engine.run(inputs=None)

    # Should use defaults
    captured = output_buffer.getvalue()
    assert "Guest" in captured
    assert "0" in captured


async def test_engine_run_type_conversion():
    """Test that various types can be passed as inputs."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": ["text", "number", "flag"], "outputs": []},
                "variables": {"text": "", "number": 0, "flag": False},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "print_text",
                        "inputs": {},
                    },
                    "print_text": {
                        "opcode": "io_print",
                        "next": "print_number",
                        "inputs": {"STRING": {"variable": "text"}},
                    },
                    "print_number": {
                        "opcode": "io_print",
                        "next": "print_flag",
                        "inputs": {"STRING": {"variable": "number"}},
                    },
                    "print_flag": {
                        "opcode": "io_print",
                        "next": None,
                        "inputs": {"STRING": {"variable": "flag"}},
                    },
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    # Capture output
    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer)

    # Run with various types
    result = await engine.run(inputs={"text": "Hello", "number": 42, "flag": True})

    # Verify all types were used
    captured = output_buffer.getvalue()
    assert "Hello" in captured
    assert "42" in captured
    assert "True" in captured


async def test_engine_run_no_params():
    """Test workflow with no parameters doesn't error on empty inputs."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {
                    "inputs": [],  # No parameters
                    "outputs": [],
                },
                "variables": {},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": None, "inputs": {}}
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    engine = Engine(program)

    # Should work fine with no inputs
    result = await engine.run(inputs={})


async def test_engine_run_no_params_with_inputs():
    """Test that providing inputs to workflow with no params raises error."""
    workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {
                    "inputs": [],  # No parameters
                    "outputs": [],
                },
                "variables": {},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": None, "inputs": {}}
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow)

    engine = Engine(program)

    # Should error if we try to provide inputs
    with pytest.raises(ValueError, match="Invalid input parameters"):
        await engine.run(inputs={"name": "Alice"})
