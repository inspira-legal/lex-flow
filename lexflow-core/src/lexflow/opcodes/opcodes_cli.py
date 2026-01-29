"""CLI utility opcodes for LexFlow - spinners, progress bars, colors.

These opcodes provide rich CLI experiences with animated feedback.
"""

import asyncio
import sys
from typing import Any, Dict, Optional

from .opcodes import opcode

# Global registry of active spinners
_spinners: Dict[int, asyncio.Task] = {}
_spinner_counter = 0
_spinner_messages: Dict[int, str] = {}


@opcode()
async def spinner_start(message: str = "Loading") -> int:
    """Start an animated spinner. Returns spinner ID to stop it later.

    Args:
        message: Message to display next to spinner

    Returns:
        Spinner ID (use with spinner_stop)

    Example:
        spinner_id = spinner_start("Fetching data")
        # ... do work ...
        spinner_stop(spinner_id, "Data loaded!")
    """
    global _spinner_counter
    _spinner_counter += 1
    spinner_id = _spinner_counter
    _spinner_messages[spinner_id] = message

    async def animate():
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while spinner_id in _spinners:
            frame = frames[i % len(frames)]
            # Clear line and write spinner
            sys.stdout.write(f"\r\033[K{frame} {_spinner_messages.get(spinner_id, message)}...")
            sys.stdout.flush()
            try:
                await asyncio.sleep(0.08)
            except asyncio.CancelledError:
                break
            i += 1

    task = asyncio.create_task(animate())
    _spinners[spinner_id] = task

    # Small delay to let spinner start
    await asyncio.sleep(0.01)
    return spinner_id


@opcode()
async def spinner_update(spinner_id: int, message: str) -> None:
    """Update the message of a running spinner.

    Args:
        spinner_id: ID from spinner_start
        message: New message to display
    """
    if spinner_id in _spinner_messages:
        _spinner_messages[spinner_id] = message


@opcode()
async def spinner_stop(spinner_id: int, message: str = "", success: bool = True) -> None:
    """Stop a spinner and show completion message.

    Args:
        spinner_id: ID from spinner_start
        message: Final message to display (empty = use original message + "done")
        success: True for checkmark, False for X mark

    Example:
        spinner_stop(spinner_id, "Loaded 42 items", success=True)
    """
    if spinner_id in _spinners:
        task = _spinners.pop(spinner_id)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        original_msg = _spinner_messages.pop(spinner_id, "")

        # Clear the line
        sys.stdout.write("\r\033[K")

        # Show final message
        icon = "✓" if success else "✗"
        final_message = message if message else f"{original_msg} done"
        sys.stdout.write(f"{icon} {final_message}\n")
        sys.stdout.flush()


@opcode()
async def spinner_fail(spinner_id: int, message: str = "Failed") -> None:
    """Stop a spinner with failure indicator.

    Args:
        spinner_id: ID from spinner_start
        message: Error message to display
    """
    await spinner_stop(spinner_id, message, success=False)


@opcode()
async def progress_bar(current: int, total: int, message: str = "", width: int = 30) -> None:
    """Display/update a progress bar.

    Args:
        current: Current progress value
        total: Total/max value
        message: Optional message to show
        width: Bar width in characters (default: 30)

    Example:
        progress_bar(25, 100, "Processing files")
        # Output: Processing files [███████░░░░░░░░░░░░░░░░░░░░░░░] 25%
    """
    if total <= 0:
        total = 1

    percent = min(100, int(current / total * 100))
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)

    prefix = f"{message} " if message else ""
    sys.stdout.write(f"\r\033[K{prefix}[{bar}] {percent}%")
    sys.stdout.flush()

    if current >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()


@opcode()
async def clear_line() -> None:
    """Clear the current terminal line."""
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


@opcode()
async def print_success(message: str) -> None:
    """Print a success message with green checkmark."""
    sys.stdout.write(f"✓ {message}\n")
    sys.stdout.flush()


@opcode()
async def print_error(message: str) -> None:
    """Print an error message with red X."""
    sys.stdout.write(f"✗ {message}\n")
    sys.stdout.flush()


@opcode()
async def print_warning(message: str) -> None:
    """Print a warning message with yellow indicator."""
    sys.stdout.write(f"⚠ {message}\n")
    sys.stdout.flush()


@opcode()
async def print_info(message: str) -> None:
    """Print an info message with blue indicator."""
    sys.stdout.write(f"ℹ {message}\n")
    sys.stdout.flush()
