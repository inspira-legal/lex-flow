"""Unit tests for Channel class."""

import asyncio
import pytest

from lexflow.channel import Channel


pytestmark = pytest.mark.asyncio


async def test_channel_basic():
    """Test basic send and receive."""
    ch = Channel(maxsize=10)

    await ch.send("hello")
    value = await ch.receive()

    assert value == "hello"


async def test_channel_multiple_values():
    """Test sending and receiving multiple values."""
    ch = Channel(maxsize=10)

    await ch.send(1)
    await ch.send(2)
    await ch.send(3)

    assert await ch.receive() == 1
    assert await ch.receive() == 2
    assert await ch.receive() == 3


async def test_channel_try_receive():
    """Test non-blocking receive."""
    ch = Channel(maxsize=10)

    # Empty channel
    value, ok = ch.try_receive()
    assert ok is False
    assert value is None

    # With value
    await ch.send("test")
    value, ok = ch.try_receive()
    assert ok is True
    assert value == "test"


async def test_channel_send_nowait():
    """Test non-blocking send."""
    ch = Channel(maxsize=2)

    assert ch.send_nowait("a") is True
    assert ch.send_nowait("b") is True
    assert ch.send_nowait("c") is False  # Buffer full


async def test_channel_close():
    """Test channel closing."""
    ch = Channel(maxsize=10)

    await ch.send("last")
    ch.close()

    assert ch.closed is True

    # Can still receive queued value
    value = await ch.receive()
    assert value == "last"

    # Cannot send to closed channel
    with pytest.raises(RuntimeError, match="closed"):
        await ch.send("fail")


async def test_channel_len():
    """Test channel length."""
    ch = Channel(maxsize=10)

    assert len(ch) == 0
    await ch.send(1)
    assert len(ch) == 1
    await ch.send(2)
    assert len(ch) == 2
    await ch.receive()
    assert len(ch) == 1


async def test_channel_empty_full():
    """Test empty and full properties."""
    ch = Channel(maxsize=2)

    assert ch.empty is True
    assert ch.full is False

    await ch.send(1)
    assert ch.empty is False
    assert ch.full is False

    await ch.send(2)
    assert ch.empty is False
    assert ch.full is True


async def test_channel_timeout():
    """Test receive with timeout."""
    ch = Channel(maxsize=10)

    with pytest.raises(asyncio.TimeoutError):
        await ch.receive(timeout=0.01)


async def test_channel_concurrent():
    """Test concurrent send and receive."""
    ch = Channel(maxsize=0)  # Unbuffered
    results = []

    async def sender():
        for i in range(5):
            await ch.send(i)

    async def receiver():
        for _ in range(5):
            value = await ch.receive()
            results.append(value)

    await asyncio.gather(sender(), receiver())

    assert results == [0, 1, 2, 3, 4]


async def test_channel_repr():
    """Test channel string representation."""
    ch = Channel(maxsize=10)
    assert "open" in repr(ch)
    ch.close()
    assert "closed" in repr(ch)
