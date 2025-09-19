# 02_simple_scoring.py
# Exercise 2: Lightweight pass/fail scoring (no external libs).

from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(__file__))
from common import get_rag_pipeline

golden_set: List[Dict[str, str]] = [
    {"query": "What are the library opening hours?", "expected": "hours"},
    {"query": "Where is the IT helpdesk located?", "expected": "helpdesk"},
    {"query": "How do I reset my password?", "expected": "password"},
    {"query": "What are the WiFi requirements?", "expected": "WiFi"},
    {"query": "How do I access VPN?", "expected": "VPN"},
]

def simple_eval(response: Any, expected_hint: str) -> str:
    """
    Heuristic: pass if any keyword token from expected_hint appears in result.
    Works with both RAGResponse objects and string responses.
    """
    # Extract text from RAGResponse object or use string directly
    if hasattr(response, 'answer'):
        result_text = response.answer
    else:
        result_text = str(response)
    
    tokens = [t.strip().lower() for t in expected_hint.split() if t.strip()]
    rlow = result_text.lower()
    return "pass" if any(t in rlow for t in tokens) else "fail"

def detailed_eval(response: Any, expected_hint: str) -> Dict[str, Any]:
    """
    More detailed evaluation including confidence and other metrics
    """
    result = {
        "basic_eval": simple_eval(response, expected_hint),
        "has_answer": False,
        "confidence": "unknown",
        "chunks_found": 0,
        "response_time": 0,
        "success": False
    }
    
    if hasattr(response, 'answer'):
        result["has_answer"] = bool(response.answer and response.answer.strip())
        result["confidence"] = getattr(response, 'confidence_level', 'unknown')
        result["chunks_found"] = getattr(response, 'chunks_found', 0)
        result["response_time"] = getattr(response, 'response_time', 0)
        result["success"] = getattr(response, 'success', False)
    else:
        result["has_answer"] = bool(str(response).strip())
    
    return result

def run():
    print("📊 SIMPLE SCORING EVALUATION")
    print("="*80)
    
    rag = get_rag_pipeline()
    passes = 0
    total_queries = len(golden_set)
    
    print(f"Testing {total_queries} queries with simple pass/fail scoring...")
    print()
    
    for i, item in enumerate(golden_set, 1):
        q = item["query"]
        expected_hint = item["expected"]
        
        try:
            response = rag(q)
            eval_result = detailed_eval(response, expected_hint)
            verdict = eval_result["basic_eval"]
            
            passes += int(verdict == "pass")
            
            # Display results
            status_emoji = "✅" if verdict == "pass" else "❌"
            print(f"{status_emoji} [{verdict.upper()}] Query {i}: {q}")
            
            if hasattr(response, 'answer'):
                print(f"   📝 Answer: {response.answer[:100]}{'...' if len(response.answer) > 100 else ''}")
                print(f"   📊 Confidence: {eval_result['confidence']}")
                print(f"   🔍 Chunks: {eval_result['chunks_found']}")
                print(f"   ⏱️  Time: {eval_result['response_time']:.2f}s")
            else:
                print(f"   📝 Answer: {str(response)[:100]}{'...' if len(str(response)) > 100 else ''}")
            
            print()
            
        except Exception as e:
            print(f"❌ [ERROR] Query {i}: {q}")
            print(f"   Error: {e}")
            print()
    
    # Summary
    pass_rate = (passes / total_queries) * 100
    print("="*80)
    print(f"📈 SUMMARY: {passes}/{total_queries} passed ({pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        print("🎉 Excellent performance! Your RAG system is working well.")
    elif pass_rate >= 60:
        print("👍 Good performance with room for improvement.")
    else:
        print("⚠️  Performance needs improvement. Consider:")
        print("   - Checking your document corpus")
        print("   - Adjusting similarity thresholds")
        print("   - Improving chunking strategy")
        print("   - Reviewing your golden query expectations")

if __name__ == "__main__":
    run()
