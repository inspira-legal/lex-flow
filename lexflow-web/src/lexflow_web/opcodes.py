"""Web-specific opcodes for interactive browser workflows.

These opcodes use Channel for communication, making them functionally pure.
Channels are passed as workflow inputs by the WebSocket handler.
"""

from lexflow import opcode
from lexflow.channel import Channel


# =============================================================================
# Interactive Opcodes (Request-Response)
# =============================================================================


@opcode()
async def web_input(web_send: Channel, web_recv: Channel, prompt: str = "") -> str:
    """Display an input field and wait for user text input."""
    await web_send.send({"type": "input_request", "prompt": prompt})
    response = await web_recv.receive()
    return str(response.get("value", ""))


@opcode()
async def web_select(
    web_send: Channel, web_recv: Channel, options: list, prompt: str = ""
) -> str:
    """Display a dropdown selection and wait for user choice."""
    str_options = [str(opt) for opt in options]
    await web_send.send(
        {"type": "select_request", "prompt": prompt, "options": str_options}
    )
    response = await web_recv.receive()
    return str(response.get("value", ""))


@opcode()
async def web_confirm(web_send: Channel, web_recv: Channel, message: str) -> bool:
    """Display a confirmation dialog and wait for yes/no response."""
    await web_send.send({"type": "confirm_request", "message": message})
    response = await web_recv.receive()
    return bool(response.get("value", False))


@opcode()
async def web_button(web_send: Channel, web_recv: Channel, label: str) -> None:
    """Display a button and wait for it to be clicked."""
    await web_send.send({"type": "button_request", "label": label})
    await web_recv.receive()


# =============================================================================
# Display Opcodes (Fire-and-Forget)
# =============================================================================


@opcode()
async def web_render(web_send: Channel, html: str) -> None:
    """Render raw HTML content in the execution panel."""
    await web_send.send({"type": "render_html", "html": html})


@opcode()
async def web_markdown(web_send: Channel, content: str) -> None:
    """Render markdown content in the execution panel."""
    await web_send.send({"type": "render_markdown", "content": content})


@opcode()
async def web_alert(web_send: Channel, message: str, variant: str = "info") -> None:
    """Display an alert message. Variant: info, success, warning, error."""
    await web_send.send({"type": "alert", "message": message, "variant": variant})


@opcode()
async def web_progress(
    web_send: Channel, value: int, max: int = 100, label: str = ""
) -> None:
    """Update the progress bar in the execution panel."""
    await web_send.send(
        {"type": "progress", "value": value, "max": max, "label": label}
    )


@opcode()
async def web_table(web_send: Channel, data: list) -> None:
    """Render a table from a list of dictionaries."""
    serialized = [
        dict(row) if isinstance(row, dict) else {"value": row} for row in data
    ]
    await web_send.send({"type": "render_table", "data": serialized})


@opcode()
async def web_image(web_send: Channel, src: str, alt: str = "") -> None:
    """Display an image by URL or base64 data URI."""
    await web_send.send({"type": "render_image", "src": src, "alt": alt})


@opcode()
async def web_clear(web_send: Channel) -> None:
    """Clear all rendered content from the execution panel."""
    await web_send.send({"type": "clear_content"})
