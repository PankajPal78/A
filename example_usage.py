#!/usr/bin/env python3
"""
Example usage script for RAG Document Q&A System API
Demonstrates all API endpoints with practical examples
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_response(response):
    """Pretty print API response"""
    try:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(json.dumps(data, indent=2))
    except:
        print(f"Status: {response.status_code}")
        print(response.text)

def health_check():
    """Check API health"""
    print_section("1. Health Check")
    response = requests.get(f"{API_BASE}/health")
    print_response(response)
    return response.status_code == 200

def upload_document(file_path):
    """Upload a document"""
    print_section(f"2. Upload Document: {file_path}")
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        print("Please provide a valid PDF or TXT file path")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/documents", files=files)
    
    print_response(response)
    
    if response.status_code == 201:
        doc_id = response.json().get('id')
        print(f"\n✓ Document uploaded successfully with ID: {doc_id}")
        return doc_id
    return None

def list_documents():
    """List all documents"""
    print_section("3. List All Documents")
    response = requests.get(f"{API_BASE}/documents")
    print_response(response)
    
    if response.status_code == 200:
        count = response.json().get('count', 0)
        print(f"\n✓ Total documents: {count}")

def get_document(doc_id):
    """Get specific document details"""
    print_section(f"4. Get Document Details (ID: {doc_id})")
    response = requests.get(f"{API_BASE}/documents/{doc_id}")
    print_response(response)

def query_all_documents(question):
    """Query all documents"""
    print_section("5. Query All Documents")
    
    data = {
        "question": question,
        "top_k": 5
    }
    
    print(f"Question: {question}")
    response = requests.post(
        f"{API_BASE}/query",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response)
    
    if response.status_code == 200:
        answer = response.json().get('answer', 'No answer')
        print(f"\n✓ Answer: {answer[:200]}...")

def query_specific_document(doc_id, question):
    """Query a specific document"""
    print_section(f"6. Query Specific Document (ID: {doc_id})")
    
    data = {
        "question": question,
        "document_id": doc_id,
        "top_k": 3
    }
    
    print(f"Question: {question}")
    response = requests.post(
        f"{API_BASE}/query",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response)

def get_stats():
    """Get system statistics"""
    print_section("7. System Statistics")
    response = requests.get(f"{API_BASE}/stats")
    print_response(response)

def delete_document(doc_id):
    """Delete a document"""
    print_section(f"8. Delete Document (ID: {doc_id})")
    
    confirm = input(f"Are you sure you want to delete document {doc_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled")
        return
    
    response = requests.delete(f"{API_BASE}/documents/{doc_id}")
    print_response(response)
    
    if response.status_code == 200:
        print(f"\n✓ Document {doc_id} deleted successfully")

def main():
    """Main example workflow"""
    print("\n" + "🚀 RAG Document Q&A System - API Example Usage" + "\n")
    
    # 1. Health Check
    if not health_check():
        print("\n❌ API is not healthy. Please start the application first:")
        print("   docker-compose up")
        return
    
    time.sleep(1)
    
    # 2. Get current stats
    get_stats()
    time.sleep(1)
    
    # 3. List existing documents
    list_documents()
    time.sleep(1)
    
    # 4. Upload a document (optional - user provides path)
    print("\n" + "-"*60)
    print("To upload a document, please provide a file path")
    print("Example: /path/to/your/document.pdf")
    print("Press Enter to skip document upload")
    print("-"*60)
    
    file_path = input("Enter file path (or press Enter to skip): ").strip()
    
    doc_id = None
    if file_path:
        doc_id = upload_document(file_path)
        if doc_id:
            time.sleep(2)  # Wait for processing
            get_document(doc_id)
            time.sleep(1)
    
    # 5. Query examples
    if doc_id:
        # Query the specific document
        query_specific_document(
            doc_id,
            "What are the main topics discussed in this document?"
        )
        time.sleep(1)
    
    # Query all documents
    query_all_documents(
        "Can you summarize the key information from the documents?"
    )
    time.sleep(1)
    
    # 6. Final stats
    get_stats()
    
    # 7. Optional deletion
    if doc_id:
        print("\n" + "-"*60)
        delete_document(doc_id)
    
    print("\n" + "="*60)
    print(" ✅ Example Usage Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Try different questions")
    print("2. Upload more documents")
    print("3. Check the Postman collection for more examples")
    print("4. Read the API documentation in README.md")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Example interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n\n❌ Error: Could not connect to API")
        print("Please make sure the application is running:")
        print("   docker-compose up")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")