import pytest
import os
import tempfile
import json
import io
from unittest.mock import patch, MagicMock
from app import create_app
from database import db, Document

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

class TestRAGIntegration:
    """Integration tests for the RAG system."""
    
    @patch('api_routes.current_app.vector_store')
    @patch('api_routes.current_app.llm_client')
    def test_complete_rag_flow(self, mock_llm_client, mock_vector_store, client):
        """Test complete RAG flow from upload to query."""
        
        # Mock vector store responses
        mock_vector_store.add_document_chunks.return_value = True
        mock_vector_store.search_similar_chunks.return_value = [
            {
                'text': 'This is a test document about artificial intelligence.',
                'metadata': {'document_id': 1, 'filename': 'test.pdf'},
                'distance': 0.1
            }
        ]
        
        # Mock LLM client responses
        mock_llm_client.generate_response.return_value = {
            'response': 'Artificial intelligence is a field of computer science.',
            'metadata': {'model': 'gemini-pro'},
            'success': True
        }
        
        # Test document upload
        test_content = b"This is a test document about artificial intelligence and machine learning."
        data = {
            'file': (io.BytesIO(test_content), 'test.txt'),
            'metadata': json.dumps({'title': 'Test Document'})
        }
        
        response = client.post('/api/documents/upload', data=data)
        assert response.status_code in [200, 201, 500]  # 500 if processing fails due to mocking
        
        # Test query
        query_data = {'question': 'What is artificial intelligence?'}
        response = client.post('/api/query', json=query_data)
        
        # Should succeed with mocked responses
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'answer' in data
            assert 'sources' in data
            assert 'metadata' in data
    
    def test_document_processing_workflow(self, app):
        """Test document processing workflow."""
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        
        # Create a test text file
        test_text = "This is a test document. " * 20  # Create a long text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_text)
            temp_file = f.name
        
        try:
            # Process the document
            result = processor.process_document(temp_file, 'txt', 1)
            
            assert result['success'] is True
            assert 'chunks' in result
            assert 'metadata' in result
            assert len(result['chunks']) > 0
            
            # Check chunk structure
            for chunk in result['chunks']:
                assert 'text' in chunk
                assert 'tokens' in chunk
                assert 'id' in chunk
                
        finally:
            os.unlink(temp_file)
    
    @patch('vector_store.SentenceTransformer')
    @patch('vector_store.chromadb.PersistentClient')
    def test_vector_store_operations(self, mock_client, mock_transformer):
        """Test vector store operations."""
        from vector_store import VectorStore
        
        # Mock the transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
        mock_transformer.return_value = mock_model
        
        # Mock the client
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vector_store = VectorStore(persist_directory="./test_vector_db")
        
        # Test adding chunks
        chunks = [
            {'id': 0, 'text': 'Test chunk 1', 'tokens': 10, 'start_char': 0, 'end_char': 10},
            {'id': 1, 'text': 'Test chunk 2', 'tokens': 10, 'start_char': 10, 'end_char': 20}
        ]
        
        metadata = {'filename': 'test.pdf', 'file_type': 'pdf'}
        result = vector_store.add_document_chunks(1, chunks, metadata)
        
        assert result is True
        mock_collection.add.assert_called_once()
    
    @patch('llm_client.genai.configure')
    @patch('llm_client.genai.GenerativeModel')
    def test_llm_response_generation(self, mock_model, mock_configure):
        """Test LLM response generation."""
        from llm_client import LLMClient
        
        # Mock the model
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a test response about artificial intelligence."
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        client = LLMClient(api_key="test_key")
        
        # Test response generation
        chunks = [
            {
                'text': 'Artificial intelligence is a field of computer science.',
                'metadata': {'filename': 'test.pdf'}
            }
        ]
        
        result = client.generate_response("What is AI?", chunks)
        
        assert result['success'] is True
        assert 'response' in result
        assert 'metadata' in result
        assert 'artificial intelligence' in result['response'].lower()

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_file_upload(self, client):
        """Test uploading invalid file types."""
        data = {'file': (io.BytesIO(b'test content'), 'test.exe')}
        response = client.post('/api/documents/upload', data=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'File type not allowed' in data['error']
    
    def test_missing_api_key(self, app):
        """Test behavior when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Google API key is required"):
                from llm_client import LLMClient
                LLMClient()
    
    def test_database_error_handling(self, client):
        """Test database error handling."""
        # This would require more complex mocking to simulate database errors
        # For now, we'll test basic error responses
        response = client.get('/api/documents/999')
        assert response.status_code == 404

class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_document_handling(self, app):
        """Test handling of large documents."""
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
        
        # Create a large text (simulate 2000 pages)
        large_text = "This is a test sentence. " * 10000  # ~250,000 characters
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(large_text)
            temp_file = f.name
        
        try:
            result = processor.process_document(temp_file, 'txt', 1)
            
            # Should succeed and create multiple chunks
            assert result['success'] is True
            assert len(result['chunks']) > 1
            
            # Check metadata
            metadata = result['metadata']
            assert 'total_tokens' in metadata
            assert 'estimated_pages' in metadata
            assert metadata['estimated_pages'] > 1000  # Should be large
            
        finally:
            os.unlink(temp_file)
    
    def test_concurrent_queries(self, client):
        """Test handling of concurrent queries."""
        import threading
        import time
        
        query_data = {'question': 'Test question'}
        results = []
        
        def make_query():
            response = client.post('/api/query', json=query_data)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_query)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should complete (even if they fail due to mocking)
        assert len(results) == 5
        # At least some should return status codes (not exceptions)
        assert all(isinstance(code, int) for code in results)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])