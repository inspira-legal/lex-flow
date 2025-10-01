# FastAPI Integration Guide

This guide shows how to expose the LexFlow engine as a REST API using FastAPI.

## Installation

Add FastAPI dependencies to your project:

```bash
uv add fastapi uvicorn python-multipart
```

## Basic FastAPI Application

Create `api/main.py`:

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Any
import asyncio
import io
from pathlib import Path
import tempfile
import json

from lexflow import Parser, Engine

app = FastAPI(title="LexFlow API", version="1.0.0")


class WorkflowExecuteRequest(BaseModel):
    """Request to execute a workflow from JSON/YAML content."""
    content: str
    workflow_name: Optional[str] = "main"
    inputs: Optional[dict[str, Any]] = {}


class WorkflowExecuteResponse(BaseModel):
    """Response from workflow execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    output: Optional[str] = None


class WorkflowValidateRequest(BaseModel):
    """Request to validate a workflow."""
    content: str


class WorkflowValidateResponse(BaseModel):
    """Response from workflow validation."""
    valid: bool
    errors: Optional[list[str]] = None
    workflows: Optional[list[str]] = None


@app.post("/workflow/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(request: WorkflowExecuteRequest):
    """
    Execute a LexFlow workflow from JSON or YAML content.

    Args:
        request: WorkflowExecuteRequest containing workflow content and parameters

    Returns:
        WorkflowExecuteResponse with execution results and captured output
    """
    try:
        # Create temporary file for workflow content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(request.content)
            temp_path = Path(f.name)

        try:
            # Parse workflow
            parser = Parser()
            program = parser.parse_file(str(temp_path))

            # Capture output using StringIO
            output_buffer = io.StringIO()

            # Create engine with output redirection
            engine = Engine(program, output=output_buffer)

            # Execute workflow
            result = await engine.run()

            # Get captured output
            captured_output = output_buffer.getvalue()

            return WorkflowExecuteResponse(
                success=True,
                result=result,
                output=captured_output
            )

        finally:
            # Cleanup temp file
            temp_path.unlink(missing_ok=True)

    except Exception as e:
        return WorkflowExecuteResponse(
            success=False,
            error=str(e)
        )


@app.post("/workflow/validate", response_model=WorkflowValidateResponse)
async def validate_workflow(request: WorkflowValidateRequest):
    """
    Validate a LexFlow workflow without executing it.

    Args:
        request: WorkflowValidateRequest containing workflow content

    Returns:
        WorkflowValidateResponse with validation results
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(request.content)
            temp_path = Path(f.name)

        try:
            # Parse and validate
            parser = Parser()
            program = parser.parse_file(str(temp_path))

            # Extract workflow names
            workflow_names = [program.main.name]
            if program.externals:
                workflow_names.extend(program.externals.keys())

            return WorkflowValidateResponse(
                valid=True,
                workflows=workflow_names
            )

        finally:
            temp_path.unlink(missing_ok=True)

    except Exception as e:
        return WorkflowValidateResponse(
            valid=False,
            errors=[str(e)]
        )


