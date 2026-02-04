"""Task-related opcodes for LexFlow async capabilities.

This module provides opcodes for working with background tasks spawned
via control_spawn, as well as channels for inter-task communication.
No external dependencies - uses standard library only.
"""

import asyncio
from typing import Any, List, Optional

from .opcodes import opcode, register_category
from ..channel import Channel

# Register category at module load time
register_category(
    id="task",
    label="Task Operations",
    prefix="task_",
    color="#0EA5E9",
    icon="⚡",
    order=270,
)

register_category(
    id="channel",
    label="Channel Operations",
    prefix="channel_",
    color="#14B8A6",
    icon="📡",
    order=271,
)

register_category(
    id="sync",
    label="Sync Primitives",
    prefix="sync_",
    color="#A855F7",
    icon="🔒",
    order=272,
)


# ============================================================================
# Task Operations
# ============================================================================


@opcode(category="task")
async def task_is_done(task) -> bool:
    """Check if a background task has completed.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        True if task is done (completed, cancelled, or failed)
    """
    return task.done


@opcode(category="task")
async def task_cancel(task) -> bool:
    """Request cancellation of a background task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        True if cancel was requested
    """
    if not task.done:
        task._task.cancel()
        return True
    return False


@opcode(category="task")
async def task_await(task, timeout: Optional[float] = None) -> Any:
    """Wait for a background task to complete and get its result.

    Args:
        task: LexFlowTask handle from control_spawn
        timeout: Optional timeout in seconds

    Returns:
        The task's return value

    Raises:
        asyncio.TimeoutError: If timeout exceeded
        Exception: If the task raised an exception
    """
    return await asyncio.wait_for(task._task, timeout=timeout)


@opcode(category="task")
async def task_await_all(tasks: List, timeout: Optional[float] = None) -> List[Any]:
    """Wait for multiple tasks to complete.

    Args:
        tasks: List of LexFlowTask handles
        timeout: Optional timeout in seconds

    Returns:
        List of results in the same order as tasks
    """

    async def wait_all():
        return await asyncio.gather(*(t._task for t in tasks))

    return await asyncio.wait_for(wait_all(), timeout=timeout)


@opcode(category="task")
async def task_result(task) -> Any:
    """Get the result of a completed task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's return value

    Raises:
        InvalidStateError: If task is not done
    """
    return task.result()


@opcode(category="task")
async def task_exception(task) -> Optional[str]:
    """Get the exception message from a failed task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        Exception message as string, or None if succeeded/not done
    """
    exc = task.exception()
    return str(exc) if exc else None


@opcode(category="task")
async def task_sleep(seconds: float) -> None:
    """Sleep for the specified number of seconds.

    Args:
        seconds: Duration to sleep
    """
    await asyncio.sleep(seconds)


@opcode(category="task")
async def task_yield() -> None:
    """Yield control to other tasks momentarily."""
    await asyncio.sleep(0)


@opcode(category="task")
async def task_id(task) -> int:
    """Get the ID of a task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's unique ID
    """
    return task.id


@opcode(category="task")
async def task_name(task) -> str:
    """Get the name of a task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's name
    """
    return task.name


# ============================================================================
# Channel Operations
# ============================================================================


@opcode(category="channel")
async def channel_create(size: int = 0) -> Channel:
    """Create a new channel for inter-task communication.

    Args:
        size: Buffer size (0 for unbuffered/synchronous)

    Returns:
        A new Channel object
    """
    return Channel(maxsize=size)


@opcode(category="channel")
async def channel_send(channel: Channel, value: Any) -> None:
    """Send a value through a channel.

    Blocks if the channel buffer is full.

    Args:
        channel: The channel to send to
        value: The value to send

    Raises:
        RuntimeError: If the channel is closed
    """
    await channel.send(value)


@opcode(category="channel")
async def channel_receive(channel: Channel, timeout: Optional[float] = None) -> Any:
    """Receive a value from a channel.

    Blocks until a value is available.

    Args:
        channel: The channel to receive from
        timeout: Optional timeout in seconds

    Returns:
        The received value

    Raises:
        asyncio.TimeoutError: If timeout exceeded
        RuntimeError: If channel is closed and empty
    """
    return await channel.receive(timeout=timeout)


@opcode(category="channel")
async def channel_try_receive(channel: Channel) -> dict:
    """Try to receive a value without blocking.

    Args:
        channel: The channel to receive from

    Returns:
        Dict with keys: value, ok (True if received)
    """
    value, ok = channel.try_receive()
    return {"value": value, "ok": ok}


@opcode(category="channel")
async def channel_close(channel: Channel) -> None:
    """Close a channel.

    Args:
        channel: The channel to close
    """
    channel.close()


@opcode(category="channel")
async def channel_len(channel: Channel) -> int:
    """Get the number of items in the channel buffer.

    Args:
        channel: The channel to check

    Returns:
        Number of items in buffer
    """
    return len(channel)


@opcode(category="channel")
async def channel_is_closed(channel: Channel) -> bool:
    """Check if a channel is closed.

    Args:
        channel: The channel to check

    Returns:
        True if closed
    """
    return channel.closed


@opcode(category="channel")
async def channel_is_empty(channel: Channel) -> bool:
    """Check if a channel buffer is empty.

    Args:
        channel: The channel to check

    Returns:
        True if empty
    """
    return channel.empty


# ============================================================================
# Synchronization Primitives
# ============================================================================


@opcode(category="sync")
async def sync_semaphore_create(permits: int = 1) -> asyncio.Semaphore:
    """Create a semaphore for limiting concurrent access.

    Args:
        permits: Number of permits (1 for mutex)

    Returns:
        An asyncio.Semaphore
    """
    return asyncio.Semaphore(permits)


@opcode(category="sync")
async def sync_semaphore_acquire(
    semaphore: asyncio.Semaphore, timeout: Optional[float] = None
) -> bool:
    """Acquire a semaphore permit.

    Args:
        semaphore: The semaphore to acquire
        timeout: Optional timeout in seconds

    Returns:
        True if acquired, False if timeout
    """
    if timeout is not None:
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
    else:
        await semaphore.acquire()
        return True


@opcode(category="sync")
async def sync_semaphore_release(semaphore: asyncio.Semaphore) -> None:
    """Release a semaphore permit.

    Args:
        semaphore: The semaphore to release
    """
    semaphore.release()


@opcode(category="sync")
async def sync_event_create() -> asyncio.Event:
    """Create an event for signaling between tasks.

    Returns:
        An asyncio.Event
    """
    return asyncio.Event()


@opcode(category="sync")
async def sync_event_set(event: asyncio.Event) -> None:
    """Set an event (signal waiting tasks).

    Args:
        event: The event to set
    """
    event.set()


@opcode(category="sync")
async def sync_event_wait(
    event: asyncio.Event, timeout: Optional[float] = None
) -> bool:
    """Wait for an event to be set.

    Args:
        event: The event to wait for
        timeout: Optional timeout in seconds

    Returns:
        True if event was set, False if timeout
    """
    if timeout is not None:
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
    else:
        await event.wait()
        return True


@opcode(category="sync")
async def sync_event_clear(event: asyncio.Event) -> None:
    """Clear an event (reset to unset state).

    Args:
        event: The event to clear
    """
    event.clear()


@opcode(category="sync")
async def sync_event_is_set(event: asyncio.Event) -> bool:
    """Check if an event is set.

    Args:
        event: The event to check

    Returns:
        True if set
    """
    return event.is_set()
