"""RAG (Retrieval Augmented Generation) opcodes for LexFlow.

This module provides opcodes for building RAG pipelines:
- PDF text extraction (requires pymupdf or pypdf)
- Text chunking (no dependencies)
- Vertex AI embeddings (requires google-cloud-aiplatform)
- Qdrant vector database operations (requires qdrant-client)
- BM25 reranking (requires bm25s)

Installation:
    pip install lexflow[rag]
"""

import asyncio
import bisect
import io
import random
import re
from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import pymupdf

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

PDF_AVAILABLE = HAS_PYMUPDF or PYPDF_AVAILABLE

try:
    import vertexai
    from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import bm25s

    BM25S_AVAILABLE = True
except ImportError:
    BM25S_AVAILABLE = False


def register_rag_opcodes():
    """Register RAG opcodes to the default registry."""
    register_category(
        id="rag",
        label="RAG Operations",
        prefix="rag_",
        color="#8B5CF6",
        icon="🔍",
        requires="rag",
        order=230,
    )

    # =========================================================================
    # Text Processing Operations (no external dependencies)
    # =========================================================================

    @opcode(category="rag")
    async def text_chunk(
        text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks for embedding.

        Args:
            text: Text to split into chunks
            chunk_size: Maximum characters per chunk (default: 500)
            overlap: Characters to overlap between chunks (default: 50)

        Returns:
            List of text chunks
        """
        if not text:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= text_len:
                break
            start = end - overlap

        return chunks

    @opcode(category="rag")
    async def text_chunk_by_sentences(
        text: str, sentences_per_chunk: int = 5, overlap: int = 1
    ) -> List[str]:
        """Split text into chunks by sentence boundaries.

        Args:
            text: Text to split into chunks
            sentences_per_chunk: Number of sentences per chunk (default: 5)
            overlap: Number of sentences to overlap (default: 1)

        Returns:
            List of text chunks split at sentence boundaries
        """
        if not text:
            return []
        if sentences_per_chunk <= 0:
            raise ValueError("sentences_per_chunk must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= sentences_per_chunk:
            raise ValueError("overlap must be less than sentences_per_chunk")

        sentence_pattern = r"(?<=[.!?])\s+"
        sentences = re.split(sentence_pattern, text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks = []
        start = 0

        while start < len(sentences):
            end = start + sentences_per_chunk
            chunk_sentences = sentences[start:end]
            chunk = " ".join(chunk_sentences)
            chunks.append(chunk)
            if end >= len(sentences):
                break
            start = end - overlap

        return chunks

    @opcode(category="rag")
    async def text_chunk_pages(
        pages: List[str], chunk_size: int = 500, overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """Split pages into chunks with page and line metadata.

        Chunks text while tracking which page(s) and line(s) each chunk spans.

        Args:
            pages: List of page texts (from pdf_extract_pages)
            chunk_size: Maximum characters per chunk (default: 500)
            overlap: Characters to overlap between chunks (default: 50)

        Returns:
            List of dicts with keys: text, page_start, page_end, line_start, line_end
        """
        if not pages:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        boundaries: List[tuple] = []  # (char_offset, page, line)
        full_text_parts = []
        offset = 0

        for page_num, page_text in enumerate(pages, start=1):
            if not page_text:
                continue
            lines = page_text.split("\n")
            for line_num, line in enumerate(lines, start=1):
                boundaries.append((offset, page_num, line_num))
                offset += len(line)
                full_text_parts.append(line)
                if line_num < len(lines):
                    offset += 1
                    full_text_parts.append("\n")
            if page_num < len(pages):
                offset += 1
                full_text_parts.append("\n")

        full_text = "".join(full_text_parts)
        if not full_text:
            return []

        boundary_offsets = [b[0] for b in boundaries]

        def get_position(char_idx: int) -> tuple:
            idx = bisect.bisect_right(boundary_offsets, char_idx) - 1
            if idx < 0:
                return (1, 1)
            return (boundaries[idx][1], boundaries[idx][2])

        chunks = []
        start = 0
        text_len = len(full_text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_text = full_text[start:end]

            start_pos = get_position(start)
            end_pos = get_position(end - 1)

            chunks.append(
                {
                    "text": chunk_text,
                    "page_start": start_pos[0],
                    "page_end": end_pos[0],
                    "line_start": start_pos[1],
                    "line_end": end_pos[1],
                }
            )

            if end >= text_len:
                break
            start = end - overlap

        return chunks

    @opcode(category="rag")
    async def text_chunk_pages_smart(
        pages: List[str],
        chunk_size: int = 1000,
        overlap: int = 200,
        min_chunk_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Split pages into chunks at sentence boundaries with page/line metadata.

        Like text_chunk_pages but tries to break at sentence endings (., !, ?)
        for better semantic coherence.

        Args:
            pages: List of page texts (from pdf_extract_pages)
            chunk_size: Target characters per chunk (default: 1000)
            overlap: Target overlap between chunks (default: 200)
            min_chunk_size: Minimum chunk size before forcing a break (default: 100)

        Returns:
            List of dicts with keys: text, page_start, page_end, line_start, line_end
        """
        if not pages:
            return []
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        boundaries: List[tuple] = []  # (char_offset, page, line)
        full_text_parts = []
        offset = 0

        for page_num, page_text in enumerate(pages, start=1):
            if not page_text:
                continue
            lines = page_text.split("\n")
            for line_num, line in enumerate(lines, start=1):
                boundaries.append((offset, page_num, line_num))
                offset += len(line)
                full_text_parts.append(line)
                if line_num < len(lines):
                    offset += 1
                    full_text_parts.append("\n")
            if page_num < len(pages):
                offset += 1
                full_text_parts.append("\n")

        full_text = "".join(full_text_parts)
        if not full_text:
            return []

        boundary_offsets = [b[0] for b in boundaries]

        def get_position(char_idx: int) -> tuple:
            idx = bisect.bisect_right(boundary_offsets, char_idx) - 1
            if idx < 0:
                return (1, 1)
            return (boundaries[idx][1], boundaries[idx][2])

        def find_break_point(text: str, target: int, min_pos: int) -> int:
            if target >= len(text):
                return len(text)
            window_start = max(min_pos, target - 100)
            window_end = min(len(text), target + 100)
            window = text[window_start:window_end]

            best_break = -1
            for i, char in enumerate(window):
                abs_pos = window_start + i
                if abs_pos > target + 50:
                    break
                if char in ".!?" and abs_pos >= min_pos:
                    if abs_pos + 1 < len(text) and text[abs_pos + 1] in " \n":
                        best_break = abs_pos + 1

            if best_break > min_pos:
                return best_break

            for i in range(target, max(min_pos, target - 50), -1):
                if text[i] in " \n":
                    return i + 1

            return target

        chunks = []
        start = 0
        text_len = len(full_text)

        while start < text_len:
            target_end = start + chunk_size
            end = find_break_point(full_text, target_end, start + min_chunk_size)
            chunk_text = full_text[start:end].strip()

            if chunk_text:
                start_pos = get_position(start)
                end_idx = min(end - 1, len(full_text) - 1)
                end_pos = get_position(end_idx)

                chunks.append(
                    {
                        "text": chunk_text,
                        "page_start": start_pos[0],
                        "page_end": end_pos[0],
                        "line_start": start_pos[1],
                        "line_end": end_pos[1],
                    }
                )

            if end >= text_len:
                break

            overlap_start = max(start, end - overlap)
            start = find_break_point(full_text, overlap_start, overlap_start)

        return chunks

    @opcode(category="rag")
    async def rag_build_chunk_payloads(
        chunks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        id_prefix: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build point IDs and payloads from text chunks for vector DB upsert.

        Args:
            chunks: List of chunk dicts with 'text', 'page_start', 'page_end'
            metadata: Extra fields merged into every payload (e.g., source, livro_id)
            id_prefix: Base for generating point IDs. If None, uses random int.
                IDs: id_prefix * 1000 + chunk_index

        Returns:
            Dict with 'ids' (List[int]) and 'payloads' (List[Dict])
        """
        if id_prefix is None:
            id_prefix = random.randint(100000, 999999)

        base = int(id_prefix) * 1000
        ids = []
        payloads = []

        for i, chunk in enumerate(chunks):
            ids.append(base + i)
            payload = {
                "text": chunk.get("text", ""),
                "chunk_index": i,
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "line_start": chunk.get("line_start"),
                "line_end": chunk.get("line_end"),
            }
            if metadata:
                payload.update(metadata)
            payloads.append(payload)

        return {"ids": ids, "payloads": payloads}

    @opcode(category="rag")
    async def bm25_rerank(
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 10,
        text_field: str = "text",
        alpha: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Rerank search results using BM25 combined with semantic scores.

        Combines the original semantic similarity score with BM25 keyword matching
        for improved retrieval quality (hybrid search).

        Args:
            query: The search query
            results: List of search results with 'payload' containing text and 'score'
            top_k: Number of results to return (default: 10)
            text_field: Field name in payload containing text (default: "text")
            alpha: Weight for semantic score vs BM25 (0=BM25 only, 1=semantic only)

        Returns:
            Reranked results with updated 'score' and 'bm25_score' added
        """
        if not BM25S_AVAILABLE:
            raise ImportError(
                "bm25s is required for bm25_rerank. Install with:\n  pip install bm25s"
            )

        if not results:
            return []

        texts = []
        for r in results:
            text = r.get(text_field, "")
            if not text:
                payload = r.get("payload", {})
                text = payload.get(text_field, "")
            texts.append(text or "")

        if not any(texts):
            return results[:top_k]

        corpus_tokens = bm25s.tokenize(texts, stopwords=None)
        query_tokens = bm25s.tokenize([query], stopwords=None)

        if not any(len(t) > 0 for t in corpus_tokens):
            return results[:top_k]

        retriever = bm25s.BM25()
        retriever.index(corpus_tokens)

        doc_indices, bm25_scores = retriever.retrieve(query_tokens, k=len(texts))
        doc_indices = doc_indices[0]
        bm25_scores = bm25_scores[0]

        idx_to_bm25 = {
            int(idx): float(score) for idx, score in zip(doc_indices, bm25_scores)
        }

        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
        max_bm25 = max_bm25 if max_bm25 > 0 else 1.0

        reranked = []
        for i, r in enumerate(results):
            original_score = r.get("score", 0)
            bm25_score = idx_to_bm25.get(i, 0.0)
            bm25_norm = bm25_score / max_bm25

            combined_score = alpha * original_score + (1 - alpha) * bm25_norm

            new_result = dict(r)
            new_result["score"] = combined_score
            new_result["semantic_score"] = original_score
            new_result["bm25_score"] = bm25_score
            reranked.append(new_result)

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]

    # =========================================================================
    # PDF Operations (prefer pymupdf ~12x faster, fallback to pypdf)
    # =========================================================================

    if PDF_AVAILABLE:

        @opcode(category="rag")
        async def pdf_extract_text(file_path: str) -> str:
            """Extract all text from a PDF file.

            Uses PyMuPDF when available (~12x faster), falls back to pypdf.

            Args:
                file_path: Path to the PDF file

            Returns:
                Extracted text from all pages concatenated
            """
            if HAS_PYMUPDF:
                doc = pymupdf.open(file_path)
                return "\n\n".join(page.get_text() for page in doc if page.get_text())
            reader = PdfReader(file_path)
            return "\n\n".join(
                page.extract_text() for page in reader.pages if page.extract_text()
            )

        @opcode(category="rag")
        async def pdf_extract_pages(file_path: str) -> List[str]:
            """Extract text from a PDF file page by page.

            Uses PyMuPDF when available (~12x faster), falls back to pypdf.

            Args:
                file_path: Path to the PDF file

            Returns:
                List of strings, one per page
            """
            if HAS_PYMUPDF:

                def _extract(path: str) -> List[str]:
                    doc = pymupdf.open(path)
                    return [page.get_text() or "" for page in doc]
            else:

                def _extract(path: str) -> List[str]:
                    reader = PdfReader(path)
                    return [page.extract_text() or "" for page in reader.pages]

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, _extract, file_path)

        @opcode(category="rag")
        async def pdf_extract_text_from_bytes(data: bytes) -> str:
            """Extract all text from PDF bytes.

            Uses PyMuPDF when available (~12x faster), falls back to pypdf.

            Args:
                data: PDF content as bytes

            Returns:
                Extracted text from all pages concatenated
            """
            if HAS_PYMUPDF:

                def _extract(pdf_data: bytes) -> str:
                    doc = pymupdf.open(stream=pdf_data, filetype="pdf")
                    return "\n\n".join(
                        page.get_text() for page in doc if page.get_text()
                    )
            else:

                def _extract(pdf_data: bytes) -> str:
                    reader = PdfReader(io.BytesIO(pdf_data))
                    return "\n\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, _extract, data)

        @opcode(category="rag")
        async def pdf_extract_pages_from_bytes(data: bytes) -> List[str]:
            """Extract text from PDF bytes page by page.

            Uses PyMuPDF when available (~12x faster), falls back to pypdf.

            Args:
                data: PDF content as bytes

            Returns:
                List of strings, one per page
            """
            if HAS_PYMUPDF:

                def _extract(pdf_data: bytes) -> List[str]:
                    doc = pymupdf.open(stream=pdf_data, filetype="pdf")
                    return [page.get_text() or "" for page in doc]
            else:

                def _extract(pdf_data: bytes) -> List[str]:
                    reader = PdfReader(io.BytesIO(pdf_data))
                    return [page.extract_text() or "" for page in reader.pages]

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, _extract, data)

        @opcode(category="rag")
        async def pdf_page_count(file_path: str) -> int:
            """Get the number of pages in a PDF file.

            Uses PyMuPDF when available, falls back to pypdf.

            Args:
                file_path: Path to the PDF file

            Returns:
                Number of pages in the PDF
            """
            if HAS_PYMUPDF:
                doc = pymupdf.open(file_path)
                return len(doc)
            reader = PdfReader(file_path)
            return len(reader.pages)

    # =========================================================================
    # Vertex AI Embeddings (require google-cloud-aiplatform)
    # =========================================================================

    if VERTEXAI_AVAILABLE:

        @opcode(category="rag")
        async def embedding_create(
            text: str,
            project: str,
            location: str = "us-central1",
            model: str = "text-embedding-004",
            task_type: str = "RETRIEVAL_DOCUMENT",
        ) -> List[float]:
            """Create an embedding vector for a single text.

            Args:
                text: Text to embed
                project: Google Cloud project ID
                location: Google Cloud region (default: "us-central1")
                model: Embedding model name (default: "text-embedding-004")
                task_type: Embedding task type (default: "RETRIEVAL_DOCUMENT").
                    Use "RETRIEVAL_QUERY" for search queries.

            Returns:
                List of floats representing the embedding vector
            """
            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)
            inputs = [TextEmbeddingInput(text=text, task_type=task_type)]
            embeddings = embedding_model.get_embeddings(inputs)
            return embeddings[0].values

        @opcode(category="rag")
        async def embedding_create_batch(
            texts: List[str],
            project: str,
            location: str = "us-central1",
            model: str = "text-embedding-004",
            task_type: str = "RETRIEVAL_DOCUMENT",
        ) -> List[List[float]]:
            """Create embedding vectors for multiple texts (more efficient).

            Args:
                texts: List of texts to embed
                project: Google Cloud project ID
                location: Google Cloud region (default: "us-central1")
                model: Embedding model name (default: "text-embedding-004")
                task_type: Embedding task type (default: "RETRIEVAL_DOCUMENT").
                    Use "RETRIEVAL_QUERY" for search queries.

            Returns:
                List of embedding vectors (each is a list of floats)
            """
            if not texts:
                return []

            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)

            batch_size = 50
            max_concurrent = 5
            batches = [
                texts[i : i + batch_size] for i in range(0, len(texts), batch_size)
            ]

            loop = asyncio.get_running_loop()
            all_embeddings: List[List[float]] = [[] for _ in batches]
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_batch(idx: int, batch: List[str]):
                inputs = [
                    TextEmbeddingInput(text=t, task_type=task_type) for t in batch
                ]
                async with semaphore:
                    embeddings = await loop.run_in_executor(
                        None, embedding_model.get_embeddings, inputs
                    )
                    all_embeddings[idx] = [e.values for e in embeddings]

            await asyncio.gather(*[process_batch(i, b) for i, b in enumerate(batches)])

            result = []
            for batch_result in all_embeddings:
                result.extend(batch_result)
            return result

    # =========================================================================
    # Qdrant Operations (require qdrant-client)
    # =========================================================================

    if QDRANT_AVAILABLE:

        @opcode(category="rag")
        async def qdrant_connect(
            url: str = "http://localhost:6333", prefer_grpc: bool = False
        ) -> Any:
            """Create a Qdrant client connection.

            Args:
                url: Qdrant server URL (default: "http://localhost:6333")
                prefer_grpc: Use gRPC for better performance (default: False)

            Returns:
                QdrantClient instance
            """
            return QdrantClient(url=url, prefer_grpc=prefer_grpc)

        @opcode(category="rag")
        async def qdrant_create_collection(
            client: Any, name: str, vector_size: int = 768
        ) -> bool:
            """Create a Qdrant collection if it doesn't exist.

            Args:
                client: QdrantClient instance
                name: Collection name
                vector_size: Dimension of embedding vectors (default: 768)

            Returns:
                True if created, False if already existed
            """
            collections = client.get_collections().collections
            exists = any(c.name == name for c in collections)

            if exists:
                return False

            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return True

        @opcode(category="rag")
        async def qdrant_collection_exists(client: Any, name: str) -> bool:
            """Check if a Qdrant collection exists.

            Args:
                client: QdrantClient instance
                name: Collection name to check

            Returns:
                True if collection exists
            """
            collections = client.get_collections().collections
            return any(c.name == name for c in collections)

        @opcode(category="rag")
        async def qdrant_delete_collection(client: Any, name: str) -> bool:
            """Delete a Qdrant collection.

            Args:
                client: QdrantClient instance
                name: Collection name to delete

            Returns:
                True if deletion was successful
            """
            client.delete_collection(collection_name=name)
            return True

        @opcode(category="rag")
        async def qdrant_upsert(
            client: Any,
            collection: str,
            point_id: int,
            vector: List[float],
            payload: Optional[Dict[str, Any]] = None,
        ) -> bool:
            """Insert or update a single point in a Qdrant collection.

            Args:
                client: QdrantClient instance
                collection: Collection name
                point_id: Unique identifier for the point
                vector: Embedding vector
                payload: Optional metadata dict

            Returns:
                True if upsert was successful
            """
            point = PointStruct(id=point_id, vector=vector, payload=payload or {})
            client.upsert(collection_name=collection, points=[point])
            return True

        @opcode(category="rag")
        async def qdrant_upsert_batch(
            client: Any,
            collection: str,
            point_ids: List[int],
            vectors: List[List[float]],
            payloads: Optional[List[Dict[str, Any]]] = None,
        ) -> bool:
            """Insert or update multiple points in a Qdrant collection.

            Uses Qdrant's upload_points for efficient internal batching.

            Args:
                client: QdrantClient instance
                collection: Collection name
                point_ids: List of unique identifiers
                vectors: List of embedding vectors
                payloads: Optional list of metadata dicts

            Returns:
                True if upsert was successful
            """
            if len(point_ids) != len(vectors):
                raise ValueError("point_ids and vectors must have the same length")
            if payloads and len(payloads) != len(point_ids):
                raise ValueError("payloads must have the same length as point_ids")

            points = [
                PointStruct(
                    id=pid,
                    vector=vector,
                    payload=payloads[i] if payloads else {},
                )
                for i, (pid, vector) in enumerate(zip(point_ids, vectors))
            ]

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: client.upload_points(
                    collection_name=collection,
                    points=points,
                    batch_size=256,
                    parallel=4,
                ),
            )
            return True

        @opcode(category="rag")
        async def qdrant_search(
            client: Any, collection: str, query_vector: List[float], limit: int = 5
        ) -> List[Dict[str, Any]]:
            """Search for similar vectors in a Qdrant collection.

            Args:
                client: QdrantClient instance
                collection: Collection name
                query_vector: Embedding vector to search for
                limit: Maximum number of results (default: 5)

            Returns:
                List of dicts with keys: id, score, payload
            """
            response = client.query_points(
                collection_name=collection, query=query_vector, limit=limit
            )

            return [
                {"id": r.id, "score": r.score, "payload": r.payload}
                for r in response.points
            ]

        @opcode(category="rag")
        async def qdrant_delete(
            client: Any, collection: str, point_ids: List[int]
        ) -> bool:
            """Delete points from a Qdrant collection by IDs.

            Args:
                client: QdrantClient instance
                collection: Collection name
                point_ids: List of point IDs to delete

            Returns:
                True if deletion was successful
            """
            from qdrant_client.models import PointIdsList

            client.delete(
                collection_name=collection,
                points_selector=PointIdsList(points=point_ids),
            )
            return True
