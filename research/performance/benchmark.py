#!/usr/bin/env python3
"""
Performance benchmark for LexFlow interpreter optimizations.

Run with:
    python research/performance/benchmark.py

Or with PyPy:
    pypy3 research/performance/benchmark.py

This benchmark compares:
1. Pure Python baseline
2. Original LexFlow interpreter
3. Optimized interpreter (v3)
"""

import asyncio
import sys
import time
from pathlib import Path

# Add research directory to path
research_dir = Path(__file__).parent
sys.path.insert(0, str(research_dir))

from lexflow import Parser
from lexflow.engine import Engine
from lexflow.runtime import Runtime
from lexflow.metrics import NullMetrics
from lexflow.opcodes import OpcodeRegistry
from lexflow.workflows import WorkflowManager

from optimized_evaluator import OptimizedEvaluator
from optimized_executor import OptimizedExecutor, Flow

# Test workflow: compute sum of 0..n-1
WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": ["n"], "outputs": []},
            "variables": {"n": 0, "total": 0},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": "init_total",
                    "inputs": {},
                },
                "init_total": {
                    "opcode": "data_set_variable_to",
                    "next": "loop",
                    "inputs": {
                        "VARIABLE": {"literal": "total"},
                        "VALUE": {"literal": 0},
                    },
                },
                "loop": {
                    "opcode": "control_for",
                    "next": "return_result",
                    "inputs": {
                        "VAR": {"literal": "i"},
                        "START": {"literal": 0},
                        "END": {"variable": "n"},
                        "BODY": {"branch": "add_to_total"},
                    },
                },
                "add_to_total": {
                    "opcode": "data_set_variable_to",
                    "next": None,
                    "inputs": {
                        "VARIABLE": {"literal": "total"},
                        "VALUE": {"node": "compute_sum"},
                    },
                },
                "compute_sum": {
                    "opcode": "operator_add",
                    "isReporter": True,
                    "inputs": {
                        "OPERAND1": {"variable": "total"},
                        "OPERAND2": {"variable": "i"},
                    },
                },
                "return_result": {
                    "opcode": "workflow_return",
                    "inputs": {
                        "VALUE": {"variable": "total"},
                    },
                },
            },
        }
    ]
}

# Parse workflow once
parser = Parser()
program = parser.parse_dict(WORKFLOW)


def pure_python(n: int) -> int:
    """Pure Python baseline."""
    total = 0
    for i in range(n):
        total = total + i
    return total


async def run_original(n: int) -> int:
    """Run with original LexFlow interpreter."""
    engine = Engine(program)
    return await engine.run(inputs={"n": n})


async def run_optimized(n: int) -> int:
    """Run with optimized interpreter."""
    runtime = Runtime(program)
    for k, v in program.main.locals.items():
        runtime.scope[k] = v
    runtime.scope["n"] = n

    metrics = NullMetrics()
    evaluator = OptimizedEvaluator(runtime, metrics)
    executor = OptimizedExecutor(runtime, evaluator, metrics)

    opcodes = OpcodeRegistry()
    evaluator.opcodes = opcodes
    executor.opcodes = opcodes

    workflows = WorkflowManager(program.externals, executor, runtime, metrics)
    evaluator.workflows = workflows

    flow = await executor.exec(program.main.body)
    return runtime.pop() if flow == Flow.RETURN and runtime.stack else None


async def main():
    # Detect runtime
    runtime_name = "PyPy" if hasattr(sys, "pypy_version_info") else "CPython"
    print("=" * 80)
    print(f"LEXFLOW PERFORMANCE BENCHMARK ({runtime_name} {sys.version.split()[0]})")
    print("=" * 80)
    print()

    # Verify correctness
    expected = pure_python(1000)
    orig = await run_original(1000)
    opt = await run_optimized(1000)
    assert expected == orig == opt, f"Mismatch: {expected} vs {orig} vs {opt}"
    print("All implementations verified correct")
    print()

    iterations = [1_000, 10_000, 100_000, 1_000_000]

    print(
        f"{'Iterations':<12} {'Python':<12} {'Original':<12} {'Optimized':<12} {'Speedup':<10} {'vs Python':<10}"
    )
    print("-" * 80)

    for n in iterations:
        # Pure Python
        start = time.perf_counter()
        pure_python(n)
        py_time = time.perf_counter() - start

        # Original
        start = time.perf_counter()
        await run_original(n)
        orig_time = time.perf_counter() - start

        # Optimized
        start = time.perf_counter()
        await run_optimized(n)
        opt_time = time.perf_counter() - start

        speedup = orig_time / opt_time if opt_time > 0 else 0
        vs_python = opt_time / py_time if py_time > 0 else 0

        print(
            f"{n:<12,} {py_time*1000:>9.1f}ms {orig_time*1000:>9.1f}ms "
            f"{opt_time*1000:>9.1f}ms {speedup:>8.2f}x {vs_python:>8.1f}x"
        )

    print()
    print("Speedup = Original / Optimized (higher = better)")
    print("vs Python = Optimized / Pure Python (lower = better)")
    print()
    print("See docs/performance/INTERPRETER_OPTIMIZATION.md for details.")


if __name__ == "__main__":
    asyncio.run(main())
