"""Tests for AST model JSON serialization with discriminators."""

import pytest
from lexflow import Parser, Program
from lexflow.ast import (
    Literal,
    Variable,
    Call,
    Opcode,
    Assign,
    Block,
    If,
    While,
    Return,
    ExprStmt,
    OpStmt,
)


def test_literal_discriminator():
    """Test Literal expression has correct discriminator."""
    lit = Literal(value=42)
    assert lit.type == "Literal"

    # Test serialization
    json_str = lit.model_dump_json()
    assert '"type":"Literal"' in json_str

    # Test deserialization
    lit2 = Literal.model_validate_json(json_str)
    assert lit2.type == "Literal"
    assert lit2.value == 42


def test_variable_discriminator():
    """Test Variable expression has correct discriminator."""
    var = Variable(name="x")
    assert var.type == "Variable"

    # Test round-trip
    json_str = var.model_dump_json()
    var2 = Variable.model_validate_json(json_str)
    assert var2.type == "Variable"
    assert var2.name == "x"


def test_call_discriminator():
    """Test Call expression has correct discriminator."""
    call = Call(name="foo", args=[])
    assert call.type == "Call"

    # Test round-trip
    json_str = call.model_dump_json()
    call2 = Call.model_validate_json(json_str)
    assert call2.type == "Call"
    assert call2.name == "foo"


def test_opcode_discriminator():
    """Test Opcode expression has correct discriminator."""
    op = Opcode(name="operator_add", args=[])
    assert op.type == "Opcode"

    # Test round-trip
    json_str = op.model_dump_json()
    op2 = Opcode.model_validate_json(json_str)
    assert op2.type == "Opcode"
    assert op2.name == "operator_add"


def test_assign_discriminator():
    """Test Assign statement has correct discriminator."""
    lit = Literal(value=10)
    assign = Assign(name="x", value=lit)
    assert assign.type == "Assign"

    # Test round-trip
    json_str = assign.model_dump_json()
    assign2 = Assign.model_validate_json(json_str)
    assert assign2.type == "Assign"
    assert assign2.name == "x"
    assert assign2.value.type == "Literal"


def test_block_discriminator():
    """Test Block statement has correct discriminator."""
    lit = Literal(value=10)
    assign = Assign(name="x", value=lit)
    block = Block(stmts=[assign])
    assert block.type == "Block"

    # Test round-trip
    json_str = block.model_dump_json()
    block2 = Block.model_validate_json(json_str)
    assert block2.type == "Block"
    assert len(block2.stmts) == 1
    assert block2.stmts[0].type == "Assign"


def test_if_discriminator():
    """Test If statement has correct discriminator."""
    cond = Literal(value=True)
    then_stmt = Block(stmts=[])
    if_stmt = If(cond=cond, then=then_stmt, else_=None)
    assert if_stmt.type == "If"

    # Test round-trip
    json_str = if_stmt.model_dump_json()
    if_stmt2 = If.model_validate_json(json_str)
    assert if_stmt2.type == "If"
    assert if_stmt2.cond.type == "Literal"


def test_while_discriminator():
    """Test While statement has correct discriminator."""
    cond = Literal(value=True)
    body = Block(stmts=[])
    while_stmt = While(cond=cond, body=body)
    assert while_stmt.type == "While"

    # Test round-trip
    json_str = while_stmt.model_dump_json()
    while_stmt2 = While.model_validate_json(json_str)
    assert while_stmt2.type == "While"


def test_return_discriminator():
    """Test Return statement has correct discriminator."""
    val = Literal(value=42)
    ret = Return(values=[val])
    assert ret.type == "Return"

    # Test round-trip
    json_str = ret.model_dump_json()
    ret2 = Return.model_validate_json(json_str)
    assert ret2.type == "Return"
    assert len(ret2.values) == 1


def test_expr_stmt_discriminator():
    """Test ExprStmt statement has correct discriminator."""
    call = Call(name="foo", args=[])
    stmt = ExprStmt(expr=call)
    assert stmt.type == "ExprStmt"

    # Test round-trip
    json_str = stmt.model_dump_json()
    stmt2 = ExprStmt.model_validate_json(json_str)
    assert stmt2.type == "ExprStmt"
    assert stmt2.expr.type == "Call"


def test_op_stmt_discriminator():
    """Test OpStmt statement has correct discriminator."""
    lit = Literal(value="Hello")
    op_stmt = OpStmt(name="io_print", args=[lit])
    assert op_stmt.type == "OpStmt"

    # Test round-trip
    json_str = op_stmt.model_dump_json()
    op_stmt2 = OpStmt.model_validate_json(json_str)
    assert op_stmt2.type == "OpStmt"
    assert op_stmt2.name == "io_print"


