import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        logger.info("LLM Client initialized with Gemini Pro")
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using the LLM with retrieved context"""
        try:
            # Prepare context from chunks
            context_text = self._prepare_context(context_chunks)
            
            # Create the prompt
            prompt = self._create_prompt(query, context_text)
            
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
            
            # Extract response text
            response_text = response.text if response.text else "No response generated"
            
            # Prepare metadata
            metadata = {
                'model': 'gemini-pro',
                'context_chunks_used': len(context_chunks),
                'context_length': len(context_text),
                'max_tokens': max_tokens
            }
            
            return {
                'response': response_text,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'response': f"Error generating response: {str(e)}",
                'metadata': {'error': str(e)},
                'success': False
            }
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved chunks"""
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            chunk_text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            
            context_parts.append(f"Source {i} (from {filename}):\n{chunk_text}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM"""
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from uploaded documents. 

Context from documents:
{context}

Question: {query}

Instructions:
1. Answer the question based ONLY on the information provided in the context above.
2. If the answer cannot be found in the context, clearly state that the information is not available in the provided documents.
3. Be concise and accurate in your response.
4. If you reference information from the context, mention which source it came from.
5. Do not make up or hallucinate information that is not in the context.

Answer:"""
        
        return prompt
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the LLM API"""
        try:
            test_response = self.model.generate_content("Hello, this is a test message.")
            return {
                'success': True,
                'message': 'Connection successful',
                'response': test_response.text if test_response.text else 'No response'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e)
            }