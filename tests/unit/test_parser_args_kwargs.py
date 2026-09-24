"""Tests for the 'args'/'kwargs' node syntax."""

import io
import warnings

import pytest
from lexflow import Parser, Engine

pytestmark = pytest.mark.asyncio


async def run(workflow: dict) -> str:
    """Run a workflow dict and return its printed output."""
    program = Parser().parse_dict(workflow)
    output = io.StringIO()
    await Engine(program, output=output).run()
    return output.getvalue()


def workflow(nodes: dict, variables: dict = None, extra: list = None) -> dict:
    main = {
        "name": "main",
        "interface": {"inputs": [], "outputs": []},
        "variables": variables or {},
        "nodes": nodes,
    }
    return {"workflows": [main] + (extra or [])}


async def test_args_bind_positionally():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "sub": {
            "opcode": "operator_subtract",
            "isReporter": True,
            "args": [{"literal": 10}, {"literal": 3}],
        },
        "show": {"opcode": "io_print", "args": [{"node": "sub"}]},
    }
    assert await run(workflow(nodes)) == "7"


async def test_kwargs_bind_by_name_regardless_of_order():
    """Legacy 'inputs' binds by position; 'kwargs' binds by name."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "sub": {
            "opcode": "operator_subtract",
            "isReporter": True,
            "kwargs": {"right": {"literal": 10}, "left": {"literal": 3}},
        },
        "show": {"opcode": "io_print", "args": [{"node": "sub"}]},
    }
    assert await run(workflow(nodes)) == "-7"


async def test_legacy_inputs_still_bind_by_position():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "sub": {
            "opcode": "operator_subtract",
            "isReporter": True,
            "inputs": {"right": {"literal": 10}, "left": {"literal": 3}},
        },
        "show": {"opcode": "io_print", "inputs": {"STRING": {"node": "sub"}}},
    }
    assert await run(workflow(nodes)) == "7"


async def test_args_and_kwargs_combine():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "joined": {
            "opcode": "string_join",
            "isReporter": True,
            "args": [{"literal": ["a", "b"]}],
            "kwargs": {"delimiter": {"literal": "-"}},
        },
        "show": {"opcode": "io_print", "args": [{"node": "joined"}]},
    }
    assert await run(workflow(nodes)) == "a-b"


async def test_mixing_inputs_with_kwargs_is_rejected():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "show": {
            "opcode": "io_print",
            "inputs": {"STRING": {"literal": "hi"}},
            "kwargs": {"values": {"literal": "hi"}},
        },
    }
    with pytest.raises(ValueError, match="mixes 'inputs' with 'args'/'kwargs'"):
        await run(workflow(nodes))


async def test_unknown_kwarg_is_reported():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "sub": {
            "opcode": "operator_subtract",
            "isReporter": True,
            "kwargs": {"esquerda": {"literal": 1}, "right": {"literal": 2}},
        },
        "show": {"opcode": "io_print", "args": [{"node": "sub"}]},
    }
    with pytest.raises(ValueError, match="unexpected keyword argument"):
        await run(workflow(nodes))


async def test_constructs_use_lowercase_slots():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "loop"},
        "loop": {
            "opcode": "control_for",
            "kwargs": {
                "var": {"literal": "i"},
                "start": {"literal": 0},
                "end": {"literal": 3},
                "body": {"branch": "show"},
            },
        },
        "show": {"opcode": "io_print", "args": [{"variable": "i"}]},
    }
    assert await run(workflow(nodes)) == "012"


async def test_if_else_and_assignment_slots():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "assign"},
        "assign": {
            "opcode": "data_set_variable_to",
            "next": "gate",
            "kwargs": {"variable": {"literal": "n"}, "value": {"literal": 5}},
        },
        "gate": {
            "opcode": "control_if_else",
            "kwargs": {
                "condition": {"node": "is_big"},
                "then": {"branch": "say_big"},
                "else": {"branch": "say_small"},
            },
        },
        "is_big": {
            "opcode": "operator_greater_than",
            "isReporter": True,
            "kwargs": {"left": {"variable": "n"}, "right": {"literal": 3}},
        },
        "say_big": {"opcode": "io_print", "args": [{"literal": "big"}]},
        "say_small": {"opcode": "io_print", "args": [{"literal": "small"}]},
    }
    assert await run(workflow(nodes)) == "big"


async def test_fork_branches_come_from_args():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "fork"},
        "fork": {
            "opcode": "control_fork",
            "args": [{"branch": "left"}, {"branch": "right"}],
        },
        "left": {"opcode": "io_print", "args": [{"literal": "L"}]},
        "right": {"opcode": "io_print", "args": [{"literal": "R"}]},
    }
    assert sorted(await run(workflow(nodes))) == ["L", "R"]


async def test_try_catch_finally_with_catch_list():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "guard"},
        "guard": {
            "opcode": "control_try",
            "kwargs": {
                "try": {"branch": "boom"},
                "catch": [
                    {
                        "exception_type": "RuntimeError",
                        "var": "err",
                        "body": {"branch": "show_error"},
                    }
                ],
                "finally": {"branch": "done"},
            },
        },
        "boom": {"opcode": "control_throw", "kwargs": {"value": {"literal": "oops"}}},
        "show_error": {"opcode": "io_print", "args": [{"variable": "err"}]},
        "done": {"opcode": "io_print", "args": [{"literal": "|done"}]},
    }
    assert await run(workflow(nodes)) == "oops|done"


async def test_workflow_call_with_keyword_arguments():
    greeter = {
        "name": "greet",
        "interface": {"inputs": ["name", "greeting"], "outputs": []},
        "variables": {"name": "World", "greeting": "Hello"},
        "nodes": {
            "start": {"opcode": "workflow_start", "next": "show"},
            "show": {
                "opcode": "io_print",
                "args": [{"variable": "greeting"}, {"variable": "name"}],
            },
        },
    }
    nodes = {
        "start": {"opcode": "workflow_start", "next": "call"},
        "call": {
            "opcode": "workflow_call",
            "kwargs": {
                "workflow": {"literal": "greet"},
                "name": {"literal": "Ana"},
            },
        },
    }
    assert await run(workflow(nodes, extra=[greeter])) == "Hello Ana"


async def test_workflow_call_rejects_unknown_keyword():
    greeter = {
        "name": "greet",
        "interface": {"inputs": ["name"], "outputs": []},
        "variables": {"name": "World"},
        "nodes": {
            "start": {"opcode": "workflow_start", "next": "show"},
            "show": {"opcode": "io_print", "args": [{"variable": "name"}]},
        },
    }
    nodes = {
        "start": {"opcode": "workflow_start", "next": "call"},
        "call": {
            "opcode": "workflow_call",
            "kwargs": {
                "workflow": {"literal": "greet"},
                "nome": {"literal": "Ana"},
            },
        },
    }
    with pytest.raises(ValueError, match="unexpected keyword argument"):
        await run(workflow(nodes, extra=[greeter]))


async def test_workflow_call_positional_args_list():
    greeter = {
        "name": "greet",
        "interface": {"inputs": ["name"], "outputs": []},
        "variables": {"name": "World"},
        "nodes": {
            "start": {"opcode": "workflow_start", "next": "show"},
            "show": {"opcode": "io_print", "args": [{"variable": "name"}]},
        },
    }
    nodes = {
        "start": {"opcode": "workflow_start", "next": "call"},
        "call": {
            "opcode": "workflow_call",
            "kwargs": {"workflow": {"literal": "greet"}},
            "args": [{"literal": "Ana"}],
        },
    }
    assert await run(workflow(nodes, extra=[greeter])) == "Ana"


async def test_legacy_inputs_warn_once_per_workflow():
    """Two legacy nodes, one warning: the count is the point of the test."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "first"},
        "first": {
            "opcode": "io_print",
            "inputs": {"STRING": {"literal": "hi"}},
            "next": "second",
        },
        "second": {"opcode": "io_print", "inputs": {"STRING": {"literal": "there"}}},
    }
    with pytest.warns(FutureWarning, match="legacy 'inputs' key") as record:
        Parser().parse_dict(workflow(nodes))
    assert len(record) == 1
    assert "2 nodes" in str(record[0].message)


