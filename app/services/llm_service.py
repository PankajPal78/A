"""
LLM service for generating responses using various LLM providers
"""
import os
from typing import List, Dict
import google.generativeai as genai
from config.settings import (
    LLM_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY,
    LLM_TEMPERATURE, LLM_MAX_TOKENS
)
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM APIs"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or LLM_PROVIDER
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == 'gemini':
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Initialized Gemini LLM")
        elif self.provider == 'openai':
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            # OpenAI client would be initialized here
            logger.info("Initialized OpenAI LLM")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_response(self, query: str, context_chunks: List[Dict]) -> Dict:
        """
        Generate a response using the LLM with context from retrieved chunks
        
        Args:
            query: User's question
            context_chunks: List of relevant document chunks
        
        Returns:
            Dictionary with response and metadata
        """
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Create prompt
        prompt = self._create_prompt(query, context)
        
        # Generate response based on provider
        if self.provider == 'gemini':
            response_text = self._generate_gemini_response(prompt)
        elif self.provider == 'openai':
            response_text = self._generate_openai_response(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        return {
            'answer': response_text,
            'context_chunks_used': len(context_chunks),
            'sources': self._extract_sources(context_chunks)
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from chunks"""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            text = chunk.get('text', '')
            context_parts.append(f"[Source {i} - {filename}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the prompt for the LLM"""
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from documents.

Context from documents:
{context}

User Question: {query}

Instructions:
1. Answer the question based ONLY on the information provided in the context above.
2. If the context doesn't contain enough information to answer the question, say so clearly.
3. Be concise and accurate in your response.
4. If you reference specific information, mention which source it came from.

Answer:"""
        
        return prompt
    
    def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                    max_output_tokens=LLM_MAX_TOKENS,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI (placeholder)"""
        # This would use the OpenAI API
        raise NotImplementedError("OpenAI provider not yet implemented")
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Extract source information from chunks"""
        sources = []
        seen_docs = set()
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            doc_id = metadata.get('document_id')
            
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                sources.append({
                    'document_id': doc_id,
                    'filename': metadata.get('filename', 'Unknown'),
                    'page_count': metadata.get('page_count', 0)
                })
        
        return sources