import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from services.vector_service import VectorService
from models.document import DocumentChunk

class TestVectorService:
    
    def setup_method(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.vector_service = VectorService(persist_directory=self.temp_dir)
    
    def teardown_method(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test that VectorService initializes correctly"""
        assert self.vector_service.client is not None
        assert self.vector_service.collection is not None
        assert self.vector_service.embedding_model is not None
    
    def test_add_document_chunks(self):
        """Test adding document chunks to vector database"""
        # Create mock chunks
        chunks = [
            DocumentChunk(
                id=1,
                document_id=1,
                chunk_index=0,
                content="This is the first chunk of text.",
                page_number=1,
                chunk_size=30
            ),
            DocumentChunk(
                id=2,
                document_id=1,
                chunk_index=1,
                content="This is the second chunk of text.",
                page_number=1,
                chunk_size=31
            )
        ]
        
        # Mock database session
        with patch('services.vector_service.db') as mock_db:
            mock_db.session.commit.return_value = None
            
            result = self.vector_service.add_document_chunks(1, chunks)
            
            assert result is True
            mock_db.session.commit.assert_called_once()
    
    def test_search_similar_chunks(self):
        """Test searching for similar chunks"""
        # First add some test chunks
        chunks = [
            DocumentChunk(
                id=1,
                document_id=1,
                chunk_index=0,
                content="Machine learning is a subset of artificial intelligence.",
                page_number=1,
                chunk_size=50
            ),
            DocumentChunk(
                id=2,
                document_id=1,
                chunk_index=1,
                content="Deep learning uses neural networks with multiple layers.",
                page_number=2,
                chunk_size=55
            )
        ]
        
        with patch('services.vector_service.db') as mock_db:
            mock_db.session.commit.return_value = None
            self.vector_service.add_document_chunks(1, chunks)
        
        # Search for similar chunks
        results = self.vector_service.search_similar_chunks(
            query="What is machine learning?",
            n_results=2
        )
        
        assert isinstance(results, list)
        # Results should contain the chunks we added
        assert len(results) <= 2
    
    def test_search_with_document_filter(self):
        """Test searching with document ID filter"""
        results = self.vector_service.search_similar_chunks(
            query="test query",
            n_results=5,
            document_ids=[1, 2]
        )
        
        assert isinstance(results, list)
        # All results should be from the specified documents
        for result in results:
            if 'metadata' in result and 'document_id' in result['metadata']:
                assert result['metadata']['document_id'] in [1, 2]
    
    def test_get_collection_stats(self):
        """Test getting collection statistics"""
        stats = self.vector_service.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert 'total_chunks' in stats
        assert 'collection_name' in stats
        assert isinstance(stats['total_chunks'], int)
    
    def test_delete_document_chunks(self):
        """Test deleting chunks for a document"""
        # Mock the collection.get method
        with patch.object(self.vector_service.collection, 'get') as mock_get:
            mock_get.return_value = {'ids': ['doc_1_chunk_1', 'doc_1_chunk_2']}
            
            with patch.object(self.vector_service.collection, 'delete') as mock_delete:
                result = self.vector_service.delete_document_chunks(1)
                
                assert result is True
                mock_get.assert_called_once_with(where={"document_id": 1})
                mock_delete.assert_called_once_with(ids=['doc_1_chunk_1', 'doc_1_chunk_2'])
    
    def test_embedding_generation(self):
        """Test that embeddings are generated correctly"""
        text = "This is a test sentence for embedding generation."
        embedding = self.vector_service.embedding_model.encode([text])
        
        assert embedding.shape[0] == 1  # One sentence
        assert embedding.shape[1] > 0  # Has embedding dimensions
        assert isinstance(embedding, type(self.vector_service.embedding_model.encode([text])))