"""Opcode clients must not leak aiohttp sessions, whatever the workflow does.

A `{node: x}` reference to a `*_create_client` reporter is re-evaluated on every
use, so a loop creates one client per call. The engine closes every session
opened during the run, on success, error or cancellation.
"""

import asyncio
import gc
from unittest.mock import patch

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from lexflow import Engine, Parser, default_registry
from lexflow.opcodes.opcodes_apollo import ApolloClient
from lexflow.opcodes.opcodes_clicksign import ClicksignClient
from lexflow.opcodes.opcodes_hubspot import HubSpotClient
from lexflow.sessions import RunSessions, current_run_sessions, open_session

pytestmark = pytest.mark.asyncio

CONTACT_IDS = ["1", "2", "3", "4", "5"]


@pytest.fixture
async def hubspot_server():
    """Local stand-in for the HubSpot API, recording each request's connection."""
    peers = []
    slow = asyncio.Event()

    async def get_contact(request):
        peers.append(request.transport.get_extra_info("peername"))
        if request.match_info["contact_id"] == "slow":
            slow.set()
            await asyncio.sleep(30)
        return web.json_response({"id": request.match_info["contact_id"]})

    app = web.Application()
    app.router.add_get("/crm/v3/objects/contacts/{contact_id}", get_contact)
    server = TestServer(app)
    await server.start_server()
    base_url = str(server.make_url("")).rstrip("/")
    with patch("lexflow.opcodes.opcodes_hubspot.HUBSPOT_API_BASE_URL", base_url):
        yield {"peers": peers, "slow": slow}
    await server.close()


@pytest.fixture
def opened_sessions(monkeypatch):
    """Every aiohttp.ClientSession created while the test runs."""
    sessions = []
    original_init = aiohttp.ClientSession.__init__

    def tracking_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        sessions.append(self)

    monkeypatch.setattr(aiohttp.ClientSession, "__init__", tracking_init)
    return sessions


@pytest.fixture
async def unclosed_reports():
    """Messages aiohttp reports for sessions garbage-collected while open."""
    loop = asyncio.get_running_loop()
    previous = loop.get_exception_handler()
    reports = []
    loop.set_exception_handler(lambda _loop, ctx: reports.append(ctx["message"]))
    yield reports
    loop.set_exception_handler(previous)


def _hubspot_loop_program(contact_ids, then=None):
    """main: for each id, hubspot_get_contact with client { node: hs_client }."""
    nodes = {
        "start": {"opcode": "workflow_start", "next": "loop"},
        "loop": {
            "opcode": "control_foreach",
            "next": then and "after",
            "kwargs": {
                "var": {"literal": "cid"},
                "iterable": {"literal": contact_ids},
                "body": {"branch": "fetch"},
            },
        },
        "fetch": {
            "opcode": "hubspot_get_contact",
            "kwargs": {
                "client": {"node": "hs_client"},
                "contact_id": {"variable": "cid"},
            },
        },
        "hs_client": {
            "opcode": "hubspot_create_client",
            "isReporter": True,
            "kwargs": {"access_token": {"literal": "test-token"}},
        },
    }
    if then:
        nodes["after"] = then
    return Parser().parse_dict({"workflows": [{"name": "main", "nodes": nodes}]})


