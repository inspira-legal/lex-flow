"""Integration test: run the full contrato_envio.yaml workflow with mocked APIs.

This test loads the actual workflow YAML and runs it end-to-end through
the LexFlow engine, mocking all HTTP calls to ReceitaWS and Clicksign sandbox.

Both opcodes modules import the same `aiohttp` module, so we use a single
patch on `aiohttp.ClientSession` with a side_effect that routes by caller:
  - ReceitaWS: uses `async with aiohttp.ClientSession() as session: session.get(url)`
  - Clicksign: uses `aiohttp.ClientSession(headers={...})` stored as `_session`
"""

import importlib.util
import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lexflow import Engine, Parser

AIOHTTP_AVAILABLE = importlib.util.find_spec("aiohttp") is not None

pytestmark = pytest.mark.asyncio

WORKFLOW_PATH = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "integrations"
    / "clicksign"
    / "contrato_envio.yaml"
)

# ============================================================================
# Mock data — simulates API responses
# ============================================================================

RECEITAWS_RESPONSE = {
    "status": "OK",
    "nome": "INSPIRA TECNOLOGIA LTDA",
    "fantasia": "INSPIRA TECH",
    "cnpj": "11222333000181",
    "logradouro": "Rua das Flores, 100",
    "municipio": "Sao Paulo",
    "uf": "SP",
    "situacao": "ATIVA",
}

ENVELOPE_RESPONSE = {
    "data": {
        "id": "env-fake-001",
        "type": "envelopes",
        "attributes": {"name": "Contrato - INSPIRA TECNOLOGIA LTDA", "status": "draft"},
    }
}

DOCUMENT_RESPONSE = {
    "data": {
        "id": "doc-fake-001",
        "type": "documents",
        "attributes": {"filename": "contrato_11.222.333/0001-81.pdf"},
    }
}

SIGNER_IDS = [
    "signer-cliente-001",
    "signer-caue-002",
    "signer-gabriel-003",
    "signer-thay-004",
]

REQUIREMENT_RESPONSE = {
    "data": {"id": "req-fake-001", "type": "requirements", "attributes": {}}
}

ACTIVATE_RESPONSE = {
    "data": {
        "id": "env-fake-001",
        "type": "envelopes",
        "attributes": {"status": "running"},
    }
}

NOTIFY_RESPONSE = {
    "data": {"id": "notif-fake-001", "type": "notifications", "attributes": {}}
}


# ============================================================================
# Helpers
# ============================================================================


def _make_signer_response(signer_id):
    return {
        "data": {
            "id": signer_id,
            "type": "signers",
            "attributes": {"name": "Signer", "email": "s@e.com"},
        }
    }


def _mock_clicksign_request(signer_ids):
    """Build a mock for ClicksignClient._session.request that routes by endpoint."""
    signer_index = {"idx": 0}

    def _route(method, url, **kwargs):
        if method == "POST" and "/envelopes/" in url and "/documents" in url:
            json_data = DOCUMENT_RESPONSE
        elif method == "POST" and "/signers" in url:
            sid = signer_ids[signer_index["idx"] % len(signer_ids)]
            signer_index["idx"] += 1
            json_data = _make_signer_response(sid)
        elif method == "POST" and "/requirements" in url:
            json_data = REQUIREMENT_RESPONSE
        elif method == "PATCH" and "/envelopes/" in url:
            json_data = ACTIVATE_RESPONSE
        elif method == "POST" and "/notifications" in url:
            json_data = NOTIFY_RESPONSE
        elif method == "POST" and url.endswith("/envelopes"):
            json_data = ENVELOPE_RESPONSE
        else:
            json_data = {}

        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value=json_data)

        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=response)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx

    return MagicMock(side_effect=_route)


def _make_clicksign_session(signer_ids):
    """Create a mock aiohttp session for Clicksign (used as _session attribute)."""
    session = MagicMock()
    session.request = _mock_clicksign_request(signer_ids)
    session.close = AsyncMock()
    return session


def _make_receitaws_session():
    """Create a mock aiohttp session for ReceitaWS (used as async context manager).

    ReceitaWS: async with aiohttp.ClientSession() as session:
                   async with session.get(url) as response:
    """
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value=RECEITAWS_RESPONSE)

    get_ctx = MagicMock()
    get_ctx.__aenter__ = AsyncMock(return_value=response)
    get_ctx.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.get = MagicMock(return_value=get_ctx)
    return session


