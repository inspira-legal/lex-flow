"""ReceitaWS CNPJ lookup opcodes for LexFlow.

This module provides opcodes for querying CNPJ data from the ReceitaWS API,
enabling Brazilian company data lookup workflows.

API Reference:
    https://www.receitaws.com.br/api
"""

import re
from typing import Any, Dict

from .opcodes import opcode, register_category

try:
    import aiohttp

    RECEITAWS_AVAILABLE = True
except ImportError:
    RECEITAWS_AVAILABLE = False


def _check_receitaws():
    if not RECEITAWS_AVAILABLE:
        raise ImportError(
            "aiohttp is required for ReceitaWS opcodes. Install with: uv add 'lexflow[receitaws]'"
        )


def register_receitaws_opcodes():
    """Register ReceitaWS opcodes to the default registry."""
    if not RECEITAWS_AVAILABLE:
        return

    register_category(
        id="receitaws",
        label="ReceitaWS Operations",
        prefix="receitaws_",
        color="#009C3B",
        icon="receitaws",
        requires="receitaws",
        order=225,
    )

    @opcode(category="receitaws")
    async def receitaws_consulta_cnpj(cnpj: str) -> Dict[str, Any]:
        """Consulta dados de uma empresa pelo CNPJ na ReceitaWS.

        Args:
            cnpj: CNPJ da empresa (aceita formatado ou apenas digitos)

        Returns:
            Dict com dados da empresa (nome, fantasia, situacao, etc.)

        Raises:
            ValueError: Se o CNPJ nao tiver 14 digitos ou a API retornar erro

        Example:
            cnpj: "11.222.333/0001-81"
        """
        _check_receitaws()

        cnpj_digits = re.sub(r"\D", "", cnpj)

        if len(cnpj_digits) != 14:
            raise ValueError(
                f"CNPJ deve ter 14 digitos, recebeu {len(cnpj_digits)}: '{cnpj}'"
            )

        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_digits}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        if data.get("status") == "ERROR":
            raise ValueError(data.get("message", "Erro desconhecido na consulta CNPJ"))

        return data
