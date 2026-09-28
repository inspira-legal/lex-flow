"""Tests for the 'lexflow migrate' command itself.

migrate_text is covered in test_migrate.py; this covers the command around it:
file collection, reporting, --diff, --write and the all-or-nothing guarantee.
"""

import json
import os
import shutil

import pytest
import yaml

from lexflow_cli.main import create_parser, handle_migrate_command

LEGACY = """\
workflows:
  - name: main
    interface: {inputs: [], outputs: []}
    variables: {}
    nodes:
      start: {opcode: workflow_start, next: show}
      show:
        opcode: io_print
        inputs:
          VALUES: {literal: "hi"}
"""

MIGRATED = """\
workflows:
  - name: main
    interface: {inputs: [], outputs: []}
    variables: {}
    nodes:
      start: {opcode: workflow_start, next: show}
      show:
        opcode: io_print
        args:
          - {literal: "hi"}
"""

BROKEN = "workflows: [ {oops\n  broken yaml\n"


def run_migrate(*argv: str) -> int:
    args = create_parser().parse_args(["migrate", *argv])
    return handle_migrate_command(args)


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "a.yaml").write_text(LEGACY)
    return tmp_path


def test_reports_without_writing_by_default(workspace, capsys):
    assert run_migrate(str(workspace)) == 0
    assert (workspace / "a.yaml").read_text() == LEGACY
    out = capsys.readouterr().out
    assert "1 nodes" in out
    assert "--write" in out


def test_write_applies_the_rewrite(workspace):
    assert run_migrate(str(workspace), "--write") == 0
    nodes = yaml.safe_load((workspace / "a.yaml").read_text())["workflows"][0]["nodes"]
    assert nodes["show"] == {"opcode": "io_print", "args": [{"literal": "hi"}]}


def test_diff_shows_the_change_without_writing(workspace, capsys):
    assert run_migrate(str(workspace), "--diff") == 0
    out = capsys.readouterr().out
    assert "-        inputs:" in out
    assert "+        args:" in out
    assert (workspace / "a.yaml").read_text() == LEGACY


def test_already_migrated_files_report_nothing_to_do(tmp_path, capsys):
    (tmp_path / "a.yaml").write_text(MIGRATED)
    assert run_migrate(str(tmp_path)) == 0
    assert "Nothing to migrate" in capsys.readouterr().out


def test_missing_path_is_reported(tmp_path, capsys):
    assert run_migrate(str(tmp_path / "nope.yaml")) == 1
    assert "No such file or directory" in capsys.readouterr().err


def test_a_broken_file_fails_the_run(tmp_path, capsys):
    (tmp_path / "b.yaml").write_text(BROKEN)
    assert run_migrate(str(tmp_path), "--write") == 1
    assert "1 of 1 files failed" in capsys.readouterr().err


def test_a_broken_file_leaves_every_other_file_untouched(workspace, capsys):
    """--write is all-or-nothing: one bad file must not leave a half-migrated tree."""
    (workspace / "b.yaml").write_text(BROKEN)
    assert run_migrate(str(workspace), "--write") == 1
    assert (workspace / "a.yaml").read_text() == LEGACY
    assert "nothing was written" in capsys.readouterr().err


def test_misbindings_are_reported(tmp_path, capsys):
    (tmp_path / "a.yaml").write_text(
        """\
workflows:
  - name: main
    interface: {inputs: [], outputs: []}
    variables: {}
    nodes:
      start: {opcode: workflow_start, next: op}
      op:
        opcode: operator_subtract
        inputs:
          right: {literal: 10}
          left: {literal: 3}
"""
    )
    assert run_migrate(str(tmp_path)) == 0
    out = capsys.readouterr().out
    assert "right -> left" in out


def test_dropped_keys_are_reported(tmp_path, capsys):
    """A key the legacy reader ignored is dropped, and the user is told."""
    (tmp_path / "a.yaml").write_text(
        """\
workflows:
  - name: main
    interface: {inputs: [], outputs: []}
    variables: {}
    nodes:
      start: {opcode: workflow_start, next: c}
      c:
        opcode: workflow_call
        inputs:
          WORKFLOW: {literal: helper}
          ARG1: {literal: "x"}
          NOTE: {literal: "ignored"}
"""
    )
    assert run_migrate(str(tmp_path), "--write") == 0
    out = capsys.readouterr().out
    assert "dropped NOTE" in out
    node = yaml.safe_load((tmp_path / "a.yaml").read_text())["workflows"][0]["nodes"]
    assert "note" not in node["c"].get("kwargs", {})


def test_json_workflows_round_trip(tmp_path):
    (tmp_path / "a.json").write_text(
        json.dumps(
            {
                "workflows": [
                    {
                        "name": "main",
                        "interface": {"inputs": [], "outputs": []},
                        "variables": {},
                        "nodes": {
                            "start": {"opcode": "workflow_start", "next": "show"},
                            "show": {
                                "opcode": "io_print",
                                "inputs": {"V": {"literal": "Petição"}},
                            },
                        },
                    }
                ]
            },
            ensure_ascii=False,
        )
    )
    assert run_migrate(str(tmp_path), "--write") == 0
    text = (tmp_path / "a.json").read_text()
    # Non-ASCII stays readable instead of being escaped
    assert "Petição" in text
    assert json.loads(text)["workflows"][0]["nodes"]["show"]["args"] == [
        {"literal": "Petição"}
    ]


