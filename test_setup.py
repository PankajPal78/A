#!/usr/bin/env python3
"""
Test script to verify the RAG system setup
"""

import os
import sys
import tempfile
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB imported successfully")
    except ImportError as e:
        print(f"✗ ChromaDB import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✓ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"✗ Sentence Transformers import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✓ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"✗ Google Generative AI import failed: {e}")
        return False
    
    return True

def test_document_processor():
    """Test document processor initialization"""
    print("\nTesting document processor...")
    
    try:
        from document_processor import DocumentProcessor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = DocumentProcessor(chroma_db_path=temp_dir)
            print("✓ Document processor initialized successfully")
            
            # Test text chunking
            sample_text = [{'content': 'Sample text for testing', 'page_number': 1}]
            chunks = processor._chunk_text(sample_text)
            print(f"✓ Text chunking works: {len(chunks)} chunks created")
            
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False
    
    return True

def test_llm_service():
    """Test LLM service initialization"""
    print("\nTesting LLM service...")
    
    try:
        from llm_service import LLMService
        
        # Test without API key (should fail gracefully)
        try:
            service = LLMService(api_key="test_key")
            print("✓ LLM service initialized (with test key)")
        except Exception as e:
            if "API key" in str(e):
                print("✓ LLM service properly validates API key")
            else:
                raise e
                
    except Exception as e:
        print(f"✗ LLM service test failed: {e}")
        return False
    
    return True

def test_flask_app():
    """Test Flask app initialization"""
    print("\nTesting Flask app...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Flask app responds to health check")
            else:
                print(f"✗ Flask app health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'app.py',
        'models.py',
        'document_processor.py',
        'llm_service.py',
        'routes.py',
        'config.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.env.example'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def main():
    """Run all tests"""
    print("RAG System Setup Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_document_processor,
        test_llm_service,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The RAG system is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Gemini API key to .env")
        print("3. Run: docker-compose up --build")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())