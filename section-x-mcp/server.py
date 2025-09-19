import psycopg
import requests
import json

from mcp.server.fastmcp import FastMCP

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# API configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

mcp = FastMCP("rag-similarity")

def generate_embeddings(text):
  response = requests.post(OLLAMA_URL, json={
    "model": EMBEDDING_MODEL,
    "input": text
  })
  data = response.json()
  embedding = data["embeddings"][0]
  return embedding

@mcp.tool()
async def search_chunks(query, limit):
  """
  Similarity search over document chunks

  Args:
    query: Natural langauge query to embed and search
    limit: Number of results to return
  """

  emb = generate_embeddings(query)

  with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
      cur.execute("""
        SELECT id, document_id, document_title, text, page_number, section_title,
          chunk_index, word_count, character_count, created_at,
          1 - (embedding <=> %s::vector) as similarity
        FROM document_chunks
        ORDER BY 1 - (embedding <=> %s::vector) DESC
        LIMIT %s

      """, (json.dumps(emb), json.dumps(emb), limit))

      results = cur.fetchall()

      return {"query": query, "limit": limit, "count": len(results), "results": results}


if __name__ == "__main__":
  mcp.run()