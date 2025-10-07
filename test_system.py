#!/usr/bin/env python3
"""
Test script for the RAG Document Q&A System
This script tests the basic functionality of the system
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_DOCUMENT_PATH = "test_document.txt"

def create_test_document():
    """Create a test document for upload"""
    test_content = """
    Machine Learning and Artificial Intelligence
    
    Machine learning is a subset of artificial intelligence (AI) that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience.
    
    There are three main types of machine learning:
    1. Supervised Learning: Learning with labeled training data
    2. Unsupervised Learning: Finding patterns in data without labels
    3. Reinforcement Learning: Learning through interaction with an environment
    
    Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data.
    
    Applications of machine learning include:
    - Image recognition and computer vision
    - Natural language processing
    - Recommendation systems
    - Autonomous vehicles
    - Medical diagnosis
    - Financial fraud detection
    
    The field of machine learning continues to evolve rapidly, with new techniques and applications being developed regularly.
    """
    
    with open(TEST_DOCUMENT_PATH, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"Created test document: {TEST_DOCUMENT_PATH}")

def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_upload_document():
    """Test document upload"""
    print("\n=== Testing Document Upload ===")
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents", files=files)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Document uploaded successfully: {data['document_id']}")
            return data['document_id']
        else:
            print(f"❌ Document upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Document upload error: {str(e)}")
        return None

def test_list_documents():
    """Test listing documents"""
    print("\n=== Testing List Documents ===")
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents")
            for doc in documents:
                print(f"  - {doc['original_filename']} ({doc['status']})")
            return documents
        else:
            print(f"❌ List documents failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ List documents error: {str(e)}")
        return []

def test_query_documents(query, document_id=None):
    """Test querying documents"""
    print(f"\n=== Testing Query: '{query}' ===")
    try:
        payload = {"query": query, "top_k": 3}
        response = requests.post(f"{BASE_URL}/api/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query successful")
            print(f"Response: {data['response'][:200]}...")
            print(f"Sources: {len(data['sources'])} chunks used")
            return data
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Query error: {str(e)}")
        return None

def test_system_stats():
    """Test system statistics"""
    print("\n=== Testing System Statistics ===")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System stats retrieved:")
            print(f"  - Total documents: {stats['total_documents']}")
            print(f"  - Completed documents: {stats['completed_documents']}")
            print(f"  - Total chunks: {stats['total_chunks']}")
            return stats
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        return None

def cleanup():
    """Clean up test files"""
    if os.path.exists(TEST_DOCUMENT_PATH):
        os.remove(TEST_DOCUMENT_PATH)
        print(f"\nCleaned up test file: {TEST_DOCUMENT_PATH}")

def main():
    """Run all tests"""
    print("🚀 Starting RAG Document Q&A System Tests")
    print("=" * 50)
    
    # Create test document
    create_test_document()
    
    # Wait for system to be ready
    print("\n⏳ Waiting for system to be ready...")
    time.sleep(5)
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Upload document
    document_id = test_upload_document()
    if document_id:
        tests_passed += 1
        
        # Wait for processing
        print("\n⏳ Waiting for document processing...")
        time.sleep(10)
    
    # Test 3: List documents
    documents = test_list_documents()
    if documents:
        tests_passed += 1
    
    # Test 4: Query documents
    test_queries = [
        "What is machine learning?",
        "What are the types of machine learning?",
        "What are some applications of machine learning?"
    ]
    
    query_results = []
    for query in test_queries:
        result = test_query_documents(query)
        if result:
            query_results.append(result)
    
    if query_results:
        tests_passed += 1
    
    # Test 5: System stats
    if test_system_stats():
        tests_passed += 1
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🏁 Test Summary: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)