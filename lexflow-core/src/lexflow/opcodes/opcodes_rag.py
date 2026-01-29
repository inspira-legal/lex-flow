"""RAG (Retrieval Augmented Generation) opcodes for LexFlow.

This module provides opcodes for building RAG pipelines:
- PDF text extraction (requires pypdf)
- Text chunking (no dependencies)
- Vertex AI embeddings (requires google-cloud-aiplatform)
- Qdrant vector database operations (requires qdrant-client)

Installation:
    pip install lexflow[rag]
    or individually:
    pip install pypdf google-cloud-aiplatform qdrant-client
"""

import re
from typing import Any, Dict, List, Optional

# Check availability of optional dependencies
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


def _check_pypdf():
    """Check if pypdf is available and raise helpful error if not."""
    if not PYPDF_AVAILABLE:
        raise ImportError(
            "pypdf is not installed. Install it with:\n"
            "  pip install lexflow[rag]\n"
            "or:\n"
            "  pip install pypdf"
        )


def _check_vertexai():
    """Check if google-cloud-aiplatform is available and raise helpful error if not."""
    if not VERTEXAI_AVAILABLE:
        raise ImportError(
            "google-cloud-aiplatform is not installed. Install it with:\n"
            "  pip install lexflow[rag]\n"
            "or:\n"
            "  pip install google-cloud-aiplatform"
        )


def _check_qdrant():
    """Check if qdrant-client is available and raise helpful error if not."""
    if not QDRANT_AVAILABLE:
        raise ImportError(
            "qdrant-client is not installed. Install it with:\n"
            "  pip install lexflow[rag]\n"
            "or:\n"
            "  pip install qdrant-client"
        )


