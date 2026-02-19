"""Utility opcodes - timing and formatting helpers."""

import time

from .opcodes import opcode, register_category

register_category(
    id="util",
    label="Utility Operations",
    prefix="util_",
    color="#78716C",
    icon="🔧",
    order=260,
)


@opcode(category="util")
async def util_time_now() -> float:
    """Get current time in seconds (monotonic clock)."""
    return time.perf_counter()


@opcode(category="util")
async def util_format_duration(start: float, end: float) -> str:
    """Format elapsed time between two timestamps as human-readable string."""
    elapsed = end - start
    if elapsed < 1:
        return f"{elapsed * 1000:.0f}ms"
    elif elapsed < 60:
        return f"{elapsed:.1f}s"
    else:
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        return f"{minutes}m{seconds:.1f}s"
