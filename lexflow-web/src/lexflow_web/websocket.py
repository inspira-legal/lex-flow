"""WebSocket handler for streaming workflow execution."""

import asyncio
import json
from typing import Any

import yaml
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from lexflow import Engine, Parser

# Import web opcodes to register them with the default registry
from . import opcodes as web_opcodes

router = APIRouter()


class StreamingWebSocketOutput:
    """Output handler that streams to WebSocket in real-time."""

    def __init__(self, websocket: WebSocket, send_queue: asyncio.Queue):
        self.websocket = websocket
        self.send_queue = send_queue
        self.buffer = ""

    def write(self, text: str) -> int:
        """Write text and queue lines for sending."""
        self.buffer += text

        if "\n" in text:
            lines = self.buffer.split("\n")
            for line in lines[:-1]:
                self.send_queue.put_nowait({"type": "output", "line": line})
            self.buffer = lines[-1]

        return len(text)

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer:
            self.send_queue.put_nowait({"type": "output", "line": self.buffer})
            self.buffer = ""


class WebContext:
    """Context manager for web opcodes providing send/receive via WebSocket."""

    def __init__(self, websocket: WebSocket, send_queue: asyncio.Queue):
        self.websocket = websocket
        self.send_queue = send_queue
        self.response_queue: asyncio.Queue[dict] = asyncio.Queue()
        self._send_token = None
        self._receive_token = None

    async def send(self, message: dict) -> None:
        """Send a message to the frontend via the send queue."""
        await self.send_queue.put(message)

    async def receive(self) -> dict:
        """Wait for a response from the frontend."""
        return await self.response_queue.get()

    def route_message(self, message: dict) -> bool:
        """Route incoming message. Returns True if it was a response message."""
        msg_type = message.get("type", "")
        if msg_type.endswith("_response"):
            self.response_queue.put_nowait(message)
            return True
        return False

    def __enter__(self):
        """Set context variables for web opcodes."""
        self._send_token = web_opcodes.web_send.set(self.send)
        self._receive_token = web_opcodes.web_receive.set(self.receive)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context variables."""
        if self._send_token:
            web_opcodes.web_send.reset(self._send_token)
        if self._receive_token:
            web_opcodes.web_receive.reset(self._receive_token)


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
                if not data.get("type", "").endswith("_response"):
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

                # Queue for outgoing messages
                send_queue: asyncio.Queue[dict] = asyncio.Queue()

                # Create output handler and web context
                output = StreamingWebSocketOutput(websocket, send_queue)
                engine = Engine(program, output=output, metrics=include_metrics)

                with WebContext(websocket, send_queue) as web_ctx:
                    result = await _execute_with_messaging(
                        engine, inputs, websocket, web_ctx, output, send_queue
                    )

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


async def _execute_with_messaging(
    engine: Engine,
    inputs: dict | None,
    websocket: WebSocket,
    web_ctx: WebContext,
    output: StreamingWebSocketOutput,
    send_queue: asyncio.Queue,
) -> Any:
    """Execute workflow with bidirectional WebSocket messaging."""

    async def sender():
        """Send queued messages to WebSocket."""
        while True:
            msg = await send_queue.get()
            if msg is None:  # Shutdown signal
                break
            try:
                await websocket.send_json(msg)
            except Exception:
                break

    async def receiver():
        """Receive messages from WebSocket and route responses."""
        while True:
            try:
                msg = await websocket.receive_json()
                web_ctx.route_message(msg)
            except WebSocketDisconnect:
                break
            except Exception:
                break

    # Start sender and receiver tasks
    sender_task = asyncio.create_task(sender())
    receiver_task = asyncio.create_task(receiver())

    try:
        # Execute workflow
        result = await engine.run(inputs=inputs if inputs else None)

        # Flush any remaining output
        output.flush()

        # Signal sender to stop and wait for it to drain the queue
        await send_queue.put(None)
        await sender_task

        return result
    finally:
        # Cancel receiver
        receiver_task.cancel()

        try:
            await receiver_task
        except asyncio.CancelledError:
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
