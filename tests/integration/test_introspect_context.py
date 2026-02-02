"""Integration tests for the introspect_context privileged opcode."""

import pytest
from lexflow import Parser, Engine

pytestmark = pytest.mark.asyncio


class TestIntrospectContext:
    """Tests for introspect_context opcode via full Engine execution."""

    async def test_introspect_context_returns_structure(self):
        """introspect_context returns expected structure."""
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {"result": None},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "store",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "store": {
                            "opcode": "data_set_variable_to",
                            "inputs": {
                                "VARIABLE": {"literal": "result"},
                                "VALUE": {"node": "get_ctx"},
                            },
                            "next": "ret",
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"variable": "result"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dict(workflow_data)
        engine = Engine(program)
        result = await engine.run()

        # Check structure
        assert "program" in result
        assert "workflows" in result
        assert "opcodes" in result

        # Check program section
        assert "globals" in result["program"]
        assert "main" in result["program"]
        assert "externals" in result["program"]

    async def test_introspect_context_shows_globals(self):
        """introspect_context includes global variables."""
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {"counter": 42, "name": "test"},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "get_ctx"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dict(workflow_data)
        engine = Engine(program)
        result = await engine.run()

        assert result["program"]["globals"]["counter"] == 42
        assert result["program"]["globals"]["name"] == "test"

    async def test_introspect_context_shows_main_workflow(self):
        """introspect_context includes main workflow metadata."""
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": ["x", "y"], "outputs": []},
                    "variables": {"x": 0, "y": 0},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "get_ctx"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dict(workflow_data)
        engine = Engine(program)
        result = await engine.run()

        assert result["program"]["main"]["name"] == "main"
        assert result["program"]["main"]["params"] == ["x", "y"]

    async def test_introspect_context_shows_external_workflows(self):
        """introspect_context includes external workflow metadata."""
        main_workflow = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "get_ctx"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        helper_workflow = {
            "workflows": [
                {
                    "name": "helper",
                    "interface": {"inputs": ["a", "b"], "outputs": []},
                    "variables": {"a": 0, "b": 0},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "add": {
                            "opcode": "operator_add",
                            "inputs": {
                                "left": {"variable": "a"},
                                "right": {"variable": "b"},
                            },
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "add"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dicts(main_workflow, [helper_workflow])
        engine = Engine(program)
        result = await engine.run()

        assert "helper" in result["program"]["externals"]
        assert result["program"]["externals"]["helper"]["params"] == ["a", "b"]

    async def test_introspect_context_shows_workflows(self):
        """introspect_context includes workflows with locals."""
        main_workflow = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "get_ctx"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        helper_workflow = {
            "workflows": [
                {
                    "name": "calculate",
                    "interface": {"inputs": ["n"], "outputs": []},
                    "variables": {"n": 10, "result": 0},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"variable": "n"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dicts(main_workflow, [helper_workflow])
        engine = Engine(program)
        result = await engine.run()

        assert "calculate" in result["workflows"]
        assert result["workflows"]["calculate"]["params"] == ["n"]
        assert result["workflows"]["calculate"]["locals"]["n"] == 10
        assert result["workflows"]["calculate"]["locals"]["result"] == 0

    async def test_introspect_context_shows_opcodes(self):
        """introspect_context includes list of available opcodes."""
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "inputs": {},
                            "next": "ret",
                        },
                        "get_ctx": {
                            "opcode": "introspect_context",
                            "isReporter": True,
                        },
                        "ret": {
                            "opcode": "workflow_return",
                            "inputs": {"VALUE": {"node": "get_ctx"}},
                            "next": None,
                        },
                    },
                }
            ]
        }

        parser = Parser()
        program = parser.parse_dict(workflow_data)
        engine = Engine(program)
        result = await engine.run()

        opcodes = result["opcodes"]
        assert isinstance(opcodes, list)
        assert "operator_add" in opcodes
        assert "io_print" in opcodes
        assert "introspect_context" in opcodes
