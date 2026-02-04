"""RAG (Retrieval Augmented Generation) opcodes for LexFlow.

This module provides opcodes for building RAG pipelines:
- PDF text extraction (requires pypdf)
- Text chunking (no dependencies)
- Vertex AI embeddings (requires google-cloud-aiplatform)
- Qdrant vector database operations (requires qdrant-client)

Installation:
    pip install lexflow[rag]
"""

import re
from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import vertexai
    from vertexai.language_models import TextEmbeddingModel

    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


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

    # =========================================================================
    # PDF Operations (require pypdf)
    # =========================================================================

    if PYPDF_AVAILABLE:

        @opcode(category="rag")
        async def pdf_extract_text(file_path: str) -> str:
            """Extract all text from a PDF file.

            Args:
                file_path: Path to the PDF file

            Returns:
                Extracted text from all pages concatenated
            """
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n\n".join(text_parts)

        @opcode(category="rag")
        async def pdf_extract_pages(file_path: str) -> List[str]:
            """Extract text from a PDF file page by page.

            Args:
                file_path: Path to the PDF file

            Returns:
                List of strings, one per page
            """
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                pages.append(page_text if page_text else "")
            return pages

        @opcode(category="rag")
        async def pdf_page_count(file_path: str) -> int:
            """Get the number of pages in a PDF file.

            Args:
                file_path: Path to the PDF file

            Returns:
                Number of pages in the PDF
            """
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
        ) -> List[float]:
            """Create an embedding vector for a single text.

            Args:
                text: Text to embed
                project: Google Cloud project ID
                location: Google Cloud region (default: "us-central1")
                model: Embedding model name (default: "text-embedding-004")

            Returns:
                List of floats representing the embedding vector
            """
            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)
            embeddings = embedding_model.get_embeddings([text])
            return embeddings[0].values

        @opcode(category="rag")
        async def embedding_create_batch(
            texts: List[str],
            project: str,
            location: str = "us-central1",
            model: str = "text-embedding-004",
        ) -> List[List[float]]:
            """Create embedding vectors for multiple texts (more efficient).

            Args:
                texts: List of texts to embed
                project: Google Cloud project ID
                location: Google Cloud region (default: "us-central1")
                model: Embedding model name (default: "text-embedding-004")

            Returns:
                List of embedding vectors (each is a list of floats)
            """
            if not texts:
                return []

            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)

            batch_size = 50
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                embeddings = embedding_model.get_embeddings(batch)
                all_embeddings.extend([e.values for e in embeddings])

            return all_embeddings

    # =========================================================================
    # Qdrant Operations (require qdrant-client)
    # =========================================================================

    if QDRANT_AVAILABLE:

        @opcode(category="rag")
        async def qdrant_connect(url: str = "http://localhost:6333") -> Any:
            """Create a Qdrant client connection.

            Args:
                url: Qdrant server URL (default: "http://localhost:6333")

            Returns:
                QdrantClient instance
            """
            return QdrantClient(url=url)

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
            id: int,
            vector: List[float],
            payload: Optional[Dict[str, Any]] = None,
        ) -> bool:
            """Insert or update a single point in a Qdrant collection.

            Args:
                client: QdrantClient instance
                collection: Collection name
                id: Unique identifier for the point
                vector: Embedding vector
                payload: Optional metadata dict

            Returns:
                True if upsert was successful
            """
            point = PointStruct(id=id, vector=vector, payload=payload or {})
            client.upsert(collection_name=collection, points=[point])
            return True

        @opcode(category="rag")
        async def qdrant_upsert_batch(
            client: Any,
            collection: str,
            ids: List[int],
            vectors: List[List[float]],
            payloads: Optional[List[Dict[str, Any]]] = None,
        ) -> bool:
            """Insert or update multiple points in a Qdrant collection.

            Args:
                client: QdrantClient instance
                collection: Collection name
                ids: List of unique identifiers
                vectors: List of embedding vectors
                payloads: Optional list of metadata dicts

            Returns:
                True if upsert was successful
            """
            if len(ids) != len(vectors):
                raise ValueError("ids and vectors must have the same length")
            if payloads and len(payloads) != len(ids):
                raise ValueError("payloads must have the same length as ids")

            points = [
                PointStruct(
                    id=id, vector=vector, payload=payloads[i] if payloads else {}
                )
                for i, (id, vector) in enumerate(zip(ids, vectors))
            ]
            client.upsert(collection_name=collection, points=points)
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
        async def qdrant_delete(client: Any, collection: str, ids: List[int]) -> bool:
            """Delete points from a Qdrant collection by IDs.

            Args:
                client: QdrantClient instance
                collection: Collection name
                ids: List of point IDs to delete

            Returns:
                True if deletion was successful
            """
            from qdrant_client.models import PointIdsList

            client.delete(
                collection_name=collection, points_selector=PointIdsList(points=ids)
            )
            return True
