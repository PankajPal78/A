from typing import List, Dict
from abc import ABC, abstractmethod
from app.config import Config

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response based on query and context"""
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using Gemini"""
        context_text = "\n\n".join(context)
        
        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, say "I don't have enough information to answer this question."

Context:
{context_text}

Question: {query}

Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response with Gemini: {str(e)}")

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using OpenAI"""
        context_text = "\n\n".join(context)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If you cannot find the answer in the context, say so."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response with OpenAI: {str(e)}")

class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""
    
    def __init__(self):
        import requests
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.requests = requests
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using Ollama"""
        context_text = "\n\n".join(context)
        
        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, say "I don't have enough information to answer this question."

Context:
{context_text}

Question: {query}

Answer:"""
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            raise Exception(f"Error generating response with Ollama: {str(e)}")

def get_llm_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider"""
    provider = Config.LLM_PROVIDER.lower()
    
    if provider == 'gemini':
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        return GeminiProvider()
    elif provider == 'openai':
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        return OpenAIProvider()
    elif provider == 'ollama':
        return OllamaProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")