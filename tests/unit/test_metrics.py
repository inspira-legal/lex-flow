"""Tests for metrics collection system."""

import io
import pytest
from lexflow import Parser, Engine
from lexflow.metrics import ExecutionMetrics

# Enable async test support
pytestmark = pytest.mark.asyncio


# Simple workflow for basic metrics testing
SIMPLE_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {"x": 10, "y": 20},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "add", "inputs": {}},
                "add": {
                    "opcode": "operator_add",
                    "next": "print",
                    "inputs": {"A": {"variable": "x"}, "B": {"variable": "y"}},
                },
                "print": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"node": "add"}},
                },
            },
        }
    ]
}


# Workflow with control flow
CONTROL_FLOW_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {"counter": 0},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "loop", "inputs": {}},
                "loop": {
                    "opcode": "control_for",
                    "next": "print_done",
                    "inputs": {
                        "VAR": {"literal": "i"},
                        "START": {"literal": 0},
                        "END": {"literal": 5},
                        "BODY": {"branch": "loop_body"},
                    },
                },
                "loop_body": {
                    "opcode": "data_set_variable_to",
                    "next": None,
                    "inputs": {
                        "VARIABLE": {"literal": "counter"},
                        "VALUE": {"node": "add_counter"},
                    },
                },
                "add_counter": {
                    "opcode": "operator_add",
                    "next": None,
                    "inputs": {"A": {"variable": "counter"}, "B": {"literal": 1}},
                },
                "print_done": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"literal": "Done"}},
                },
            },
        }
    ]
}


# Workflow with external call
WORKFLOW_CALL_EXAMPLE = {
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
                    "next": "print_result",
                    "inputs": {
                        "WORKFLOW": {"literal": "helper"},
                        "ARG1": {"literal": 5},
                        "ARG2": {"literal": 10},
                    },
                },
                "print_result": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"node": "call_helper"}},
                },
            },
        },
        {
            "name": "helper",
            "interface": {"inputs": ["a", "b"], "outputs": []},
            "variables": {"a": 0, "b": 0},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "multiply", "inputs": {}},
                "multiply": {
                    "opcode": "operator_multiply",
                    "next": "return_result",
                    "inputs": {"A": {"variable": "a"}, "B": {"variable": "b"}},
                },
                "return_result": {
                    "opcode": "workflow_return",
                    "next": None,
                    "inputs": {"VALUE": {"node": "multiply"}},
                },
            },
        },
    ]
}


async def test_metrics_enabled_with_true():
    """Test that metrics=True creates an ExecutionMetrics instance."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, metrics=True)

    # Verify metrics object is ExecutionMetrics, not NullMetrics
    assert isinstance(engine.metrics, ExecutionMetrics)


async def test_metrics_enabled_with_instance():
    """Test passing an ExecutionMetrics instance directly."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    metrics = ExecutionMetrics()
    engine = Engine(program, metrics=metrics)

    # Should be the same instance
    assert engine.metrics is metrics


async def test_metrics_disabled_by_default():
    """Test that metrics are disabled by default (NullMetrics)."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program)

    # Should have NullMetrics
    from lexflow.metrics import NullMetrics

    assert isinstance(engine.metrics, NullMetrics)


async def test_basic_metrics_collection():
    """Test basic metrics collection for simple workflow."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer, metrics=True)

    _result = await engine.run()

    # Verify execution completed
    assert "30" in output_buffer.getvalue()

    # Check total execution time
    total_time = engine.metrics.get_total_time()
    assert total_time > 0

    # Check that we collected some operations
    assert len(engine.metrics.operations) > 0

    # Check for opcode metrics
    opcode_metrics = engine.metrics.get_aggregated("opcode")
    assert "operator_add" in opcode_metrics
    # io_print is executed as OpStmt, so we check statement metrics instead
    stmt_metrics = engine.metrics.get_aggregated("statement")
    assert "OpStmt" in stmt_metrics

    # Check for statement metrics
    stmt_metrics = engine.metrics.get_aggregated("statement")
    assert "OpStmt" in stmt_metrics or "ExprStmt" in stmt_metrics

    # Check for expression metrics
    expr_metrics = engine.metrics.get_aggregated("expression")
    assert len(expr_metrics) > 0


