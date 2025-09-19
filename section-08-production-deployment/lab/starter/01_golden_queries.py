# 01_golden_queries.py
# Exercise 1: Golden queries — run your pipeline on a tiny eval set.

from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(__file__))
from common import get_rag_pipeline

# TODO: Define your golden set of test queries with expected answers
# These should be queries you know the system should be able to answer
golden_set: List[Dict[str, str]] = [
    # TODO: Add 3-5 test queries with expected answer hints
    # Example:
    # {"query": "What are the library opening hours?", "expected": "The library is open"},
    # {"query": "Where is the IT helpdesk located?", "expected": "Located on the"},
    # {"query": "How do I reset my password?", "expected": "password reset"},
]

def run():
    """
    TODO: Implement the golden queries evaluation
    1. Get the RAG pipeline using get_rag_pipeline()
    2. Loop through each item in golden_set
    3. For each query:
       - Call the RAG pipeline with the query
       - Print the query, answer, and expected hint
       - Handle both RAGResponse objects and string responses
    4. Add error handling for failed queries
    """
    print("🧪 GOLDEN QUERIES EVALUATION")
    print("="*80)
    
    # TODO: Get the RAG pipeline
    # rag = get_rag_pipeline()
    
    # TODO: Loop through golden_set and test each query
    # for i, item in enumerate(golden_set, 1):
    #     q = item["query"]
    #     expected_hint = item["expected"]
    #     
    #     print(f"\n📋 Query {i}: {q}")
    #     print(f"Expected hint: {expected_hint}")
    #     print("-" * 60)
    #     
    #     try:
    #         # TODO: Call RAG pipeline and handle response
    #         # response = rag(q)
    #         # TODO: Print results (handle RAGResponse vs string)
    #     except Exception as e:
    #         print(f"❌ Error: {e}")
    
    print(f"\n🎯 Evaluation complete!")
    print("💡 Look for patterns in what works well and what needs improvement.")

if __name__ == "__main__":
    run()
