# server.py
import os
import json
import logging
from typing import Any, Dict, List, Optional

import requests
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mcp-rag")

# --- Environment ---
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = int(os.getenv("PGPORT", "5050"))
PG_DB = os.getenv("PGDATABASE", "pgvector")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASS = os.getenv("PGPASSWORD", "postgres")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/embed")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
TOP_K = int(os.getenv("TOP_K", "8"))

# --- MCP server ---
mcp = FastMCP("rag-similarity")

def get_db():
    return psycopg.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )

def create_embedding(text: str) -> List[float]:
    payload = {"model": EMBEDDING_MODEL, "input": text}
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Ollama embed returns {"embeddings": [[...]]} or {"embedding":[...]} depending on version
    if "embeddings" in data:
        return data["embeddings"][0]
    if "embedding" in data:
        return data["embedding"]
    raise RuntimeError(f"Unexpected embedding response keys: {list(data.keys())}")

def _as_json(obj: Any) -> Any:
    if obj is None:
        return {}
    if isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            return obj
    return obj


@mcp.tool()
async def search_chunks(
    query: str,
    limit: int = TOP_K,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Similarity search over document_chunks using pgvector.

    Args:
        query: Natural-language query to embed and search.
        limit: Number of results to return.
        filters: Optional filters including:
            - document_id: Filter by specific document ID
            - document_title: Filter by document title (partial match)
            - page_number: Filter by specific page number
            - section_title: Filter by section title (partial match)
            - chunk_index: Filter by specific chunk index
            - min_word_count: Minimum word count
            - max_word_count: Maximum word count
    """
    emb = create_embedding(query)
    where_clauses = ["TRUE"]
    where_params: List[Any] = []

    if filters:
        if (doc_id := filters.get("document_id")):
            where_clauses.append("document_id = %s")
            where_params.append(doc_id)
        if (doc_title := filters.get("document_title")):
            where_clauses.append("document_title ILIKE %s")
            where_params.append(f"%{doc_title}%")
        if (page_num := filters.get("page_number")):
            where_clauses.append("page_number = %s")
            where_params.append(page_num)
        if (section := filters.get("section_title")):
            where_clauses.append("section_title ILIKE %s")
            where_params.append(f"%{section}%")
        if (chunk_idx := filters.get("chunk_index")):
            where_clauses.append("chunk_index = %s")
            where_params.append(chunk_idx)
        if (min_words := filters.get("min_word_count")):
            where_clauses.append("word_count >= %s")
            where_params.append(min_words)
        if (max_words := filters.get("max_word_count")):
            where_clauses.append("word_count <= %s")
            where_params.append(max_words)

    where_sql = " AND ".join(where_clauses)

    sql = f"""
        SELECT
            id,
            document_id,
            document_title,
            text,
            page_number,
            section_title,
            chunk_index,
            word_count,
            character_count,
            created_at,
            1 - (embedding <=> %s::vector) AS similarity
        FROM document_chunks
        WHERE {where_sql}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    params: List[Any] = [emb] + where_params + [emb, limit]

    with get_db() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": str(r["id"]),
            "document_id": r["document_id"],
            "document_title": r["document_title"],
            "text": r["text"],
            "page_number": r.get("page_number"),
            "section_title": r.get("section_title"),
            "chunk_index": r.get("chunk_index"),
            "word_count": r.get("word_count"),
            "character_count": r.get("character_count"),
            "created_at": r.get("created_at").isoformat() if r.get("created_at") else None,
            "similarity": float(r["similarity"]),
        })

    return {"query": query, "limit": limit, "count": len(results), "results": results}

@mcp.tool()
async def similar_to_chunk_tool(chunk_id: str, limit: int = 5) -> Dict[str, Any]:
    with get_db() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT embedding FROM document_chunks WHERE id = %s", (chunk_id,))
        row = cur.fetchone()
        if not row or not row.get("embedding"):
            return {"chunk_id": chunk_id, "count": 0, "results": []}
        emb = row["embedding"]

        sql = """
            SELECT
                id,
                document_id,
                document_title,
                text,
                page_number,
                section_title,
                chunk_index,
                word_count,
                character_count,
                created_at,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            WHERE id <> %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        cur.execute(sql, (emb, chunk_id, emb, limit))
        rows = cur.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": str(r["id"]),
            "document_id": r["document_id"],
            "document_title": r["document_title"],
            "text": r["text"],
            "page_number": r.get("page_number"),
            "section_title": r.get("section_title"),
            "chunk_index": r.get("chunk_index"),
            "word_count": r.get("word_count"),
            "character_count": r.get("character_count"),
            "created_at": r.get("created_at").isoformat() if r.get("created_at") else None,
            "similarity": float(r["similarity"]),
        })
    return {"chunk_id": chunk_id, "limit": limit, "count": len(results), "results": results}

if __name__ == "__main__":
    # Runs an stdio MCP server (Claude Desktop can launch via command)
    mcp.run()
