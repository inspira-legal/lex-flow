"""Example demonstrating the metrics collection system.

This example shows how to collect and analyze performance metrics
for workflow execution.
"""

import asyncio
from lexflow import Parser, Engine, ExecutionMetrics


# Workflow that performs various operations
WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {"sum": 0},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "loop", "inputs": {}},
                "loop": {
                    "opcode": "control_for",
                    "next": "print_result",
                    "inputs": {
                        "VAR": {"literal": "i"},
                        "START": {"literal": 0},
                        "END": {"literal": 10},
                        "BODY": {"branch": "loop_body"},
                    },
                },
                "loop_body": {
                    "opcode": "data_set_variable_to",
                    "next": None,
                    "inputs": {
                        "VARIABLE": {"literal": "sum"},
                        "VALUE": {"node": "add_sum"},
                    },
                },
                "add_sum": {
                    "opcode": "operator_add",
                    "next": None,
                    "inputs": {"A": {"variable": "sum"}, "B": {"variable": "i"}},
                },
                "print_result": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"variable": "sum"}},
                },
            },
        }
    ]
}


async def main():
    """Run workflow with metrics enabled."""
    print("=== LexFlow Metrics Example ===\n")

    # Parse workflow
    parser = Parser()
    program = parser.parse_dict(WORKFLOW)

    # Create engine with metrics enabled
    print("Running workflow with metrics collection...\n")
    engine = Engine(program, metrics=True)

    # Run workflow
    await engine.run()

    # Get formatted report
    print("\n" + engine.get_metrics_report(top_n=15))

    # Get summary
    print("\nSummary: " + engine.get_metrics_summary())

    # Access specific metrics
    print("\n=== Detailed Metrics ===")

    opcode_metrics = engine.metrics.get_aggregated("opcode")
    print("\nOpcode calls:")
    for name, metrics in opcode_metrics.items():
        print(
            f"  {name}: {metrics.count} calls, {metrics.total_time:.6f}s total, {metrics.avg_time:.6f}s avg"
        )

    stmt_metrics = engine.metrics.get_aggregated("statement")
    print("\nStatement executions:")
    for name, metrics in stmt_metrics.items():
        print(f"  {name}: {metrics.count} calls, {metrics.total_time:.6f}s total")

    # Get top 3 slowest opcodes
    print("\n=== Top 3 Slowest Opcodes ===")
    top_opcodes = engine.metrics.get_top_operations("opcode", n=3, sort_by="total_time")
    for i, (name, metrics) in enumerate(top_opcodes, 1):
        print(f"{i}. {name}: {metrics.total_time:.6f}s total ({metrics.count} calls)")

    # Export metrics as JSON
    print("\n=== Export Metrics ===")

    metrics_json = engine.metrics.to_json(indent=2)
    print(f"Exported {len(metrics_json)} bytes of JSON metrics data")

    # Show how to use custom metrics instance
    print("\n=== Using Custom Metrics Instance ===")
    custom_metrics = ExecutionMetrics()
    engine2 = Engine(program, metrics=custom_metrics)
    await engine2.run()
    print(f"Custom metrics collected {len(custom_metrics.operations)} operations")
    print(f"Total execution time: {custom_metrics.get_total_time():.6f}s")


if __name__ == "__main__":
    asyncio.run(main())
