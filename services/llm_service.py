"""
LLM service for generating responses using various providers
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Import LLM providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: str, query: str) -> str:
        """Generate response using the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return GEMINI_AVAILABLE and self.api_key is not None and self.model is not None
    
    def generate_response(self, prompt: str, context: str, query: str) -> str:
        """Generate response using Gemini"""
        try:
            if not self.is_available():
                raise ValueError("Gemini provider is not available or not configured")
            
            full_prompt = f"{prompt}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            raise

class OpenAIProvider(LLMProvider):
    """OpenAI GPT LLM provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key) if OPENAI_AVAILABLE and self.api_key else None
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return OPENAI_AVAILABLE and self.api_key is not None and self.client is not None
    
    def generate_response(self, prompt: str, context: str, query: str) -> str:
        """Generate response using OpenAI"""
        try:
            if not self.is_available():
                raise ValueError("OpenAI provider is not available or not configured")
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            raise

class LLMService:
    """Service for managing LLM providers and generating responses"""
    
    def __init__(self, provider_name: str = "gemini"):
        self.provider_name = provider_name.lower()
        self.providers = {
            'gemini': GeminiProvider(),
            'openai': OpenAIProvider()
        }
        
        # Set primary provider
        self.primary_provider = self.providers.get(self.provider_name)
        if not self.primary_provider or not self.primary_provider.is_available():
            # Fallback to any available provider
            for name, provider in self.providers.items():
                if provider.is_available():
                    self.primary_provider = provider
                    self.provider_name = name
                    logger.info(f"Using fallback LLM provider: {name}")
                    break
        
        if not self.primary_provider or not self.primary_provider.is_available():
            raise ValueError("No LLM provider is available. Please configure API keys.")
        
        logger.info(f"Initialized LLM service with provider: {self.provider_name}")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for RAG responses"""
        return """You are a helpful AI assistant that answers questions based on provided document context. 

Instructions:
1. Use ONLY the information provided in the context to answer questions
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Be concise but comprehensive in your responses
4. If you find conflicting information in the context, mention it
5. Always cite which part of the context supports your answer when possible
6. Do not make up information that is not in the provided context

Your goal is to provide accurate, helpful answers based solely on the document content provided."""
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate response using retrieved context chunks
        Returns response with metadata
        """
        try:
            start_time = time.time()
            
            # Prepare context from chunks
            context_parts = []
            source_info = []
            
            for i, chunk in enumerate(context_chunks):
                text = chunk.get('text', '')
                metadata = chunk.get('metadata', {})
                
                # Add chunk text to context
                context_parts.append(f"[Source {i+1}] {text}")
                
                # Collect source information
                source_info.append({
                    'chunk_id': chunk.get('id'),
                    'document_id': metadata.get('document_id'),
                    'filename': metadata.get('filename'),
                    'chunk_index': metadata.get('chunk_index'),
                    'similarity_score': chunk.get('similarity_score', 0.0)
                })
            
            # Combine context
            context = "\n\n".join(context_parts)
            
            # Generate response
            system_prompt = self.get_system_prompt()
            response_text = self.primary_provider.generate_response(
                prompt=system_prompt,
                context=context,
                query=query
            )
            
            generation_time = time.time() - start_time
            
            return {
                'response': response_text,
                'sources': source_info,
                'context_chunks_used': len(context_chunks),
                'generation_time': generation_time,
                'provider': self.provider_name
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers"""
        provider_status = {}
        for name, provider in self.providers.items():
            provider_status[name] = {
                'available': provider.is_available(),
                'is_primary': name == self.provider_name
            }
        
        return {
            'current_provider': self.provider_name,
            'providers': provider_status
        }