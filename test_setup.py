#!/usr/bin/env python3
"""
Test script to verify the RAG system setup and configuration.
Run this script to check if all components are working correctly.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
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
    
    try:
        import PyPDF2
        print("✓ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError as e:
        print(f"✗ python-docx import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables and configuration."""
    print("\nTesting environment...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✓ .env file found")
    else:
        print("⚠ .env file not found, using .env.example")
        if os.path.exists('.env.example'):
            print("✓ .env.example file found")
        else:
            print("✗ No environment configuration found")
            return False
    
    # Check Google API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and api_key != 'your_google_api_key_here':
        print("✓ Google API key configured")
    else:
        print("⚠ Google API key not configured or using placeholder")
    
    return True

def test_directories():
    """Test if required directories exist or can be created."""
    print("\nTesting directories...")
    
    directories = ['data', 'uploads', 'data/vector_db']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Directory {directory} ready")
        except Exception as e:
            print(f"✗ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from database import db, init_db
        from app import create_app
        
        app = create_app()
        with app.app_context():
            init_db()
            print("✓ Database initialized successfully")
        
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_document_processor():
    """Test document processor functionality."""
    print("\nTesting document processor...")
    
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test chunking
        test_text = "This is a test document. " * 100
        chunks = processor.chunk_text(test_text)
        
        if chunks and len(chunks) > 0:
            print("✓ Document processor working correctly")
            return True
        else:
            print("✗ Document processor failed to create chunks")
            return False
            
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization."""
    print("\nTesting vector store...")
    
    try:
        from vector_store import VectorStore
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(persist_directory=temp_dir)
            
            # Test embedding generation
            test_texts = ["This is a test document.", "Another test document."]
            embeddings = vector_store.generate_embeddings(test_texts)
            
            if embeddings and len(embeddings) == 2:
                print("✓ Vector store working correctly")
                return True
            else:
                print("✗ Vector store failed to generate embeddings")
                return False
                
    except Exception as e:
        print(f"✗ Vector store test failed: {e}")
        return False

def test_llm_client():
    """Test LLM client (without making actual API calls)."""
    print("\nTesting LLM client...")
    
    try:
        from llm_client import LLMClient
        
        # Test with a dummy API key
        test_key = "test_key_12345"
        client = LLMClient(api_key=test_key)
        
        print("✓ LLM client initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ LLM client test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application creation."""
    print("\nTesting Flask application...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Test if app has required attributes
        if hasattr(app, 'document_processor') and hasattr(app, 'vector_store') and hasattr(app, 'rag_pipeline'):
            print("✓ Flask application created successfully")
            return True
        else:
            print("✗ Flask application missing required components")
            return False
            
    except Exception as e:
        print(f"✗ Flask application test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("RAG System Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_directories,
        test_database,
        test_document_processor,
        test_vector_store,
        test_llm_client,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The RAG system is ready to use.")
        print("\nNext steps:")
        print("1. Set your Google API key in the .env file")
        print("2. Run: python app.py")
        print("3. Test the API at: http://localhost:5000/health")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check your Python version (3.9+ required)")
        print("3. Verify all environment variables are set correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)