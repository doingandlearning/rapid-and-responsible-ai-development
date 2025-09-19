CREATE INDEX IF NOT EXISTS embedding_cosine_idx 
ON items 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

CREATE INDEX IF NOT EXISTS embedding_cosine_idx
ON items
USING hnsw (embedding vector_cosine_ops)
WITH (m = 6, ef_construction = 64);