def register_rag_opcodes():
    """Register RAG opcodes to the default registry."""
    from .opcodes import default_registry

    # ==========================================================================
    # Text Processing Operations (no external dependencies - always registered)
    # ==========================================================================

    @default_registry.register()
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

        Example:
            text: "Long document text..."
            chunk_size: 500
            overlap: 50
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

    @default_registry.register()
    async def text_chunk_by_sentences(
        text: str, sentences_per_chunk: int = 5, overlap: int = 1
    ) -> List[str]:
        """Split text into chunks by sentence boundaries.

        Args:
            text: Text to split into chunks
            sentences_per_chunk: Number of sentences per chunk (default: 5)
            overlap: Number of sentences to overlap between chunks (default: 1)

        Returns:
            List of text chunks split at sentence boundaries

        Example:
            text: "First sentence. Second sentence. Third sentence."
            sentences_per_chunk: 2
            overlap: 1
        """
        if not text:
            return []

        if sentences_per_chunk <= 0:
            raise ValueError("sentences_per_chunk must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= sentences_per_chunk:
            raise ValueError("overlap must be less than sentences_per_chunk")

        # Split by sentence-ending punctuation followed by whitespace
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

    # ==========================================================================
    # PDF Operations (require pypdf)
    # ==========================================================================

    if PYPDF_AVAILABLE:

        @default_registry.register()
        async def pdf_extract_text(file_path: str) -> str:
            """Extract all text from a PDF file.

            Args:
                file_path: Path to the PDF file

            Returns:
                Extracted text from all pages concatenated

            Example:
                file_path: "/path/to/document.pdf"
            """
            _check_pypdf()

            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n\n".join(text_parts)

        @default_registry.register()
        async def pdf_extract_pages(file_path: str) -> List[str]:
            """Extract text from a PDF file page by page.

            Args:
                file_path: Path to the PDF file

            Returns:
                List of strings, one per page

            Example:
                file_path: "/path/to/document.pdf"
            """
            _check_pypdf()

            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                pages.append(page_text if page_text else "")
            return pages

        @default_registry.register()
        async def pdf_page_count(file_path: str) -> int:
            """Get the number of pages in a PDF file.

            Args:
                file_path: Path to the PDF file

            Returns:
                Number of pages in the PDF

            Example:
                file_path: "/path/to/document.pdf"
            """
            _check_pypdf()

            reader = PdfReader(file_path)
            return len(reader.pages)

    # ==========================================================================
    # Vertex AI Embeddings (require google-cloud-aiplatform)
    # ==========================================================================

    if VERTEXAI_AVAILABLE:

        @default_registry.register()
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

            Example:
                text: "What is machine learning?"
                project: "my-gcp-project"
                location: "us-central1"
                model: "text-embedding-004"

            Note:
                Requires Google Cloud authentication via:
                - gcloud auth application-default login
                - Or GOOGLE_APPLICATION_CREDENTIALS environment variable
            """
            _check_vertexai()

            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)
            embeddings = embedding_model.get_embeddings([text])
            return embeddings[0].values

        @default_registry.register()
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

            Example:
                texts: ["First document", "Second document"]
                project: "my-gcp-project"
                location: "us-central1"

            Note:
                More efficient than calling embedding_create multiple times.
                Automatically batches into groups of 250 (Vertex AI limit).
            """
            _check_vertexai()

            if not texts:
                return []

            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained(model)

            # Vertex AI has limits on both count (250) and tokens (20000)
            # Use smaller batches to stay within token limits
            batch_size = 50
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                embeddings = embedding_model.get_embeddings(batch)
                all_embeddings.extend([e.values for e in embeddings])

            return all_embeddings

    # ==========================================================================
    # Qdrant Operations (require qdrant-client)
    # ==========================================================================

    if QDRANT_AVAILABLE:

        @default_registry.register()
        async def qdrant_connect(url: str = "http://localhost:6333") -> Any:
            """Create a Qdrant client connection.

            Args:
                url: Qdrant server URL (default: "http://localhost:6333")

            Returns:
                QdrantClient instance

            Example:
                url: "http://localhost:6333"
            """
            _check_qdrant()
            return QdrantClient(url=url)

        @default_registry.register()
        async def qdrant_create_collection(
            client: Any, name: str, vector_size: int = 768
        ) -> bool:
            """Create a Qdrant collection if it doesn't exist.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                name: Collection name
                vector_size: Dimension of embedding vectors (default: 768 for text-embedding-004)

            Returns:
                True if collection was created, False if it already existed

            Example:
                client: { node: qdrant_client }
                name: "my_documents"
                vector_size: 768
            """
            _check_qdrant()

            collections = client.get_collections().collections
            exists = any(c.name == name for c in collections)

            if exists:
                return False

            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return True

        @default_registry.register()
        async def qdrant_collection_exists(client: Any, name: str) -> bool:
            """Check if a Qdrant collection exists.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                name: Collection name to check

            Returns:
                True if collection exists, False otherwise

            Example:
                client: { node: qdrant_client }
                name: "my_documents"
            """
            _check_qdrant()

            collections = client.get_collections().collections
            return any(c.name == name for c in collections)

        @default_registry.register()
        async def qdrant_delete_collection(client: Any, name: str) -> bool:
            """Delete a Qdrant collection.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                name: Collection name to delete

            Returns:
                True if deletion was successful

            Example:
                client: { node: qdrant_client }
                name: "my_documents"
            """
            _check_qdrant()

            client.delete_collection(collection_name=name)
            return True

        @default_registry.register()
        async def qdrant_upsert(
            client: Any,
            collection: str,
            id: int,
            vector: List[float],
            payload: Optional[Dict[str, Any]] = None,
        ) -> bool:
            """Insert or update a single point in a Qdrant collection.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                collection: Collection name
                id: Unique identifier for the point (integer)
                vector: Embedding vector (list of floats)
                payload: Optional metadata dict (e.g., {"text": "...", "source": "file.pdf"})

            Returns:
                True if upsert was successful

            Example:
                client: { node: qdrant_client }
                collection: "my_documents"
                id: 1
                vector: [0.1, 0.2, ...]
                payload: {"text": "Document content", "source": "doc.pdf", "page": 1}
            """
            _check_qdrant()

            point = PointStruct(id=id, vector=vector, payload=payload or {})
            client.upsert(collection_name=collection, points=[point])
            return True

        @default_registry.register()
        async def qdrant_upsert_batch(
            client: Any,
            collection: str,
            ids: List[int],
            vectors: List[List[float]],
            payloads: Optional[List[Dict[str, Any]]] = None,
        ) -> bool:
            """Insert or update multiple points in a Qdrant collection.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                collection: Collection name
                ids: List of unique identifiers (integers)
                vectors: List of embedding vectors
                payloads: Optional list of metadata dicts (same length as ids)

            Returns:
                True if upsert was successful

            Example:
                client: { node: qdrant_client }
                collection: "my_documents"
                ids: [1, 2, 3]
                vectors: [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]]
                payloads: [{"text": "Doc 1"}, {"text": "Doc 2"}, {"text": "Doc 3"}]

            Note:
                More efficient than calling qdrant_upsert multiple times.
            """
            _check_qdrant()

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

        @default_registry.register()
        async def qdrant_search(
            client: Any, collection: str, query_vector: List[float], limit: int = 5
        ) -> List[Dict[str, Any]]:
            """Search for similar vectors in a Qdrant collection.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                collection: Collection name
                query_vector: Embedding vector to search for
                limit: Maximum number of results to return (default: 5)

            Returns:
                List of dicts with keys: id, score, payload

            Example:
                client: { node: qdrant_client }
                collection: "my_documents"
                query_vector: [0.1, 0.2, ...]
                limit: 5
            """
            _check_qdrant()

            response = client.query_points(
                collection_name=collection, query=query_vector, limit=limit
            )

            return [
                {"id": r.id, "score": r.score, "payload": r.payload}
                for r in response.points
            ]

        @default_registry.register()
        async def qdrant_delete(client: Any, collection: str, ids: List[int]) -> bool:
            """Delete points from a Qdrant collection by IDs.

            Args:
                client: QdrantClient instance (from qdrant_connect)
                collection: Collection name
                ids: List of point IDs to delete

            Returns:
                True if deletion was successful

            Example:
                client: { node: qdrant_client }
                collection: "my_documents"
                ids: [1, 2, 3]
            """
            _check_qdrant()

            from qdrant_client.models import PointIdsList

            client.delete(
                collection_name=collection, points_selector=PointIdsList(points=ids)
            )
            return True
