"""Task-related opcodes for LexFlow async capabilities.

This module provides opcodes for working with background tasks spawned
via control_spawn, as well as channels for inter-task communication.
"""

import asyncio
from typing import Any, List, Optional

from .opcodes import default_registry
from ..channel import Channel


@default_registry.register()
async def task_is_done(task) -> bool:
    """Check if a background task has completed.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        True if task is done (completed, cancelled, or failed)
    """
    return task.done


@default_registry.register()
async def task_cancel(task) -> bool:
    """Request cancellation of a background task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        True if cancel was requested (task may still be running briefly)
    """
    if not task.done:
        task._task.cancel()
        return True
    return False


@default_registry.register()
async def task_await(task, timeout: Optional[float] = None) -> Any:
    """Wait for a background task to complete and get its result.

    Args:
        task: LexFlowTask handle from control_spawn
        timeout: Optional timeout in seconds

    Returns:
        The task's return value (usually None for spawn tasks)

    Raises:
        asyncio.TimeoutError: If timeout exceeded
        Exception: If the task raised an exception
    """
    return await asyncio.wait_for(task._task, timeout=timeout)


@default_registry.register()
async def task_await_all(tasks: List, timeout: Optional[float] = None) -> List[Any]:
    """Wait for multiple tasks to complete.

    Args:
        tasks: List of LexFlowTask handles
        timeout: Optional timeout in seconds for all tasks combined

    Returns:
        List of results in the same order as tasks

    Raises:
        asyncio.TimeoutError: If timeout exceeded
        Exception: If any task raised an exception
    """

    async def wait_all():
        return await asyncio.gather(*(t._task for t in tasks))

    return await asyncio.wait_for(wait_all(), timeout=timeout)


@default_registry.register()
async def task_result(task) -> Any:
    """Get the result of a completed task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's return value

    Raises:
        InvalidStateError: If task is not done
        Exception: If the task raised an exception
    """
    return task.result()


@default_registry.register()
async def task_exception(task) -> Optional[str]:
    """Get the exception message from a failed task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        Exception message as string, or None if task succeeded or not done
    """
    exc = task.exception()
    return str(exc) if exc else None


@default_registry.register()
async def task_sleep(seconds: float) -> None:
    """Sleep for the specified number of seconds.

    Args:
        seconds: Duration to sleep
    """
    await asyncio.sleep(seconds)


@default_registry.register()
async def task_yield() -> None:
    """Yield control to other tasks momentarily.

    Useful for cooperative multitasking when doing CPU-bound work
    in a background task.
    """
    await asyncio.sleep(0)


@default_registry.register()
async def task_id(task) -> int:
    """Get the ID of a task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's unique ID
    """
    return task.id


@default_registry.register()
async def task_name(task) -> str:
    """Get the name of a task.

    Args:
        task: LexFlowTask handle from control_spawn

    Returns:
        The task's name
    """
    return task.name


# ============ Channel Operations ============


@default_registry.register()
async def channel_create(size: int = 0) -> Channel:
    """Create a new channel for inter-task communication.

    Args:
        size: Buffer size (0 for unbuffered/synchronous)

    Returns:
        A new Channel object
    """
    return Channel(maxsize=size)


@default_registry.register()
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


@default_registry.register()
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


@default_registry.register()
async def channel_try_receive(channel: Channel) -> dict:
    """Try to receive a value without blocking.

    Args:
        channel: The channel to receive from

    Returns:
        Dict with keys:
        - value: The received value (None if nothing received)
        - ok: True if a value was received, False otherwise
    """
    value, ok = channel.try_receive()
    return {"value": value, "ok": ok}


@default_registry.register()
async def channel_close(channel: Channel) -> None:
    """Close a channel.

    After closing, no more values can be sent.

    Args:
        channel: The channel to close
    """
    channel.close()


@default_registry.register()
async def channel_len(channel: Channel) -> int:
    """Get the number of items in the channel buffer.

    Args:
        channel: The channel to check

    Returns:
        Number of items in buffer
    """
    return len(channel)


@default_registry.register()
async def channel_is_closed(channel: Channel) -> bool:
    """Check if a channel is closed.

    Args:
        channel: The channel to check

    Returns:
        True if closed
    """
    return channel.closed


@default_registry.register()
async def channel_is_empty(channel: Channel) -> bool:
    """Check if a channel buffer is empty.

    Args:
        channel: The channel to check

    Returns:
        True if empty
    """
    return channel.empty


# ============ Synchronization Primitives ============


@default_registry.register()
async def sync_semaphore_create(permits: int = 1) -> asyncio.Semaphore:
    """Create a semaphore for limiting concurrent access.

    Args:
        permits: Number of permits (1 for mutex)

    Returns:
        An asyncio.Semaphore
    """
    return asyncio.Semaphore(permits)


@default_registry.register()
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


@default_registry.register()
async def sync_semaphore_release(semaphore: asyncio.Semaphore) -> None:
    """Release a semaphore permit.

    Args:
        semaphore: The semaphore to release
    """
    semaphore.release()


@default_registry.register()
async def sync_event_create() -> asyncio.Event:
    """Create an event for signaling between tasks.

    Returns:
        An asyncio.Event
    """
    return asyncio.Event()


@default_registry.register()
async def sync_event_set(event: asyncio.Event) -> None:
    """Set an event (signal waiting tasks).

    Args:
        event: The event to set
    """
    event.set()


@default_registry.register()
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


@default_registry.register()
async def sync_event_clear(event: asyncio.Event) -> None:
    """Clear an event (reset to unset state).

    Args:
        event: The event to clear
    """
    event.clear()


@default_registry.register()
async def sync_event_is_set(event: asyncio.Event) -> bool:
    """Check if an event is set.

    Args:
        event: The event to check

    Returns:
        True if set
    """
    return event.is_set()
