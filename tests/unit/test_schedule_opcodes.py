"""Tests for schedule opcodes."""

import pytest
from lexflow import default_registry

pytestmark = pytest.mark.asyncio


async def test_schedule_after_returns_timing_info():
    result = await default_registry.call("schedule_after", [0.05])
    assert "started_at" in result
    assert "completed_at" in result
    assert "elapsed_seconds" in result
    assert result["elapsed_seconds"] >= 0.05


async def test_schedule_after_with_timezone():
    result = await default_registry.call("schedule_after", [0.05, "America/Sao_Paulo"])
    assert "started_at" in result
    assert "-03:00" in result["started_at"] or "-02:00" in result["started_at"]


async def test_schedule_interval_yields_correct_count():
    gen = await default_registry.call("schedule_interval", [0.02, 3])
    ticks = []
    async for tick in gen:
        ticks.append(tick)
    assert len(ticks) == 3


async def test_schedule_interval_tick_structure():
    gen = await default_registry.call("schedule_interval", [0.02, 1])
    async for tick in gen:
        assert "iteration" in tick
        assert "scheduled_time" in tick
        assert "actual_time" in tick
        assert "drift_seconds" in tick
        assert "next_scheduled_time" in tick
        assert tick["iteration"] == 0


async def test_schedule_interval_iterations_increment():
    gen = await default_registry.call("schedule_interval", [0.02, 3])
    iterations = []
    async for tick in gen:
        iterations.append(tick["iteration"])
    assert iterations == [0, 1, 2]


async def test_schedule_daily_tick_structure():
    """Test daily generator yields correct structure (with max_iterations=1 and immediate fire)."""
    # We can't easily test daily in a unit test (would wait until target time).
    # Instead, test that the generator is created and is an async generator.
    gen = await default_registry.call("schedule_daily", [0, 0, 0, "UTC", 1])
    assert hasattr(gen, "__aiter__")
    assert hasattr(gen, "__anext__")


async def test_schedule_cron_available():
    """Test schedule_cron is registered when croniter is available."""
    try:
        import croniter  # noqa: F401

        opcodes = default_registry.list_opcodes()
        assert "schedule_cron" in opcodes
    except ImportError:
        opcodes = default_registry.list_opcodes()
        assert "schedule_cron" not in opcodes


async def test_schedule_cron_tick_structure():
    """Test cron generator yields correct structure."""
    pytest.importorskip("croniter")
    # Every second — should fire very quickly
    gen = await default_registry.call("schedule_cron", ["* * * * * *", 1])
    ticks = []
    async for tick in gen:
        ticks.append(tick)
    assert len(ticks) == 1
    assert "iteration" in ticks[0]
    assert "scheduled_time" in ticks[0]
    assert "actual_time" in ticks[0]
    assert "drift_seconds" in ticks[0]
    assert "next_scheduled_time" in ticks[0]


async def test_schedule_interval_with_timezone():
    gen = await default_registry.call(
        "schedule_interval", [0.02, 1, "America/Sao_Paulo"]
    )
    async for tick in gen:
        assert "-03:00" in tick["scheduled_time"] or "-02:00" in tick["scheduled_time"]
