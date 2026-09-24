"""A node reached along several paths is parsed once and shared.

Before memoization the parser inlined the continuation of a gate into
every branch that flowed into it, so a chain of gates whose branches
rejoin grew the tree exponentially in the number of gates: one real
workflow of 3,285 nodes parsed into 560,309 AST objects and took
seconds. The parse result is unchanged (same unfolded structure), only
the sharing is new.
"""

import time

from lexflow import Engine, Parser
from lexflow.ast import Block, If


def _rejoining_gates(depth: int) -> dict:
    """``depth`` if/else gates in a row, both branches of each falling
    into the same continuation, which is the next gate."""
    nodes = {"start": {"opcode": "start", "next": "gate0"}}
    for i in range(depth):
        cont = f"gate{i + 1}" if i + 1 < depth else "tail"
        nodes[f"gate{i}"] = {
            "opcode": "control_if_else",
            "inputs": {
                "CONDITION": {"literal": True},
                "THEN": {"branch": f"then{i}"},
                "ELSE": {"branch": f"else{i}"},
            },
        }
        nodes[f"then{i}"] = {
            "opcode": "data_set_variable_to",
            "inputs": {"VARIABLE": {"literal": "x"}, "VALUE": {"literal": i}},
            "next": cont,
        }
        nodes[f"else{i}"] = {
            "opcode": "data_set_variable_to",
            "inputs": {"VARIABLE": {"literal": "x"}, "VALUE": {"literal": -i}},
            "next": cont,
        }
    nodes["tail"] = {
        "opcode": "data_set_variable_to",
        "inputs": {"VARIABLE": {"literal": "done"}, "VALUE": {"literal": True}},
    }
    return {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {"x": 0, "done": False},
                "nodes": nodes,
            }
        ]
    }


def _distinct_objects(program) -> int:
    from pydantic import BaseModel

    seen: set[int] = set()
    stack = [program]
    while stack:
        o = stack.pop()
        if isinstance(o, BaseModel):
            if id(o) in seen:
                continue
            seen.add(id(o))
            stack.extend(getattr(o, k) for k in type(o).model_fields)
        elif isinstance(o, dict):
            stack.extend(o.values())
        elif isinstance(o, (list, tuple)):
            stack.extend(o)
    return len(seen)


class TestSharedContinuation:
    """The continuation shared by both branches is one Statement object."""

    def test_both_branches_share_the_tail_statement(self):
        program = Parser().parse_dict(_rejoining_gates(1))
        gate = program.main.body.stmts[0]
        assert isinstance(gate, If)
        then_tail = gate.then.stmts[-1]
        else_tail = gate.else_.stmts[-1]
        assert then_tail is else_tail

    def test_size_is_linear_in_the_node_table_not_the_path_space(self):
        # 20 rejoining gates = 2**20 paths. Unshared, the tree has millions
        # of objects; shared, a few hundred.
        program = Parser().parse_dict(_rejoining_gates(20))
        assert _distinct_objects(program) < 500

    def test_each_path_still_carries_the_whole_continuation(self):
        # Sharing must not change what a path executes: walking THEN of
        # every gate reaches the tail, and so does walking ELSE.
        program = Parser().parse_dict(_rejoining_gates(3))

        def last_along(pick):
            stmt = program.main.body.stmts[0]
            while isinstance(stmt, If):
                branch = pick(stmt)
                stmt = branch.stmts[-1] if isinstance(branch, Block) else branch
            return stmt

        by_then = last_along(lambda s: s.then)
        by_else = last_along(lambda s: s.else_)
        assert by_then is by_else
        assert by_then.name == "done"


class TestWalkVisitsTheDagOnce:
    """Anything that traverses the AST must follow the DAG, not the path space."""

    def test_walk_yields_each_object_once(self):
        from lexflow.ast import walk

        program = Parser().parse_dict(_rejoining_gates(20))
        visited = list(walk(program.main.body))
        assert len(visited) == len({id(n) for n in visited})
        assert len(visited) < 500

    def test_engine_construction_stays_linear(self):
        # 20 rejoining gates = 2**20 paths. Walking them instead of the DAG
        # took 13s here and blew the suite's 10s timeout.
        program = Parser().parse_dict(_rejoining_gates(20))
        start = time.perf_counter()
        Engine(program)
        assert time.perf_counter() - start < 1.0
