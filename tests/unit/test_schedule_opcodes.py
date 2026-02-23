"""Tests for schedule opcodes."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from lexflow import default_registry

pytestmark = pytest.mark.asyncio


class TestScheduleAfter:
    async def test_returns_timing_info(self):
        result = await default_registry.call("schedule_after", [0.05])
        assert "started_at" in result
        assert "completed_at" in result
        assert "elapsed_seconds" in result
        assert result["elapsed_seconds"] >= 0.05

    async def test_with_timezone(self):
        result = await default_registry.call(
            "schedule_after", [0.05, "America/Sao_Paulo"]
        )
        assert "started_at" in result
        assert "-03:00" in result["started_at"] or "-02:00" in result["started_at"]

    async def test_negative_seconds_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            await default_registry.call("schedule_after", [-1])

    async def test_zero_seconds_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            await default_registry.call("schedule_after", [0])

    async def test_exceeds_max_seconds_raises(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            await default_registry.call("schedule_after", [86400 * 366])

    async def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Invalid timezone"):
            await default_registry.call("schedule_after", [0.05, "Not/A_Timezone"])


class TestScheduleInterval:
    async def test_yields_correct_count(self):
        gen = await default_registry.call("schedule_interval", [0.02, 3])
        ticks = []
        async for tick in gen:
            ticks.append(tick)
        assert len(ticks) == 3

    async def test_tick_structure(self):
        gen = await default_registry.call("schedule_interval", [0.02, 1])
        async for tick in gen:
            assert "iteration" in tick
            assert "scheduled_time" in tick
            assert "actual_time" in tick
            assert "drift_seconds" in tick
            assert "next_scheduled_time" in tick
            assert tick["iteration"] == 0

    async def test_iterations_increment(self):
        gen = await default_registry.call("schedule_interval", [0.02, 3])
        iterations = []
        async for tick in gen:
            iterations.append(tick["iteration"])
        assert iterations == [0, 1, 2]

    async def test_with_timezone(self):
        gen = await default_registry.call(
            "schedule_interval", [0.02, 1, "America/Sao_Paulo"]
        )
        async for tick in gen:
            assert (
                "-03:00" in tick["scheduled_time"] or "-02:00" in tick["scheduled_time"]
            )

    async def test_negative_seconds_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            await default_registry.call("schedule_interval", [-1])

    async def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Invalid timezone"):
            await default_registry.call("schedule_interval", [1, None, "Bad/Zone"])


class TestScheduleDaily:
    async def test_tick_structure(self):
        gen = await default_registry.call("schedule_daily", [0, 0, 0, "UTC", 1])
        assert hasattr(gen, "__aiter__")
        assert hasattr(gen, "__anext__")

    async def test_fires_with_correct_fields(self):
        """Test daily generator yields correct structure using datetime mock."""
        from lexflow.opcodes import opcodes_schedule

        base = datetime(2025, 6, 15, 9, 59, 59, 0)
        after_sleep = datetime(2025, 6, 15, 10, 0, 0, 5000)

        call_count = 0

        def mock_now(tz):
            nonlocal call_count
            call_count += 1
            # Calls 1-2: before target (initial now + delay check)
            if call_count <= 2:
                return base.replace(tzinfo=tz)
            # Call 3+: after sleep
            return after_sleep.replace(tzinfo=tz)

        with (
            patch.object(opcodes_schedule, "_now", side_effect=mock_now),
            patch("asyncio.sleep") as mock_sleep,
        ):
            gen = await default_registry.call("schedule_daily", [10, 0, 0, "UTC", 1])
            ticks = []
            async for tick in gen:
                ticks.append(tick)

            assert len(ticks) == 1
            assert ticks[0]["iteration"] == 0
            assert "scheduled_time" in ticks[0]
            assert "actual_time" in ticks[0]
            assert "drift_seconds" in ticks[0]
            assert "next_scheduled_time" in ticks[0]
            mock_sleep.assert_called()

    async def test_schedules_tomorrow_if_past(self):
        """If target time already passed today, schedules for tomorrow."""
        from lexflow.opcodes import opcodes_schedule

        # Current time is 11:00, target is 10:00 -> should schedule for tomorrow
        now = datetime(2025, 6, 15, 11, 0, 0, 0)
        tomorrow_target = datetime(2025, 6, 16, 10, 0, 0, 0)
        after_sleep = tomorrow_target + timedelta(milliseconds=5)

        call_count = 0

        def mock_now(tz):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return now.replace(tzinfo=tz)
            return after_sleep.replace(tzinfo=tz)

        with (
            patch.object(opcodes_schedule, "_now", side_effect=mock_now),
            patch("asyncio.sleep"),
        ):
            gen = await default_registry.call("schedule_daily", [10, 0, 0, "UTC", 1])
            ticks = []
            async for tick in gen:
                ticks.append(tick)

            assert "2025-06-16" in ticks[0]["scheduled_time"]

    async def test_invalid_hour_raises(self):
        with pytest.raises(ValueError, match="hour must be 0-23"):
            await default_registry.call("schedule_daily", [25])

    async def test_invalid_minute_raises(self):
        with pytest.raises(ValueError, match="minute must be 0-59"):
            await default_registry.call("schedule_daily", [10, 60])

    async def test_invalid_second_raises(self):
        with pytest.raises(ValueError, match="second must be 0-59"):
            await default_registry.call("schedule_daily", [10, 0, 60])

    async def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Invalid timezone"):
            await default_registry.call("schedule_daily", [10, 0, 0, "Nope/Zone"])


class TestScheduleCron:
    async def test_available_when_croniter_installed(self):
        try:
            import croniter  # noqa: F401

            assert "schedule_cron" in default_registry.list_opcodes()
        except ImportError:
            assert "schedule_cron" not in default_registry.list_opcodes()

    async def test_tick_structure(self):
        pytest.importorskip("croniter")
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

    async def test_invalid_expression_raises(self):
        pytest.importorskip("croniter")
        with pytest.raises(ValueError, match="Invalid cron expression"):
            await default_registry.call("schedule_cron", ["not a cron"])

    async def test_invalid_timezone_raises(self):
        pytest.importorskip("croniter")
        with pytest.raises(ValueError, match="Invalid timezone"):
            await default_registry.call(
                "schedule_cron", ["* * * * *", None, "Bad/Zone"]
            )
