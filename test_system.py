#!/usr/bin/env python3
"""
Simple test script to verify the RAG system is working correctly
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_DOCUMENT_PATH = "sample_document.pdf"  # You can create this for testing

def test_health():
    """Test basic health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_llm_connection():
    """Test LLM service connection"""
    print("🔍 Testing LLM connection...")
    try:
        response = requests.post(f"{BASE_URL}/api/query/test-llm")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'connected':
                print("✅ LLM connection successful")
                return True
            else:
                print(f"❌ LLM connection failed: {data.get('message')}")
                return False
        else:
            print(f"❌ LLM test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM test error: {e}")
        return False

def test_document_upload():
    """Test document upload (if test document exists)"""
    print("🔍 Testing document upload...")
    
    if not os.path.exists(TEST_DOCUMENT_PATH):
        print(f"⚠️  Test document {TEST_DOCUMENT_PATH} not found, skipping upload test")
        return True
    
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
        
        if response.status_code in [200, 201, 202]:
            print("✅ Document upload successful")
            return True
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return False

def test_query_system():
    """Test querying the system"""
    print("🔍 Testing query system...")
    
    test_queries = [
        "What is machine learning?",
        "Can you explain the main concepts?",
        "What are the key points discussed?"
    ]
    
    for query in test_queries:
        try:
            payload = {"query": query}
            response = requests.post(
                f"{BASE_URL}/api/query/ask",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and data['response']:
                    print(f"✅ Query successful: '{query}'")
                    print(f"   Response: {data['response'][:100]}...")
                else:
                    print(f"⚠️  Query returned empty response: '{query}'")
            else:
                print(f"❌ Query failed: {response.status_code} - {query}")
                return False
        except Exception as e:
            print(f"❌ Query error: {e}")
            return False
    
    return True

def test_system_stats():
    """Test system statistics"""
    print("🔍 Testing system statistics...")
    
    try:
        # Test document stats
        response = requests.get(f"{BASE_URL}/api/documents/stats")
        if response.status_code == 200:
            print("✅ Document stats retrieved")
        else:
            print(f"❌ Document stats failed: {response.status_code}")
            return False
        
        # Test query stats
        response = requests.get(f"{BASE_URL}/api/query/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query stats retrieved: {data}")
        else:
            print(f"❌ Query stats failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Stats test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG System Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("LLM Connection", test_llm_connection),
        ("Document Upload", test_document_upload),
        ("Query System", test_query_system),
        ("System Statistics", test_system_stats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The RAG system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the system configuration.")
        return 1

if __name__ == "__main__":
    exit(main())