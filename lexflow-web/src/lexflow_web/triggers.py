"""Dynamic HTTP trigger routes from workflow definitions."""

import io
import logging
from dataclasses import dataclass

from fastapi import APIRouter, BackgroundTasks, Request

from lexflow import Engine, Parser, Program, Workflow

logger = logging.getLogger(__name__)


@dataclass
class HttpTrigger:
    """HTTP trigger parsed from workflow trigger dict."""

    method: str
    path: str


def get_triggered_workflows(program: Program) -> list[tuple[Workflow, HttpTrigger]]:
    """Return workflows with HTTP triggers and their parsed trigger config."""
    result = []
    for wf in [program.main, *program.externals.values()]:
        trigger = _parse_http_trigger(wf.trigger)
        if trigger:
            result.append((wf, trigger))
    return result


def _parse_http_trigger(trigger_data: dict | None) -> HttpTrigger | None:
    """Parse a trigger dict into HttpTrigger if it's an HTTP trigger."""
    if not trigger_data or trigger_data.get("type") != "http":
        return None
    return HttpTrigger(
        method=trigger_data.get("method", "POST").upper(),
        path=trigger_data["path"],
    )


async def _run_workflow_background(program: Program, inputs: dict) -> None:
    """Execute a workflow in background."""
    try:
        output_buffer = io.StringIO()
        engine = Engine(program, output=output_buffer)
        await engine.run(inputs=inputs)
        logger.debug("Trigger workflow completed")
        if output_buffer.getvalue():
            logger.debug("Workflow output:\n%s", output_buffer.getvalue())
    except Exception:
        logger.exception("Trigger workflow failed")


async def _build_inputs(request: Request, params: list[str]) -> dict:
    """Extract request data into workflow inputs based on declared params."""
    inputs = {}
    if "body" in params:
        inputs["body"] = await request.json()
    if "headers" in params:
        inputs["headers"] = dict(request.headers)
    if "query_params" in params:
        inputs["query_params"] = dict(request.query_params)
    return inputs


def build_trigger_router(workflow_paths: list[str]) -> APIRouter:
    """Parse workflow files and create routes for HTTP triggers."""
    router = APIRouter()
    parser = Parser()

    for path in workflow_paths:
        program = parser.parse_file(path)

        for wf, trigger in get_triggered_workflows(program):
            _register_trigger_route(router, trigger, program, wf.params)
            logger.info(
                "Registered trigger: %s %s -> workflow '%s'",
                trigger.method,
                trigger.path,
                wf.name,
            )

    return router


def _register_trigger_route(
    router: APIRouter, trigger: HttpTrigger, program: Program, params: list[str]
) -> None:
    """Register a single trigger route on the router."""

    async def handler(request: Request, background_tasks: BackgroundTasks):
        inputs = await _build_inputs(request, params)
        background_tasks.add_task(_run_workflow_background, program, inputs)
        return {"status": "accepted"}

    router.add_api_route(trigger.path, handler, methods=[trigger.method])
