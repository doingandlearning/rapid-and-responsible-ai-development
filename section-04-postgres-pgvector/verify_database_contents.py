import psycopg

DB_CONFIG = {
  "dbname": "pgvector",
  "user": "postgres",
  "password": "postgres",
  "host": "localhost",
  "port": "5050"
}


with psycopg.connect(**DB_CONFIG) as conn:
  with conn.cursor() as cur:
    cur.execute("SELECT count(*) from items")
    results = cur.fetchone()
    print(results)
    