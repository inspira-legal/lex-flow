"""Tests for ReceitaWS CNPJ lookup opcodes."""

import importlib.util

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lexflow import default_registry

AIOHTTP_AVAILABLE = importlib.util.find_spec("aiohttp") is not None

pytestmark = pytest.mark.asyncio


# ============================================================================
# Helpers
# ============================================================================


def _mock_aiohttp_response(status=200, json_data=None):
    """Create a mock aiohttp response."""
    response = AsyncMock()
    response.status = status
    response.json = AsyncMock(return_value=json_data or {})

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


def _mock_aiohttp_session(response_ctx):
    """Create a mock aiohttp.ClientSession."""
    session = MagicMock()
    session.get = MagicMock(return_value=response_ctx)

    session_ctx = MagicMock()
    session_ctx.__aenter__ = AsyncMock(return_value=session)
    session_ctx.__aexit__ = AsyncMock(return_value=False)
    return session_ctx


# ============================================================================
# ReceitaWS Consulta CNPJ
# ============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestReceitawsConsultaCnpj:
    async def test_strips_non_digit_characters(self):
        company_data = {
            "status": "OK",
            "nome": "Empresa Teste LTDA",
            "cnpj": "12345678000100",
        }
        response_ctx = _mock_aiohttp_response(200, company_data)
        session_ctx = _mock_aiohttp_session(response_ctx)

        with patch(
            "lexflow_opcodes.receitaws.aiohttp.ClientSession",
            return_value=session_ctx,
        ):
            result = await default_registry.call(
                "receitaws_consulta_cnpj", ["12.345.678/0001-00"]
            )

        assert result["cnpj"] == "12345678000100"
        # Verify the URL used stripped digits
        session = await session_ctx.__aenter__()
        session.get.assert_called_once()
        call_url = session.get.call_args[0][0]
        assert "12345678000100" in call_url

    async def test_valid_cnpj_returns_company_data(self):
        company_data = {
            "status": "OK",
            "nome": "Empresa Teste LTDA",
            "fantasia": "Empresa Teste",
            "cnpj": "11222333000181",
            "situacao": "ATIVA",
            "tipo": "MATRIZ",
        }
        response_ctx = _mock_aiohttp_response(200, company_data)
        session_ctx = _mock_aiohttp_session(response_ctx)

        with patch(
            "lexflow_opcodes.receitaws.aiohttp.ClientSession",
            return_value=session_ctx,
        ):
            result = await default_registry.call(
                "receitaws_consulta_cnpj", ["11222333000181"]
            )

        assert result["status"] == "OK"
        assert result["nome"] == "Empresa Teste LTDA"
        assert result["fantasia"] == "Empresa Teste"
        assert result["situacao"] == "ATIVA"

    async def test_invalid_cnpj_length_raises_error(self):
        with pytest.raises(ValueError, match="CNPJ deve ter 14 digitos"):
            await default_registry.call("receitaws_consulta_cnpj", ["1234567"])

    async def test_error_response_raises_valueerror(self):
        error_data = {
            "status": "ERROR",
            "message": "CNPJ inválido",
        }
        response_ctx = _mock_aiohttp_response(200, error_data)
        session_ctx = _mock_aiohttp_session(response_ctx)

        with patch(
            "lexflow_opcodes.receitaws.aiohttp.ClientSession",
            return_value=session_ctx,
        ):
            with pytest.raises(ValueError, match="CNPJ inválido"):
                await default_registry.call(
                    "receitaws_consulta_cnpj", ["11222333000181"]
                )

    async def test_empty_cnpj_raises_error(self):
        with pytest.raises(ValueError, match="CNPJ deve ter 14 digitos"):
            await default_registry.call("receitaws_consulta_cnpj", [""])


# ============================================================================
# Graceful Degradation
# ============================================================================


@pytest.mark.skipif(AIOHTTP_AVAILABLE, reason="Test only when aiohttp is not installed")
class TestReceitawsGracefulDegradation:
    def test_opcode_not_registered(self):
        opcodes = default_registry.list_opcodes()
        receitaws_opcodes = [op for op in opcodes if op.startswith("receitaws_")]
        assert receitaws_opcodes == []
