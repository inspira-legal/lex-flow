"""Tests for RAG opcodes and new built-in opcodes."""

import pytest

from lexflow import default_registry
from lexflow.opcodes.opcodes_rag import BM25S_AVAILABLE

pytestmark = pytest.mark.asyncio


# Helper to call opcodes through the registry
async def call(name, args):
    return await default_registry.call(name, args)


# =========================================================================
# text_chunk tests
# =========================================================================


class TestTextChunk:
    async def test_basic_chunking(self):
        text = "a" * 100
        chunks = await call("text_chunk", [text, 30, 10])
        assert len(chunks) > 1
        assert all(len(c) <= 30 for c in chunks)

    async def test_empty_text(self):
        assert await call("text_chunk", [""]) == []

    async def test_text_shorter_than_chunk(self):
        chunks = await call("text_chunk", ["hello", 100, 10])
        assert chunks == ["hello"]

    async def test_overlap_produces_overlapping_content(self):
        text = "abcdefghijklmnopqrstuvwxyz"
        chunks = await call("text_chunk", [text, 10, 5])
        assert len(chunks) > 1
        # Second chunk should start where first chunk ends minus overlap
        assert chunks[1][:5] == chunks[0][5:]

    async def test_invalid_chunk_size(self):
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            await call("text_chunk", ["hello", 0])

    async def test_negative_overlap(self):
        with pytest.raises(ValueError, match="overlap cannot be negative"):
            await call("text_chunk", ["hello", 10, -1])

    async def test_overlap_exceeds_chunk_size(self):
        with pytest.raises(ValueError, match="overlap must be less than chunk_size"):
            await call("text_chunk", ["hello", 10, 10])


# =========================================================================
# text_chunk_by_sentences tests
# =========================================================================


class TestTextChunkBySentences:
    async def test_basic_sentence_chunking(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = await call("text_chunk_by_sentences", [text, 2, 0])
        assert len(chunks) == 2

    async def test_empty_text(self):
        assert await call("text_chunk_by_sentences", [""]) == []

    async def test_single_sentence(self):
        chunks = await call("text_chunk_by_sentences", ["Only one sentence.", 5])
        assert len(chunks) == 1
        assert "Only one sentence." in chunks[0]


# =========================================================================
# rag_build_chunk_payloads tests
# =========================================================================


class TestBuildChunkPayloads:
    async def test_basic_payload_build(self):
        chunks = [
            {"text": "chunk1", "page_start": 1, "page_end": 1},
            {"text": "chunk2", "page_start": 2, "page_end": 2},
        ]
        result = await call("rag_build_chunk_payloads", [chunks])
        assert len(result["ids"]) == 2
        assert len(result["payloads"]) == 2
        assert result["payloads"][0]["text"] == "chunk1"
        assert result["payloads"][0]["chunk_index"] == 0

    async def test_with_metadata(self):
        chunks = [{"text": "chunk1", "page_start": 1, "page_end": 1}]
        result = await call(
            "rag_build_chunk_payloads", [chunks, {"source": "test.pdf"}]
        )
        assert result["payloads"][0]["source"] == "test.pdf"

    async def test_with_id_prefix(self):
        chunks = [{"text": "chunk1", "page_start": 1, "page_end": 1}]
        result = await call("rag_build_chunk_payloads", [chunks, None, 42])
        assert result["ids"][0] == 42000

    async def test_empty_chunks(self):
        result = await call("rag_build_chunk_payloads", [[]])
        assert result["ids"] == []
        assert result["payloads"] == []


# =========================================================================
# bm25_rerank tests
# =========================================================================


class TestBm25Rerank:
    @pytest.mark.skipif(not BM25S_AVAILABLE, reason="bm25s not installed")
    async def test_basic_reranking(self):
        results = [
            {"text": "python programming language", "score": 0.9},
            {"text": "java programming language", "score": 0.8},
            {"text": "cooking recipes for dinner", "score": 0.7},
        ]
        reranked = await call("bm25_rerank", ["python programming", results, 3])
        assert len(reranked) == 3
        assert "bm25_score" in reranked[0]
        assert "semantic_score" in reranked[0]

    @pytest.mark.skipif(not BM25S_AVAILABLE, reason="bm25s not installed")
    async def test_empty_results(self):
        assert await call("bm25_rerank", ["query", []]) == []

    @pytest.mark.skipif(not BM25S_AVAILABLE, reason="bm25s not installed")
    async def test_top_k_limits_output(self):
        results = [{"text": f"document {i}", "score": 0.5} for i in range(10)]
        reranked = await call("bm25_rerank", ["document", results, 3])
        assert len(reranked) == 3

    @pytest.mark.skipif(BM25S_AVAILABLE, reason="bm25s is installed")
    async def test_raises_when_bm25s_not_available(self):
        with pytest.raises(ImportError, match="bm25s is required"):
            await call("bm25_rerank", ["query", [{"text": "doc", "score": 0.5}]])


# =========================================================================
# Built-in opcode tests (string_format, list_pluck, list_enumerate)
# =========================================================================


class TestStringFormat:
    async def test_basic_format(self):
        result = await call("string_format", ["Hello {0}!", "World"])
        assert result == "Hello World!"

    async def test_multiple_placeholders(self):
        result = await call("string_format", ["{0} + {1} = {2}", 1, 2, 3])
        assert result == "1 + 2 = 3"


class TestListPluck:
    async def test_basic_pluck(self):
        items = [{"name": "Alice"}, {"name": "Bob"}]
        result = await call("list_pluck", [items, "name"])
        assert result == ["Alice", "Bob"]

    async def test_empty_list(self):
        result = await call("list_pluck", [[], "name"])
        assert result == []


class TestListEnumerate:
    async def test_basic_enumerate(self):
        result = await call("list_enumerate", [["a", "b", "c"]])
        assert result == [[0, "a"], [1, "b"], [2, "c"]]

    async def test_custom_start(self):
        result = await call("list_enumerate", [["a", "b"], 1])
        assert result == [[1, "a"], [2, "b"]]

    async def test_empty_list(self):
        result = await call("list_enumerate", [[]])
        assert result == []
