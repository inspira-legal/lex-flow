"""Unit tests for task management."""

import asyncio
import pytest

from lexflow.tasks import LexFlowTask, TaskManager


pytestmark = pytest.mark.asyncio


async def test_task_manager_spawn():
    """Test spawning a task."""
    manager = TaskManager()

    async def worker():
        await asyncio.sleep(0.01)
        return "done"

    task = manager.spawn(worker(), name="test_task")

    assert isinstance(task, LexFlowTask)
    assert task.id == 1
    assert task.name == "test_task"
    assert not task.done

    # Wait for completion
    await task._task
    assert task.done
    assert task.result() == "done"

    await manager.cleanup()


async def test_task_manager_multiple_tasks():
    """Test spawning multiple tasks."""
    manager = TaskManager()
    results = []

    async def worker(n):
        await asyncio.sleep(0.01)
        results.append(n)

    task1 = manager.spawn(worker(1), name="task1")
    task2 = manager.spawn(worker(2), name="task2")
    task3 = manager.spawn(worker(3), name="task3")

    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3

    # Wait for all
    await asyncio.gather(task1._task, task2._task, task3._task)

    assert 1 in results
    assert 2 in results
    assert 3 in results

    await manager.cleanup()


async def test_task_manager_cancel():
    """Test canceling a task."""
    manager = TaskManager()

    async def slow_worker():
        await asyncio.sleep(10)

    task = manager.spawn(slow_worker(), name="slow")

    assert manager.cancel(task.id)
    await asyncio.sleep(0.01)
    assert task.done
    assert task.cancelled

    await manager.cleanup()


async def test_task_manager_wait():
    """Test waiting for a task."""
    manager = TaskManager()

    async def worker():
        await asyncio.sleep(0.01)
        return 42

    task = manager.spawn(worker(), name="test")
    result = await manager.wait(task.id)

    assert result == 42

    await manager.cleanup()


async def test_task_manager_wait_timeout():
    """Test waiting with timeout."""
    manager = TaskManager()

    async def slow_worker():
        await asyncio.sleep(10)

    task = manager.spawn(slow_worker(), name="slow")

    with pytest.raises(asyncio.TimeoutError):
        await manager.wait(task.id, timeout=0.01)

    await manager.cleanup()


async def test_task_exception():
    """Test getting exception from failed task."""
    manager = TaskManager()

    async def failing_worker():
        raise ValueError("test error")

    task = manager.spawn(failing_worker(), name="failing")

    await asyncio.sleep(0.01)
    assert task.done
    exc = task.exception()
    assert exc is not None
    assert "test error" in str(exc)

    await manager.cleanup()


async def test_task_manager_cleanup():
    """Test cleanup cancels all running tasks."""
    manager = TaskManager()

    async def slow_worker():
        await asyncio.sleep(10)

    task1 = manager.spawn(slow_worker(), name="slow1")
    task2 = manager.spawn(slow_worker(), name="slow2")

    await manager.cleanup()

    assert task1.done
    assert task2.done


async def test_task_manager_list_tasks():
    """Test listing all tasks."""
    manager = TaskManager()

    async def worker():
        await asyncio.sleep(0.1)

    manager.spawn(worker(), name="task1")
    manager.spawn(worker(), name="task2")

    tasks = manager.list_tasks()
    assert len(tasks) == 2
    assert tasks[0].name == "task1"
    assert tasks[1].name == "task2"

    await manager.cleanup()


async def test_task_manager_get():
    """Test getting a task by ID."""
    manager = TaskManager()

    async def worker():
        await asyncio.sleep(0.1)

    task = manager.spawn(worker(), name="test")

    retrieved = manager.get(task.id)
    assert retrieved is task
    assert manager.get(999) is None

    await manager.cleanup()