@app.post("/workflow/upload", response_model=WorkflowExecuteResponse)
async def upload_and_execute(
    file: UploadFile = File(...),
    workflow_name: str = "main"
):
    """
    Upload and execute a workflow file (JSON or YAML).

    Args:
        file: Uploaded workflow file
        workflow_name: Name of workflow to execute (default: "main")

    Returns:
        WorkflowExecuteResponse with execution results
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Execute using the execute endpoint logic
        request = WorkflowExecuteRequest(
            content=content_str,
            workflow_name=workflow_name
        )

        return await execute_workflow(request)

    except Exception as e:
        return WorkflowExecuteResponse(
            success=False,
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from lexflow.opcodes import OpcodeRegistry
    registry = OpcodeRegistry()
    return {
        "status": "healthy",
        "opcodes_loaded": len(registry.list_opcodes())
    }


@app.get("/opcodes")
async def list_opcodes():
    """List all available opcodes."""
    from lexflow.opcodes import OpcodeRegistry
    registry = OpcodeRegistry()
    return {
        "opcodes": registry.list_opcodes()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the API

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Output Capture

LexFlow automatically captures all workflow output (from `io_print` opcodes) when used with FastAPI. This is achieved using Python's built-in `redirect_stdout` mechanism.

### How It Works

```python
# In the execute_workflow endpoint:

# 1. Create a StringIO buffer
output_buffer = io.StringIO()

# 2. Pass it to the Engine
engine = Engine(program, output=output_buffer)

# 3. Execute the workflow
result = await engine.run()

# 4. Get captured output
captured_output = output_buffer.getvalue()

# 5. Return in response
return WorkflowExecuteResponse(
    success=True,
    result=result,
    output=captured_output  # All print statements captured here!
)
```

### Benefits

- **Clean API Responses**: Output is separated from execution results
- **No Pollution**: Workflow prints don't pollute server logs
- **Debugging**: Clients can see exactly what the workflow printed
- **Testing**: Easy to verify workflow behavior
- **Flexibility**: Can redirect to files, multiple streams, or callbacks

### Example Response

When a workflow contains:
```yaml
nodes:
  print_hello:
    opcode: io_print
    inputs:
      STRING:
        literal: "Processing data...\n"
```

The API response will be:
```json
{
  "success": true,
  "result": null,
  "output": "Processing data...\n",
  "error": null
}
```

### Advanced: Streaming Output

For long-running workflows, you can stream output using WebSockets:

```python
from lexflow.output import StreamingOutput
from fastapi import WebSocket

@app.websocket("/workflow/execute/stream")
async def execute_workflow_stream(websocket: WebSocket):
    await websocket.accept()

    async def send_output(line):
        await websocket.send_json({"type": "output", "data": line})

    # Stream output line by line
    stream = StreamingOutput(send_output)
    engine = Engine(program, output=stream)
    result = await engine.run()
    stream.flush()

    await websocket.send_json({"type": "result", "data": result})
```

### Alternative: Log to File

For auditing or debugging:

```python
import tempfile

with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as log_file:
    engine = Engine(program, output=log_file)
    result = await engine.run()
    log_path = log_file.name

# Log file contains all workflow output
```

## API Endpoints

### Execute Workflow (POST /workflow/execute)

Execute a workflow from JSON/YAML content.

**Request:**
```json
{
  "content": "{\"workflows\": [...]}",
  "workflow_name": "main",
  "inputs": {
    "param1": "value1",
    "param2": 42
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": "workflow result",
  "output": "captured output",
  "error": null
}
```

### Validate Workflow (POST /workflow/validate)

Validate workflow syntax without executing.

**Request:**
```json
{
  "content": "{\"workflows\": [...]}"
}
```

**Response:**
```json
{
  "valid": true,
  "errors": null,
  "workflows": ["main", "helper"]
}
```

### Upload and Execute (POST /workflow/upload)

Upload a workflow file and execute it.

**Request:**
- Multipart form with `file` field
- Optional query parameter: `workflow_name=main`

**Response:**
```json
{
  "success": true,
  "result": "workflow result",
  "output": "captured output from workflow",
  "error": null
}
```

### Health Check (GET /health)

Check API health and loaded opcodes.

**Response:**
```json
{
  "status": "healthy",
  "opcodes_loaded": 52
}
```

### List Opcodes (GET /opcodes)

Get all available opcodes.

**Response:**
```json
{
  "opcodes": ["io_print", "operator_add", "control_if_else", ...]
}
```

## Example Usage

### Using cURL

```bash
# Execute workflow from file
curl -X POST http://localhost:8000/workflow/execute \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "content": $(cat examples/simple_hello.json | jq -Rs .),
  "workflow_name": "main"
}
EOF

# Upload and execute
curl -X POST http://localhost:8000/workflow/upload \
  -F "file=@examples/simple_hello.json" \
  -F "workflow_name=main"

# Validate workflow
curl -X POST http://localhost:8000/workflow/validate \
  -H "Content-Type: application/json" \
  -d '{"content": "{\"workflows\": []}"}'
```

### Using Python Requests

```python
import requests
import json

# Execute workflow
with open('examples/simple_hello.json') as f:
    workflow_content = f.read()

response = requests.post(
    'http://localhost:8000/workflow/execute',
    json={
        'content': workflow_content,
        'workflow_name': 'main',
        'inputs': {}
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Result: {result['result']}")
```

### Using JavaScript/Fetch

```javascript
// Execute workflow
const response = await fetch('http://localhost:8000/workflow/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: JSON.stringify(workflowData),
    workflow_name: 'main',
    inputs: { param1: 'value' }
  })
});

const result = await response.json();
console.log('Success:', result.success);
console.log('Result:', result.result);
```

## Advanced Configuration

### Adding Custom Opcodes

```python
from lexflow.opcodes import OpcodeRegistry, opcode, BaseOpcode, params

# Create custom registry
registry = OpcodeRegistry()

@params(
    x={"type": int, "description": "First value"},
    y={"type": int, "description": "Second value"}
)
@opcode("custom_multiply")
class CustomMultiply(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = params['x'] * params['y'] * 100
        state.push(result)
        return True

# Use in FastAPI app
app = FastAPI()
# ... rest of implementation using custom registry
```

### Adding Authentication

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials

@app.post("/workflow/execute")
async def execute_workflow(
    request: WorkflowExecuteRequest,
    token: str = Depends(verify_token)
):
    # Implementation...
    pass
```

### Streaming Output

For long-running workflows with print statements:

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.post("/workflow/execute/stream")
async def execute_workflow_stream(request: WorkflowExecuteRequest):
    async def generate():
        # Capture stdout and stream it
        # Implementation depends on your needs
        yield "Starting execution...\n"
        # ... execute workflow
        yield "Completed!\n"

    return StreamingResponse(generate(), media_type="text/plain")
```

## Deployment

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY lexflow-core ./lexflow-core
COPY lexflow-cli ./lexflow-cli
COPY api ./api

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t lexflow-api .
docker run -p 8000:8000 lexflow-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    volumes:
      - ./examples:/app/examples:ro
```

## Testing

Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_opcodes():
    response = client.get("/opcodes")
    assert response.status_code == 200
    assert "opcodes" in response.json()

def test_execute_workflow():
    workflow = {
        "workflows": [{
            "name": "main",
            "interface": {"inputs": [], "outputs": []},
            "variables": {},
            "nodes": {
                "start": {
                    "opcode": "workflow_start",
                    "next": None,
                    "inputs": {}
                }
            }
        }]
    }

    response = client.post(
        "/workflow/execute",
        json={
            "content": json.dumps(workflow),
            "workflow_name": "main"
        }
    )

    assert response.status_code == 200
    assert response.json()["success"] == True
```

Run tests:

```bash
uv run pytest tests/test_api.py -v
```

## Security Considerations

1. **Input Validation**: Always validate workflow content before execution
2. **Rate Limiting**: Add rate limiting for public APIs
3. **Timeouts**: Set execution timeouts to prevent infinite loops
4. **Sandboxing**: Consider running workflows in isolated environments
5. **Authentication**: Implement proper auth for production use
6. **CORS**: Configure CORS settings appropriately

## Next Steps

- Add workflow persistence (database storage)
- Implement async execution with job queues
- Add WebSocket support for real-time execution updates
- Create workflow templates and library system
- Add metrics and monitoring (Prometheus, Grafana)
