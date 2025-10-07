import pytest
import os
import tempfile
from app.vector_store import VectorStore
from app.config import Config

def test_vector_store_initialization():
    """Test vector store initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        Config.VECTOR_DB_PATH = tmpdir
        vector_store = VectorStore()
        assert vector_store.collection is not None
        assert vector_store.embedding_model is not None

def test_add_and_search_documents():
    """Test adding and searching documents"""
    with tempfile.TemporaryDirectory() as tmpdir:
        Config.VECTOR_DB_PATH = tmpdir
        vector_store = VectorStore()
        
        # Add documents
        chunks = [
            {'text': 'Python is a programming language', 'chunk_index': 0, 'metadata': {}},
            {'text': 'Machine learning is a subset of AI', 'chunk_index': 1, 'metadata': {}}
        ]
        vector_store.add_documents(chunks, document_id=1)
        
        # Search
        results = vector_store.search('Python programming', top_k=1)
        assert len(results) > 0
        assert 'text' in results[0]

def test_get_collection_stats():
    """Test getting collection statistics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        Config.VECTOR_DB_PATH = tmpdir
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        
        assert 'total_chunks' in stats
        assert 'collection_name' in stats