def test_names_mode_binds_by_name_when_the_order_matches(tmp_path):
    (tmp_path / "a.yaml").write_text(
        """\
workflows:
  - name: main
    interface: {inputs: [], outputs: []}
    variables: {}
    nodes:
      start: {opcode: workflow_start, next: op}
      op:
        opcode: operator_subtract
        inputs:
          left: {literal: 10}
          right: {literal: 3}
"""
    )
    assert run_migrate(str(tmp_path), "--names", "--write") == 0
    node = yaml.safe_load((tmp_path / "a.yaml").read_text())["workflows"][0]["nodes"]
    assert node["op"]["kwargs"] == {"left": {"literal": 10}, "right": {"literal": 3}}


def test_a_write_failure_rolls_back_every_other_file(workspace, capsys):
    """--write is all-or-nothing for write errors too, not just migration errors."""
    locked = workspace / "locked"
    locked.mkdir()
    (locked / "b.yaml").write_text(LEGACY)
    locked.chmod(0o555)
    try:
        assert run_migrate(str(workspace), "--write") == 1
        assert (workspace / "a.yaml").read_text() == LEGACY
        assert "nothing was changed" in capsys.readouterr().err
    finally:
        locked.chmod(0o755)


def temporaries(directory):
    """The migration's temporaries are hidden, so a bare '*' glob misses them."""
    return list(directory.glob(".*.tmp")) + list(directory.glob("*.tmp"))


def test_no_temporary_files_are_left_behind(workspace):
    assert run_migrate(str(workspace), "--write") == 0
    assert temporaries(workspace) == []


def test_an_interrupt_mid_write_leaves_no_temporaries(workspace, monkeypatch):
    """Ctrl-C is not an OSError, so only the cleanup on the way out catches it."""
    (workspace / "b.yaml").write_text(LEGACY)
    real = shutil.copymode
    seen = []

    def interrupt_on_the_second(*args, **kwargs):
        seen.append(args)
        if len(seen) == 2:
            raise KeyboardInterrupt
        return real(*args, **kwargs)

    monkeypatch.setattr("lexflow_cli.main.shutil.copymode", interrupt_on_the_second)
    with pytest.raises(KeyboardInterrupt):
        run_migrate(str(workspace), "--write")
    assert temporaries(workspace) == []


def test_a_binary_file_fails_that_file_only(workspace, capsys):
    (workspace / "blob.json").write_bytes(b"\xff\xfe\x00binary")
    assert run_migrate(str(workspace), "--write") == 1
    assert (workspace / "a.yaml").read_text() == LEGACY
    assert "not a text file" in capsys.readouterr().err


def test_a_duplicate_key_gets_its_own_message(workspace, capsys):
    (workspace / "dup.yaml").write_text(
        "workflows:\n  - name: main\n    nodes: {}\n    nodes: {}\n"
    )
    assert run_migrate(str(workspace)) == 1
    err = capsys.readouterr().err
    assert "duplicate key" in err
    assert "allow_duplicate_keys" not in err


@pytest.mark.parametrize("mode", [0o600, 0o640])
def test_the_file_mode_survives_the_rewrite(workspace, mode):
    """A file its owner locked down must not come back more readable.

    0o640 is the case that senses the copymode: mkstemp already creates at 0o600.
    """
    private = workspace / "a.yaml"
    private.chmod(mode)
    assert run_migrate(str(workspace), "--write") == 0
    assert private.stat().st_mode & 0o777 == mode


def test_a_symlink_is_migrated_through_not_replaced(workspace, tmp_path):
    target = tmp_path / "target.yaml"
    target.write_text(LEGACY)
    link = workspace / "link.yaml"
    link.symlink_to(target)

    assert run_migrate(str(workspace), "--write") == 0
    assert link.is_symlink()
    assert "args:" in target.read_text()


def test_a_hard_linked_file_is_refused(workspace, capsys):
    other = workspace / "other.yaml"
    os.link(workspace / "a.yaml", other)
    assert run_migrate(str(workspace), "--write") == 1
    assert (workspace / "a.yaml").read_text() == LEGACY
    assert "hard links" in capsys.readouterr().err


def test_an_unwritable_file_is_refused_cleanly(workspace, capsys):
    (workspace / "a.yaml").chmod(0o444)
    try:
        assert run_migrate(str(workspace), "--write") == 1
        assert "not writable" in capsys.readouterr().err
        assert (workspace / "a.yaml").read_text() == LEGACY
        # The protection the user put on the file is still there
        assert (workspace / "a.yaml").stat().st_mode & 0o777 == 0o444
    finally:
        (workspace / "a.yaml").chmod(0o644)
