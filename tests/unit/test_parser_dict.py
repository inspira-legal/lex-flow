"""Tests for Parser.parse_dict() and Parser.parse_dicts() functionality."""

import pytest
from lexflow import Parser


def test_parse_dict_simple():
    """Test parsing a simple workflow from dictionary."""
    workflow_data = {
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
    program = parser.parse_dict(workflow_data)

    assert program is not None
    assert program.main.name == "main"
    assert len(program.externals) == 0


def test_parse_dict_with_variables():
    """Test parsing workflow with variables."""
    workflow_data = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {
                    "count": 42,
                    "message": "Hello"
                },
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
    program = parser.parse_dict(workflow_data)

    assert program.main.locals == {"count": 42, "message": "Hello"}
    assert program.globals == {"count": 42, "message": "Hello"}


def test_parse_dict_with_inputs():
    """Test parsing workflow with interface inputs."""
    workflow_data = {
        "workflows": [
            {
                "name": "main",
                "interface": {
                    "inputs": ["name", "age"],
                    "outputs": []
                },
                "variables": {
                    "name": "Guest",
                    "age": 0
                },
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
    program = parser.parse_dict(workflow_data)

    assert program.main.params == ["name", "age"]
    assert program.main.locals == {"name": "Guest", "age": 0}


def test_parse_dict_with_externals():
    """Test parsing workflow with external workflows."""
    workflow_data = {
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
            },
            {
                "name": "helper",
                "interface": {"inputs": ["x"], "outputs": []},
                "variables": {"x": 0},
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
    program = parser.parse_dict(workflow_data)

    assert program.main.name == "main"
    assert len(program.externals) == 1
    assert "helper" in program.externals
    assert program.externals["helper"].params == ["x"]


def test_parse_dict_no_workflows():
    """Test that parsing dict without workflows raises error."""
    workflow_data = {"workflows": []}

    parser = Parser()
    with pytest.raises(ValueError, match="No workflows found"):
        parser.parse_dict(workflow_data)


def test_parse_dict_no_main():
    """Test that parsing dict without main workflow raises error."""
    workflow_data = {
        "workflows": [
            {
                "name": "helper",
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
    with pytest.raises(ValueError, match="No 'main' workflow found"):
        parser.parse_dict(workflow_data)


def test_parse_dicts_simple():
    """Test parsing multiple dictionaries."""
    main_data = {
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

    helper_data = {
        "workflows": [
            {
                "name": "helper1",
                "interface": {"inputs": ["x"], "outputs": []},
                "variables": {"x": 0},
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
    program = parser.parse_dicts(main_data, [helper_data])

    assert program.main.name == "main"
    assert len(program.externals) == 1
    assert "helper1" in program.externals


def test_parse_dicts_multiple_includes():
    """Test parsing with multiple included dictionaries."""
    main_data = {
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

    helper1_data = {
        "workflows": [
            {
                "name": "helper1",
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

    helper2_data = {
        "workflows": [
            {
                "name": "helper2",
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
    program = parser.parse_dicts(main_data, [helper1_data, helper2_data])

    assert program.main.name == "main"
    assert len(program.externals) == 2
    assert "helper1" in program.externals
    assert "helper2" in program.externals


def test_parse_dicts_duplicate_names():
    """Test that duplicate workflow names raise error."""
    main_data = {
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

    helper1_data = {
        "workflows": [
            {
                "name": "helper",
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

    helper2_data = {
        "workflows": [
            {
                "name": "helper",  # Duplicate name
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
    with pytest.raises(ValueError, match="Duplicate workflow name"):
        parser.parse_dicts(main_data, [helper1_data, helper2_data])


def test_parse_dicts_no_includes():
    """Test parse_dicts with no includes (should work like parse_dict)."""
    main_data = {
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
    program = parser.parse_dicts(main_data, None)

    assert program.main.name == "main"
    assert len(program.externals) == 0