def test_program_json_serialization_simple():
    """Test Program can be serialized and deserialized via JSON."""
    workflow_data = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {"x": 10},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": None, "inputs": {}}
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow_data)

    # Serialize to JSON
    program_json = program.model_dump_json()

    # Deserialize from JSON
    program2 = Program.model_validate_json(program_json)

    # Verify equality
    assert program2.main.name == program.main.name
    assert program2.globals == program.globals
    assert program2.main.body.type == "Block"


def test_program_json_serialization_with_externals():
    """Test Program with external workflows serializes correctly."""
    main_workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "call_helper",
                        "inputs": {},
                    },
                    "call_helper": {
                        "opcode": "workflow_call",
                        "next": None,
                        "inputs": {"WORKFLOW": {"literal": "helper"}},
                    },
                },
            }
        ]
    }

    helper_workflow = {
        "workflows": [
            {
                "name": "helper",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": None, "inputs": {}}
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dicts(main_workflow, [helper_workflow])

    # Serialize to JSON
    program_json = program.model_dump_json()

    # Deserialize from JSON
    program2 = Program.model_validate_json(program_json)

    # Verify externals preserved
    assert "helper" in program2.externals
    assert program2.externals["helper"].name == "helper"

    # Verify main workflow call preserved with correct type
    main_body_stmts = program2.main.body.stmts
    assert main_body_stmts[0].type == "ExprStmt"
    assert main_body_stmts[0].expr.type == "Call"


def test_nested_expressions_serialization():
    """Test nested expressions preserve discriminators."""
    # Create nested opcode: add(literal(1), variable(x))
    lit = Literal(value=1)
    var = Variable(name="x")
    add_op = Opcode(name="operator_add", args=[lit, var])

    # Serialize
    json_str = add_op.model_dump_json()

    # Deserialize
    add_op2 = Opcode.model_validate_json(json_str)

    # Verify all types preserved
    assert add_op2.type == "Opcode"
    assert add_op2.args[0].type == "Literal"
    assert add_op2.args[1].type == "Variable"
    assert add_op2.args[0].value == 1
    assert add_op2.args[1].name == "x"


def test_complex_workflow_serialization():
    """Test complex workflow with multiple statement types."""
    workflow_data = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": ["n"], "outputs": []},
                "variables": {"n": 5, "sum": 0},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": "init", "inputs": {}},
                    "init": {
                        "opcode": "data_set_variable_to",
                        "next": "loop",
                        "inputs": {
                            "VARIABLE": {"literal": "sum"},
                            "VALUE": {"literal": 0},
                        },
                    },
                    "loop": {
                        "opcode": "control_while",
                        "next": "print",
                        "inputs": {
                            "CONDITION": {"node": "check"},
                            "BODY": {"branch": "add"},
                        },
                    },
                    "check": {
                        "opcode": "operator_gt",
                        "inputs": {"LEFT": {"variable": "n"}, "RIGHT": {"literal": 0}},
                    },
                    "add": {
                        "opcode": "data_set_variable_to",
                        "next": "decrement",
                        "inputs": {
                            "VARIABLE": {"literal": "sum"},
                            "VALUE": {"node": "add_op"},
                        },
                    },
                    "add_op": {
                        "opcode": "operator_add",
                        "inputs": {
                            "LEFT": {"variable": "sum"},
                            "RIGHT": {"variable": "n"},
                        },
                    },
                    "decrement": {
                        "opcode": "data_set_variable_to",
                        "next": None,
                        "inputs": {
                            "VARIABLE": {"literal": "n"},
                            "VALUE": {"node": "sub_op"},
                        },
                    },
                    "sub_op": {
                        "opcode": "operator_sub",
                        "inputs": {"LEFT": {"variable": "n"}, "RIGHT": {"literal": 1}},
                    },
                    "print": {
                        "opcode": "workflow_return",
                        "next": None,
                        "inputs": {"VALUE": {"variable": "sum"}},
                    },
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(workflow_data)

    # Serialize to JSON
    program_json = program.model_dump_json()

    # Deserialize from JSON
    program2 = Program.model_validate_json(program_json)

    # Verify structure preserved
    assert program2.main.name == "main"
    assert program2.main.params == ["n"]
    assert program2.main.locals["n"] == 5

    # Verify statements have correct types
    main_stmts = program2.main.body.stmts
    assert main_stmts[0].type == "Assign"  # init
    assert main_stmts[1].type == "While"  # loop
    assert main_stmts[2].type == "Return"  # print

    # Verify while loop body
    while_stmt = main_stmts[1]
    assert while_stmt.body.type == "Block"
    assert len(while_stmt.body.stmts) == 2  # add and decrement
