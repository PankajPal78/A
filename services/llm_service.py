import google.generativeai as genai
import os
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], 
                         max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate a response using the LLM with retrieved context
        """
        try:
            # Prepare context from chunks
            context_text = self._prepare_context(context_chunks)
            
            # Create prompt
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
            response_text = response.text if response.text else "I couldn't generate a response."
            
            # Prepare metadata
            metadata = {
                "model": "gemini-pro",
                "context_chunks_used": len(context_chunks),
                "prompt_tokens": len(prompt.split()),
                "response_tokens": len(response_text.split())
            }
            
            logger.info(f"Generated response with {len(context_chunks)} context chunks")
            
            return {
                "response": response_text,
                "metadata": metadata,
                "context_chunks": context_chunks
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return {
                "response": f"I encountered an error while processing your query: {str(e)}",
                "metadata": {"error": str(e)},
                "context_chunks": context_chunks
            }
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context text from retrieved chunks
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            document_id = metadata.get('document_id', 'Unknown')
            chunk_index = metadata.get('chunk_index', i)
            
            context_parts.append(
                f"Source {i} (Document {document_id}, Chunk {chunk_index}):\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for the LLM
        """
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided document context. 
Use only the information from the context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.

Context from documents:
{context}

Question: {query}

Please provide a comprehensive and accurate answer based on the context above. If you reference specific information, mention which source it came from."""

        return prompt
    
    def test_connection(self) -> bool:
        """
        Test the connection to the LLM service
        """
        try:
            test_response = self.model.generate_content("Hello, this is a test.")
            return test_response.text is not None
        except Exception as e:
            logger.error(f"LLM service connection test failed: {str(e)}")
            return False