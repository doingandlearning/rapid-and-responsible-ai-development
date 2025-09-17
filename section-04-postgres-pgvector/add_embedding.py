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

# commit to database
def add_book_to_db(book):
  """
  Assumes the book has the following keys:
  - title
  - authors (list of authors)
  - first_publish_year
  - subject
  """
  conn = psycopg.connect(**DB_CONFIG)
  cur = conn.cursor()

  description = f"""Book titled {book["title"]} by {", ".join(book["authors"])}. 
  First published in {book["first_publish_year"]}
  This is a book about {book["subject"]}
  """

  embedding = get_embeddings(description)

  cur.execute(
    """
    INSERT into items (name, item_data, embedding)
    VALUES (%s, %s, %s)
    """,
    (book["title"], json.dumps(book), embedding)
  )

  conn.commit()
  cur.close()
  conn.close()

add_book_to_db({"title": "Lake of Darkness",
    "authors": ["Adam Roberts"],
    "first_publish_year": 2024,
    "subject": ["fiction", "sci-fi", "hard sci-fi"]
    })