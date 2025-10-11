"""Metrics collection system for LexFlow execution performance tracking.

This module provides comprehensive performance metrics for workflow execution,
including timing for nodes, statements, expressions, opcodes, and workflow calls.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from collections import defaultdict
import time
import json
from contextlib import contextmanager


@dataclass
class OperationMetric:
    """Metrics for a single operation execution."""

    operation_type: str  # "node", "statement", "expression", "opcode", "workflow_call"
    name: str  # node_id, statement type, opcode name, workflow name
    duration: float  # seconds
    timestamp: float  # when it started
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional context


@dataclass
class AggregatedMetrics:
    """Aggregated statistics for a specific operation."""

    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0

    def update(self, duration: float):
        """Update statistics with a new duration measurement."""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.avg_time = self.total_time / self.count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "count": self.count,
            "total_time": self.total_time,
            "min_time": self.min_time if self.min_time != float('inf') else 0.0,
            "max_time": self.max_time,
            "avg_time": self.avg_time,
        }


class ExecutionMetrics:
    """Collects and aggregates execution metrics for a workflow run.

    Usage:
        metrics = ExecutionMetrics()
        engine = Engine(program, metrics=metrics)
        await engine.run()

        # Get report
        print(metrics.get_report())

        # Get raw data
        data = metrics.to_dict()
    """

    def __init__(self):
        self.operations: list[OperationMetric] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Aggregated metrics by operation type and name
        # Using defaultdict so new operation types can be added dynamically
        self._aggregated: defaultdict[str, dict[str, AggregatedMetrics]] = defaultdict(
            lambda: defaultdict(AggregatedMetrics)
        )

    def start_execution(self):
        """Mark the start of workflow execution."""
        self.start_time = time.perf_counter()

    def end_execution(self):
        """Mark the end of workflow execution."""
        self.end_time = time.perf_counter()

    def record(
        self,
        operation_type: str,
        name: str,
        duration: float,
        metadata: Optional[dict[str, Any]] = None
    ):
        """Record a single operation execution.

        Args:
            operation_type: Type of operation (node, statement, expression, opcode, workflow_call)
            name: Identifier for the operation
            duration: Time taken in seconds
            metadata: Optional additional context
        """
        timestamp = time.perf_counter()
        metric = OperationMetric(
            operation_type=operation_type,
            name=name,
            duration=duration,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        self.operations.append(metric)

        # Update aggregated metrics
        # defaultdict will automatically create the nested structure
        self._aggregated[operation_type][name].update(duration)

    @contextmanager
    def measure(
        self,
        operation_type: str,
        name: str,
        metadata: Optional[dict[str, Any]] = None
    ):
        """Context manager for measuring operation duration.

        Usage:
            with metrics.measure("opcode", "io_print"):
                await some_operation()
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.record(operation_type, name, duration, metadata)

    def get_total_time(self) -> float:
        """Get total execution time."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    def get_aggregated(self, operation_type: str) -> dict[str, AggregatedMetrics]:
        """Get aggregated metrics for a specific operation type."""
        if operation_type in self._aggregated:
            return dict(self._aggregated[operation_type])
        return {}

    def get_top_operations(
        self,
        operation_type: str,
        n: int = 10,
        sort_by: str = "total_time"
    ) -> list[tuple[str, AggregatedMetrics]]:
        """Get top N operations by a specific metric.

        Args:
            operation_type: Type of operation to analyze
            n: Number of results to return
            sort_by: Metric to sort by (total_time, avg_time, count, max_time)

        Returns:
            List of (name, metrics) tuples sorted by the specified metric
        """
        aggregated = self._aggregated.get(operation_type, {})
        sorted_ops = sorted(
            aggregated.items(),
            key=lambda x: getattr(x[1], sort_by),
            reverse=True
        )
        return sorted_ops[:n]

    def to_dict(self) -> dict[str, Any]:
        """Convert all metrics to a dictionary."""
        return {
            "total_execution_time": self.get_total_time(),
            "operation_count": len(self.operations),
            "aggregated": {
                op_type: {
                    name: metrics.to_dict()
                    for name, metrics in agg.items()
                }
                for op_type, agg in self._aggregated.items()
            },
            "operations": [
                {
                    "type": op.operation_type,
                    "name": op.name,
                    "duration": op.duration,
                    "timestamp": op.timestamp,
                    "metadata": op.metadata,
                }
                for op in self.operations
            ]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def get_report(self, top_n: int = 10) -> str:
        """Generate a formatted text report of execution metrics.

        Args:
            top_n: Number of top operations to show per category

        Returns:
            Formatted multi-line string report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("LEXFLOW EXECUTION METRICS REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Overall stats
        lines.append(f"Total Execution Time: {self.get_total_time():.6f} seconds")
        lines.append(f"Total Operations: {len(self.operations)}")
        lines.append("")

        # Report for each operation type
        for op_type in ["opcode", "statement", "workflow_call", "expression", "node"]:
            aggregated = self._aggregated.get(op_type, {})
            if not aggregated:
                continue

            lines.append("-" * 80)
            lines.append(f"{op_type.upper().replace('_', ' ')} METRICS")
            lines.append("-" * 80)

            # Get top operations by total time
            top_ops = self.get_top_operations(op_type, n=top_n, sort_by="total_time")

            if top_ops:
                lines.append(f"{'Name':<30} {'Count':>8} {'Total(s)':>12} {'Avg(s)':>12} {'Min(s)':>12} {'Max(s)':>12}")
                lines.append("-" * 80)

                for name, metrics in top_ops:
                    lines.append(
                        f"{name:<30} {metrics.count:>8} {metrics.total_time:>12.6f} "
                        f"{metrics.avg_time:>12.6f} {metrics.min_time:>12.6f} {metrics.max_time:>12.6f}"
                    )

            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def get_summary(self) -> str:
        """Generate a brief summary of metrics.

        Returns:
            Brief one-line summary
        """
        total_time = self.get_total_time()
        op_count = len(self.operations)

        # Count by type
        type_counts = defaultdict(int)
        for op in self.operations:
            type_counts[op.operation_type] += 1

        summary_parts = [f"Total: {total_time:.4f}s"]
        summary_parts.append(f"Ops: {op_count}")

        if type_counts:
            type_summary = ", ".join(
                f"{op_type}: {count}"
                for op_type, count in sorted(type_counts.items())
            )
            summary_parts.append(f"({type_summary})")

        return " | ".join(summary_parts)


# Null metrics object for when metrics are disabled
class NullMetrics:
    """No-op metrics collector for when metrics are disabled.

    This provides the same interface as ExecutionMetrics but does nothing,
    ensuring zero overhead when metrics collection is not needed.
    """

    def start_execution(self):
        pass

    def end_execution(self):
        pass

    def record(self, operation_type: str, name: str, duration: float, metadata: Optional[dict[str, Any]] = None):
        pass

    @contextmanager
    def measure(self, operation_type: str, name: str, metadata: Optional[dict[str, Any]] = None):
        yield

    def get_total_time(self) -> float:
        return 0.0

    def get_aggregated(self, operation_type: str) -> dict[str, AggregatedMetrics]:
        return {}

    def get_top_operations(self, operation_type: str, n: int = 10, sort_by: str = "total_time") -> list:
        return []

    def to_dict(self) -> dict[str, Any]:
        return {}

    def to_json(self, indent: int = 2) -> str:
        return "{}"

    def get_report(self, top_n: int = 10) -> str:
        return "Metrics collection disabled"

    def get_summary(self) -> str:
        return "Metrics disabled"
