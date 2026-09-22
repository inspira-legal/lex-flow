"""Tests for the 'lexflow migrate' transformation."""

import yaml

from lexflow_cli.migrate import find_misbindings, migrate_text


def migrate_yaml(text: str) -> dict:
    migrated, _, _ = migrate_text(text, ".yaml")
    return yaml.safe_load(migrated)


def node(text: str, node_id: str) -> dict:
    return migrate_yaml(text)["workflows"][0]["nodes"][node_id]


HEADER = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
"""


def test_opcode_inputs_become_positional_args():
    source = (
        HEADER
        + """      show:
        opcode: io_print
        inputs:
          STRING:
            literal: "hi"
"""
    )
    assert node(source, "show") == {
        "opcode": "io_print",
        "args": [{"literal": "hi"}],
    }


def test_construct_slots_become_lowercase_kwargs():
    source = (
        HEADER
        + """      loop:
        opcode: control_for
        inputs:
          VAR:
            literal: i
          START:
            literal: 0
          END:
            literal: 3
          BODY:
            branch: show
"""
    )
    assert node(source, "loop")["kwargs"] == {
        "var": {"literal": "i"},
        "start": {"literal": 0},
        "end": {"literal": 3},
        "body": {"branch": "show"},
    }


def test_fork_branches_become_args():
    source = (
        HEADER
        + """      fork:
        opcode: control_fork
        inputs:
          BRANCH1:
            branch: a
          BRANCH2:
            branch: b
"""
    )
    assert node(source, "fork") == {
        "opcode": "control_fork",
        "args": [{"branch": "a"}, {"branch": "b"}],
    }


def test_try_catches_become_a_catch_list():
    source = (
        HEADER
        + """      guard:
        opcode: control_try
        inputs:
          TRY:
            branch: risky
          CATCH1:
            exception_type: ValueError
            var: err
            body:
              branch: handler
          FINALLY:
            branch: cleanup
"""
    )
    assert node(source, "guard")["kwargs"] == {
        "try": {"branch": "risky"},
        "catch": [
            {
                "exception_type": "ValueError",
                "var": "err",
                "body": {"branch": "handler"},
            }
        ],
        "finally": {"branch": "cleanup"},
    }


def test_workflow_call_splits_name_from_arguments():
    source = (
        HEADER
        + """      call:
        opcode: workflow_call
        inputs:
          WORKFLOW:
            literal: greet
          ARG1:
            literal: Ana
          ARG2:
            literal: 30
"""
    )
    assert node(source, "call") == {
        "opcode": "workflow_call",
        "kwargs": {"workflow": {"literal": "greet"}},
        "args": [{"literal": "Ana"}, {"literal": 30}],
    }


def test_return_values_become_args():
    source = (
        HEADER
        + """      done:
        opcode: workflow_return
        inputs:
          VALUE1:
            variable: a
          VALUE2:
            variable: b
"""
    )
    assert node(source, "done")["args"] == [{"variable": "a"}, {"variable": "b"}]


def test_empty_inputs_are_dropped():
    source = (
        HEADER
        + """      start:
        opcode: workflow_start
        next: show
        inputs: {}
"""
    )
    assert node(source, "start") == {"opcode": "workflow_start", "next": "show"}


def test_already_migrated_nodes_are_left_alone():
    source = (
        HEADER
        + """      show:
        opcode: io_print
        args:
          - literal: "hi"
"""
    )
    migrated, count, _ = migrate_text(source, ".yaml")
    assert count == 0
    assert migrated == source


def test_comments_are_preserved():
    source = (
        HEADER
        + """      # greet the user
      show:
        opcode: io_print
        inputs:
          STRING:
            literal: "hi"
"""
    )
    migrated, _, _ = migrate_text(source, ".yaml")
    assert "# greet the user" in migrated


def test_misbinding_detector_flags_names_out_of_signature_order():
    data = yaml.safe_load(
        HEADER
        + """      search:
        opcode: web_search
        isReporter: true
        inputs:
          query:
            variable: query
          max_results:
            literal: 5
"""
    )
    warnings = find_misbindings(data)
    assert len(warnings) == 1
    assert "max_results -> client" in warnings[0]


def test_misbinding_detector_stays_quiet_when_order_matches():
    data = yaml.safe_load(
        HEADER
        + """      sum:
        opcode: operator_add
        isReporter: true
        inputs:
          left:
            literal: 1
          right:
            literal: 2
"""
    )
    assert find_misbindings(data) == []


def test_json_workflows_are_migrated():
    source = (
        '{"workflows": [{"name": "main", "nodes": '
        '{"show": {"opcode": "io_print", "inputs": {"STRING": {"literal": "hi"}}}}}]}'
    )
    migrated, count, _ = migrate_text(source, ".json")
    assert count == 1
    import json

    node_data = json.loads(migrated)["workflows"][0]["nodes"]["show"]
    assert node_data == {"opcode": "io_print", "args": [{"literal": "hi"}]}


def test_non_workflow_documents_are_left_alone():
    source = "name: not-a-workflow\nvalue: 3\n"
    migrated, count, warnings = migrate_text(source, ".yaml")
    assert (migrated, count, warnings) == (source, 0, [])


def test_names_mode_uses_kwargs_when_names_match_the_signature():
    source = (
        HEADER
        + """      sum:
        opcode: operator_add
        isReporter: true
        inputs:
          left:
            literal: 1
          right:
            literal: 2
"""
    )
    migrated, _, _ = migrate_text(source, ".yaml", use_names=True)
    node_data = yaml.safe_load(migrated)["workflows"][0]["nodes"]["sum"]
    assert node_data["kwargs"] == {"left": {"literal": 1}, "right": {"literal": 2}}


def test_names_mode_keeps_positional_args_when_names_would_rebind():
    source = (
        HEADER
        + """      search:
        opcode: web_search
        isReporter: true
        inputs:
          query:
            variable: query
          max_results:
            literal: 5
"""
    )
    migrated, _, _ = migrate_text(source, ".yaml", use_names=True)
    node_data = yaml.safe_load(migrated)["workflows"][0]["nodes"]["search"]
    assert node_data["args"] == [{"variable": "query"}, {"literal": 5}]
    assert "kwargs" not in node_data


def test_names_mode_keeps_positional_args_for_decorative_names():
    source = (
        HEADER
        + """      show:
        opcode: string_upper
        isReporter: true
        inputs:
          STRING:
            literal: "hi"
"""
    )
    migrated, _, _ = migrate_text(source, ".yaml", use_names=True)
    node_data = yaml.safe_load(migrated)["workflows"][0]["nodes"]["show"]
    assert node_data["args"] == [{"literal": "hi"}]
