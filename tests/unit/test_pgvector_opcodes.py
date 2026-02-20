"""Tests for PgVector opcodes."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from lexflow.opcodes.opcodes_pgvector import _validate_table_name

pytestmark = pytest.mark.asyncio


# =========================================================================
# Table name validation tests
# =========================================================================


def test_validate_table_name_valid():
    assert _validate_table_name("livros") == "livros"
    assert _validate_table_name("my_collection") == "my_collection"
    assert _validate_table_name("_private") == "_private"
    assert _validate_table_name("Collection123") == "Collection123"


def test_validate_table_name_rejects_sql_injection():
    with pytest.raises(ValueError, match="Invalid collection name"):
        _validate_table_name("livros; DROP TABLE users")

    with pytest.raises(ValueError, match="Invalid collection name"):
        _validate_table_name("name' OR '1'='1")

    with pytest.raises(ValueError, match="Invalid collection name"):
        _validate_table_name("table-with-dashes")

    with pytest.raises(ValueError, match="Invalid collection name"):
        _validate_table_name("123starts_with_number")

    with pytest.raises(ValueError, match="Invalid collection name"):
        _validate_table_name("")


# =========================================================================
# Opcode registration tests
# =========================================================================


def test_pgvector_category_always_registered():
    """Category should be registered even without asyncpg installed."""
    from lexflow.opcodes import default_registry

    categories = default_registry.list_categories()
    pgvector_cat = [c for c in categories if c.id == "pgvector"]
    assert len(pgvector_cat) == 1
    assert pgvector_cat[0].label == "PgVector Operations"
    assert pgvector_cat[0].prefix == "pgvector_"


def test_pgvector_opcodes_registered_when_available():
    """Opcodes should be registered when asyncpg/pgvector are available."""
    try:
        import asyncpg  # noqa: F401
        import pgvector  # noqa: F401

        available = True
    except ImportError:
        available = False

    from lexflow.opcodes import default_registry

    opcode_names = default_registry.list_opcodes()
    pgvector_ops = [n for n in opcode_names if n.startswith("pgvector_")]

    if available:
        assert len(pgvector_ops) == 9
        expected = {
            "pgvector_connect",
            "pgvector_create_collection",
            "pgvector_collection_exists",
            "pgvector_delete_collection",
            "pgvector_upsert",
            "pgvector_upsert_batch",
            "pgvector_search",
            "pgvector_delete",
            "pgvector_disconnect",
        }
        assert set(pgvector_ops) == expected
    else:
        assert len(pgvector_ops) == 0


# =========================================================================
# Opcode logic tests (with mocked asyncpg)
# =========================================================================


@pytest.fixture
def mock_pool():
    """Create a mock asyncpg pool with async context manager support."""
    pool = MagicMock()
    conn = AsyncMock()

    # conn.transaction() returns an async context manager
    tx_ctx = MagicMock()
    tx_ctx.__aenter__ = AsyncMock(return_value=tx_ctx)
    tx_ctx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction.return_value = tx_ctx

    # pool.acquire() returns an async context manager (not a coroutine)
    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(return_value=conn)
    acquire_ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire.return_value = acquire_ctx

    pool._conn = conn
    return pool


# Only run opcode logic tests if asyncpg is available
try:
    import asyncpg  # noqa: F401

    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False


@pytest.mark.skipif(not HAS_ASYNCPG, reason="asyncpg not installed")
class TestPgvectorOpcodeLogic:
    async def test_create_collection_new(self, mock_pool):
        from lexflow.opcodes import default_registry

        mock_pool._conn.fetchval = AsyncMock(return_value=False)
        result = await default_registry.call(
            "pgvector_create_collection", [mock_pool, "livros", 768]
        )
        assert result is True
        assert (
            mock_pool._conn.execute.call_count == 2
        )  # CREATE EXTENSION + CREATE TABLE

    async def test_create_collection_exists(self, mock_pool):
        from lexflow.opcodes import default_registry

        mock_pool._conn.fetchval = AsyncMock(return_value=True)
        result = await default_registry.call(
            "pgvector_create_collection", [mock_pool, "livros", 768]
        )
        assert result is False

    async def test_collection_exists(self, mock_pool):
        from lexflow.opcodes import default_registry

        mock_pool._conn.fetchval = AsyncMock(return_value=True)
        result = await default_registry.call(
            "pgvector_collection_exists", [mock_pool, "livros"]
        )
        assert result is True

    async def test_delete_collection(self, mock_pool):
        from lexflow.opcodes import default_registry

        result = await default_registry.call(
            "pgvector_delete_collection", [mock_pool, "livros"]
        )
        assert result is True

    async def test_upsert(self, mock_pool):
        from lexflow.opcodes import default_registry

        result = await default_registry.call(
            "pgvector_upsert",
            [mock_pool, "livros", 1, [0.1, 0.2, 0.3], {"text": "hello"}],
        )
        assert result is True
        mock_pool._conn.execute.assert_called_once()

    async def test_upsert_batch_validation(self, mock_pool):
        from lexflow.opcodes import default_registry

        with pytest.raises(
            ValueError, match="point_ids and vectors must have the same length"
        ):
            await default_registry.call(
                "pgvector_upsert_batch",
                [mock_pool, "livros", [1, 2], [[0.1]], None],
            )

    async def test_search(self, mock_pool):
        from lexflow.opcodes import default_registry

        mock_rows = [
            {"id": 1, "score": 0.95, "payload": '{"text": "hello"}'},
            {"id": 2, "score": 0.80, "payload": '{"text": "world"}'},
        ]
        mock_pool._conn.fetch = AsyncMock(return_value=mock_rows)

        result = await default_registry.call(
            "pgvector_search",
            [mock_pool, "livros", [0.1, 0.2, 0.3], 5],
        )

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["score"] == 0.95
        assert result[0]["payload"] == {"text": "hello"}

    async def test_delete(self, mock_pool):
        from lexflow.opcodes import default_registry

        result = await default_registry.call(
            "pgvector_delete",
            [mock_pool, "livros", [1, 2, 3]],
        )
        assert result is True

    async def test_disconnect(self):
        from lexflow.opcodes import default_registry

        mock_pool = AsyncMock()
        result = await default_registry.call("pgvector_disconnect", [mock_pool])
        assert result is True
        mock_pool.close.assert_called_once()

    async def test_upsert_invalid_table_name(self, mock_pool):
        from lexflow.opcodes import default_registry

        with pytest.raises(ValueError, match="Invalid collection name"):
            await default_registry.call(
                "pgvector_upsert",
                [mock_pool, "bad; DROP TABLE", 1, [0.1], None],
            )
