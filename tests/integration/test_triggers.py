"""Integration tests for HTTP trigger routes."""

import tempfile

import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

from lexflow_web.triggers import (
    HttpTrigger,
    build_trigger_router,
    get_triggered_workflows,
    _parse_http_trigger,
)
from lexflow import Parser


# ============ Helpers ============


def _write_workflow(workflow_dict: dict) -> str:
    """Write workflow dict to temp YAML file, return path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(workflow_dict, f)
        return f.name


def _create_app_with_trigger(workflow_dict: dict) -> FastAPI:
    """Create a minimal FastAPI app with trigger routes from a workflow dict."""
    app = FastAPI()
    router = build_trigger_router([_write_workflow(workflow_dict)])
    app.include_router(router)
    return app


# ============ Workflow fixtures ============

POST_TRIGGER_WORKFLOW = {
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

GET_TRIGGER_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "http", "method": "GET", "path": "/health"},
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

HEADERS_TRIGGER_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "http", "method": "POST", "path": "/with-headers"},
            "interface": {"inputs": ["body", "headers"], "outputs": []},
            "variables": {"body": {}, "headers": {}},
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

QUERY_PARAMS_TRIGGER_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "http", "method": "GET", "path": "/with-query"},
            "interface": {"inputs": ["query_params"], "outputs": []},
            "variables": {"query_params": {}},
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

NO_TRIGGER_WORKFLOW = {
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

FAILING_TRIGGER_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "trigger": {"type": "http", "method": "POST", "path": "/will-fail"},
            "interface": {"inputs": ["body"], "outputs": []},
            "variables": {"body": {}},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": "fail_node",
                    "inputs": {},
                },
                "fail_node": {
                    "opcode": "control_throw",
                    "next": None,
                    "inputs": {"VALUE": {"literal": "intentional error"}},
                },
            },
        }
    ]
}


# ============ Unit tests for trigger parsing ============


def test_parse_http_trigger():
    trigger = _parse_http_trigger({"type": "http", "method": "post", "path": "/test"})
    assert trigger == HttpTrigger(method="POST", path="/test")


def test_parse_http_trigger_default_method():
    trigger = _parse_http_trigger({"type": "http", "path": "/test"})
    assert trigger.method == "POST"


def test_parse_http_trigger_non_http():
    assert _parse_http_trigger({"type": "cron"}) is None


def test_parse_http_trigger_none():
    assert _parse_http_trigger(None) is None


def test_get_triggered_workflows_filters():
    parser = Parser()
    program = parser.parse_dict(POST_TRIGGER_WORKFLOW)
    triggered = get_triggered_workflows(program)
    assert len(triggered) == 1
    wf, trigger = triggered[0]
    assert wf.name == "main"
    assert trigger.path == "/webhooks/test"


def test_get_triggered_workflows_empty():
    parser = Parser()
    program = parser.parse_dict(NO_TRIGGER_WORKFLOW)
    assert get_triggered_workflows(program) == []


# ============ Route integration tests ============


def test_trigger_route_returns_accepted():
    """POST to trigger path returns 200 with accepted status."""
    app = _create_app_with_trigger(POST_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.post(
        "/webhooks/test",
        json={"event": "test", "data": {"id": 123}},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_trigger_route_wrong_path():
    app = _create_app_with_trigger(POST_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.post("/webhooks/nonexistent", json={})
    assert response.status_code == 404


def test_trigger_route_wrong_method():
    """GET to POST-only trigger returns 405."""
    app = _create_app_with_trigger(POST_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.get("/webhooks/test")
    assert response.status_code == 405


def test_trigger_get_method():
    app = _create_app_with_trigger(GET_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_no_trigger_no_routes():
    app = _create_app_with_trigger(NO_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.post("/webhooks/test", json={})
    assert response.status_code == 404


def test_trigger_with_headers():
    """Workflow declaring headers input receives request headers."""
    app = _create_app_with_trigger(HEADERS_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.post(
        "/with-headers",
        json={"data": 1},
        headers={"X-Custom": "test-value"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_trigger_with_query_params():
    """Workflow declaring query_params input receives query string."""
    app = _create_app_with_trigger(QUERY_PARAMS_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.get("/with-query?foo=bar&baz=42")
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_trigger_failing_workflow_still_returns_accepted():
    """A workflow that throws still returns 200 (fire-and-forget)."""
    app = _create_app_with_trigger(FAILING_TRIGGER_WORKFLOW)
    client = TestClient(app)
    response = client.post("/will-fail", json={"data": 1})
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


# ============ create_app integration ============


def test_create_app_with_workflow_paths():
    """create_app(workflow_paths=...) registers trigger routes."""
    from lexflow_web.app import create_app

    tmp_path = _write_workflow(POST_TRIGGER_WORKFLOW)
    app = create_app(workflow_paths=[tmp_path])
    client = TestClient(app)
    response = client.post("/webhooks/test", json={"test": True})
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_create_app_without_workflows():
    """create_app() without workflows still works (no trigger routes)."""
    from lexflow_web.app import create_app

    app = create_app()
    client = TestClient(app)
    response = client.post("/webhooks/test", json={})
    assert response.status_code == 404
