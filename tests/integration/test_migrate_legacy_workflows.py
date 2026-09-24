"""Migrating a legacy workflow must not change what it means.

The fixtures are real workflows as they were written before the migration:
control flow, fork, spawn, timeout, try/catch, workflow calls and reporters,
all in the legacy 'inputs' form.
"""

import inspect
import json
import re
from pathlib import Path

import pytest
import yaml

from lexflow import Parser, default_registry
from lexflow.visualizer import WorkflowVisualizer
from lexflow_cli.migrate import collect_files, migrate_text

LEGACY = Path(__file__).resolve().parents[1] / "fixtures" / "legacy_workflows"


def load(text: str, suffix: str) -> dict:
    return json.loads(text) if suffix == ".json" else yaml.safe_load(text)


def canonical(value):
    """Rewrite every opcode call as parameter name -> argument.

    Positional and keyword arguments that bind to the same parameters compare
    equal, so a migration that only changes how arguments are written shows up
    as no change at all.
    """
    if isinstance(value, list):
        return [canonical(v) for v in value]
    if not isinstance(value, dict):
        return value

    result = {k: canonical(v) for k, v in value.items()}
    if value.get("type") in ("Opcode", "OpStmt"):
        signature = default_registry.signatures.get(value["name"])
        if signature:
            parameters = list(signature.parameters.values())
            # A variadic opcode takes no keywords, so its arguments stay
            # positional here too: [x] and {values: x} are not the same call
            variadic = any(
                p.kind is inspect.Parameter.VAR_POSITIONAL for p in parameters
            )
            names = [] if variadic else [p.name for p in parameters]
            bound = {
                names[i] if i < len(names) else i: arg
                for i, arg in enumerate(result.pop("args", []))
            }
            bound.update(result.pop("kwargs", {}))
            result["arguments"] = bound
    return result


def nodes_drawn(rendering: str) -> list[str]:
    """Every 'opcode (node_id)' the visualizer drew, in order."""
    return re.findall(r"\b(\w+ \(\w+\))", rendering)


@pytest.mark.parametrize("use_names", [False, True], ids=["positional", "names"])
@pytest.mark.parametrize(
    "path", collect_files([str(LEGACY)]), ids=lambda p: str(p.name)
)
def test_migrated_workflow_parses_to_the_same_ast(path, use_names):
    text = path.read_text()
    migrated, migrated_nodes, _ = migrate_text(text, path.suffix, use_names)
    if not migrated_nodes:
        pytest.skip("nothing to migrate")

    before = load(text, path.suffix)
    after = load(migrated, path.suffix)

    assert len(before["workflows"]) == len(after["workflows"])

    compared = 0
    for old_wf, new_wf in zip(before["workflows"], after["workflows"]):
        try:
            expected = Parser()._parse_workflow(old_wf).model_dump()
        except Exception:
            continue  # workflow does not parse before migration either
        assert canonical(Parser()._parse_workflow(new_wf).model_dump()) == canonical(
            expected
        )
        compared += 1

    # Otherwise a fixture whose workflows all fail to parse passes vacuously
    assert compared, "no workflow in this fixture could be compared"


@pytest.mark.parametrize(
    "path", collect_files([str(LEGACY)]), ids=lambda p: str(p.name)
)
def test_visualizer_draws_the_same_tree_before_and_after_migration(path):
    """The visualizer reads nodes through NodeArgs, so both forms must render alike.

    Argument labels change (VALUES becomes 1), the structure must not.
    """
    text = path.read_text()
    migrated, migrated_nodes, _ = migrate_text(text, path.suffix)
    if not migrated_nodes:
        pytest.skip("nothing to migrate")

    visualizer = WorkflowVisualizer()
    before = visualizer.visualize_program(load(text, path.suffix))
    after = visualizer.visualize_program(load(migrated, path.suffix))

    assert nodes_drawn(before) == nodes_drawn(after)
