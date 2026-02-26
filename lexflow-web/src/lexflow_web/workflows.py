"""Workflow execution endpoints for LexFlow web API."""

import io
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lexflow import Engine, Parser

router = APIRouter()

# Examples directory (relative to project root)
EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"


class WorkflowRunInput(BaseModel):
    """Input for running a named workflow."""

    inputs: dict[str, Any] = {}


class WorkflowRunResponse(BaseModel):
    """Response from workflow execution."""

    success: bool
    result: Any = None
    output: str = ""
    error: str | None = None


@router.post("/{category}/{name}", response_model=WorkflowRunResponse)
async def run_workflow(category: str, name: str, data: WorkflowRunInput):
    """Execute a named workflow from the examples directory.

    Loads the YAML file at examples/{category}/{name}.yaml,
    parses it, and runs it with the provided inputs.
    """
    # Resolve and validate the file path
    file_path = EXAMPLES_DIR / "showcase" / category / f"{name}.yaml"

    if not file_path.exists():
        # Try .yml extension
        file_path = file_path.with_suffix(".yml")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Workflow not found: {category}/{name}")

    # Security check: ensure path is within examples dir
    try:
        file_path.resolve().relative_to(EXAMPLES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")

    try:
        content = file_path.read_text()
        workflow_data = yaml.safe_load(content)

        parser = Parser()
        program = parser.parse_dict(workflow_data)

        output_buffer = io.StringIO()
        engine = Engine(program, output=output_buffer)

        result = await engine.run(inputs=data.inputs)

        return WorkflowRunResponse(
            success=True,
            result=result,
            output=output_buffer.getvalue(),
        )
    except yaml.YAMLError as e:
        return WorkflowRunResponse(success=False, error=f"YAML parse error: {e}")
    except Exception as e:
        return WorkflowRunResponse(success=False, error=str(e))
