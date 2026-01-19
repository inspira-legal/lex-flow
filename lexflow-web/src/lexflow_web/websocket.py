"""WebSocket handler for streaming workflow execution."""

import asyncio
import json
from typing import Any

import yaml
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from lexflow import Engine, Parser

router = APIRouter()


class WebSocketOutput:
    """Output handler that sends to WebSocket asynchronously."""

    def __init__(self, websocket: WebSocket, loop: asyncio.AbstractEventLoop):
        self.websocket = websocket
        self.loop = loop
        self.buffer = ""

    def write(self, text: str) -> int:
        """Write text and send to websocket on newlines."""
        self.buffer += text

        if "\n" in text:
            lines = self.buffer.split("\n")
            for line in lines[:-1]:
                # Schedule async send
                asyncio.run_coroutine_threadsafe(self._send_line(line), self.loop)
            self.buffer = lines[-1]

        return len(text)

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer:
            asyncio.run_coroutine_threadsafe(self._send_line(self.buffer), self.loop)
            self.buffer = ""

    async def _send_line(self, line: str):
        """Send a line to websocket."""
        try:
            await self.websocket.send_json({"type": "output", "line": line})
        except Exception:
            pass  # Client may have disconnected


class SimpleWebSocketOutput:
    """Simpler output handler that buffers everything for later sending."""

    def __init__(self):
        self.lines = []
        self.buffer = ""

    def write(self, text: str) -> int:
        """Write text and buffer lines."""
        self.buffer += text

        if "\n" in text:
            lines = self.buffer.split("\n")
            for line in lines[:-1]:
                self.lines.append(line)
            self.buffer = lines[-1]

        return len(text)

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer:
            self.lines.append(self.buffer)
            self.buffer = ""

    def get_lines(self) -> list[str]:
        """Get all buffered lines."""
        return self.lines


def _parse_workflow_content(content: str) -> dict:
    """Parse workflow content as YAML or JSON."""
    content = content.strip()
    if content.startswith("{"):
        return json.loads(content)
    return yaml.safe_load(content)


@router.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """WebSocket endpoint for streaming workflow execution."""
    await websocket.accept()

    try:
        while True:
            # Wait for execution request
            data = await websocket.receive_json()

            if data.get("type") != "start":
                await websocket.send_json(
                    {"type": "error", "message": "Expected 'start' message"}
                )
                continue

            workflow_content = data.get("workflow", "")
            inputs = data.get("inputs", {})
            include_metrics = data.get("include_metrics", False)

            try:
                # Parse workflow
                workflow_data = _parse_workflow_content(workflow_content)

                parser = Parser()
                program = parser.parse_dict(workflow_data)

                # Use simple buffered output for cleaner async handling
                output = SimpleWebSocketOutput()
                engine = Engine(program, output=output, metrics=include_metrics)

                # Execute workflow
                result = await engine.run(inputs=inputs if inputs else None)

                # Flush any remaining output
                output.flush()

                # Send buffered output lines
                for line in output.get_lines():
                    await websocket.send_json({"type": "output", "line": line})

                # Send completion message
                response: dict[str, Any] = {
                    "type": "complete",
                    "result": _serialize_result(result),
                }

                if include_metrics:
                    response["metrics"] = engine.metrics.to_dict()

                await websocket.send_json(response)

            except yaml.YAMLError as e:
                await websocket.send_json(
                    {"type": "error", "message": f"YAML parse error: {e}"}
                )
            except json.JSONDecodeError as e:
                await websocket.send_json(
                    {"type": "error", "message": f"JSON parse error: {e}"}
                )
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass


def _serialize_result(result: Any) -> Any:
    """Serialize result for JSON transmission."""
    if result is None:
        return None
    if isinstance(result, (str, int, float, bool)):
        return result
    if isinstance(result, (list, tuple)):
        return [_serialize_result(item) for item in result]
    if isinstance(result, dict):
        return {str(k): _serialize_result(v) for k, v in result.items()}
    return str(result)
