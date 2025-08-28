import aiofiles
from core.opcodes import opcode, BaseOpcode
from pydantic_ai import Agent, DocumentUrl, BinaryContent
from pydantic_ai.models.google import GoogleModel, GoogleProvider
from pydantic import BaseModel

import re

from typing import List


class Reference(BaseModel):
    pag: int


class Paragraph(BaseModel):
    text: str
    references: List[Reference]


class DocumentSummary(BaseModel):
    doc: str
    paragraphs: List[Paragraph]


class StructuredAnswer(BaseModel):
    answer: List[DocumentSummary]


@opcode("ai_agent_call")
class AIAgentCall(BaseOpcode):
    async def execute(self, state, stmt, engine):
        document_url = state.pop()
        system_prompt = state.pop()

        document = DocumentUrl(url=document_url, media_type="application/pdf")

        try:
            provider = GoogleProvider(vertexai=True)
            model = GoogleModel("gemini-1.5-flash", provider=provider)

            agent = Agent(
                model=model,
                system_prompt=system_prompt,
                output_type=StructuredAnswer,
            )

            result = await agent.run([document])
            state.push(result.output)

        except Exception as e:
            error_response = f"AI Error: {str(e)}"
            state.push(error_response)

        return True


@opcode("ai_load_document")
class AiLoadDocument(BaseOpcode):
    async def execute(self, state, stmt, engine):
        file_path = state.pop()
        mime_type = state.pop()

        try:
            async with aiofiles.open(file_path, mode="rb") as f:
                content = await f.read()
                b_content = BinaryContent(data=content, media_type=mime_type)
                state.push(b_content)
        except Exception as e:
            error_response = f"File Load Error: {str(e)}"
            state.push(error_response)

        return True


@opcode("ai_load_prompt")
class AILoadPrompt(BaseOpcode):
    async def execute(self, state, stmt, engine):
        file_path = state.pop()

        try:
            async with aiofiles.open(file_path, mode="r") as f:
                content = await f.read()
                state.push(content)
        except Exception as e:
            error_response = f"File Load Error: {str(e)}"
            state.push(error_response)

        return True


@opcode("ai_format_answer")
class AIFormatStructuredAnswer(BaseOpcode):
    async def execute(self, state, stmt, engine):
        structured_answer = state.pop()
        pages_reference = False

        try:
            if isinstance(structured_answer, StructuredAnswer):
                formatted_output = self._format_structured_answer(
                    structured_answer, pages_reference
                )
            else:
                formatted_output = str(structured_answer)

            state.push(formatted_output)
        except Exception as e:
            error_response = f"Format Error: {str(e)}"
            state.push(error_response)

        return True

    def _format_structured_answer(
        self, answer: StructuredAnswer, pages_reference: bool = False
    ) -> str:
        output_parts = []

        for doc_summary in answer.answer:
            doc_parts = []

            if doc_summary.doc and doc_summary.doc.strip():
                doc_parts.append(f"## {doc_summary.doc}\n")

            for paragraph in doc_summary.paragraphs:
                paragraph_text = paragraph.text.strip()

                if pages_reference and paragraph.references:
                    page_refs = [str(ref.pag) for ref in paragraph.references]
                    if page_refs:
                        page_refs_str = ", ".join(sorted(set(page_refs)))
                        paragraph_text += f" (p. {page_refs_str})"

                doc_parts.append(paragraph_text)

            if doc_parts:
                output_parts.append("\n\n".join(doc_parts))

        result = "\n\n".join(output_parts)

        result = self._sanitize_markdown_formatting(result)

        return result

    def _sanitize_markdown_formatting(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"\n(#+\s)", r"\n\n\1", text)
        text = re.sub(r"(#+\s.*)\n([^\n])", r"\1\n\n\2", text)

        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()
