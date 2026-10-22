"""aiohttp sessions opened by opcode clients, closed by the engine at end of run."""

import asyncio
from contextvars import ContextVar
from typing import Any, List, Optional

import aiohttp


class RunSessions:
    """Sessions opened during one run, sharing one connection pool."""

    def __init__(self):
        self._sessions: List[aiohttp.ClientSession] = []
        self._connector: Optional[aiohttp.TCPConnector] = None

    def open(self, **kwargs: Any) -> aiohttp.ClientSession:
        """Open a session on the run's connector and track it."""
        if self._connector is None:
            self._connector = aiohttp.TCPConnector()
        session = aiohttp.ClientSession(
            connector=self._connector, connector_owner=False, **kwargs
        )
        # Clients closed mid-run (e.g. one per loop iteration) are dropped here
        self._sessions = [s for s in self._sessions if not s.closed]
        self._sessions.append(session)
        return session

    async def close(self) -> None:
        """Close every tracked session, then the shared connector."""
        sessions, self._sessions = self._sessions, []
        # A failing close must not mask the run's own result or error
        await asyncio.gather(*(s.close() for s in sessions), return_exceptions=True)
        if self._connector is not None:
            connector, self._connector = self._connector, None
            await asyncio.gather(connector.close(), return_exceptions=True)


current_run_sessions: ContextVar[Optional[RunSessions]] = ContextVar(
    "current_run_sessions", default=None
)


def open_session(**kwargs: Any) -> aiohttp.ClientSession:
    """Open a ClientSession, tracked by the current run when there is one."""
    run = current_run_sessions.get()
    if run is None:
        return aiohttp.ClientSession(**kwargs)
    return run.open(**kwargs)
