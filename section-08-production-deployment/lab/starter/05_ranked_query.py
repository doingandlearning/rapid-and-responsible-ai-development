# 05_ranked_query.py
# Exercise 5: Advanced ranked queries with JSONB metadata and vector similarity.
# Usage: python 05_ranked_query.py "How do I reset my password?"

import sys
import json
import os
from typing import List, Dict, Any
sys.path.append(os.path.dirname(__file__))
from common import embed_text, get_conn

def run_ranked_query(query_text: str, sim_weight: float = 0.8, priority_weight: float = 0.2, limit: int = 10):
    """
    TODO: Implement ranked query combining vector similarity with JSONB metadata scoring
    1. Generate embedding for the query text
    2. Create SQL query that combines:
       - Vector similarity (1 - distance)
       - JSONB metadata fields (priority, relevance, last_updated)
       - Weighted scoring formula
    3. Execute query and display results with metrics
    4. Handle cases where metadata might not exist
    """
    print(f"🔍 RANKED QUERY: '{query_text}'")
    print(f"📊 Weights - Similarity: {sim_weight}, Priority: {priority_weight}")
    print("="*80)
    
    try:
        # TODO: Generate embedding
        print("🔄 Generating embedding...")
        # vec: List[float] = embed_text(query_text)
        # vec_literal = "'" + "[" + ",".join(f"{x:.7f}" for x in vec) + "]" + "'"
        # print(f"✅ Generated {len(vec)}-dimensional embedding")

        # TODO: Create ranked query with JSONB metadata
        # sql = f"""
        # WITH scored AS (
        #   SELECT
        #     id,
        #     text,
        #     document_title,
        #     page_number,
        #     section_title,
        #     LEFT(text, 160) AS preview,
        #     1 - (embedding <=> {vec_literal}::vector) AS similarity,
        #     COALESCE((metadata->>'priority')::int, 0) AS priority,
        #     COALESCE((metadata->>'relevance')::float, 0.5) AS relevance,
        #     COALESCE((metadata->>'last_updated')::text, 'unknown') AS last_updated
        #   FROM document_chunks
        #   WHERE embedding IS NOT NULL
        # )
        # SELECT
        #   id,
        #   document_title,
        #   page_number,
        #   section_title,
        #   preview,
        #   ROUND(similarity::numeric, 4) AS similarity,
        #   priority,
        #   ROUND(relevance::numeric, 4) AS relevance,
        #   ROUND((similarity * {sim_weight} + priority * {priority_weight} + relevance * 0.1)::numeric, 4) AS final_score,
        #   last_updated
        # FROM scored
        # ORDER BY final_score DESC
        # LIMIT {limit};
        # """

        print("\n📋 Executing ranked query...")
        print("-" * 40)
        print("TODO: Implement the ranked query execution")

        # TODO: Execute query and display results
        # with get_conn() as conn, conn.cursor() as cur:
        #     cur.execute(sql)
        #     rows = cur.fetchall()
        #     
        #     if not rows:
        #         print("❌ No results found")
        #         return
        #     
        #     # Display results
        #     print(f"✅ Found {len(rows)} results:")
        #     print()
        #     
        #     for i, row in enumerate(rows, 1):
        #         (id, doc_title, page_num, section, preview, similarity, 
        #          priority, relevance, final_score, last_updated) = row
        #         
        #         print(f"🏆 Rank {i} (Score: {final_score})")
        #         print(f"   📄 Document: {doc_title}")
        #         if page_num:
        #             print(f"   📖 Page: {page_num}")
        #         if section:
        #             print(f"   📑 Section: {section}")
        #         print(f"   📝 Preview: {preview}...")
        #         print(f"   📊 Metrics:")
        #         print(f"      • Similarity: {similarity}")
        #         print(f"      • Priority: {priority}")
        #         print(f"      • Relevance: {relevance}")
        #         if last_updated != 'unknown':
        #             print(f"      • Updated: {last_updated}")
        #         print()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure PostgreSQL is running on port 5050")
        print("  • Check that document_chunks table exists with embeddings")
        print("  • Verify that metadata column exists (JSONB)")

def run_simple_ranked(query_text: str, limit: int = 5):
    """
    TODO: Implement simple ranked query without JSONB metadata (fallback)
    1. Generate embedding for the query
    2. Create simple similarity-based query
    3. Execute and display results
    """
    print(f"🔍 SIMPLE RANKED QUERY: '{query_text}'")
    print("="*60)
    
    try:
        # TODO: Generate embedding
        # vec: List[float] = embed_text(query_text)
        # vec_literal = "'" + "[" + ",".join(f"{x:.7f}" for x in vec) + "]" + "'"

        # TODO: Create simple similarity query
        # sql = f"""
        # SELECT 
        #     id,
        #     document_title,
        #     page_number,
        #     section_title,
        #     LEFT(text, 200) AS preview,
        #     ROUND((1 - (embedding <=> {vec_literal}::vector))::numeric, 4) AS similarity
        # FROM document_chunks
        # WHERE embedding IS NOT NULL
        # ORDER BY embedding <=> {vec_literal}::vector
        # LIMIT {limit};
        # """

        # TODO: Execute and display results
        print("TODO: Implement simple ranked query")

    except Exception as e:
        print(f"❌ Error: {e}")

def demonstrate_ranking_strategies():
    """
    TODO: Implement demonstration of different ranking strategies
    1. Define different weight combinations for similarity vs priority
    2. Test each strategy with the same query
    3. Display results for comparison
    4. Provide recommendations
    """
    print("🎯 RANKING STRATEGIES DEMONSTRATION")
    print("="*80)
    
    test_query = "password reset"
    
    strategies = [
        ("Similarity only", 1.0, 0.0),
        ("Similarity + Priority", 0.8, 0.2),
        ("Balanced", 0.6, 0.4),
        ("Priority heavy", 0.3, 0.7)
    ]
    
    for name, sim_weight, priority_weight in strategies:
        print(f"\n📊 Strategy: {name}")
        print(f"   Weights - Similarity: {sim_weight}, Priority: {priority_weight}")
        print("-" * 60)
        print("TODO: Implement strategy comparison")
        
        # TODO: Test each strategy
        # try:
        #     run_ranked_query(test_query, sim_weight, priority_weight, limit=3)
        # except Exception as e:
        #     print(f"   ❌ Error: {e}")
        #     # Fallback to simple ranking
        #     run_simple_ranked(test_query, limit=3)

def main():
    """
    TODO: Implement main function with command line argument handling
    1. Parse command line arguments
    2. Handle --strategies flag for demonstration
    3. Try advanced ranked query first, fallback to simple if needed
    """
    if len(sys.argv) < 2:
        print("Usage: python 05_ranked_query.py \"<query text>\" [--strategies]")
        print("Examples:")
        print("  python 05_ranked_query.py \"How do I reset my password?\"")
        print("  python 05_ranked_query.py \"WiFi setup\" --strategies")
        sys.exit(1)

    query_text = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--strategies":
        demonstrate_ranking_strategies()
    else:
        print("TODO: Implement main query execution")
        # TODO: Try advanced ranked query first
        # try:
        #     run_ranked_query(query_text)
        # except Exception as e:
        #     print(f"⚠️  Advanced query failed: {e}")
        #     print("🔄 Falling back to simple ranked query...")
        #     run_simple_ranked(query_text)

if __name__ == "__main__":
    main()
