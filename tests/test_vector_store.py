import pytest
import tempfile
import os
from services.vector_store import VectorStore

class TestVectorStore:
    """Test cases for VectorStore"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(persist_directory=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_documents(self):
        """Test adding documents to vector store"""
        document_id = "test_doc_1"
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'This is the first chunk of text.',
                'metadata': {'chunk_index': 0}
            },
            {
                'id': 'chunk_2', 
                'text': 'This is the second chunk of text.',
                'metadata': {'chunk_index': 1}
            }
        ]
        
        self.vector_store.add_documents(document_id, chunks)
        
        # Verify documents were added
        stats = self.vector_store.get_stats()
        assert stats['total_chunks'] == 2
    
    def test_search_documents(self):
        """Test searching for documents"""
        document_id = "test_doc_2"
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'Machine learning is a subset of artificial intelligence.',
                'metadata': {'chunk_index': 0}
            },
            {
                'id': 'chunk_2',
                'text': 'Deep learning uses neural networks with multiple layers.',
                'metadata': {'chunk_index': 1}
            }
        ]
        
        self.vector_store.add_documents(document_id, chunks)
        
        # Search for relevant content
        results = self.vector_store.search("What is machine learning?", top_k=2)
        
        assert len(results) > 0
        assert all('text' in result for result in results)
        assert all('metadata' in result for result in results)
    
    def test_delete_document(self):
        """Test deleting documents"""
        document_id = "test_doc_3"
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'This document will be deleted.',
                'metadata': {'chunk_index': 0}
            }
        ]
        
        self.vector_store.add_documents(document_id, chunks)
        
        # Verify document was added
        stats_before = self.vector_store.get_stats()
        assert stats_before['total_chunks'] == 1
        
        # Delete document
        self.vector_store.delete_document(document_id)
        
        # Verify document was deleted
        stats_after = self.vector_store.get_stats()
        assert stats_after['total_chunks'] == 0
    
    def test_empty_search(self):
        """Test search with no documents"""
        results = self.vector_store.search("test query", top_k=5)
        assert results == []
    
    def test_get_stats(self):
        """Test getting vector store statistics"""
        stats = self.vector_store.get_stats()
        assert 'total_chunks' in stats
        assert 'collection_name' in stats
        assert isinstance(stats['total_chunks'], int)