async def test_args_kwargs_workflows_do_not_warn():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "show"},
        "show": {"opcode": "io_print", "args": [{"literal": "hi"}]},
    }
    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        Parser().parse_dict(workflow(nodes))


# ============= Shape validation =============


@pytest.mark.parametrize(
    "node,message",
    [
        (
            {"opcode": "io_print", "args": {"a": {"literal": 1}}},
            "'args' must be a list",
        ),
        (
            {"opcode": "io_print", "kwargs": [{"literal": 1}]},
            "'kwargs' must be a mapping",
        ),
        (
            {"opcode": "io_print", "inputs": [{"literal": 1}]},
            "'inputs' must be a mapping",
        ),
        (
            {"opcode": "io_print", "args": [], "inputs": {}},
            "mixes 'inputs' with 'args'/'kwargs'",
        ),
    ],
)
async def test_malformed_node_arguments_are_rejected(node, message):
    nodes = {"start": {"opcode": "workflow_start", "next": "n"}, "n": node}
    with pytest.raises(ValueError, match=message):
        Parser().parse_dict(workflow(nodes))


async def test_non_string_kwargs_keys_are_rejected():
    """YAML turns a bare 'on' into True, which pydantic would reject cryptically."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {"opcode": "io_print", "kwargs": {True: {"literal": 1}}},
    }
    with pytest.raises(ValueError, match="keys must be strings"):
        Parser().parse_dict(workflow(nodes))


async def test_catch_must_be_a_list():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "t"},
        "t": {
            "opcode": "control_try",
            "kwargs": {
                "try": {"branch": "b"},
                "catch": {"exception_type": "ValueError"},
            },
        },
        "b": {"opcode": "io_print", "args": [{"literal": "x"}]},
    }
    with pytest.raises(ValueError, match="'catch' must be a list"):
        Parser().parse_dict(workflow(nodes))


async def test_catch_handlers_must_be_mappings():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "t"},
        "t": {
            "opcode": "control_try",
            "kwargs": {"try": {"branch": "b"}, "catch": ["ValueError"]},
        },
        "b": {"opcode": "io_print", "args": [{"literal": "x"}]},
    }
    with pytest.raises(ValueError, match="handler must be a mapping"):
        Parser().parse_dict(workflow(nodes))


# ============= Unknown construct slots =============

BODY = {"b": {"opcode": "io_print", "args": [{"literal": "x"}]}}


@pytest.mark.parametrize(
    "node,unknown",
    [
        (
            {
                "opcode": "control_for",
                "kwargs": {
                    "var": {"literal": "i"},
                    "start": {"literal": 0},
                    "end": {"literal": 3},
                    "STEP": {"literal": 2},
                    "body": {"branch": "b"},
                },
            },
            "STEP",
        ),
        (
            {
                "opcode": "control_if",
                "kwargs": {"CONDITION": {"literal": True}, "then": {"branch": "b"}},
            },
            "CONDITION",
        ),
        (
            {
                "opcode": "control_try",
                "kwargs": {
                    "try": {"branch": "b"},
                    "catch": [],
                    "FINALLY": {"branch": "b"},
                },
            },
            "FINALLY",
        ),
        (
            {
                "opcode": "control_while",
                "kwargs": {"conditon": {"literal": False}, "body": {"branch": "b"}},
            },
            "conditon",
        ),
        (
            {
                "opcode": "data_set_variable_to",
                "kwargs": {"variable": {"literal": "x"}, "VALUE": {"literal": 1}},
            },
            "VALUE",
        ),
    ],
)
async def test_unknown_construct_slot_is_rejected(node, unknown):
    """An UPPERCASE or misspelled slot used to be dropped without a word."""
    nodes = {"start": {"opcode": "workflow_start", "next": "n"}, "n": node, **BODY}
    with pytest.raises(ValueError, match=f"unknown slot\\(s\\) {unknown}"):
        Parser().parse_dict(workflow(nodes))


async def test_known_construct_slots_are_accepted():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {
            "opcode": "control_for",
            "kwargs": {
                "var": {"literal": "i"},
                "start": {"literal": 0},
                "end": {"literal": 2},
                "step": {"literal": 1},
                "body": {"branch": "b"},
            },
        },
        **BODY,
    }
    assert await run(workflow(nodes)) == "xx"


async def test_legacy_uppercase_slots_still_parse():
    """The rejection must apply to the new syntax only."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {
            "opcode": "control_for",
            "inputs": {
                "VAR": {"literal": "i"},
                "START": {"literal": 0},
                "END": {"literal": 2},
                "STEP": {"literal": 1},
                "BODY": {"branch": "b"},
            },
        },
        "b": {"opcode": "io_print", "inputs": {"S": {"literal": "x"}}},
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        assert await run(workflow(nodes)) == "xx"


