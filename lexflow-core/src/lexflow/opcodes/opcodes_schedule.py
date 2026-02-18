"""Schedule opcodes for LexFlow time-based workflow control.

Provides one-shot delays, recurring intervals, daily timers,
and cron-based scheduling as async generators for use with
control_async_foreach.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional
from zoneinfo import ZoneInfo

from .opcodes import opcode, register_category

try:
    from croniter import croniter

    CRONITER_AVAILABLE = True
except ImportError:
    CRONITER_AVAILABLE = False


register_category(
    id="schedule",
    label="Schedule Operations",
    prefix="schedule_",
    color="#F59E0B",
    icon="⏰",
    order=275,
)


def _now(tz: ZoneInfo) -> datetime:
    return datetime.now(tz)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@opcode(category="schedule")
async def schedule_after(seconds: float, timezone: str = "UTC") -> dict:
    """Wait for a delay then return timing info.

    Args:
        seconds: Number of seconds to wait
        timezone: IANA timezone for timestamps (e.g. "America/Sao_Paulo")

    Returns:
        Dict with started_at, completed_at, elapsed_seconds
    """
    tz = ZoneInfo(timezone)
    started_at = _now(tz)
    await asyncio.sleep(seconds)
    completed_at = _now(tz)
    return {
        "started_at": _iso(started_at),
        "completed_at": _iso(completed_at),
        "elapsed_seconds": (completed_at - started_at).total_seconds(),
    }


@opcode(category="schedule")
async def schedule_interval(
    seconds: float,
    max_iterations: Optional[int] = None,
    timezone: str = "UTC",
) -> AsyncGenerator[dict, None]:
    """Recurring fixed-rate timer as an async generator.

    Uses fixed-rate scheduling measured from start time to prevent
    drift accumulation. Use with control_async_foreach.

    Args:
        seconds: Interval between ticks in seconds
        max_iterations: Stop after N iterations (None for infinite)
        timezone: IANA timezone for timestamps

    Yields:
        Dict with iteration, scheduled_time, actual_time, drift_seconds,
        next_scheduled_time
    """
    tz = ZoneInfo(timezone)

    async def gen():
        start = _now(tz)
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            scheduled = start + timedelta(seconds=seconds * iteration)
            if iteration > 0:
                delay = (scheduled - _now(tz)).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)
            actual = _now(tz)
            drift = (actual - scheduled).total_seconds()
            next_scheduled = start + timedelta(seconds=seconds * (iteration + 1))
            yield {
                "iteration": iteration,
                "scheduled_time": _iso(scheduled),
                "actual_time": _iso(actual),
                "drift_seconds": drift,
                "next_scheduled_time": _iso(next_scheduled),
            }
            iteration += 1

    return gen()


@opcode(category="schedule")
async def schedule_daily(
    hour: int,
    minute: int = 0,
    second: int = 0,
    timezone: str = "UTC",
    max_iterations: Optional[int] = None,
) -> AsyncGenerator[dict, None]:
    """Daily timer that fires at a specific time each day.

    If today's target time has already passed, the first fire is
    scheduled for tomorrow. Use with control_async_foreach.

    Args:
        hour: Hour of day (0-23)
        minute: Minute (0-59)
        second: Second (0-59)
        timezone: IANA timezone for scheduling
        max_iterations: Stop after N iterations (None for infinite)

    Yields:
        Dict with iteration, scheduled_time, actual_time, drift_seconds,
        next_scheduled_time
    """
    tz = ZoneInfo(timezone)

    async def gen():
        now = _now(tz)
        target = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
        if target <= now:
            target += timedelta(days=1)

        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            delay = (target - _now(tz)).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            actual = _now(tz)
            drift = (actual - target).total_seconds()
            next_target = target + timedelta(days=1)
            yield {
                "iteration": iteration,
                "scheduled_time": _iso(target),
                "actual_time": _iso(actual),
                "drift_seconds": drift,
                "next_scheduled_time": _iso(next_target),
            }
            target = next_target
            iteration += 1

    return gen()


if CRONITER_AVAILABLE:

    @opcode(category="schedule")
    async def schedule_cron(
        expression: str,
        max_iterations: Optional[int] = None,
        timezone: str = "UTC",
    ) -> AsyncGenerator[dict, None]:
        """Cron-based recurring timer as an async generator.

        Requires the croniter package. Use with control_async_foreach.

        Args:
            expression: Cron expression (e.g. "*/5 * * * *" for every 5 min)
            max_iterations: Stop after N iterations (None for infinite)
            timezone: IANA timezone for scheduling

        Yields:
            Dict with iteration, scheduled_time, actual_time, drift_seconds,
            next_scheduled_time
        """
        tz = ZoneInfo(timezone)

        async def gen():
            now = _now(tz)
            cron = croniter(expression, now)
            iteration = 0
            while max_iterations is None or iteration < max_iterations:
                target = cron.get_next(datetime)
                delay = (target - _now(tz)).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)
                actual = _now(tz)
                drift = (actual - target).total_seconds()
                # Peek at next scheduled time with a separate iterator
                peek = croniter(expression, target)
                next_target = peek.get_next(datetime)
                yield {
                    "iteration": iteration,
                    "scheduled_time": _iso(target),
                    "actual_time": _iso(actual),
                    "drift_seconds": drift,
                    "next_scheduled_time": _iso(next_target),
                }
                iteration += 1

        return gen()
