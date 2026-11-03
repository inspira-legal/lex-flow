"""Tests for the workflow visualizer.

The visualizer reads nodes through NodeArgs, so it has to render the legacy
'inputs' form and the 'args'/'kwargs' form the same way.
"""

import pytest

from lexflow.visualizer import WorkflowVisualizer, _labelled_arguments
from lexflow.parser import NodeArgs


def render(nodes: dict) -> str:
    workflow = {
        "name": "main",
        "interface": {"inputs": [], "outputs": []},
        "variables": {},
        "nodes": nodes,
    }
    return WorkflowVisualizer().visualize_workflow(workflow)


class TestLabelledArguments:
    def test_positional_arguments_are_numbered(self):
        args = NodeArgs.from_node({"args": [{"literal": "a"}, {"literal": "b"}]})
        assert _labelled_arguments(args) == [
            ("1", {"literal": "a"}),
            ("2", {"literal": "b"}),
        ]

    def test_keyword_arguments_keep_their_name(self):
        args = NodeArgs.from_node({"kwargs": {"left": {"literal": 1}}})
        assert _labelled_arguments(args) == [("left", {"literal": 1})]

    def test_positional_arguments_come_before_keyword_ones(self):
        args = NodeArgs.from_node(
            {"args": [{"literal": 1}], "kwargs": {"right": {"literal": 2}}}
        )
        assert [label for label, _ in _labelled_arguments(args)] == ["1", "right"]

    def test_legacy_inputs_keep_their_original_labels(self):
        args = NodeArgs.from_node({"inputs": {"LEFT": {"literal": 1}}})
        assert _labelled_arguments(args) == [("LEFT", {"literal": 1})]


class TestRendering:
    def test_renders_a_plain_opcode(self):
        out = render(
            {
                "start": {"opcode": "workflow_start", "next": "p"},
                "p": {"opcode": "io_print", "args": [{"literal": "hi"}]},
            }
        )
        assert "io_print" in out
        assert "hi" in out

    def test_renders_an_if_with_both_branches(self):
        out = render(
            {
                "start": {"opcode": "workflow_start", "next": "c"},
                "c": {
                    "opcode": "control_if_else",
                    "kwargs": {
                        "condition": {"literal": True},
                        "then": {"branch": "yes"},
                        "else": {"branch": "no"},
                    },
                },
                "yes": {"opcode": "io_print", "args": [{"literal": "yes"}]},
                "no": {"opcode": "io_print", "args": [{"literal": "no"}]},
            }
        )
        assert "control_if_else" in out
        assert "yes" in out and "no" in out

    def test_renders_a_try_with_catch_and_finally(self):
        out = render(
            {
                "start": {"opcode": "workflow_start", "next": "t"},
                "t": {
                    "opcode": "control_try",
                    "kwargs": {
                        "try": {"branch": "risky"},
                        "catch": [
                            {"exception_type": "ValueError", "body": {"branch": "oops"}}
                        ],
                        "finally": {"branch": "cleanup"},
                    },
                },
                "risky": {"opcode": "io_print", "args": [{"literal": "risky"}]},
                "oops": {"opcode": "io_print", "args": [{"literal": "oops"}]},
                "cleanup": {"opcode": "io_print", "args": [{"literal": "cleanup"}]},
            }
        )
        assert "ValueError" in out
        assert "cleanup" in out

    def test_empty_program_is_reported(self):
        assert WorkflowVisualizer().visualize_program({"workflows": []}) == (
            "No workflows found"
        )

    def test_program_renders_every_workflow(self):
        out = WorkflowVisualizer().visualize_program(
            {
                "workflows": [
                    {
                        "name": "main",
                        "interface": {"inputs": [], "outputs": []},
                        "variables": {},
                        "nodes": {"start": {"opcode": "workflow_start"}},
                    },
                    {
                        "name": "helper",
                        "interface": {"inputs": [], "outputs": []},
                        "variables": {},
                        "nodes": {"start": {"opcode": "workflow_start"}},
                    },
                ]
            }
        )
        assert "main" in out and "helper" in out


LEGACY_AND_MIGRATED = [
    pytest.param(
        {"opcode": "io_print", "inputs": {"VALUES": {"literal": "hi"}}},
        {"opcode": "io_print", "args": [{"literal": "hi"}]},
        id="opcode",
    ),
    pytest.param(
        {
            "opcode": "control_while",
            "inputs": {"CONDITION": {"literal": False}, "BODY": {"branch": "b"}},
        },
        {
            "opcode": "control_while",
            "kwargs": {"condition": {"literal": False}, "body": {"branch": "b"}},
        },
        id="while",
    ),
    pytest.param(
        {
            "opcode": "control_fork",
            "inputs": {"BRANCH1": {"branch": "b"}, "BRANCH2": {"branch": "b"}},
        },
        {"opcode": "control_fork", "args": [{"branch": "b"}, {"branch": "b"}]},
        id="fork",
    ),
]


@pytest.mark.parametrize("legacy,migrated", LEGACY_AND_MIGRATED)
def test_both_syntaxes_render_the_same_shape(legacy, migrated):
    """A migrated node must draw the same tree as the legacy one it came from."""
    body = {"b": {"opcode": "io_print", "args": [{"literal": "x"}]}}
    before = render(
        {"start": {"opcode": "workflow_start", "next": "n"}, "n": legacy, **body}
    )
    after = render(
        {"start": {"opcode": "workflow_start", "next": "n"}, "n": migrated, **body}
    )
    # Labels differ (VALUES vs 1), the structure must not
    assert before.count("\n") == after.count("\n")
    assert legacy["opcode"] in before and legacy["opcode"] in after
