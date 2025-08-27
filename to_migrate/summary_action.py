import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

import structlog
from pydantic import Field
from pydantic_ai import Agent, BinaryContent
from pydantic_graph import BaseNode, End, GraphRunContext

from app.ai.actions.utils import ActionMixin
from app.ai.base import BaseWorkflowState, Blob
from app.ai.exceptions import ActionInputError, ModelExecutionError
from app.ai.model_config import model_long_summary
from app.ai.prompts.loader import load_prompt
from app.ai.summary.formatter import estimate_paragraph_range, format_answer, sanitize_markdown_formatting
from app.ai.summary.schemas import StructuredAnswer
from app.ai.summary.utils import error_summary_response

logger = structlog.get_logger(__name__)


class BaseSummaryState(BaseWorkflowState):
    pages_reference: bool = Field(False)
    prompt_path: str
    prompt_path_aggregator: str
    extract_text_before_summary: bool = Field(False)
    include_individual_summaries: bool = Field(True)
    include_consolidated_summary: bool = Field(True)
    partial_summaries: List[StructuredAnswer] = Field(
        default_factory=list, exclude=True
    )
    consolidated_summary: Optional[str] = Field(None, exclude=True)
    individual_summaries_formatted: Optional[str] = Field(None, exclude=True)
    output: Optional[str] = Field(None, json_schema_extra={"include_in_metadata": True})
    query: Optional[str] = Field(None, exclude=True)


@dataclass
class SummaryNode(BaseNode[BaseSummaryState], ActionMixin):
    node_name: str = "Summary Executor"
    agent: Agent = field(init=False)

    async def summarize_document(self, doc: Union[str, Blob], query: Optional[str] = None) -> StructuredAnswer:
        if query == "":
            raise ValueError("Query cannot be empty.")

        system_prompt = self.system_prompt.format(
            query=query
        )
        
        agent = self.create_agent(
            system_prompt=system_prompt,
            result_type=StructuredAnswer,
            model_settings=model_long_summary,
        )
        if isinstance(doc, str):
            prompt = f"{system_prompt}\n{doc}"

        elif isinstance(doc, Blob):
            prompt = [
                f"{system_prompt} {doc.file_name}",
                BinaryContent(
                    data=doc.data, kind="binary", media_type=doc.content_type
                ),
            ]

        else:
            raise ValueError("Invalid document type for summarization.")

        try:
            result = await agent.run(prompt)
            return result.output
        except Exception as e:
            logger.warning(f"Error while summarizing document: {e}", exc_info=True)
            return error_summary_response(doc_file_name=doc.file_name)

    async def run(
        self, ctx: GraphRunContext[BaseSummaryState]
    ) -> Union[
        "ConsolidatedSummaryNode", "SummaryFormatterNode", "IndividualSummariesNode"
    ]:
        node_logger = logger.bind(node=self.node_name)
        node_logger.info("Starting summary execution for document.")

        self.system_prompt = await load_prompt(ctx.state.prompt_path)

        if not ctx.state.documents:
            raise ActionInputError("No documents provided.")

        documents = self.validate_documents(ctx, self.node_name)
        inputs = self.prepare_inputs(documents, ctx.state.extract_text_before_summary)
        query = ctx.state.query
        try:
            individual_summaries = await asyncio.gather(
                *[self.summarize_document(doc, query) for doc in inputs]
            )
        except Exception as e:
            raise ModelExecutionError(
                f"Failed while summarizing documents in parallel: {e}",
                original_exception=e,
            )

        ctx.state.partial_summaries = individual_summaries

        if len(individual_summaries) == 1:
            node_logger.info(
                "Single document detected. Routing to IndividualSummariesNode for formatting."
            )
            if (
                ctx.state.include_individual_summaries
                or ctx.state.include_consolidated_summary
            ):
                return IndividualSummariesNode()
            else:
                raise ActionInputError(
                    "Neither consolidated nor individual summaries are requested for a single document."
                )

        node_logger.info(
            "Multiple documents detected. Proceeding to summary aggregation or individual summary."
        )
        if ctx.state.include_consolidated_summary:
            return ConsolidatedSummaryNode()
        elif ctx.state.include_individual_summaries:
            return IndividualSummariesNode()
        else:
            raise ActionInputError(
                "Neither consolidated nor individual summaries are requested."
            )

