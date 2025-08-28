from typing import List
import re
from pydantic import BaseModel


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


def format_structured_answer(
    answer: StructuredAnswer, pages_reference: bool = False
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

    result = sanitize_markdown_formatting(result)

    return result


def sanitize_markdown_formatting(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"\n(#+\s)", r"\n\n\1", text)
    text = re.sub(r"(#+\s.*)\n([^\n])", r"\1\n\n\2", text)

    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