async def test_workflow_return_rejects_args_and_value_together():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "r"},
        "r": {
            "opcode": "workflow_return",
            "args": [{"literal": 1}],
            "kwargs": {"value": {"literal": 2}},
        },
    }
    with pytest.raises(ValueError, match="either 'args' or 'value'"):
        Parser().parse_dict(workflow(nodes))


async def test_workflow_call_keeps_accepting_callee_keywords():
    """workflow_call's extra kwargs are the callee's parameters, not typos."""
    helper = {
        "name": "greet",
        "interface": {"inputs": ["name"], "outputs": []},
        "variables": {"name": ""},
        "nodes": {
            "start": {"opcode": "workflow_start", "next": "p"},
            "p": {"opcode": "io_print", "args": [{"variable": "name"}]},
        },
    }
    nodes = {
        "start": {"opcode": "workflow_start", "next": "c"},
        "c": {
            "opcode": "workflow_call",
            "kwargs": {"workflow": {"literal": "greet"}, "name": {"literal": "Ana"}},
        },
    }
    assert await run(workflow(nodes, extra=[helper])) == "Ana"


# ============= Workflow argument binding =============

GREET = {
    "name": "greet",
    "interface": {"inputs": ["name"], "outputs": []},
    "variables": {"name": ""},
    "nodes": {
        "start": {"opcode": "workflow_start", "next": "p"},
        "p": {"opcode": "io_print", "args": [{"variable": "name"}]},
    },
}


