import pytest
import json
from pathlib import Path
from typing import Dict, Any

from core.models import Workflow, Program
from core.ast import (
    Program as ASTProgram,
    Statement,
    Value,
    ValueType,
    StatementList,
    WorkflowDef,
)
from core.state import WorkflowState
from core.engine import Engine
from core.loader import WorkflowLoader


@pytest.fixture
def sample_workflow_data() -> Dict[str, Any]:
    """Basic workflow data for testing."""
    return {
        "workflows": [
            {
                "name": "test_workflow",
                "interface": {"inputs": [], "outputs": []},
                "variables": {"1": ["test_var", "hello"]},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "print_node",
                        "inputs": {},
                    },
                    "print_node": {
                        "opcode": "io_print",
                        "next": None,
                        "inputs": {"STRING": [1, "Hello World\n"]},
                    },
                },
            }
        ]
    }


@pytest.fixture
def sample_workflow(sample_workflow_data) -> Workflow:
    """Parsed workflow model for testing."""
    program = Program.model_validate(sample_workflow_data)
    return program.workflows[0]


@pytest.fixture
def simple_ast_program() -> ASTProgram:
    """Simple AST program for testing."""
    statements = [
        Statement(opcode="workflow_start", inputs={}),
        Statement(
            opcode="io_print",
            inputs={"STRING": Value(type=ValueType.LITERAL, data="Test\n")},
        ),
    ]

    workflow_def = WorkflowDef(
        name="test",
        inputs=[],
        outputs=[],
        variables={},
        body=StatementList(statements=statements),
        node_data={},
    )

    return ASTProgram(
        variables={},
        workflows={"test": workflow_def},
        main=StatementList(statements=[]),
        node_map={},
    )


@pytest.fixture
def workflow_state(simple_ast_program) -> WorkflowState:
    """WorkflowState instance for testing."""
    return WorkflowState(simple_ast_program)


@pytest.fixture
def engine(simple_ast_program) -> Engine:
    """Engine instance for testing."""
    return Engine(simple_ast_program)


@pytest.fixture
def workflow_loader() -> WorkflowLoader:
    """WorkflowLoader instance for testing."""
    return WorkflowLoader()


@pytest.fixture
def temp_workflow_file(tmp_path, sample_workflow_data) -> Path:
    """Create a temporary workflow file for testing."""
    workflow_file = tmp_path / "test_workflow.json"
    workflow_file.write_text(json.dumps(sample_workflow_data, indent=2))
    return workflow_file


@pytest.fixture
def math_workflow_data() -> Dict[str, Any]:
    """Workflow with mathematical operations for testing."""
    return {
        "workflows": [
            {
                "name": "math_test",
                "interface": {"inputs": ["x", "y"], "outputs": ["result"]},
                "variables": {"1": ["x", 0], "2": ["y", 0], "3": ["result", 0]},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": "add", "inputs": {}},
                    "add": {
                        "opcode": "operator_add",
                        "next": "return",
                        "inputs": {"OPERAND1": [3, "1"], "OPERAND2": [3, "2"]},
                    },
                    "return": {
                        "opcode": "workflow_return",
                        "next": None,
                        "inputs": {"VALUE": [2, "add"]},
                    },
                },
            }
        ]
    }


@pytest.fixture
def fixtures_path() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def integration_path() -> Path:
    """Path to integration test workflows."""
    return Path(__file__).parent / "integration"

