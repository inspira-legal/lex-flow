"""Tests for utility opcodes (opcodes_util.py)."""

import pytest

from lexflow.opcodes.opcodes_util import util_time_now, util_format_duration

pytestmark = pytest.mark.asyncio


async def test_time_now_returns_float():
    result = await util_time_now()
    assert isinstance(result, float)
    assert result > 0


async def test_time_now_is_monotonic():
    t1 = await util_time_now()
    t2 = await util_time_now()
    assert t2 >= t1


async def test_format_duration_milliseconds():
    result = await util_format_duration(0.0, 0.5)
    assert result == "500ms"


async def test_format_duration_sub_millisecond():
    result = await util_format_duration(0.0, 0.001)
    assert result == "1ms"


async def test_format_duration_seconds():
    result = await util_format_duration(0.0, 5.3)
    assert result == "5.3s"


async def test_format_duration_minutes():
    result = await util_format_duration(0.0, 125.5)
    assert result == "2m5.5s"


async def test_format_duration_exact_one_second():
    result = await util_format_duration(0.0, 1.0)
    assert result == "1.0s"


async def test_format_duration_zero():
    result = await util_format_duration(0.0, 0.0)
    assert result == "0ms"
