"""Channel implementation for LexFlow async communication.

Provides Go-style channels for communication between concurrent tasks,
particularly useful for Fork branches.
"""

import asyncio
from typing import Any, Optional, Tuple


class Channel:
    """An async channel for communication between concurrent tasks.

    Channels provide a way for concurrent code (Fork branches, spawned tasks)
    to communicate safely. They support buffered and unbuffered operation.

    Example:
        # Create a channel with buffer size 10
        ch = Channel(maxsize=10)

        # In one task:
        await ch.send("hello")

        # In another task:
        value = await ch.receive()

        # Close when done
        ch.close()
    """

    def __init__(self, maxsize: int = 0):
        """Create a new channel.

        Args:
            maxsize: Maximum items in buffer. 0 means unbuffered (synchronous).
        """
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._closed = False
        self._maxsize = maxsize

    @property
    def closed(self) -> bool:
        """Check if the channel is closed."""
        return self._closed

    async def send(self, value: Any) -> None:
        """Send a value through the channel.

        Blocks if the channel buffer is full (or immediately for unbuffered).

        Args:
            value: The value to send

        Raises:
            RuntimeError: If the channel is closed
        """
        if self._closed:
            raise RuntimeError("Cannot send to closed channel")
        await self._queue.put(value)

    def send_nowait(self, value: Any) -> bool:
        """Try to send a value without blocking.

        Args:
            value: The value to send

        Returns:
            True if sent, False if channel full or closed
        """
        if self._closed:
            return False
        try:
            self._queue.put_nowait(value)
            return True
        except asyncio.QueueFull:
            return False

    async def receive(self, timeout: Optional[float] = None) -> Any:
        """Receive a value from the channel.

        Blocks until a value is available or channel is closed.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            The received value

        Raises:
            asyncio.TimeoutError: If timeout exceeded
            RuntimeError: If channel is closed and empty
        """
        if timeout is not None:
            try:
                return await asyncio.wait_for(self._queue.get(), timeout=timeout)
            except asyncio.TimeoutError:
                raise
        else:
            # Check for closed empty channel
            if self._closed and self._queue.empty():
                raise RuntimeError("Channel closed")
            return await self._queue.get()

    def try_receive(self) -> Tuple[Any, bool]:
        """Try to receive a value without blocking.

        Returns:
            Tuple of (value, ok) where ok is True if a value was received
        """
        try:
            value = self._queue.get_nowait()
            return (value, True)
        except asyncio.QueueEmpty:
            return (None, False)

    def close(self) -> None:
        """Close the channel.

        After closing, no more values can be sent. Pending receives will
        continue to work until the channel is empty.
        """
        self._closed = True

    def __len__(self) -> int:
        """Get the number of items in the channel buffer."""
        return self._queue.qsize()

    @property
    def empty(self) -> bool:
        """Check if the channel buffer is empty."""
        return self._queue.empty()

    @property
    def full(self) -> bool:
        """Check if the channel buffer is full."""
        return self._queue.full() if self._maxsize > 0 else False

    def __repr__(self) -> str:
        status = "closed" if self._closed else "open"
        return f"Channel({status}, size={len(self)}/{self._maxsize})"