def _build_unified_client_session(clicksign_session, receitaws_session):
    """Build a single aiohttp.ClientSession mock that routes by call pattern.

    - Clicksign calls: ClientSession(headers={...}) → returns clicksign_session
    - ReceitaWS calls: ClientSession() used as async context manager → returns receitaws_session
    """

    class UnifiedSession:
        """Dual-purpose mock: works as constructor return AND async context manager."""

        def __init__(self_, **kwargs):
            # Clicksign passes headers=; ReceitaWS passes nothing
            self_._is_clicksign = "headers" in kwargs

        async def __aenter__(self_):
            # Only ReceitaWS uses `async with ClientSession() as session:`
            return receitaws_session

        async def __aexit__(self_, *args):
            return False

        def __getattr__(self_, name):
            # Clicksign accesses .request, .close, etc. directly
            return getattr(clicksign_session, name)

    return UnifiedSession


def _build_failing_client_session(receitaws_session):
    """Build a ClientSession mock where Clicksign API always returns 401."""

    def _fail_request(method, url, **kwargs):
        error_response = AsyncMock()
        error_response.status = 401
        error_response.json = AsyncMock(
            return_value={
                "errors": [{"detail": "Invalid access token", "code": "unauthorized"}]
            }
        )
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=error_response)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx

    failing_session = MagicMock()
    failing_session.request = MagicMock(side_effect=_fail_request)
    failing_session.close = AsyncMock()

    return _build_unified_client_session(failing_session, receitaws_session)


WORKFLOW_INPUTS = {
    "clicksign_token": "fake-sandbox-token",
    "cnpj": "11.222.333/0001-81",
    "num_usuarios": 10,
    "mrr": 5000,
    "signatario_nome": "Maria Silva",
    "signatario_email": "maria@empresa.com",
    "template_id": "tmpl-fake-001",
    "data_limite": "2025-12-31T23:59:59-03:00",
}


# ============================================================================
# Tests
# ============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestContratoEnvioWorkflow:
    async def test_full_workflow_execution(self):
        """Run contrato_envio.yaml end-to-end with mocked APIs."""
        assert WORKFLOW_PATH.exists(), f"Workflow not found: {WORKFLOW_PATH}"

        parser = Parser()
        program = parser.parse_file(str(WORKFLOW_PATH))
        output = io.StringIO()

        cs_session = _make_clicksign_session(SIGNER_IDS)
        rw_session = _make_receitaws_session()
        unified = _build_unified_client_session(cs_session, rw_session)

        with patch("aiohttp.ClientSession", unified):
            engine = Engine(program, output=output)
            await engine.run(inputs=WORKFLOW_INPUTS)

        printed = output.getvalue()

        # Verify the full flow executed correctly
        assert "Envio de Contrato via Clicksign" in printed
        assert "INSPIRA TECNOLOGIA LTDA" in printed
        assert "Cliente Clicksign criado" in printed
        assert "Envelope criado: env-fake-001" in printed
        assert "Documento adicionado: doc-fake-001" in printed
        assert "Signatario cliente adicionado: Maria Silva" in printed
        assert "Signatario interno adicionado: Caue Silva" in printed
        assert "Signatario interno adicionado: Gabriel Santos" in printed
        assert "Signatario interno adicionado: Thay Oliveira" in printed
        assert "Envelope ativado" in printed
        assert "Contrato enviado com sucesso" in printed
        assert "Cliente Clicksign fechado" in printed

    async def test_workflow_handles_api_error(self):
        """Verify try/catch handles Clicksign API errors gracefully."""
        assert WORKFLOW_PATH.exists()

        parser = Parser()
        program = parser.parse_file(str(WORKFLOW_PATH))
        output = io.StringIO()

        rw_session = _make_receitaws_session()
        unified = _build_failing_client_session(rw_session)

        with patch("aiohttp.ClientSession", unified):
            engine = Engine(program, output=output)
            await engine.run(
                inputs={**WORKFLOW_INPUTS, "clicksign_token": "invalid-token"}
            )

        printed = output.getvalue()

        # Should hit the error handler and still close the client
        assert "ERRO no envio do contrato" in printed
        assert "Cliente Clicksign fechado" in printed
