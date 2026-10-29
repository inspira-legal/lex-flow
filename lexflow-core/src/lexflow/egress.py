"""Outbound guard for opcode HTTP sessions: only public addresses are reachable."""

import ipaddress
from typing import Any, List, Optional, Sequence

import aiohttp

BLOCKED_HOSTNAMES = {"metadata.google.internal"}

BLOCKED_NETWORKS = [
    ipaddress.ip_network(net)
    for net in (
        "0.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "224.0.0.0/4",
        "240.0.0.0/4",
        "::/128",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
        "ff00::/8",
    )
]


class BlockedDestinationError(aiohttp.ClientError):
    """The request targets an internal address (metadata server, private network)."""


def check_hostname(host: str) -> None:
    """Refuse hostnames that always point inside the platform."""
    if host.rstrip(".").lower() in BLOCKED_HOSTNAMES:
        raise BlockedDestinationError(
            f"Blocked request to '{host}': the cloud metadata server is not "
            "reachable from workflows. HTTP opcodes only reach public hosts."
        )


def check_address(host: str, address: str) -> None:
    """Refuse an address that falls in a blocked network."""
    ip = ipaddress.ip_address(address.split("%")[0])
    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    for net in BLOCKED_NETWORKS:
        if ip in net:
            raise BlockedDestinationError(
                f"Blocked request to '{host}': it resolves to {ip}, an internal "
                f"address ({net}). HTTP opcodes only reach public hosts."
            )


class GuardedConnector(aiohttp.TCPConnector):
    """TCPConnector that validates every address after DNS, before connecting.

    aiohttp connects to exactly the addresses returned here, so a hostname that
    re-resolves to an internal IP (DNS rebinding) and every redirect hop are
    checked on the IP actually used.
    """

    async def _resolve_host(
        self, host: str, port: int, traces: Optional[Sequence[Any]] = None
    ) -> List[Any]:
        check_hostname(host)
        hosts = await super()._resolve_host(host, port, traces=traces)
        for resolved in hosts:
            check_address(host, resolved["host"])
        return hosts
