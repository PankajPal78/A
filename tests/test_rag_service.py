import pytest
from unittest.mock import patch, MagicMock
from services.rag_service import RAGService
from services.vector_service import VectorService
from services.llm_service import LLMService
from models.document import Document

class TestRAGService:
    
    def setup_method(self):
        self.mock_vector_service = MagicMock(spec=VectorService)
        self.mock_llm_service = MagicMock(spec=LLMService)
        self.rag_service = RAGService(self.mock_vector_service, self.mock_llm_service)
    
    def test_process_query_success(self):
        """Test successful query processing"""
        # Mock vector search results
        mock_chunks = [
            {
                'content': 'Machine learning is a subset of AI.',
                'metadata': {'document_id': 1, 'chunk_index': 0}
            },
            {
                'content': 'It uses algorithms to learn patterns.',
                'metadata': {'document_id': 1, 'chunk_index': 1}
            }
        ]
        self.mock_vector_service.search_similar_chunks.return_value = mock_chunks
        
        # Mock LLM response
        mock_llm_response = {
            'response': 'Machine learning is a subset of artificial intelligence.',
            'metadata': {'context_chunks_used': 2, 'model': 'gemini-pro'},
            'context_chunks': mock_chunks
        }
        self.mock_llm_service.generate_response.return_value = mock_llm_response
        
        result = self.rag_service.process_query("What is machine learning?")
        
        assert result['response'] == 'Machine learning is a subset of artificial intelligence.'
        assert result['metadata']['context_chunks_used'] == 2
        assert result['metadata']['search_performed'] is True
        assert result['metadata']['no_results'] is False
        assert len(result['context_chunks']) == 2
        
        # Verify that vector search was called
        self.mock_vector_service.search_similar_chunks.assert_called_once()
        # Verify that LLM was called
        self.mock_llm_service.generate_response.assert_called_once()
    
    def test_process_query_no_results(self):
        """Test query processing when no relevant chunks are found"""
        self.mock_vector_service.search_similar_chunks.return_value = []
        
        result = self.rag_service.process_query("What is quantum computing?")
        
        assert "couldn't find any relevant information" in result['response']
        assert result['metadata']['context_chunks_used'] == 0
        assert result['metadata']['search_performed'] is True
        assert result['metadata']['no_results'] is True
        assert result['context_chunks'] == []
        
        # Verify that LLM was not called
        self.mock_llm_service.generate_response.assert_not_called()
    
    def test_process_query_with_document_filter(self):
        """Test query processing with document ID filter"""
        mock_chunks = [{'content': 'Test content', 'metadata': {}}]
        self.mock_vector_service.search_similar_chunks.return_value = mock_chunks
        
        mock_llm_response = {
            'response': 'Test response',
            'metadata': {'context_chunks_used': 1},
            'context_chunks': mock_chunks
        }
        self.mock_llm_service.generate_response.return_value = mock_llm_response
        
        result = self.rag_service.process_query(
            "Test query",
            document_ids=[1, 2],
            max_chunks=3,
            max_tokens=500
        )
        
        # Verify that vector search was called with correct parameters
        self.mock_vector_service.search_similar_chunks.assert_called_once_with(
            query="Test query",
            n_results=3,
            document_ids=[1, 2]
        )
        
        # Verify that LLM was called with correct parameters
        self.mock_llm_service.generate_response.assert_called_once_with(
            query="Test query",
            context_chunks=mock_chunks,
            max_tokens=500
        )
    
    def test_process_query_vector_service_error(self):
        """Test query processing when vector service fails"""
        self.mock_vector_service.search_similar_chunks.side_effect = Exception("Vector service error")
        
        result = self.rag_service.process_query("Test query")
        
        assert "encountered an error" in result['response']
        assert result['metadata']['search_performed'] is False
        assert 'error' in result['metadata']
    
    def test_process_query_llm_service_error(self):
        """Test query processing when LLM service fails"""
        mock_chunks = [{'content': 'Test content', 'metadata': {}}]
        self.mock_vector_service.search_similar_chunks.return_value = mock_chunks
        self.mock_llm_service.generate_response.side_effect = Exception("LLM service error")
        
        result = self.rag_service.process_query("Test query")
        
        assert "encountered an error" in result['response']
        assert result['metadata']['search_performed'] is True
        assert 'error' in result['metadata']
    
    @patch('services.rag_service.Document')
    def test_get_available_documents(self, mock_document_class):
        """Test getting available documents"""
        # Mock document instances
        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {'id': 1, 'filename': 'doc1.pdf'}
        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {'id': 2, 'filename': 'doc2.pdf'}
        
        mock_document_class.query.filter_by.return_value.all.return_value = [mock_doc1, mock_doc2]
        
        result = self.rag_service.get_available_documents()
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        
        # Verify that the query was made correctly
        mock_document_class.query.filter_by.assert_called_once_with(processing_status='completed')
    
    @patch('services.rag_service.Document')
    def test_get_document_stats(self, mock_document_class):
        """Test getting document statistics"""
        # Mock query methods
        mock_query = MagicMock()
        mock_document_class.query = mock_query
        
        mock_query.count.return_value = 10
        mock_query.filter_by.return_value.count.side_effect = [8, 2]  # processed, failed
        mock_query.filter_by.return_value.all.return_value = [
            MagicMock(total_chunks=5),
            MagicMock(total_chunks=3)
        ]
        
        # Mock vector service stats
        self.mock_vector_service.get_collection_stats.return_value = {'total_chunks': 8}
        
        result = self.rag_service.get_document_stats()
        
        assert result['documents']['total'] == 10
        assert result['documents']['processed'] == 8
        assert result['documents']['failed'] == 2
        assert result['vector_database']['total_chunks'] == 8
    
    def test_get_document_stats_error(self):
        """Test error handling in get_document_stats"""
        with patch('services.rag_service.Document') as mock_document_class:
            mock_document_class.query.count.side_effect = Exception("Database error")
            
            result = self.rag_service.get_document_stats()
            
            assert result['documents']['total'] == 0
            assert result['documents']['processed'] == 0
            assert result['documents']['failed'] == 0