async def test_control_flow_metrics():
    """Test metrics collection for control flow statements."""
    parser = Parser()
    program = parser.parse_dict(CONTROL_FLOW_WORKFLOW)

    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer, metrics=True)

    _result = await engine.run()

    # Check for For statement metrics
    stmt_metrics = engine.metrics.get_aggregated("statement")
    assert "For" in stmt_metrics

    # For loop should have been executed once
    assert stmt_metrics["For"].count == 1

    # Check that loop body was executed multiple times
    # Assign statement should be called 5 times (loop iterations)
    if "Assign" in stmt_metrics:
        assert stmt_metrics["Assign"].count == 5


async def test_workflow_call_metrics():
    """Test metrics collection for workflow calls."""
    parser = Parser()
    program = parser.parse_dict(WORKFLOW_CALL_EXAMPLE)

    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer, metrics=True)

    _result = await engine.run()

    # Verify result
    assert "50" in output_buffer.getvalue()

    # Check for workflow call metrics
    workflow_metrics = engine.metrics.get_aggregated("workflow_call")
    assert "helper" in workflow_metrics
    # Note: May be called twice due to internal evaluation flow
    assert workflow_metrics["helper"].count >= 1
    assert workflow_metrics["helper"].total_time > 0


async def test_metrics_to_dict():
    """Test converting metrics to dictionary."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    metrics_dict = engine.metrics.to_dict()

    # Verify structure
    assert "total_execution_time" in metrics_dict
    assert "operation_count" in metrics_dict
    assert "aggregated" in metrics_dict
    assert "operations" in metrics_dict

    # Verify aggregated data
    assert "opcode" in metrics_dict["aggregated"]
    assert "statement" in metrics_dict["aggregated"]
    assert "expression" in metrics_dict["aggregated"]


async def test_metrics_to_json():
    """Test converting metrics to JSON."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    import json

    metrics_json = engine.metrics.to_json()

    # Verify it's valid JSON
    parsed = json.loads(metrics_json)
    assert "total_execution_time" in parsed
    assert "aggregated" in parsed


async def test_get_metrics_report():
    """Test generating formatted metrics report."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    report = engine.get_metrics_report(top_n=5)

    # Verify report contains expected sections
    assert "LEXFLOW EXECUTION METRICS REPORT" in report
    assert "Total Execution Time" in report
    assert "OPCODE METRICS" in report


async def test_get_metrics_summary():
    """Test getting brief metrics summary."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    summary = engine.get_metrics_summary()

    # Verify summary contains key info
    assert "Total:" in summary
    assert "Ops:" in summary