class TestNoLeakedSessions:
    async def test_client_node_in_foreach_leaves_no_unclosed_session(
        self, hubspot_server, unclosed_reports
    ):
        await Engine(_hubspot_loop_program(CONTACT_IDS)).run()
        gc.collect()

        assert unclosed_reports == []

    async def test_every_session_opened_in_the_run_is_closed(
        self, hubspot_server, opened_sessions
    ):
        await Engine(_hubspot_loop_program(CONTACT_IDS)).run()

        assert len(opened_sessions) == len(CONTACT_IDS)
        assert all(s.closed for s in opened_sessions)

    async def test_clients_of_one_run_share_connections(self, hubspot_server):
        await Engine(_hubspot_loop_program(CONTACT_IDS)).run()

        assert len(hubspot_server["peers"]) == len(CONTACT_IDS)
        assert len(set(hubspot_server["peers"])) == 1

    async def test_sessions_closed_when_the_run_fails(
        self, hubspot_server, opened_sessions
    ):
        throw = {"opcode": "control_throw", "kwargs": {"value": {"literal": "boom"}}}
        engine = Engine(_hubspot_loop_program(CONTACT_IDS, then=throw))

        with pytest.raises(RuntimeError, match="boom"):
            await engine.run()

        assert len(opened_sessions) == len(CONTACT_IDS)
        assert all(s.closed for s in opened_sessions)

    async def test_sessions_closed_when_the_run_is_cancelled(
        self, hubspot_server, opened_sessions
    ):
        engine = Engine(_hubspot_loop_program(["1", "slow"]))
        run = asyncio.create_task(engine.run())
        await asyncio.wait_for(hubspot_server["slow"].wait(), timeout=5)

        run.cancel()
        with pytest.raises(asyncio.CancelledError):
            await run

        assert len(opened_sessions) == 2
        assert all(s.closed for s in opened_sessions)

    async def test_run_tracking_ends_with_the_run(self, hubspot_server):
        await Engine(_hubspot_loop_program(CONTACT_IDS)).run()

        assert current_run_sessions.get() is None


class TestLazySession:
    @pytest.mark.parametrize(
        "make_client",
        [
            lambda: HubSpotClient("token"),
            lambda: ApolloClient("key"),
            lambda: ClicksignClient("token"),
        ],
    )
    async def test_no_session_until_first_request(self, make_client, opened_sessions):
        client = make_client()

        assert client._session is None
        assert opened_sessions == []

    async def test_client_reused_after_run_reopens_its_session(self, hubspot_server):
        client = HubSpotClient("test-token")
        run = RunSessions()
        token = current_run_sessions.set(run)
        await client.get("/crm/v3/objects/contacts/1")
        current_run_sessions.reset(token)
        await run.close()

        assert await client.get("/crm/v3/objects/contacts/2") == {"id": "2"}
        await client.close()


class TestCloseClient:
    @pytest.mark.parametrize(
        "opcode_name, make_client",
        [
            ("hubspot_close_client", lambda: HubSpotClient("token")),
            ("apollo_close_client", lambda: ApolloClient("key")),
            ("clicksign_close_client", lambda: ClicksignClient("token")),
        ],
    )
    async def test_close_is_idempotent(self, opcode_name, make_client):
        client = make_client()
        assert await default_registry.call(opcode_name, [client]) is True

        session = client._get_session()
        assert await default_registry.call(opcode_name, [client]) is True
        assert await default_registry.call(opcode_name, [client]) is True
        assert session.closed

    async def test_close_inside_the_run_then_engine_close(
        self, hubspot_server, opened_sessions
    ):
        close = {
            "opcode": "hubspot_close_client",
            "kwargs": {"client": {"node": "hs_client"}},
        }
        await Engine(_hubspot_loop_program(["1"], then=close)).run()

        assert all(s.closed for s in opened_sessions)

    async def test_http_session_outside_control_with(self, opened_sessions):
        session = await default_registry.call("http_session_create", [])
        assert session._session is None
        await session.close()
        await session.close()
        assert opened_sessions == []


class TestOpenSession:
    async def test_untracked_outside_a_run(self):
        session = open_session()
        try:
            assert session.connector_owner
        finally:
            await session.close()

    async def test_tracked_and_closed_with_the_run(self):
        run = RunSessions()
        token = current_run_sessions.set(run)
        try:
            first, second = open_session(), open_session()
        finally:
            current_run_sessions.reset(token)

        assert first.connector is second.connector
        await run.close()
        assert first.closed and second.closed
        assert first.connector is None or first.connector.closed

    async def test_run_close_is_idempotent(self):
        run = RunSessions()
        run.open()
        await run.close()
        await run.close()