async def test_workflow_rejects_an_argument_given_twice():
    """The opcode path has this sensor; the workflow path needs its own."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "c"},
        "c": {
            "opcode": "workflow_call",
            "args": [{"literal": "Ana"}],
            "kwargs": {"workflow": {"literal": "greet"}, "name": {"literal": "Bia"}},
        },
    }
    with pytest.raises(ValueError, match="multiple values for argument"):
        await run(workflow(nodes, extra=[GREET]))


# ============= Load-time validation =============


async def test_opcode_keyword_typo_is_caught_before_execution():
    """A ValueError at call time would be swallowed by the workflow's own catch."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "t"},
        "t": {
            "opcode": "control_try",
            "kwargs": {
                "try": {"branch": "bad"},
                "catch": [{"exception_type": "ValueError", "body": {"branch": "oops"}}],
            },
        },
        "bad": {
            "opcode": "operator_subtract",
            "kwargs": {"left": {"literal": 10}, "rigth": {"literal": 3}},
        },
        "oops": {"opcode": "io_print", "args": [{"literal": "swallowed"}]},
    }
    with pytest.raises(ValueError, match=r"unexpected keyword argument\(s\) rigth"):
        await run(workflow(nodes))


async def test_workflow_keyword_typo_is_caught_before_execution():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "c"},
        "c": {
            "opcode": "workflow_call",
            "kwargs": {"workflow": {"literal": "greet"}, "nome": {"literal": "Ana"}},
        },
    }
    program = Parser().parse_dict(workflow(nodes, extra=[GREET]))
    with pytest.raises(ValueError, match=r"unexpected keyword argument\(s\) nome"):
        Engine(program)


