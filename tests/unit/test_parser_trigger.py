"""Tests for parser trigger extraction."""

from lexflow import Parser


WORKFLOW_WITH_TRIGGER = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "http", "method": "POST", "path": "/webhooks/test"},
            "interface": {"inputs": ["body"], "outputs": []},
            "variables": {"body": {}},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": "print_body",
                    "inputs": {},
                },
                "print_body": {
                    "opcode": "io_print",
                    "next": None,
                    "inputs": {"STRING": {"variable": "body"}},
                },
            },
        }
    ]
}

WORKFLOW_NO_TRIGGER = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": None,
                    "inputs": {},
                },
            },
        }
    ]
}

WORKFLOW_NON_HTTP_TRIGGER = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "cron", "schedule": "0 * * * *"},
            "interface": {"inputs": [], "outputs": []},
            "variables": {},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": None,
                    "inputs": {},
                },
            },
        }
    ]
}


def test_parser_extracts_trigger():
    """Parser stores trigger dict as-is."""
    parser = Parser()
    program = parser.parse_dict(WORKFLOW_WITH_TRIGGER)
    assert program.main.trigger is not None
    assert program.main.trigger["type"] == "http"
    assert program.main.trigger["method"] == "POST"
    assert program.main.trigger["path"] == "/webhooks/test"


def test_parser_no_trigger():
    parser = Parser()
    program = parser.parse_dict(WORKFLOW_NO_TRIGGER)
    assert program.main.trigger is None


def test_parser_preserves_non_http_trigger():
    """Non-HTTP triggers are preserved as raw dicts for future consumers."""
    parser = Parser()
    program = parser.parse_dict(WORKFLOW_NON_HTTP_TRIGGER)
    assert program.main.trigger is not None
    assert program.main.trigger["type"] == "cron"
