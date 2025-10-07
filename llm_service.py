import os
import logging
import google.generativeai as genai
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Gemini API for RAG responses"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using RAG pipeline"""
        try:
            # Prepare context from retrieved chunks
            context = self._prepare_context(context_chunks)
            
            # Create the prompt
            prompt = self._create_rag_prompt(query, context)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            return {
                'success': True,
                'response': response.text,
                'sources': self._extract_sources(context_chunks),
                'context_used': len(context_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': "I apologize, but I encountered an error while processing your query. Please try again."
            }
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(context_chunks, 1):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            page_number = metadata.get('page_number', 'Unknown')
            document_id = metadata.get('document_id', 'Unknown')
            
            context_parts.append(f"""
Source {i} (Document ID: {document_id}, Page: {page_number}):
{content}
""")
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create a comprehensive RAG prompt"""
        return f"""You are a helpful AI assistant that answers questions based on the provided document context. 

Instructions:
1. Answer the user's question using ONLY the information provided in the context below.
2. If the context doesn't contain enough information to answer the question, say so clearly.
3. Cite specific sources when possible by referencing the document ID and page number.
4. Be concise but comprehensive in your response.
5. If the question is not related to the document content, politely redirect to document-related topics.

Context from documents:
{context}

User Question: {query}

Answer:"""
    
    def _extract_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from context chunks"""
        sources = []
        
        for chunk in context_chunks:
            metadata = chunk.get('metadata', {})
            sources.append({
                'document_id': metadata.get('document_id'),
                'page_number': metadata.get('page_number'),
                'similarity_score': chunk.get('similarity_score', 0),
                'chunk_size': metadata.get('chunk_size', 0)
            })
        
        return sources
    
    def test_connection(self) -> bool:
        """Test the connection to Gemini API"""
        try:
            response = self.model.generate_content("Hello, this is a test.")
            return response.text is not None
        except Exception as e:
            logger.error(f"Error testing Gemini connection: {str(e)}")
            return False