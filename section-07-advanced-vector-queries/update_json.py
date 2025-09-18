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
        cur.execute("""
            UPDATE document_chunks 
            SET meta_data = jsonb_set(
                COALESCE(meta_data, '{}'::jsonb),
                '{has_section}',
                'true'::jsonb
            )
            WHERE section_title IS NOT NULL;
        """)
        conn.commit()
