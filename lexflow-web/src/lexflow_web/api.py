"""REST API endpoints for LexFlow web frontend."""

import io
import json
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lexflow import Engine, Parser
from lexflow_web.visualization import workflow_to_tree

router = APIRouter()

# Find examples directory (relative to project root)
# Path: api.py -> lexflow_web -> src -> lexflow-web -> lex-flow -> examples
EXAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "examples"


class WorkflowInput(BaseModel):
    """Input for workflow parsing/execution."""

    workflow: str
    inputs: dict[str, Any] | None = None
    include_metrics: bool = False


class ParseResponse(BaseModel):
    """Response from parse endpoint."""

    success: bool
    tree: dict | None = None
    interface: dict | None = None
    error: str | None = None


class ValidateResponse(BaseModel):
    """Response from validate endpoint."""

    valid: bool
    errors: list[str] = []


class ExecuteResponse(BaseModel):
    """Response from execute endpoint."""

    success: bool
    result: Any = None
    output: str = ""
    metrics: dict | None = None
    error: str | None = None


class ExampleInfo(BaseModel):
    """Example workflow information."""

    name: str
    path: str
    category: str


class ExampleContent(BaseModel):
    """Example workflow content."""

    name: str
    path: str
    content: str


def _parse_workflow_content(content: str) -> dict:
    """Parse workflow content as YAML or JSON."""
    content = content.strip()
    # Try JSON first if it looks like JSON
    if content.startswith("{"):
        return json.loads(content)
    # Otherwise try YAML
    return yaml.safe_load(content)


@router.post("/parse", response_model=ParseResponse)
async def parse_workflow(data: WorkflowInput):
    """Parse workflow and return visualization tree."""
    try:
        workflow_data = _parse_workflow_content(data.workflow)
        tree = workflow_to_tree(workflow_data)

        if "error" in tree:
            return ParseResponse(success=False, error=tree["error"])

        return ParseResponse(
            success=True,
            tree=tree,
            interface=tree.get("interface", {}),
        )
    except yaml.YAMLError as e:
        return ParseResponse(success=False, error=f"YAML parse error: {e}")
    except json.JSONDecodeError as e:
        return ParseResponse(success=False, error=f"JSON parse error: {e}")
    except Exception as e:
        return ParseResponse(success=False, error=str(e))


@router.post("/validate", response_model=ValidateResponse)
async def validate_workflow(data: WorkflowInput):
    """Validate workflow syntax."""
    errors = []
    try:
        workflow_data = _parse_workflow_content(data.workflow)

        # Try to parse with the actual parser
        parser = Parser()
        parser.parse_dict(workflow_data)

        return ValidateResponse(valid=True)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e}")
    except Exception as e:
        errors.append(str(e))

    return ValidateResponse(valid=False, errors=errors)


@router.post("/execute", response_model=ExecuteResponse)
async def execute_workflow(data: WorkflowInput):
    """Execute workflow and return result."""
    try:
        workflow_data = _parse_workflow_content(data.workflow)

        # Parse and execute
        parser = Parser()
        program = parser.parse_dict(workflow_data)

        # Capture output
        output_buffer = io.StringIO()
        engine = Engine(program, output=output_buffer, metrics=data.include_metrics)

        # Execute with inputs
        result = await engine.run(inputs=data.inputs)

        response = ExecuteResponse(
            success=True,
            result=result,
            output=output_buffer.getvalue(),
        )

        if data.include_metrics:
            response.metrics = engine.metrics.to_dict()

        return response
    except yaml.YAMLError as e:
        return ExecuteResponse(success=False, error=f"YAML parse error: {e}")
    except json.JSONDecodeError as e:
        return ExecuteResponse(success=False, error=f"JSON parse error: {e}")
    except Exception as e:
        return ExecuteResponse(success=False, error=str(e))


@router.get("/examples", response_model=list[ExampleInfo])
async def list_examples():
    """List available example workflows."""
    examples = []

    if not EXAMPLES_DIR.exists():
        return examples

    # Walk through examples directory
    for category_dir in sorted(EXAMPLES_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith("_") or category_dir.name.startswith("."):
            continue

        category = category_dir.name

        for file_path in sorted(category_dir.iterdir()):
            if file_path.suffix in (".yaml", ".yml", ".json"):
                relative_path = f"{category}/{file_path.name}"
                examples.append(
                    ExampleInfo(
                        name=file_path.stem,
                        path=relative_path,
                        category=category,
                    )
                )

    return examples


@router.get("/examples/{category}/{filename}", response_model=ExampleContent)
async def get_example(category: str, filename: str):
    """Get example workflow content."""
    file_path = EXAMPLES_DIR / category / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Example not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    # Security check: ensure path is within examples dir
    try:
        file_path.resolve().relative_to(EXAMPLES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")

    content = file_path.read_text()
    return ExampleContent(
        name=file_path.stem,
        path=f"{category}/{filename}",
        content=content,
    )