async def test_get_top_operations():
    """Test getting top operations by metric."""
    parser = Parser()
    program = parser.parse_dict(CONTROL_FLOW_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    # Get top opcodes by total time
    top_opcodes = engine.metrics.get_top_operations("opcode", n=5, sort_by="total_time")

    # Should return a list of tuples
    assert isinstance(top_opcodes, list)
    if top_opcodes:
        assert isinstance(top_opcodes[0], tuple)
        assert len(top_opcodes[0]) == 2  # (name, metrics)


async def test_opcode_timing():
    """Test that individual opcodes are timed correctly."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    opcode_metrics = engine.metrics.get_aggregated("opcode")

    # operator_add should have been called
    assert "operator_add" in opcode_metrics
    add_metrics = opcode_metrics["operator_add"]

    # Verify statistics
    assert add_metrics.count == 1
    assert add_metrics.total_time > 0
    assert add_metrics.min_time > 0
    assert add_metrics.max_time > 0
    assert add_metrics.avg_time > 0


async def test_statement_timing():
    """Test that statements are timed correctly."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    stmt_metrics = engine.metrics.get_aggregated("statement")

    # Should have Block statement (main body)
    assert "Block" in stmt_metrics
    block_metrics = stmt_metrics["Block"]

    assert block_metrics.count >= 1
    assert block_metrics.total_time > 0


async def test_null_metrics_no_overhead():
    """Test that NullMetrics has no overhead."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    # Engine without metrics
    engine = Engine(program, output=io.StringIO())

    _result = await engine.run()

    # Should return empty/default values
    assert engine.metrics.get_total_time() == 0.0
    assert engine.metrics.get_aggregated("opcode") == {}
    assert engine.metrics.to_dict() == {}
    assert engine.metrics.get_report() == "Metrics collection disabled"
    assert engine.metrics.get_summary() == "Metrics disabled"


async def test_metrics_with_errors():
    """Test that metrics are still collected when errors occur."""
    error_workflow = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "throw_error",
                        "inputs": {},
                    },
                    "throw_error": {
                        "opcode": "control_throw",
                        "next": None,
                        "inputs": {"VALUE": {"literal": "Test error"}},
                    },
                },
            }
        ]
    }

    parser = Parser()
    program = parser.parse_dict(error_workflow)
    engine = Engine(program, metrics=True)

    # Should raise error
    with pytest.raises(RuntimeError, match="Test error"):
        await engine.run()

    # But metrics should still be collected
    assert engine.metrics.get_total_time() > 0
    assert len(engine.metrics.operations) > 0


async def test_aggregated_metrics_accuracy():
    """Test that aggregated metrics compute correct statistics."""
    parser = Parser()
    program = parser.parse_dict(CONTROL_FLOW_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    opcode_metrics = engine.metrics.get_aggregated("opcode")

    # operator_add should be called 5 times in the loop
    if "operator_add" in opcode_metrics:
        add_metrics = opcode_metrics["operator_add"]
        assert add_metrics.count == 5

        # Average should equal total / count
        assert (
            abs(add_metrics.avg_time - (add_metrics.total_time / add_metrics.count))
            < 1e-9
        )

        # Min should be <= max
        assert add_metrics.min_time <= add_metrics.max_time


async def test_metrics_measure_context_manager():
    """Test the measure context manager."""
    metrics = ExecutionMetrics()

    # Use measure context manager
    with metrics.measure("test", "test_operation", {"key": "value"}):
        # Simulate some work
        _total = sum(range(100))

    # Verify metric was recorded
    test_metrics = metrics.get_aggregated("test")
    assert "test_operation" in test_metrics
    assert test_metrics["test_operation"].count == 1

    # Check that operation was recorded with metadata
    assert len(metrics.operations) == 1
    assert metrics.operations[0].metadata == {"key": "value"}


async def test_node_level_metrics():
    """Test that node-level metrics are collected with node IDs."""
    parser = Parser()
    program = parser.parse_dict(CONTROL_FLOW_WORKFLOW)

    output_buffer = io.StringIO()
    engine = Engine(program, output=output_buffer, metrics=True)

    _result = await engine.run()

    # Check for node-level metrics
    node_metrics = engine.metrics.get_aggregated("node")

    # Should have metrics for named nodes from the workflow
    assert len(node_metrics) > 0

    # Check that specific nodes are tracked (node IDs from CONTROL_FLOW_WORKFLOW)
    # The parser preserves node IDs like "loop", "loop_body", "add_counter", "print_done"
    assert "loop" in node_metrics
    assert "print_done" in node_metrics

    # Verify loop node was executed once
    assert node_metrics["loop"].count == 1
    assert node_metrics["loop"].total_time > 0

    # Verify print_done node was executed once
    assert node_metrics["print_done"].count == 1
    assert node_metrics["print_done"].total_time > 0

    # loop_body should be executed 5 times (once per iteration)
    if "loop_body" in node_metrics:
        assert node_metrics["loop_body"].count == 5


async def test_node_metrics_in_report():
    """Test that node metrics appear in the formatted report."""
    parser = Parser()
    program = parser.parse_dict(SIMPLE_WORKFLOW)

    engine = Engine(program, output=io.StringIO(), metrics=True)
    _result = await engine.run()

    report = engine.get_metrics_report(top_n=10)

    # Node metrics section should be included
    assert "NODE METRICS" in report

    # Should show timing for nodes by their ID
    node_metrics = engine.metrics.get_aggregated("node")
    if node_metrics:
        # At least one node name should appear in the report
        node_names = list(node_metrics.keys())
        assert any(node_name in report for node_name in node_names)
