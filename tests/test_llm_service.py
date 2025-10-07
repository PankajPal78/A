import pytest
from unittest.mock import patch, MagicMock
from services.llm_service import LLMService

class TestLLMService:
    
    def setup_method(self):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-api-key'}):
            with patch('services.llm_service.genai.configure'):
                with patch('services.llm_service.genai.GenerativeModel'):
                    self.llm_service = LLMService()
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Gemini API key is required"):
                LLMService()
    
    def test_prepare_context(self):
        """Test context preparation from chunks"""
        chunks = [
            {
                'content': 'This is the first chunk about machine learning.',
                'metadata': {'document_id': 1, 'chunk_index': 0}
            },
            {
                'content': 'This is the second chunk about neural networks.',
                'metadata': {'document_id': 1, 'chunk_index': 1}
            }
        ]
        
        context = self.llm_service._prepare_context(chunks)
        
        assert 'Source 1' in context
        assert 'Source 2' in context
        assert 'machine learning' in context
        assert 'neural networks' in context
        assert 'Document 1' in context
    
    def test_create_prompt(self):
        """Test prompt creation"""
        query = "What is machine learning?"
        context = "Source 1: Machine learning is a subset of AI.\nSource 2: It uses algorithms to learn patterns."
        
        prompt = self.llm_service._create_prompt(query, context)
        
        assert query in prompt
        assert context in prompt
        assert "helpful AI assistant" in prompt
        assert "based on the provided document context" in prompt
    
    @patch('services.llm_service.genai.types.GenerationConfig')
    def test_generate_response_success(self, mock_gen_config):
        """Test successful response generation"""
        # Mock the model and response
        mock_response = MagicMock()
        mock_response.text = "Machine learning is a subset of artificial intelligence that focuses on algorithms."
        
        self.llm_service.model.generate_content.return_value = mock_response
        
        chunks = [
            {
                'content': 'Machine learning is a subset of AI.',
                'metadata': {'document_id': 1, 'chunk_index': 0}
            }
        ]
        
        result = self.llm_service.generate_response(
            query="What is machine learning?",
            context_chunks=chunks,
            max_tokens=1000
        )
        
        assert 'response' in result
        assert 'metadata' in result
        assert 'context_chunks' in result
        assert result['response'] == "Machine learning is a subset of artificial intelligence that focuses on algorithms."
        assert result['metadata']['context_chunks_used'] == 1
        assert result['context_chunks'] == chunks
    
    def test_generate_response_error(self):
        """Test error handling in response generation"""
        # Mock the model to raise an exception
        self.llm_service.model.generate_content.side_effect = Exception("API Error")
        
        chunks = [{'content': 'Test content', 'metadata': {}}]
        
        result = self.llm_service.generate_response(
            query="Test query",
            context_chunks=chunks
        )
        
        assert 'response' in result
        assert 'metadata' in result
        assert 'error' in result['metadata']
        assert "I encountered an error" in result['response']
    
    def test_generate_response_empty_response(self):
        """Test handling of empty response from model"""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.text = None
        
        self.llm_service.model.generate_content.return_value = mock_response
        
        chunks = [{'content': 'Test content', 'metadata': {}}]
        
        result = self.llm_service.generate_response(
            query="Test query",
            context_chunks=chunks
        )
        
        assert result['response'] == "I couldn't generate a response."
    
    @patch('services.llm_service.genai.types.GenerationConfig')
    def test_generate_response_with_generation_config(self, mock_gen_config):
        """Test that generation config is used correctly"""
        mock_response = MagicMock()
        mock_response.text = "Test response"
        
        self.llm_service.model.generate_content.return_value = mock_response
        
        chunks = [{'content': 'Test content', 'metadata': {}}]
        
        self.llm_service.generate_response(
            query="Test query",
            context_chunks=chunks,
            max_tokens=500
        )
        
        # Verify that generate_content was called with the right parameters
        call_args = self.llm_service.model.generate_content.call_args
        assert call_args[1]['generation_config'] is not None
    
    def test_test_connection_success(self):
        """Test successful connection test"""
        mock_response = MagicMock()
        mock_response.text = "Hello, this is a test."
        
        self.llm_service.model.generate_content.return_value = mock_response
        
        result = self.llm_service.test_connection()
        
        assert result is True
    
    def test_test_connection_failure(self):
        """Test connection test failure"""
        self.llm_service.model.generate_content.side_effect = Exception("Connection failed")
        
        result = self.llm_service.test_connection()
        
        assert result is False