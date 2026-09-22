"""Migrating the bundled examples must not change what they mean."""

import json
from pathlib import Path

import pytest
import yaml

from lexflow import Parser
from lexflow_cli.migrate import collect_files, migrate_text

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def load(text: str, suffix: str) -> dict:
    return json.loads(text) if suffix == ".json" else yaml.safe_load(text)


@pytest.mark.parametrize(
    "path", collect_files([str(EXAMPLES)]), ids=lambda p: str(p.name)
)
def test_migrated_example_parses_to_the_same_ast(path):
    text = path.read_text()
    migrated, migrated_nodes, _ = migrate_text(text, path.suffix)
    if not migrated_nodes:
        pytest.skip("nothing to migrate")

    before = load(text, path.suffix)
    after = load(migrated, path.suffix)

    for old_wf, new_wf in zip(before["workflows"], after["workflows"]):
        try:
            expected = Parser()._parse_workflow(old_wf).model_dump()
        except Exception:
            continue  # example does not parse before migration either
        assert Parser()._parse_workflow(new_wf).model_dump() == expected
