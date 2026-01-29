"""Task management for LexFlow background tasks.

This module provides infrastructure for spawning and managing background tasks
within LexFlow workflows.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional
from itertools import count


@dataclass
class LexFlowTask:
    """A background task handle."""

    id: int
    name: str
    _task: asyncio.Task = field(repr=False)

    @property
    def done(self) -> bool:
        """Check if the task has completed."""
        return self._task.done()

    @property
    def cancelled(self) -> bool:
        """Check if the task was cancelled."""
        return self._task.cancelled()

    def result(self) -> Any:
        """Get the task result. Raises exception if task failed or not done."""
        return self._task.result()

    def exception(self) -> Optional[BaseException]:
        """Get the task exception, or None if task succeeded or not done."""
        if not self._task.done():
            return None
        try:
            self._task.result()
            return None
        except asyncio.CancelledError:
            return None
        except BaseException as e:
            return e


class TaskManager:
    """Manages background tasks for a workflow execution."""

    def __init__(self):
        self._tasks: dict[int, LexFlowTask] = {}
        self._id_counter = count(1)

    def spawn(self, coro, name: str = "") -> LexFlowTask:
        """Spawn a coroutine as a background task.

        Args:
            coro: The coroutine to run in the background
            name: Optional name for the task

        Returns:
            LexFlowTask handle for tracking the task
        """
        task_id = next(self._id_counter)
        task_name = name or f"task_{task_id}"
        asyncio_task = asyncio.create_task(coro, name=task_name)
        lex_task = LexFlowTask(id=task_id, name=task_name, _task=asyncio_task)
        self._tasks[task_id] = lex_task
        return lex_task

    def cancel(self, task_id: int) -> bool:
        """Cancel a task by ID.

        Args:
            task_id: The task ID to cancel

        Returns:
            True if task was found and cancel requested, False if not found
        """
        if task_id not in self._tasks:
            return False
        task = self._tasks[task_id]
        if not task.done:
            task._task.cancel()
        return True

    async def wait(self, task_id: int, timeout: Optional[float] = None) -> Any:
        """Wait for a task to complete and return its result.

        Args:
            task_id: The task ID to wait for
            timeout: Optional timeout in seconds

        Returns:
            The task's return value

        Raises:
            KeyError: If task not found
            asyncio.TimeoutError: If timeout exceeded
            Exception: If the task raised an exception
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task {task_id} not found")
        task = self._tasks[task_id]
        return await asyncio.wait_for(task._task, timeout=timeout)

    def get(self, task_id: int) -> Optional[LexFlowTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[LexFlowTask]:
        """List all tracked tasks."""
        return list(self._tasks.values())

    async def cleanup(self) -> None:
        """Cancel all running tasks and wait for them to finish."""
        for task in self._tasks.values():
            if not task.done:
                task._task.cancel()

        # Wait for all tasks to complete (cancelled or otherwise)
        if self._tasks:
            await asyncio.gather(
                *(t._task for t in self._tasks.values()), return_exceptions=True
            )
        self._tasks.clear()