async def test_unregistered_opcodes_are_left_to_the_runtime():
    """An engine with a custom registry must still load a program it cannot check."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {"opcode": "not_a_real_opcode", "kwargs": {"whatever": {"literal": 1}}},
    }
    Engine(Parser().parse_dict(workflow(nodes)))


async def test_legacy_return_ignores_a_bare_value_beside_a_numbered_one():
    """The legacy reader read VALUE1 and ignored VALUE; that must not change."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "r"},
        "r": {
            "opcode": "workflow_return",
            "inputs": {"VALUE1": {"literal": "a"}, "VALUE": {"literal": "b"}},
        },
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        program = Parser().parse_dict(workflow(nodes))
    values = program.main.body.stmts[0].values
    assert [v.value for v in values] == ["a"]


# ============= Positional args on constructs =============


@pytest.mark.parametrize(
    "opcode,kwargs",
    [
        ("control_if", {"then": {"branch": "b"}}),
        ("control_while", {"body": {"branch": "b"}}),
        ("control_try", {"try": {"branch": "b"}}),
        ("data_set_variable_to", {"variable": {"literal": "x"}}),
    ],
)
async def test_constructs_without_a_positional_family_reject_args(opcode, kwargs):
    """Writing 'args' on a construct is the natural mistake when migrating by hand."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {"opcode": opcode, "args": [{"literal": True}], "kwargs": kwargs},
        "b": {"opcode": "io_print", "args": [{"literal": "x"}]},
    }
    with pytest.raises(ValueError, match="takes no positional arguments"):
        Parser().parse_dict(workflow(nodes))


async def test_fork_and_return_still_take_args():
    nodes = {
        "start": {"opcode": "workflow_start", "next": "f"},
        "f": {"opcode": "control_fork", "args": [{"branch": "a"}, {"branch": "b"}]},
        "a": {"opcode": "io_print", "args": [{"literal": "A"}]},
        "b": {"opcode": "io_print", "args": [{"literal": "B"}]},
    }
    assert await run(workflow(nodes)) == "AB"


# ============= Load-time validation, remaining shapes =============


def _in_try(bad_node: dict, extra=None) -> dict:
    """Put a node inside try/catch ValueError, where a runtime error is swallowed."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "t"},
        "t": {
            "opcode": "control_try",
            "kwargs": {
                "try": {"branch": "bad"},
                "catch": [{"exception_type": "ValueError", "body": {"branch": "h"}}],
            },
        },
        "bad": bad_node,
        "h": {"opcode": "io_print", "args": [{"literal": "swallowed"}]},
    }
    return workflow(nodes, extra=extra)


@pytest.mark.parametrize(
    "node,message",
    [
        (
            {"opcode": "io_print", "kwargs": {"values": {"literal": "x"}}},
            "variadic",
        ),
        (
            {
                "opcode": "operator_subtract",
                "args": [{"literal": 1}],
                "kwargs": {"left": {"literal": 2}},
            },
            "multiple values",
        ),
        (
            {"opcode": "operator_subtract", "args": [{"literal": 1}]},
            "requires 2 arguments",
        ),
        (
            {"opcode": "workflow_call", "kwargs": {"workflow": {"literal": "nope"}}},
            "unknown workflow",
        ),
    ],
)
async def test_binding_errors_are_caught_before_the_catch_can_swallow_them(
    node, message
):
    with pytest.raises(ValueError, match=message):
        Engine(Parser().parse_dict(_in_try(node)))


