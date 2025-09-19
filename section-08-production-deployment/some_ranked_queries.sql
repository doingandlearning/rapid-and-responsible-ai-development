WITH scored AS (
  SELECT
    id,
    text,
    meta_data,
    1 - (embedding <=> %s::vector) AS similarity,
    -- boost more recent documents
    (meta_data->>'year')::int AS year
  FROM chunks
  WHERE meta_data->>'audience' = 'international'
    AND meta_data->>'department' = 'informatics'
)
SELECT
  id,
  text,
  similarity,
  year,
  (similarity * 0.8 + (year - 2020) * 0.05) AS final_score
FROM scored
ORDER BY final_score DESC
LIMIT 10;

---

WITH scored AS (
  SELECT
    id,
    text,
    meta_data,
    1 - (embedding <=> %s::vector) AS similarity,
    CASE WHEN meta_data->>'doc_type' = 'handbook' THEN 0.2 ELSE 0 END AS handbook_bonus
  FROM chunks
)
SELECT
  id,
  text,
  similarity,
  handbook_bonus,
  (similarity + handbook_bonus) AS final_score
FROM scored
ORDER BY final_score DESC
LIMIT 10;
