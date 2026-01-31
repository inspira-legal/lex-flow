"""WebSocket handler for streaming workflow execution."""

import asyncio
import json
from typing import Any

import yaml
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from lexflow import Engine, Parser
from lexflow.channel import Channel

# Import web opcodes to register them with the default registry
from . import opcodes as web_opcodes  # noqa: F401

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

                # Queue for outgoing messages (used by StreamingWebSocketOutput)
                send_queue: asyncio.Queue[dict] = asyncio.Queue()

                # Create channels for web opcodes (functionally pure communication)
                web_send_channel = Channel(maxsize=100)
                web_recv_channel = Channel(maxsize=100)

                # Create output handler
                output = StreamingWebSocketOutput(websocket, send_queue)
                engine = Engine(program, output=output, metrics=include_metrics)

                # Only inject web channels if workflow declares them as inputs
                main_params = set(program.main.params)
                all_inputs = inputs.copy() if inputs else {}
                if "web_send" in main_params:
                    all_inputs["web_send"] = web_send_channel
                if "web_recv" in main_params:
                    all_inputs["web_recv"] = web_recv_channel

                # Only pass channels to messaging handler if workflow uses them
                uses_web_channels = "web_send" in main_params
                result = await _execute_with_messaging(
                    engine,
                    all_inputs if all_inputs else None,
                    websocket,
                    web_send_channel if uses_web_channels else None,
                    web_recv_channel if uses_web_channels else None,
                    output,
                    send_queue,
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
    web_send_channel: Channel | None,
    web_recv_channel: Channel | None,
    output: StreamingWebSocketOutput,
    send_queue: asyncio.Queue,
) -> Any:
    """Execute workflow with bidirectional WebSocket messaging via channels."""
    disconnected = asyncio.Event()

    async def channel_to_websocket():
        """Forward messages from web_send channel to WebSocket."""
        while not disconnected.is_set():
            try:
                msg = await asyncio.wait_for(web_send_channel.receive(), timeout=0.1)
                await websocket.send_json(msg)
            except asyncio.TimeoutError:
                continue
            except RuntimeError:
                # Channel closed
                break
            except Exception:
                break

    async def output_queue_sender():
        """Send queued output messages to WebSocket."""
        while True:
            try:
                msg = await asyncio.wait_for(send_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                if disconnected.is_set():
                    break
                continue
            if msg is None:  # Shutdown signal
                break
            try:
                await websocket.send_json(msg)
            except Exception:
                break

    async def websocket_receiver():
        """Receive messages from WebSocket and forward responses to channel."""
        try:
            while True:
                msg = await websocket.receive_json()
                # Forward responses to channel if available
                if web_recv_channel is not None and msg.get("type", "").endswith(
                    "_response"
                ):
                    await web_recv_channel.send(msg)
        except WebSocketDisconnect:
            disconnected.set()
        except Exception:
            disconnected.set()

    # Collect all tasks for cleanup
    tasks: list[asyncio.Task] = []

    # Start bridge tasks
    if web_send_channel is not None:
        tasks.append(asyncio.create_task(channel_to_websocket()))
    tasks.append(asyncio.create_task(output_queue_sender()))

    # Start receiver task
    receiver_task = asyncio.create_task(websocket_receiver())
    tasks.append(receiver_task)

    # Run engine in a task so we can cancel it on disconnect
    engine_task = asyncio.create_task(engine.run(inputs=inputs))
    tasks.append(engine_task)

    try:
        # Wait for either execution to complete or WebSocket to disconnect
        done, _ = await asyncio.wait(
            [engine_task, receiver_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if engine_task in done:
            # Normal completion - get result (may raise if engine failed)
            result = engine_task.result()

            # Flush any remaining output
            output.flush()

            # Signal output sender to stop
            await send_queue.put(None)

            # Close web_send channel to stop channel_sender_task
            if web_send_channel is not None:
                web_send_channel.close()

            return result
        else:
            # WebSocket disconnected - cancel execution
            raise WebSocketDisconnect()

    finally:
        # Signal disconnection to stop polling tasks
        disconnected.set()

        # Close channels to unblock any waiting operations
        if web_send_channel is not None:
            web_send_channel.close()
        if web_recv_channel is not None:
            web_recv_channel.close()

        # Signal output queue to stop
        await send_queue.put(None)

        # Cancel all tasks and wait for them to complete
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to finish (with timeout to avoid hanging)
        if tasks:
            await asyncio.wait(tasks, timeout=1.0)


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
