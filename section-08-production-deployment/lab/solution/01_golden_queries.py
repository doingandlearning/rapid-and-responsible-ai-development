# 01_golden_queries.py
# Exercise 1: Golden queries — run your pipeline on a tiny eval set.

from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(__file__))
from common import get_rag_pipeline

golden_set: List[Dict[str, str]] = [
    {"query": "What are the library opening hours?", "expected": "The library is open"},
    {"query": "Where is the IT helpdesk located?", "expected": "Located on the"},
    {"query": "How do I reset my password?", "expected": "password reset"},
    {"query": "What are the WiFi requirements?", "expected": "WiFi"},
    {"query": "How do I access VPN?", "expected": "VPN"},
]

def run():
    print("🧪 GOLDEN QUERIES EVALUATION")
    print("="*80)
    
    rag = get_rag_pipeline()
    total_queries = len(golden_set)
    
    for i, item in enumerate(golden_set, 1):
        q = item["query"]
        expected_hint = item["expected"]
        
        print(f"\n📋 Query {i}/{total_queries}: {q}")
        print(f"Expected hint: {expected_hint}")
        print("-" * 60)
        
        try:
            response = rag(q)
            
            # Handle RAGResponse object
            if hasattr(response, 'answer'):
                answer = response.answer
                confidence = getattr(response, 'confidence_level', 'unknown')
                chunks_found = getattr(response, 'chunks_found', 0)
                response_time = getattr(response, 'response_time', 0)
                success = getattr(response, 'success', False)
                
                print(f"✅ Answer: {answer}")
                print(f"📊 Confidence: {confidence}")
                print(f"🔍 Chunks found: {chunks_found}")
                print(f"⏱️  Response time: {response_time:.2f}s")
                print(f"🎯 Success: {success}")
                
                # Show sources if available
                if hasattr(response, 'sources') and response.sources:
                    print(f"📚 Sources: {len(response.sources)}")
                    for j, source in enumerate(response.sources[:3], 1):
                        doc = source.get('document', 'Unknown')
                        page = source.get('page', '')
                        similarity = source.get('similarity', 0)
                        print(f"   {j}. {doc}{f', Page {page}' if page else ''} ({similarity:.2f})")
            else:
                # Fallback for string response
                print(f"✅ Answer: {response}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*80)
    
    print(f"\n🎯 Evaluation complete! Tested {total_queries} golden queries.")
    print("💡 Look for patterns in what works well and what needs improvement.")

if __name__ == "__main__":
    run()
