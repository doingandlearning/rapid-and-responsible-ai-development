import requests
import psycopg
import json

DB_CONFIG = {
  "dbname": "pgvector",
  "user": "postgres",
  "password": "postgres",
  "host": "localhost",
  "port": "5050"
}

OLLAMA_URL = "http://localhost:11434/api/embed"

# generate embeddings
def get_embeddings(text):
  data = {
    "model": "bge-m3",
    "input": text
  }

  response = requests.post(OLLAMA_URL, 
                          json=data
  )
  response.raise_for_status()
  data = response.json()
  embedding = data.get("embeddings", [])
  if len(embedding) == 0:
    raise Exception("No embeddings.")
  return embedding[0]

def get_k_nearest_neighbors(user_embedding, k=3):
  with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
      cur.execute(
        """
        SELECT name, 1 - (embedding <=> %s) AS similarity
        FROM items
        ORDER BY similarity DESC
        LIMIT %s
        """,
        (json.dumps(user_embedding), k)

      )
      results = cur.fetchall()
      return results

if __name__ == "__main__":
  user_query = input("What do you want books about? ")
  user_embedding = get_embeddings(f"Books about {user_query}")
  results = get_k_nearest_neighbors(user_embedding)
  for name, similarity in results:
    print(f"{name} (Similarity: {similarity:.4f})")
      
