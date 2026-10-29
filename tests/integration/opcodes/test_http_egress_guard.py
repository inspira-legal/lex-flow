"""http_* opcodes refuse internal destinations: metadata server, loopback, private networks.

The check runs on the address aiohttp actually connects to, after DNS and on every
redirect hop (WAVE-988).
"""

import functools
import socket

import pytest
from aiohttp import web
from aiohttp.abc import AbstractResolver
from aiohttp.test_utils import TestServer

from lexflow import Engine, Parser, default_registry, sessions
from lexflow.egress import (
    BlockedDestinationError,
    GuardedConnector,
    check_address,
    check_hostname,
)

pytestmark = pytest.mark.asyncio

BLOCKED_ADDRESSES = [
    ("metadata", "169.254.169.254"),
    ("link-local", "169.254.1.1"),
    ("loopback", "127.0.0.1"),
    ("private 10/8", "10.20.30.40"),
    ("private 172.16/12", "172.16.0.1"),
    ("private 192.168/16", "192.168.1.1"),
    ("cgnat", "100.64.0.1"),
    ("this network", "0.0.0.0"),
    ("multicast", "224.0.0.1"),
    ("reserved", "240.0.0.1"),
    ("ipv6 loopback", "::1"),
    ("ipv6 unspecified", "::"),
    ("ipv6 link-local", "fe80::1"),
    ("ipv6 link-local with zone", "fe80::1%eth0"),
    ("ipv6 unique local", "fd00::1"),
    ("ipv6 multicast", "ff02::1"),
    ("ipv4-mapped metadata", "::ffff:169.254.169.254"),
    ("ipv4-mapped private", "::ffff:10.0.0.1"),
    ("ipv4-compatible", "::127.0.0.1"),
    ("nat64 metadata", "64:ff9b::a9fe:a9fe"),
    ("6to4 loopback", "2002:7f00:1::"),
    ("teredo", "2001:0:4136:e378::1"),
]


class StaticResolver(AbstractResolver):
    """Resolve hostnames from a fixed table, like a DNS answer the attacker controls."""

    def __init__(self, table):
        self.table = table

    async def resolve(self, host, port=0, family=socket.AF_INET):
        if host not in self.table:
            raise OSError(f"no fake DNS entry for {host}")
        return [
            {
                "hostname": host,
                "host": self.table[host],
                "port": port,
                "family": socket.AF_INET,
                "proto": 0,
                "flags": socket.AI_NUMERICHOST,
            }
        ]

    async def close(self):
        pass


@pytest.fixture
def fake_dns(monkeypatch):
    """Route opcode sessions through a static DNS table."""
    table = {}
    connector = functools.partial(GuardedConnector, resolver=StaticResolver(table))
    monkeypatch.setattr(sessions, "GuardedConnector", connector)
    return table


@pytest.fixture
async def local_server():
    """Local HTTP server with an /ok route and a /redirect route to ?to=<url>."""

    async def ok(request):
        return web.json_response({"ok": True})

    async def redirect(request):
        raise web.HTTPFound(request.query["to"])

    app = web.Application()
    app.router.add_get("/ok", ok)
    app.router.add_get("/redirect", redirect)
    server = TestServer(app, host="127.0.0.1")
    await server.start_server()
    yield server
    await server.close()


class TestAddressCheck:
    @pytest.mark.parametrize(
        "address",
        [a for _, a in BLOCKED_ADDRESSES],
        ids=[n for n, _ in BLOCKED_ADDRESSES],
    )
    def test_blocked_address(self, address):
        with pytest.raises(BlockedDestinationError, match="internal address"):
            check_address("evil.example", address)

    @pytest.mark.parametrize("address", ["8.8.8.8", "1.1.1.1", "2001:4860:4860::8888"])
    def test_public_address_passes(self, address):
        check_address("api.example.com", address)

    @pytest.mark.parametrize(
        "host",
        [
            "metadata.google.internal",
            "metadata",
            "metadata.google.internal.",
            "METADATA.google.internal",
        ],
    )
    def test_metadata_hostname_blocked(self, host):
        with pytest.raises(BlockedDestinationError, match="metadata server"):
            check_hostname(host)


class TestHttpOpcodesRefuseInternalDestinations:
    @pytest.mark.parametrize(
        "opcode,args",
        [
            ("http_get", ["http://169.254.169.254/computeMetadata/v1/"]),
            ("http_post", ["http://10.20.30.40:6379/"]),
            ("http_post_json", ["http://127.0.0.1:8080/", {"a": 1}]),
            ("http_post_data", ["http://192.168.0.10/", "x=1"]),
            ("http_request", ["PUT", "http://[::1]:8080/"]),
            ("http_request", ["GET", "http://[::ffff:169.254.169.254]/"]),
        ],
    )
    async def test_literal_internal_ip_is_refused(self, opcode, args):
        with pytest.raises(BlockedDestinationError):
            await default_registry.call(opcode, args)

    async def test_metadata_hostname_is_refused(self):
        with pytest.raises(BlockedDestinationError, match="metadata server"):
            await default_registry.call(
                "http_get", ["http://metadata.google.internal/computeMetadata/v1/"]
            )

    async def test_hostname_resolving_to_internal_ip_is_refused(self, fake_dns):
        fake_dns["rebind.example"] = "10.20.30.40"
        with pytest.raises(BlockedDestinationError, match="rebind.example"):
            await default_registry.call("http_get", ["http://rebind.example/"])

    @pytest.mark.usefixtures("allow_loopback")
    async def test_redirect_to_internal_is_refused(self, local_server):
        url = str(local_server.make_url("/redirect"))
        target = "http://169.254.169.254/computeMetadata/v1/"
        with pytest.raises(BlockedDestinationError, match="169.254.169.254"):
            await default_registry.call("http_get", [f"{url}?to={target}"])

    @pytest.mark.usefixtures("allow_loopback")
    async def test_redirect_to_hostname_resolving_internal_is_refused(
        self, local_server, fake_dns
    ):
        fake_dns["public.example"] = "127.0.0.1"
        fake_dns["rebind.example"] = "10.0.0.5"
        url = f"http://public.example:{local_server.port}/redirect"
        with pytest.raises(BlockedDestinationError, match="rebind.example"):
            await default_registry.call(
                "http_get", [f"{url}?to=http://rebind.example/"]
            )

    @pytest.mark.usefixtures("allow_loopback")
    async def test_public_destination_passes(self, local_server, fake_dns):
        # public.example stands for a public host: loopback is allowed in this test only
        fake_dns["public.example"] = "127.0.0.1"
        result = await default_registry.call(
            "http_get", [f"http://public.example:{local_server.port}/ok"]
        )
        assert result["status"] == 200
        assert result["json"] == {"ok": True}

    async def test_refused_inside_a_run_with_a_clear_error(self):
        program = Parser().parse_dict(
            {
                "workflows": [
                    {
                        "name": "main",
                        "nodes": {
                            "start": {"opcode": "workflow_start", "next": "fetch"},
                            "fetch": {
                                "opcode": "http_get",
                                "kwargs": {
                                    "url": {
                                        "literal": "http://169.254.169.254/computeMetadata/v1/?token=s3cret"
                                    }
                                },
                            },
                        },
                    }
                ]
            }
        )
        with pytest.raises(BlockedDestinationError) as err:
            await Engine(program).run()
        message = str(err.value)
        assert "only reach public hosts" in message
        assert "s3cret" not in message
