#!/usr/bin/env python3
"""
Example usage script for the RAG Document Q&A System.
This script demonstrates how to use the system programmatically.
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """Test if the API is running."""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API is healthy")
            return True
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running.")
        return False

def upload_document(file_path, metadata=None):
    """Upload a document to the system."""
    print(f"Uploading document: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return None
    
    # Prepare the file and metadata
    files = {'file': open(file_path, 'rb')}
    data = {}
    if metadata:
        data['metadata'] = json.dumps(metadata)
    
    try:
        response = requests.post(f"{API_BASE}/documents/upload", files=files, data=data)
        files['file'].close()
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ Document uploaded successfully: {result['document']['original_filename']}")
            return result['document']['id']
        else:
            print(f"✗ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return None

def query_documents(question, document_ids=None, max_chunks=5):
    """Query the documents."""
    print(f"Querying: {question}")
    
    payload = {
        "question": question,
        "max_chunks": max_chunks
    }
    
    if document_ids:
        payload["document_ids"] = document_ids
    
    try:
        response = requests.post(f"{API_BASE}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✓ Query successful")
                print(f"Answer: {result['answer']}")
                print(f"Sources: {len(result['sources'])} documents")
                print(f"Response time: {result['metadata']['response_time']:.2f}s")
                return result
            else:
                print(f"✗ Query failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
                return None
        else:
            print(f"✗ Query request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Query error: {e}")
        return None

def get_documents():
    """Get list of all documents."""
    print("Getting document list...")
    
    try:
        response = requests.get(f"{API_BASE}/documents")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Found {result['count']} documents")
            for doc in result['documents']:
                print(f"  - {doc['original_filename']} (ID: {doc['id']}, Status: {doc['processing_status']})")
            return result['documents']
        else:
            print(f"✗ Failed to get documents: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error getting documents: {e}")
        return []

def create_sample_document():
    """Create a sample document for testing."""
    sample_text = """
    Artificial Intelligence and Machine Learning
    
    Artificial Intelligence (AI) is a branch of computer science that aims to create 
    intelligent machines that can perform tasks that typically require human intelligence. 
    These tasks include learning, reasoning, problem-solving, perception, and language understanding.
    
    Machine Learning (ML) is a subset of AI that focuses on the development of algorithms 
    and statistical models that enable computer systems to improve their performance on a 
    specific task through experience, without being explicitly programmed.
    
    There are three main types of machine learning:
    1. Supervised Learning: Learning with labeled training data
    2. Unsupervised Learning: Finding patterns in data without labels
    3. Reinforcement Learning: Learning through interaction with an environment
    
    Deep Learning is a subset of machine learning that uses artificial neural networks 
    with multiple layers to model and understand complex patterns in data. It has been 
    particularly successful in areas such as image recognition, natural language processing, 
    and speech recognition.
    
    Applications of AI and ML include:
    - Autonomous vehicles
    - Medical diagnosis
    - Financial trading
    - Recommendation systems
    - Natural language processing
    - Computer vision
    - Robotics
    
    The future of AI holds great promise for solving complex problems and improving 
    human life, but also raises important questions about ethics, privacy, and the 
    impact on employment and society.
    """
    
    sample_file = "sample_ai_document.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"✓ Created sample document: {sample_file}")
    return sample_file

def main():
    """Main example function."""
    print("RAG Document Q&A System - Example Usage")
    print("=" * 50)
    
    # Test API health
    if not test_health():
        print("\nPlease start the API server first:")
        print("python app.py")
        return
    
    print("\n" + "=" * 50)
    
    # Create and upload a sample document
    sample_file = create_sample_document()
    document_id = upload_document(sample_file, {"title": "AI and ML Overview"})
    
    if not document_id:
        print("Failed to upload document. Exiting.")
        return
    
    # Wait a moment for processing
    print("Waiting for document processing...")
    time.sleep(2)
    
    # Get document list
    print("\n" + "=" * 50)
    documents = get_documents()
    
    # Query the documents
    print("\n" + "=" * 50)
    queries = [
        "What is artificial intelligence?",
        "What are the types of machine learning?",
        "What are some applications of AI?",
        "What is deep learning?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = query_documents(query, [document_id])
        if result:
            print(f"Answer: {result['answer'][:200]}...")
        print("-" * 30)
    
    # Clean up
    print("\nCleaning up...")
    if os.path.exists(sample_file):
        os.remove(sample_file)
        print(f"✓ Removed sample file: {sample_file}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()