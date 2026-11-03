import ipaddress

import pytest

from lexflow import egress

LOOPBACK = [ipaddress.ip_network("127.0.0.0/8"), ipaddress.ip_network("::1/128")]


@pytest.fixture
def allow_loopback(monkeypatch):
    """Let opcode sessions reach the local test servers (loopback is blocked in production)."""
    allowed = [net for net in egress.BLOCKED_NETWORKS if net not in LOOPBACK]
    monkeypatch.setattr(egress, "BLOCKED_NETWORKS", allowed)
