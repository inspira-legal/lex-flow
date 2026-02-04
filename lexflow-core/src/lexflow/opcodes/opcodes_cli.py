"""CLI utility opcodes for LexFlow - spinners, progress bars, colors.

These opcodes provide rich CLI experiences with animated feedback.
No external dependencies - uses standard library only.
"""

import asyncio
import sys

from .opcodes import opcode, register_category

# Register category at module load time
register_category(
    id="cli",
    label="CLI Operations",
    prefix="cli_",
    color="#EC4899",
    icon="💻",
    order=250,
)


class Spinner:
    """A spinner instance with local state."""

    def __init__(self, message: str):
        self.message = message
        self.running = True
        self._task: asyncio.Task = None

    async def _animate(self):
        """Animation loop."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self.running:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r\033[K{frame} {self.message}...")
            sys.stdout.flush()
            try:
                await asyncio.sleep(0.08)
            except asyncio.CancelledError:
                break
            i += 1

    def start(self):
        """Start the animation task."""
        self._task = asyncio.create_task(self._animate())

    async def stop(self, message: str = "", success: bool = True):
        """Stop the spinner and show final message."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        sys.stdout.write("\r\033[K")
        icon = "✓" if success else "✗"
        final_message = message if message else f"{self.message} done"
        sys.stdout.write(f"{icon} {final_message}\n")
        sys.stdout.flush()


@opcode(category="cli")
async def spinner_start(message: str = "Loading") -> Spinner:
    """Start an animated spinner.

    Args:
        message: Message to display next to spinner

    Returns:
        Spinner object (use with spinner_stop, spinner_update)
    """
    spinner = Spinner(message)
    spinner.start()
    await asyncio.sleep(0.01)
    return spinner


@opcode(category="cli")
async def spinner_update(spinner: Spinner, message: str) -> None:
    """Update the message of a running spinner.

    Args:
        spinner: Spinner object from spinner_start
        message: New message to display
    """
    spinner.message = message


@opcode(category="cli")
async def spinner_stop(
    spinner: Spinner, message: str = "", success: bool = True
) -> None:
    """Stop a spinner and show completion message.

    Args:
        spinner: Spinner object from spinner_start
        message: Final message (empty = original message + "done")
        success: True for checkmark, False for X mark
    """
    await spinner.stop(message, success)


@opcode(category="cli")
async def spinner_fail(spinner: Spinner, message: str = "Failed") -> None:
    """Stop a spinner with failure indicator.

    Args:
        spinner: Spinner object from spinner_start
        message: Error message to display
    """
    await spinner.stop(message, success=False)


@opcode(category="cli")
async def progress_bar(
    current: int, total: int, message: str = "", width: int = 30
) -> None:
    """Display/update a progress bar.

    Args:
        current: Current progress value
        total: Total/max value
        message: Optional message to show
        width: Bar width in characters (default: 30)
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


@opcode(category="cli")
async def clear_line() -> None:
    """Clear the current terminal line."""
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


@opcode(category="cli")
async def print_success(message: str) -> None:
    """Print a success message with green checkmark."""
    sys.stdout.write(f"✓ {message}\n")
    sys.stdout.flush()


@opcode(category="cli")
async def print_error(message: str) -> None:
    """Print an error message with red X."""
    sys.stdout.write(f"✗ {message}\n")
    sys.stdout.flush()


@opcode(category="cli")
async def print_warning(message: str) -> None:
    """Print a warning message with yellow indicator."""
    sys.stdout.write(f"⚠ {message}\n")
    sys.stdout.flush()


@opcode(category="cli")
async def print_info(message: str) -> None:
    """Print an info message with blue indicator."""
    sys.stdout.write(f"ℹ {message}\n")
    sys.stdout.flush()
