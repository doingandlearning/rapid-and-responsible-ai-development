#!/usr/bin/env python3
"""
Test script to verify direct OpenAI API calls work correctly.
This demonstrates the direct API approach used in the RAG pipeline.
"""

import requests
import json
import os

def test_openai_api_direct():
    """Test direct OpenAI API call without the library."""
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your-api-key-here":
        print("❌ OPENAI_API_KEY not set or using placeholder value")
        print("   Set your API key: export OPENAI_API_KEY='your-actual-key'")
        return False
    
    print("🧪 Testing direct OpenAI API call...")
    
    # Test payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful assistant for Edinburgh University IT Services."
            },
            {
                "role": "user", 
                "content": "What is the university's password policy?"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make the API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Extract information
        answer = data['choices'][0]['message']['content']
        usage = data.get('usage', {})
        tokens_used = usage.get('total_tokens', 0)
        
        print("✅ Direct API call successful!")
        print(f"   Response: {answer[:100]}...")
        print(f"   Tokens used: {tokens_used}")
        print(f"   Model: {data['model']}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("   Authentication failed - check your API key")
        elif e.response.status_code == 429:
            print("   Rate limit exceeded - try again later")
        else:
            print(f"   Status code: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_api_key_validity():
    """Test if API key is valid by checking models endpoint."""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your-api-key-here":
        print("❌ OPENAI_API_KEY not set")
        return False
    
    print("🔑 Testing API key validity...")
    
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            print("✅ API key is valid!")
            print(f"   Available models: {len(models.get('data', []))}")
            
            # Check for gpt-3.5-turbo
            model_names = [model['id'] for model in models.get('data', [])]
            if 'gpt-3.5-turbo' in model_names:
                print("   ✅ gpt-3.5-turbo is available")
            else:
                print("   ⚠️  gpt-3.5-turbo not found in available models")
            
            return True
        else:
            print(f"❌ API key invalid: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking API key: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Direct OpenAI API Integration")
    print("=" * 50)
    
    # Test 1: API key validity
    if not test_api_key_validity():
        print("\n❌ API key test failed - cannot proceed")
        return 1
    
    print()
    
    # Test 2: Direct API call
    if not test_openai_api_direct():
        print("\n❌ Direct API call test failed")
        return 1
    
    print("\n✅ All tests passed!")
    print("   Direct API integration is working correctly")
    print("   Ready to use with the RAG pipeline")
    
    return 0

if __name__ == "__main__":
    exit(main())
