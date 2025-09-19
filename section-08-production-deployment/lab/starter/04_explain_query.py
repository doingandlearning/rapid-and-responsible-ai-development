# 04_explain_query.py
# Exercise 4: Inspect a vector search plan via EXPLAIN ANALYZE.
# Usage:
#   python 04_explain_query.py "How do I reset my password?" "<=>"
# Distance op: "<=>" for cosine, "<->" for L2; default "<=>".

import sys
import json
import os
from typing import List
sys.path.append(os.path.dirname(__file__))
from common import embed_text, get_conn

def main():
    """
    TODO: Implement EXPLAIN ANALYZE for vector queries
    1. Parse command line arguments (query text and optional distance operator)
    2. Generate embedding for the query text
    3. Execute EXPLAIN ANALYZE query on document_chunks table
    4. Display the query plan with analysis tips
    """
    if len(sys.argv) < 2:
        print("Usage: python 04_explain_query.py \"<query text>\" [<op>]")
        print("Example: python 04_explain_query.py \"How do I reset my password?\"")
        print("Distance operators:")
        print("  <=>  - Cosine similarity (default)")
        print("  <->  - L2 distance")
        sys.exit(1)

    query_text = sys.argv[1]
    op = sys.argv[2] if len(sys.argv) > 2 else "<=>"

    print(f"🔍 EXPLAIN ANALYZE for query: '{query_text}'")
    print(f"📊 Using distance operator: {op}")
    print("="*80)

    try:
        # TODO: Generate embedding
        print("🔄 Generating embedding...")
        # vec: List[float] = embed_text(query_text)
        # vec_literal = "'" + "[" + ",".join(f"{x:.7f}" for x in vec) + "]" + "'"
        # print(f"✅ Generated {len(vec)}-dimensional embedding")

        # TODO: Prepare EXPLAIN ANALYZE query using document_chunks table
        # sql = f"""
        # EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
        # SELECT 
        #     id,
        #     text,
        #     document_title,
        #     page_number,
        #     section_title,
        #     1 - (embedding {op} {vec_literal}::vector) as similarity_score
        # FROM document_chunks
        # WHERE embedding IS NOT NULL
        # ORDER BY embedding {op} {vec_literal}::vector
        # LIMIT 5;
        # """

        print("\n📋 Executing EXPLAIN ANALYZE...")
        print("-" * 40)
        print("TODO: Implement the EXPLAIN ANALYZE query execution")

        # TODO: Execute query and display results
        # with get_conn() as conn, conn.cursor() as cur:
        #     cur.execute(sql)
        #     plan_lines = [row[0] for row in cur.fetchall()]
        #     
        #     for line in plan_lines:
        #         print(line)
        
        print("\n" + "="*80)
        print("📊 Query Plan Analysis:")
        print("Look for:")
        print("  • Index usage (Index Scan vs Seq Scan)")
        print("  • Execution time (should be < 100ms for good performance)")
        print("  • Buffer usage (lower is better)")
        print("  • Vector operations (should use pgvector index)")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure PostgreSQL is running on port 5050")
        print("  • Check that pgvector extension is installed")
        print("  • Verify that document_chunks table exists with embeddings")
        sys.exit(1)

def compare_index_types(query_text: str):
    """
    TODO: Implement comparison of different index types and distance operators
    1. Generate embedding for the query
    2. Test both cosine similarity (<=>) and L2 distance (<->)
    3. Display execution times and index usage for each
    4. Provide recommendations
    """
    print(f"\n🔬 COMPARING INDEX TYPES for: '{query_text}'")
    print("="*80)
    
    try:
        # TODO: Generate embedding
        # vec: List[float] = embed_text(query_text)
        # vec_literal = "'" + "[" + ",".join(f"{x:.7f}" for x in vec) + "]" + "'"
        
        # TODO: Test different distance operators
        operators = [
            ("<=>", "Cosine similarity"),
            ("<->", "L2 distance")
        ]
        
        for op, description in operators:
            print(f"\n📊 Testing {description} ({op}):")
            print("-" * 40)
            print("TODO: Implement operator comparison")
            
            # TODO: Execute EXPLAIN ANALYZE for each operator
            # sql = f"""
            # EXPLAIN (ANALYZE, BUFFERS)
            # SELECT id, document_title, page_number
            # FROM document_chunks
            # WHERE embedding IS NOT NULL
            # ORDER BY embedding {op} {vec_literal}::vector
            # LIMIT 5;
            # """
            
            # with get_conn() as conn, conn.cursor() as cur:
            #     cur.execute(sql)
            #     plan_lines = [row[0] for row in cur.fetchall()]
            #     
            #     # Extract key metrics
            #     for line in plan_lines:
            #         if "Execution Time:" in line:
            #             print(f"⏱️  {line}")
            #         elif "Planning Time:" in line:
            #             print(f"📋 {line}")
            #         elif "Index" in line and "Scan" in line:
            #             print(f"🔍 {line}")
        
        print(f"\n💡 Recommendations:")
        print(f"  • Use cosine similarity (<=>) for most text similarity tasks")
        print(f"  • L2 distance (<->) is faster but may be less accurate for text")
        print(f"  • Ensure you have a vector index: CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);")
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        if len(sys.argv) < 3:
            print("Usage: python 04_explain_query.py --compare \"<query text>\"")
            sys.exit(1)
        compare_index_types(sys.argv[2])
    else:
        main()