@dataclass
class SummaryByParagraphNode(BaseNode[BaseSummaryState], ActionMixin):
    node_name: str = "Summary Executor by Paragraph"
    agent: Agent = field(init=False)

    async def summarize_document(
        self, doc: Union[str, Blob], paragraph_range: Tuple[int, int], query: Optional[str] = None
    ) -> StructuredAnswer:
        min_p, max_p = paragraph_range
        if query == "":
            raise ValueError("Query cannot be empty.")

        system_prompt = self.system_prompt.format(
            paragraphs_min=min_p, 
            paragraphs_max=max_p,
            query=query
        )
        agent = self.create_agent(
            system_prompt=system_prompt,
            result_type=StructuredAnswer,
            model_settings=model_long_summary,
        )
        if isinstance(doc, str):
            prompt = f"{system_prompt}\n{doc}"
        elif isinstance(doc, Blob):
            prompt = [
                f"{system_prompt} {doc.file_name}",
                BinaryContent(
                    data=doc.data, kind="binary", media_type=doc.content_type
                ),
            ]
        else:
            raise ValueError("Invalid document type for summarization.")

        try:
            result = await agent.run(prompt)
            return result.output

        except Exception as e:
            logger.warning(f"Error while summarizing document: {e}", exc_info=True)
            return error_summary_response(doc_file_name=doc.file_name)

    async def run(
        self, ctx: GraphRunContext[BaseSummaryState]
    ) -> Union[
        "ConsolidatedSummaryNode", "SummaryFormatterNode", "IndividualSummariesNode"
    ]:
        node_logger = logger.bind(node=self.node_name)
        node_logger.info("Starting Summary generation for documents.")
        self.system_prompt = await load_prompt(ctx.state.prompt_path)

        if not ctx.state.documents:
            raise ActionInputError("No documents provided in workflow state.")

        paragraph_ranges = estimate_paragraph_range(ctx.state.documents)

        documents = self.validate_documents(ctx, self.node_name)
        inputs = self.prepare_inputs(documents, ctx.state.extract_text_before_summary)
        query = ctx.state.query
        try:
            summaries = await asyncio.gather(
                *[
                    self.summarize_document(doc, paragraph_range, query)
                    for doc, paragraph_range in zip(inputs, paragraph_ranges)
                ]
            )
        except Exception as e:
            raise ModelExecutionError(
                f"Failed while summarizing documents in parallel: {e}",
                original_exception=e,
            )

        ctx.state.partial_summaries = summaries

        if len(summaries) == 1:
            node_logger.info(
                "Only one document found. Routing to IndividualSummariesNode for formatting."
            )
            if (
                ctx.state.include_individual_summaries
                or ctx.state.include_consolidated_summary
            ):
                return IndividualSummariesNode()
            else:
                raise ActionInputError(
                    "Neither consolidated nor individual summaries are requested for a single document."
                )

        node_logger.info(
            "Multiple summaries generated; proceeding to aggregation or individual summary."
        )
        if ctx.state.include_consolidated_summary:
            return ConsolidatedSummaryNode()
        elif ctx.state.include_individual_summaries:
            return IndividualSummariesNode()
        else:
            raise ActionInputError(
                "Neither consolidated nor individual summaries are requested for multiple documents."
            )


@dataclass
class ConsolidatedSummaryNode(BaseNode[BaseSummaryState], ActionMixin):
    node_name: str = "Consolidated Summary Generator"
    agent: Agent = field(init=False)

    async def run(
        self, ctx: GraphRunContext[BaseSummaryState]
    ) -> "SummaryFormatterNode":
        node_logger = logger.bind(node=self.node_name)
        node_logger.info("Starting consolidated summary generation.")

        query=ctx.state.query

        system_prompt = await load_prompt(ctx.state.prompt_path_aggregator)
        system_prompt = system_prompt.format(query=query)
        agent = self.create_agent(
            system_prompt=system_prompt,
            result_type=str,
            model_settings=model_long_summary,
        )

        if not ctx.state.partial_summaries:
            raise ActionInputError("No partial summaries available to aggregate.")

        summaries_text = ctx.state.partial_summaries
        prompt = f"{system_prompt}\n{summaries_text}"

        try:
            result = await agent.run(prompt)
            ctx.state.consolidated_summary = result.output
        except Exception as e:
            raise ModelExecutionError(
                f"Error during consolidated summary generation: {e}",
                original_exception=e,
            )
        if ctx.state.include_individual_summaries:
            return IndividualSummariesNode()
        else:
            return SummaryFormatterNode()


@dataclass
class IndividualSummariesNode(BaseNode[BaseSummaryState]):
    node_name: str = "Individual Summaries Formatter"

    async def run(
        self, ctx: GraphRunContext[BaseSummaryState]
    ) -> "SummaryFormatterNode":
        node_logger = logger.bind(node=self.node_name)
        node_logger.info("Starting individual summaries formatting.")

        if not ctx.state.partial_summaries:
            node_logger.warning(
                "No partial summaries available to format individually."
            )
            return SummaryFormatterNode()

        formatted_individual_summaries = format_answer(
            response=ctx.state.partial_summaries,
            pages_reference=ctx.state.pages_reference,
        )
        ctx.state.individual_summaries_formatted = formatted_individual_summaries
        return SummaryFormatterNode()


@dataclass
class SummaryFormatterNode(BaseNode[BaseSummaryState]):
    node_name: str = "Summary Formatter"

    async def run(self, ctx: GraphRunContext[BaseSummaryState]) -> End[str]:
        node_logger = logger.bind(node=self.node_name)
        node_logger.info("Starting Output Formatter.")

        final_answer_parts = []
        is_single_document = len(ctx.state.partial_summaries) == 1

        if ctx.state.include_consolidated_summary:
            if is_single_document:
                if ctx.state.individual_summaries_formatted:
                    final_answer_parts.append(ctx.state.individual_summaries_formatted)
            elif ctx.state.consolidated_summary:
                final_answer_parts.append(ctx.state.consolidated_summary)

        if (
            ctx.state.include_individual_summaries
            and ctx.state.individual_summaries_formatted
        ):
            if not is_single_document and ctx.state.include_consolidated_summary:
                final_answer_parts.append(ctx.state.individual_summaries_formatted)
            elif not ctx.state.include_consolidated_summary or is_single_document:
                if not (is_single_document and ctx.state.include_consolidated_summary):
                    final_answer_parts.append(ctx.state.individual_summaries_formatted)

        ctx.state.output = sanitize_markdown_formatting("\n\n".join(final_answer_parts))
        node_logger.info("Summary completed successfully.")
        return End(ctx.state.output)
