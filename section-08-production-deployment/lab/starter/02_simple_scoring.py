# 02_simple_scoring.py
# Exercise 2: Lightweight pass/fail scoring (no external libs).

from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(__file__))
from common import get_rag_pipeline

# TODO: Define your golden set of test queries with expected answers
golden_set: List[Dict[str, str]] = [
    # TODO: Add 3-5 test queries with expected answer hints
    # Example:
    # {"query": "What are the library opening hours?", "expected": "hours"},
    # {"query": "Where is the IT helpdesk located?", "expected": "helpdesk"},
    # {"query": "How do I reset my password?", "expected": "password"},
]

def simple_eval(response: Any, expected_hint: str) -> str:
    """
    TODO: Implement simple pass/fail evaluation
    Heuristic: pass if any keyword token from expected_hint appears in result.
    Works with both RAGResponse objects and string responses.
    
    Steps:
    1. Extract text from RAGResponse object or use string directly
    2. Split expected_hint into tokens
    3. Check if any token appears in the result text (case-insensitive)
    4. Return "pass" or "fail"
    """
    # TODO: Extract text from response
    # if hasattr(response, 'answer'):
    #     result_text = response.answer
    # else:
    #     result_text = str(response)
    
    # TODO: Implement keyword matching logic
    # tokens = [t.strip().lower() for t in expected_hint.split() if t.strip()]
    # rlow = result_text.lower()
    # return "pass" if any(t in rlow for t in tokens) else "fail"
    
    return "fail"  # Placeholder

def detailed_eval(response: Any, expected_hint: str) -> Dict[str, Any]:
    """
    TODO: Implement detailed evaluation including confidence and other metrics
    Return a dictionary with:
    - basic_eval: result from simple_eval()
    - has_answer: boolean indicating if there's a non-empty answer
    - confidence: confidence level from RAGResponse (if available)
    - chunks_found: number of chunks used (if available)
    - response_time: response time in seconds (if available)
    - success: whether the pipeline succeeded (if available)
    """
    result = {
        "basic_eval": "fail",  # TODO: Call simple_eval()
        "has_answer": False,   # TODO: Check if response has answer
        "confidence": "unknown",  # TODO: Extract from RAGResponse
        "chunks_found": 0,     # TODO: Extract from RAGResponse
        "response_time": 0,    # TODO: Extract from RAGResponse
        "success": False       # TODO: Extract from RAGResponse
    }
    
    # TODO: Handle RAGResponse object attributes
    # if hasattr(response, 'answer'):
    #     result["has_answer"] = bool(response.answer and response.answer.strip())
    #     result["confidence"] = getattr(response, 'confidence_level', 'unknown')
    #     result["chunks_found"] = getattr(response, 'chunks_found', 0)
    #     result["response_time"] = getattr(response, 'response_time', 0)
    #     result["success"] = getattr(response, 'success', False)
    # else:
    #     result["has_answer"] = bool(str(response).strip())
    
    return result

def run():
    """
    TODO: Implement the scoring evaluation
    1. Get the RAG pipeline
    2. Loop through golden_set
    3. For each query:
       - Call RAG pipeline
       - Run detailed evaluation
       - Track pass/fail results
       - Display results with metrics
    4. Calculate and display summary statistics
    """
    print("📊 SIMPLE SCORING EVALUATION")
    print("="*80)
    
    # TODO: Get RAG pipeline and initialize counters
    # rag = get_rag_pipeline()
    # passes = 0
    # total_queries = len(golden_set)
    
    print(f"Testing queries with simple pass/fail scoring...")
    print()
    
    # TODO: Loop through queries and evaluate
    # for i, item in enumerate(golden_set, 1):
    #     q = item["query"]
    #     expected_hint = item["expected"]
    #     
    #     try:
    #         # TODO: Call RAG pipeline and evaluate
    #         # response = rag(q)
    #         # eval_result = detailed_eval(response, expected_hint)
    #         # verdict = eval_result["basic_eval"]
    #         # passes += int(verdict == "pass")
    #         
    #         # TODO: Display results
    #     except Exception as e:
    #         print(f"❌ [ERROR] Query {i}: {q}")
    #         print(f"   Error: {e}")
    
    # TODO: Calculate and display summary
    # pass_rate = (passes / total_queries) * 100
    # print("="*80)
    # print(f"📈 SUMMARY: {passes}/{total_queries} passed ({pass_rate:.1f}%)")
    
    print("TODO: Implement the scoring evaluation")

if __name__ == "__main__":
    run()
