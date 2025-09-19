#!/usr/bin/env python3
"""
Test script to verify implementations of Section 8 lab exercises.
Run this to check if your implementations are working correctly.
"""

import sys
import os
import subprocess
import time
import requests
from typing import List, Dict, Any

def test_imports():
    """Test that all modules can be imported without errors."""
    print("🔍 Testing imports...")
    
    modules = [
        "01_golden_queries",
        "02_simple_scoring", 
        "03_healthcheck_app",
        "04_explain_query",
        "05_ranked_query"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_golden_queries():
    """Test golden queries implementation."""
    print("\n🧪 Testing golden queries...")
    
    try:
        from golden_queries import run, golden_set
        
        # Check if golden_set is defined and not empty
        if not golden_set or len(golden_set) == 0:
            print("  ⚠️  golden_set is empty - add some test queries")
            return False
        
        # Check if queries have expected structure
        for item in golden_set:
            if "query" not in item or "expected" not in item:
                print("  ❌ golden_set items must have 'query' and 'expected' keys")
                return False
        
        print(f"  ✅ Found {len(golden_set)} test queries")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_simple_scoring():
    """Test simple scoring implementation."""
    print("\n📊 Testing simple scoring...")
    
    try:
        from simple_scoring import simple_eval, detailed_eval, golden_set
        
        # Test simple_eval function
        test_response = "The library is open from 9am to 5pm"
        test_expected = "library hours"
        
        result = simple_eval(test_response, test_expected)
        if result not in ["pass", "fail"]:
            print("  ❌ simple_eval should return 'pass' or 'fail'")
            return False
        
        # Test detailed_eval function
        eval_result = detailed_eval(test_response, test_expected)
        required_keys = ["basic_eval", "has_answer", "confidence", "chunks_found", "response_time", "success"]
        
        for key in required_keys:
            if key not in eval_result:
                print(f"  ❌ detailed_eval missing key: {key}")
                return False
        
        print("  ✅ Scoring functions implemented")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_healthcheck_app():
    """Test health check app implementation."""
    print("\n🏥 Testing health check app...")
    
    try:
        from healthcheck_app import app
        
        # Test that Flask app is created
        if not app:
            print("  ❌ Flask app not created")
            return False
        
        # Test that routes are defined
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ["/", "/health", "/health/detailed"]
        
        for route in expected_routes:
            if route not in routes:
                print(f"  ❌ Missing route: {route}")
                return False
        
        print("  ✅ Health check app structure looks good")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_explain_query():
    """Test explain query implementation."""
    print("\n🔍 Testing explain query...")
    
    try:
        from explain_query import main, compare_index_types
        
        # Test that functions are callable
        if not callable(main):
            print("  ❌ main function not callable")
            return False
        
        if not callable(compare_index_types):
            print("  ❌ compare_index_types function not callable")
            return False
        
        print("  ✅ Explain query functions implemented")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ranked_query():
    """Test ranked query implementation."""
    print("\n🏆 Testing ranked query...")
    
    try:
        from ranked_query import run_ranked_query, run_simple_ranked, demonstrate_ranking_strategies, main
        
        # Test that functions are callable
        functions = [run_ranked_query, run_simple_ranked, demonstrate_ranking_strategies, main]
        
        for func in functions:
            if not callable(func):
                print(f"  ❌ Function {func.__name__} not callable")
                return False
        
        print("  ✅ Ranked query functions implemented")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_common_module():
    """Test common module functionality."""
    print("\n🔧 Testing common module...")
    
    try:
        from common import get_rag_pipeline, embed_text, get_conn, check_database_health
        
        # Test that functions are callable
        functions = [get_rag_pipeline, embed_text, get_conn, check_database_health]
        
        for func in functions:
            if not callable(func):
                print(f"  ❌ Function {func.__name__} not callable")
                return False
        
        print("  ✅ Common module functions available")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def run_integration_test():
    """Run a simple integration test."""
    print("\n🚀 Running integration test...")
    
    try:
        # Test that we can import and call basic functions
        from common import get_rag_pipeline
        
        # This might fail if RAG pipeline is not available, which is OK
        try:
            rag = get_rag_pipeline()
            print("  ✅ RAG pipeline accessible")
        except Exception as e:
            print(f"  ⚠️  RAG pipeline not accessible: {e}")
            print("  💡 This is OK if you haven't completed Section 6 yet")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 SECTION 8 LAB IMPLEMENTATION TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Common Module", test_common_module),
        ("Golden Queries", test_golden_queries),
        ("Simple Scoring", test_simple_scoring),
        ("Health Check App", test_healthcheck_app),
        ("Explain Query", test_explain_query),
        ("Ranked Query", test_ranked_query),
        ("Integration", run_integration_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your implementations look good.")
        print("💡 You can now run the individual exercises:")
        print("   python 01_golden_queries.py")
        print("   python 02_simple_scoring.py")
        print("   python 03_healthcheck_app.py")
        print("   python 04_explain_query.py \"test query\"")
        print("   python 05_ranked_query.py \"test query\"")
    else:
        print("⚠️  Some tests failed. Check the errors above and fix your implementations.")
        print("💡 Remember to implement the TODO items in each file.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
