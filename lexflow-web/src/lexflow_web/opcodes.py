"""Web-specific opcodes for interactive browser workflows."""

from contextvars import ContextVar
from typing import Callable, Awaitable

from lexflow import opcode

# Type aliases
WebSender = Callable[[dict], Awaitable[None]]
WebReceiver = Callable[[], Awaitable[dict]]

# Context variables set by websocket handler before engine.run()
web_send: ContextVar[WebSender | None] = ContextVar("web_send", default=None)
web_receive: ContextVar[WebReceiver | None] = ContextVar("web_receive", default=None)


def _get_sender() -> WebSender:
    """Get the web sender, raising if not in web context."""
    sender = web_send.get()
    if sender is None:
        raise RuntimeError("web_* opcodes require a web context (WebSocket connection)")
    return sender


def _get_receiver() -> WebReceiver:
    """Get the web receiver, raising if not in web context."""
    receiver = web_receive.get()
    if receiver is None:
        raise RuntimeError("web_* opcodes require a web context (WebSocket connection)")
    return receiver


# =============================================================================
# Interactive Opcodes (Request-Response)
# =============================================================================


@opcode()
async def web_input(prompt: str = "") -> str:
    """Display an input field and wait for user text input."""
    sender = _get_sender()
    receiver = _get_receiver()

    await sender({"type": "input_request", "prompt": prompt})
    response = await receiver()

    return str(response.get("value", ""))


@opcode()
async def web_select(options: list, prompt: str = "") -> str:
    """Display a dropdown selection and wait for user choice."""
    sender = _get_sender()
    receiver = _get_receiver()

    # Ensure options are strings
    str_options = [str(opt) for opt in options]

    await sender({"type": "select_request", "prompt": prompt, "options": str_options})
    response = await receiver()

    return str(response.get("value", ""))


@opcode()
async def web_confirm(message: str) -> bool:
    """Display a confirmation dialog and wait for yes/no response."""
    sender = _get_sender()
    receiver = _get_receiver()

    await sender({"type": "confirm_request", "message": message})
    response = await receiver()

    return bool(response.get("value", False))


@opcode()
async def web_button(label: str) -> None:
    """Display a button and wait for it to be clicked."""
    sender = _get_sender()
    receiver = _get_receiver()

    await sender({"type": "button_request", "label": label})
    await receiver()  # Just wait for click, no return value needed


# =============================================================================
# Display Opcodes (Fire-and-Forget)
# =============================================================================


@opcode()
async def web_render(html: str) -> None:
    """Render raw HTML content in the execution panel."""
    sender = _get_sender()
    await sender({"type": "render_html", "html": html})


@opcode()
async def web_markdown(content: str) -> None:
    """Render markdown content in the execution panel."""
    sender = _get_sender()
    await sender({"type": "render_markdown", "content": content})


@opcode()
async def web_alert(message: str, variant: str = "info") -> None:
    """Display an alert message. Variant: info, success, warning, error."""
    sender = _get_sender()
    await sender({"type": "alert", "message": message, "variant": variant})


@opcode()
async def web_progress(value: int, max: int = 100, label: str = "") -> None:
    """Update the progress bar in the execution panel."""
    sender = _get_sender()
    await sender({"type": "progress", "value": value, "max": max, "label": label})


@opcode()
async def web_table(data: list) -> None:
    """Render a table from a list of dictionaries."""
    sender = _get_sender()
    # Ensure data is serializable
    serialized = [
        dict(row) if isinstance(row, dict) else {"value": row} for row in data
    ]
    await sender({"type": "render_table", "data": serialized})


@opcode()
async def web_image(src: str, alt: str = "") -> None:
    """Display an image by URL or base64 data URI."""
    sender = _get_sender()
    await sender({"type": "render_image", "src": src, "alt": alt})


@opcode()
async def web_clear() -> None:
    """Clear all rendered content from the execution panel."""
    sender = _get_sender()
    await sender({"type": "clear_content"})
