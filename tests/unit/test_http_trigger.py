"""Tests for workflow trigger field in AST."""

from lexflow.ast import Workflow, Program, Block


def test_workflow_trigger_optional():
    """Workflow trigger should be None by default."""
    wf = Workflow(name="main", params=[], body=Block(stmts=[]))
    assert wf.trigger is None


def test_workflow_with_trigger_dict():
    """Workflow trigger stores raw dict from YAML."""
    trigger = {"type": "http", "method": "POST", "path": "/webhooks/test"}
    wf = Workflow(name="main", params=["body"], body=Block(stmts=[]), trigger=trigger)
    assert wf.trigger is not None
    assert wf.trigger["path"] == "/webhooks/test"


def test_workflow_trigger_preserved_in_program():
    """Trigger dict survives through Program construction."""
    trigger = {"type": "http", "path": "/hooks/main"}
    main = Workflow(name="main", params=["body"], body=Block(stmts=[]), trigger=trigger)
    program = Program(main=main)
    assert program.main.trigger == trigger