async def test_a_typo_in_a_reporter_is_caught_too():
    """The OpStmt case had a sensor; the Opcode (reporter) case did not."""
    node = {
        "opcode": "io_print",
        "args": [{"node": "sub"}],
    }
    program = workflow(
        {
            "start": {"opcode": "workflow_start", "next": "p"},
            "p": node,
            "sub": {
                "opcode": "operator_subtract",
                "isReporter": True,
                "kwargs": {"left": {"literal": 10}, "rigth": {"literal": 3}},
            },
        }
    )
    with pytest.raises(ValueError, match=r"keyword argument\(s\) rigth"):
        Engine(Parser().parse_dict(program))


async def test_a_typo_nested_inside_a_kwargs_value_is_caught():
    """walk() must descend into dict-valued fields, not just lists."""
    program = workflow(
        {
            "start": {"opcode": "workflow_start", "next": "a"},
            "a": {
                "opcode": "data_set_variable_to",
                "kwargs": {"variable": {"literal": "x"}, "value": {"node": "sub"}},
            },
            "sub": {
                "opcode": "operator_subtract",
                "isReporter": True,
                "kwargs": {"left": {"literal": 10}, "rigth": {"literal": 3}},
            },
        }
    )
    with pytest.raises(ValueError, match=r"keyword argument\(s\) rigth"):
        Engine(Parser().parse_dict(program))


async def test_a_rejected_program_is_not_left_on_the_engine():
    good = workflow(
        {
            "start": {"opcode": "workflow_start", "next": "p"},
            "p": {"opcode": "io_print", "args": [{"literal": "ok"}]},
        }
    )
    bad = workflow(
        {
            "start": {"opcode": "workflow_start", "next": "s"},
            "s": {
                "opcode": "operator_subtract",
                "kwargs": {"left": {"literal": 1}, "rigth": {"literal": 2}},
            },
        }
    )
    engine = Engine(Parser().parse_dict(good))
    loaded = engine.program
    with pytest.raises(ValueError):
        engine.load_program(Parser().parse_dict(bad))
    assert engine.program is loaded


# ============= Slot table sensors =============


async def test_data_get_variable_is_accepted_as_a_reporter():
    """A positive case: the override slot must not reject every valid reporter."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "p"},
        "p": {"opcode": "io_print", "args": [{"node": "get"}]},
        "get": {
            "opcode": "data_get_variable",
            "isReporter": True,
            "kwargs": {"variable": {"literal": "x"}},
        },
    }
    assert await run(workflow(nodes, variables={"x": "value"})) == "value"


@pytest.mark.parametrize(
    "opcode,kwargs,unknown",
    [
        ("try_catch", {"try": {"branch": "b"}, "FINALLY": {"branch": "b"}}, "FINALLY"),
        ("return", {"VALUE": {"literal": 1}}, "VALUE"),
        ("assign", {"variable": {"literal": "x"}, "VALUE": {"literal": 1}}, "VALUE"),
    ],
)
async def test_alias_opcodes_share_the_slot_table(opcode, kwargs, unknown):
    """Dropping an alias would send FINALLY/VALUE back to being silently ignored."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "n"},
        "n": {"opcode": opcode, "kwargs": kwargs},
        "b": {"opcode": "io_print", "args": [{"literal": "x"}]},
    }
    with pytest.raises(ValueError, match=f"unknown slot\\(s\\) {unknown}"):
        Parser().parse_dict(workflow(nodes))


async def test_fork_rejects_args_named_as_a_slot():
    """'args' is a positional family, never a named slot."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "f"},
        "f": {"opcode": "control_fork", "kwargs": {"args": [{"branch": "b"}]}},
        "b": {"opcode": "io_print", "args": [{"literal": "x"}]},
    }
    with pytest.raises(ValueError, match=r"unknown slot\(s\) args"):
        Parser().parse_dict(workflow(nodes))
