#!/usr/bin/env python3
"""
Demo script for the RAG Document Q&A System
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if the API is running"""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
            return True
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure it's running on localhost:5000")
        return False

def upload_document(file_path):
    """Upload a document"""
    print(f"Uploading document: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Document uploaded successfully: {data['document']['original_filename']}")
            return data['document']['id']
        else:
            print(f"✗ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return None

def ask_question(question, document_id=None):
    """Ask a question using the RAG system"""
    print(f"Question: {question}")
    
    payload = {
        "question": question,
        "max_results": 5
    }
    
    if document_id:
        payload["document_ids"] = [document_id]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query/ask",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Answer: {data['answer']}")
            print(f"Sources used: {data['context_used']} chunks")
            if data.get('sources'):
                print("Source documents:")
                for source in data['sources']:
                    print(f"  - Document ID: {source['document_id']}, Page: {source['page_number']}")
            return True
        else:
            print(f"✗ Query failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Query error: {e}")
        return False

def list_documents():
    """List uploaded documents"""
    print("Listing documents...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents/")
        if response.status_code == 200:
            data = response.json()
            print(f"Total documents: {data['total']}")
            for doc in data['documents']:
                print(f"  - ID: {doc['id']}, Name: {doc['original_filename']}, Status: {doc['processing_status']}")
            return data['documents']
        else:
            print(f"✗ Failed to list documents: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error listing documents: {e}")
        return []

def main():
    """Run the demo"""
    print("RAG Document Q&A System Demo")
    print("=" * 50)
    
    # Test API health
    if not test_health():
        print("\nPlease start the API first:")
        print("1. Run: ./start.sh")
        print("2. Or run: docker-compose up --build")
        return
    
    print()
    
    # Upload sample document
    sample_file = "sample_document.txt"
    if os.path.exists(sample_file):
        document_id = upload_document(sample_file)
        if not document_id:
            print("Failed to upload document. Exiting.")
            return
        
        # Wait for processing
        print("Waiting for document processing...")
        time.sleep(5)
        
        print()
        
        # Ask questions
        questions = [
            "What is the main topic of this document?",
            "What are the key applications of AI in healthcare?",
            "What challenges does AI face in healthcare?",
            "What is the future outlook for AI in healthcare?",
            "How does AI help with drug discovery?"
        ]
        
        for question in questions:
            ask_question(question, document_id)
            print()
        
        # List documents
        list_documents()
        
    else:
        print(f"Sample document {sample_file} not found. Creating it...")
        # The sample document should already exist from our setup
        print("Please run the demo again after the sample document is created.")
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main()