from typing import Optional, Type

import structlog
from pydantic import Field
from pydantic_graph import Graph

from app.ai.actions.summary_action import (
    BaseSummaryState,
    ConsolidatedSummaryNode,
    IndividualSummariesNode,
    SummaryByParagraphNode,
    SummaryFormatterNode,
)
from app.ai.base import GraphAction

logger = structlog.get_logger(__name__)


class LongSummaryState(BaseSummaryState):
    output: Optional[str] = Field(None, json_schema_extra={"include_in_metadata": True})
    prompt_path: str = "app/ai/prompts/long_summary.txt"
    prompt_path_aggregator: str = "app/ai/prompts/short_summary_consolidated.txt"
    include_individual_summaries: bool = Field(True)
    include_consolidated_summary: bool = Field(True)


class LongSummaryGraphAction(GraphAction):
    name = "Long Summary"
    description = "Generates a detailed summary of one or more PDF documents."
    allow_multiple_docs = True

    @property
    def state_class(self) -> Type[LongSummaryState]:
        return LongSummaryState

    @property
    def graph(self) -> Graph:
        return Graph(
            nodes=(
                SummaryByParagraphNode,
                ConsolidatedSummaryNode,
                IndividualSummariesNode,
                SummaryFormatterNode,
            ),
            state_type=LongSummaryState,
        )

    @property
    def start_node(self) -> Type[SummaryByParagraphNode]:
        return SummaryByParagraphNode
