"""PgVector (PostgreSQL + pgvector) opcodes for LexFlow.

This module provides opcodes for vector similarity search using PostgreSQL
with the pgvector extension, as an alternative to Qdrant.

Installation:
    pip install lexflow[pgvector]

Requires a PostgreSQL instance with pgvector extension installed.
"""

import asyncio
import json
import re
from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import asyncpg
    from pgvector.asyncpg import register_vector

    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False


def _check_pgvector():
    """Raise ImportError if asyncpg/pgvector are not installed."""
    if not PGVECTOR_AVAILABLE:
        raise ImportError(
            "asyncpg and pgvector are required. Install with:\n"
            "  uv add 'lexflow[pgvector]'"
        )


_VALID_TABLE_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_table_name(name: str) -> str:
    """Validate table name to prevent SQL injection."""
    if not _VALID_TABLE_NAME.match(name):
        raise ValueError(
            f"Invalid collection name: {name!r}. Must match [a-zA-Z_][a-zA-Z0-9_]*"
        )
    return name


def register_pgvector_opcodes():
    """Register PgVector opcodes to the default registry."""
    register_category(
        id="pgvector",
        label="PgVector Operations",
        prefix="pgvector_",
        color="#336791",
        icon="🐘",
        requires="pgvector",
        order=235,
    )

    if not PGVECTOR_AVAILABLE:
        return

    @opcode(category="pgvector")
    async def pgvector_connect(
        dsn: str,
        min_size: int = 1,
        max_size: int = 10,
        ensure_extension: bool = True,
    ) -> Any:
        """Create an asyncpg connection pool with pgvector support.

        Args:
            dsn: PostgreSQL connection string
            min_size: Minimum pool connections (default: 1)
            max_size: Maximum pool connections (default: 10)
            ensure_extension: Run CREATE EXTENSION IF NOT EXISTS vector (default: True).
                Set to False if the extension is pre-configured or the user lacks privileges.

        Returns:
            asyncpg.Pool instance with pgvector type registered
        """
        if ensure_extension:
            conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=10.0)
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.close()

        async def _init_connection(conn):
            await register_vector(conn)

        pool = await asyncpg.create_pool(
            dsn, min_size=min_size, max_size=max_size, init=_init_connection
        )
        return pool

    @opcode(category="pgvector")
    async def pgvector_create_collection(
        pool: Any, name: str, vector_size: int = 768
    ) -> bool:
        """Create a pgvector collection (table) if it doesn't exist.

        Creates the pgvector extension and a table with id, embedding, and payload columns.

        Args:
            pool: asyncpg.Pool instance
            name: Collection (table) name
            vector_size: Dimension of embedding vectors (default: 768)

        Returns:
            True if created, False if already existed
        """
        table = _validate_table_name(name)
        async with pool.acquire() as conn:
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                "WHERE table_name = $1)",
                table,
            )
            if exists:
                return False

            await conn.execute(
                f'CREATE TABLE "{table}" ('
                f"  id BIGINT PRIMARY KEY,"
                f"  embedding vector({int(vector_size)}),"
                f"  payload JSONB DEFAULT '{{}}'::jsonb"
                f")"
            )
            return True

    @opcode(category="pgvector")
    async def pgvector_collection_exists(pool: Any, name: str) -> bool:
        """Check if a pgvector collection (table) exists.

        Args:
            pool: asyncpg.Pool instance
            name: Collection (table) name to check

        Returns:
            True if collection exists
        """
        table = _validate_table_name(name)
        async with pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                "WHERE table_name = $1)",
                table,
            )

    @opcode(category="pgvector")
    async def pgvector_delete_collection(pool: Any, name: str) -> bool:
        """Delete a pgvector collection (table).

        Args:
            pool: asyncpg.Pool instance
            name: Collection (table) name to delete

        Returns:
            True if deletion was successful
        """
        table = _validate_table_name(name)
        async with pool.acquire() as conn:
            await conn.execute(f'DROP TABLE IF EXISTS "{table}"')
        return True

    @opcode(category="pgvector")
    async def pgvector_upsert(
        pool: Any,
        collection: str,
        point_id: int,
        vector: List[float],
        payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Insert or update a single vector point in a pgvector collection.

        Args:
            pool: asyncpg.Pool instance
            collection: Collection (table) name
            point_id: Unique identifier for the point
            vector: Embedding vector
            payload: Optional metadata dict

        Returns:
            True if upsert was successful
        """
        table = _validate_table_name(collection)
        async with pool.acquire() as conn:
            await conn.execute(
                f'INSERT INTO "{table}" (id, embedding, payload) '
                f"VALUES ($1, $2, $3) "
                f"ON CONFLICT (id) DO UPDATE SET "
                f"embedding = EXCLUDED.embedding, payload = EXCLUDED.payload",
                point_id,
                vector,
                json.dumps(payload or {}).replace("\\u0000", "").replace("\x00", ""),
            )
        return True

    @opcode(category="pgvector")
    async def pgvector_upsert_batch(
        pool: Any,
        collection: str,
        point_ids: List[int],
        vectors: List[List[float]],
        payloads: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Insert or update multiple vector points in a pgvector collection.

        Args:
            pool: asyncpg.Pool instance
            collection: Collection (table) name
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

        table = _validate_table_name(collection)
        rows = [
            (
                pid,
                vec,
                json.dumps(payloads[i] if payloads else {})
                .replace("\\u0000", "")
                .replace("\x00", ""),
            )
            for i, (pid, vec) in enumerate(zip(point_ids, vectors))
        ]

        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    f'INSERT INTO "{table}" (id, embedding, payload) '
                    f"VALUES ($1, $2, $3) "
                    f"ON CONFLICT (id) DO UPDATE SET "
                    f"embedding = EXCLUDED.embedding, payload = EXCLUDED.payload",
                    rows,
                )
        return True

    @opcode(category="pgvector")
    async def pgvector_search(
        pool: Any,
        collection: str,
        query_vector: List[float],
        limit: int = 5,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in a pgvector collection.

        Uses cosine distance (<=> operator) for similarity ranking.
        Optionally filters by JSONB payload fields.

        Args:
            pool: asyncpg.Pool instance
            collection: Collection (table) name
            query_vector: Embedding vector to search for
            limit: Maximum number of results (default: 5)
            filter_field: Optional payload field name to filter on (legacy)
            filter_value: Value the filter_field must match (legacy)
            filters: Optional dict of payload field->value pairs to filter on.
                     Empty string values are ignored. Takes precedence over
                     filter_field/filter_value when provided.

        Returns:
            List of dicts with keys: id, score, payload
        """
        table = _validate_table_name(collection)

        # Build WHERE conditions and params
        # Base params: $1 = query_vector, $2 = limit
        where_clauses: List[str] = []
        params: List[Any] = [query_vector, limit]
        param_idx = 3

        if filters:
            # New multi-filter mode: build compound WHERE
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                where_clauses.append(
                    "payload->>$%d = $%d" % (param_idx, param_idx + 1)
                )
                params.append(key)
                params.append(str(value))
                param_idx += 2
        elif filter_field and filter_value is not None:
            # Legacy single-filter mode (backward compat)
            where_clauses.append(
                "payload->>$%d = $%d" % (param_idx, param_idx + 1)
            )
            params.append(filter_field)
            params.append(filter_value)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses) + " "

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT id, 1 - (embedding <=> $1) AS score, payload "
                f'FROM "{table}" '
                f"{where_sql}"
                f"ORDER BY embedding <=> $1 "
                f"LIMIT $2",
                *params,
            )
        return [
            {
                "id": row["id"],
                "score": float(row["score"]),
                "payload": json.loads(row["payload"]),
            }
            for row in rows
        ]

    @opcode(category="pgvector")
    async def pgvector_delete(pool: Any, collection: str, point_ids: List[int]) -> bool:
        """Delete points from a pgvector collection by IDs.

        Args:
            pool: asyncpg.Pool instance
            collection: Collection (table) name
            point_ids: List of point IDs to delete

        Returns:
            True if deletion was successful
        """
        table = _validate_table_name(collection)
        async with pool.acquire() as conn:
            await conn.execute(
                f'DELETE FROM "{table}" WHERE id = ANY($1)',
                point_ids,
            )
        return True

    @opcode(category="pgvector")
    async def pgvector_disconnect(pool: Any) -> bool:
        """Close a pgvector connection pool.

        Args:
            pool: asyncpg.Pool instance to close

        Returns:
            True if pool was closed successfully
        """
        await pool.close()
        return True
