from typing import List, Type, Union

import structlog
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_graph import GraphRunContext

from app.ai.base import Blob
from app.ai.exceptions import ActionInputError
from app.ai.model_config import GOOGLE_MODEL
from app.ai.summary.formatter import extract_text_from_doc

logger = structlog.get_logger(__name__)


class ActionMixin:
    @staticmethod
    def create_agent(
        system_prompt: str,
        result_type: Type = str,
        model_settings: dict = None,
        model: Model = None,
    ) -> Agent:
        """Creates an agent with the specified prompt and result type."""
        return Agent(
            model=model or GOOGLE_MODEL,
            model_settings=model_settings,
            system_prompt=system_prompt,
            result_type=result_type,
        )

    @staticmethod
    def validate_documents(ctx: GraphRunContext, node_name: str) -> List[Blob]:
        """Validates that at least one document exists."""
        if not ctx.state.documents:
            raise ActionInputError(
                f"No documents provided in state at node '{node_name}'."
            )
        return ctx.state.documents

    @staticmethod
    def prepare_inputs(
        documents: List[Blob], extract_text: bool
    ) -> List[Union[str, Blob]]:
        """Returns either the raw PDFs or extracted text depending on flag."""
        if extract_text:
            logger.info("Extracting text from documents before to send to LLM")
            return extract_text_from_doc(documents)

        logger.info("Send PDFs directly to LLM")
        return documents
