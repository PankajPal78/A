import os
import logging
import google.generativeai as genai
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Handles LLM interactions using Google Gemini"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        logger.info("LLM service initialized with Gemini")
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a response using the LLM with retrieved context"""
        try:
            # Prepare context from chunks
            context_text = self._prepare_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract sources
            sources = self._extract_sources(context_chunks)
            
            return {
                'answer': response.text,
                'sources': sources,
                'metadata': {
                    'model': 'gemini-pro',
                    'context_chunks_used': len(context_chunks),
                    'prompt_length': len(prompt)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from retrieved chunks"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"Context {i}:\n{chunk['text']}\n")
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM"""
        return f"""You are a helpful assistant that answers questions based on the provided context. 
        Use only the information from the context to answer the question. If the context doesn't contain 
        enough information to answer the question, say so clearly.

        Context:
        {context}

        Question: {query}

        Please provide a comprehensive and accurate answer based on the context provided. 
        If you reference specific information, mention which context section it came from.
        """
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from chunks"""
        sources = []
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            sources.append({
                'document_id': metadata.get('document_id'),
                'chunk_id': metadata.get('chunk_id'),
                'chunk_index': metadata.get('chunk_index'),
                'similarity_score': 1 - chunk.get('distance', 0) if chunk.get('distance') is not None else None
            })
        return sources
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service"""
        try:
            test_response = self.model.generate_content("Hello, this is a test.")
            return test_response.text is not None
        except Exception as e:
            logger.error(f"Error testing LLM connection: {str(e)}")
            return False