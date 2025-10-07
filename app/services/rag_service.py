"""
RAG (Retrieval-Augmented Generation) service
Orchestrates document retrieval and response generation
"""
from typing import Dict, Optional
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from config.settings import TOP_K_RESULTS
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG pipeline service"""
    
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        logger.info("RAG Service initialized")
    
    def query(self, question: str, document_id: Optional[int] = None, top_k: int = TOP_K_RESULTS) -> Dict:
        """
        Process a user query through the RAG pipeline
        
        Args:
            question: User's question
            document_id: Optional filter by specific document
            top_k: Number of chunks to retrieve
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Step 1: Retrieve relevant chunks
            logger.info(f"Retrieving relevant chunks for query: {question[:100]}")
            relevant_chunks = self.vector_store.search(
                query=question,
                top_k=top_k,
                document_id=document_id
            )
            
            if not relevant_chunks:
                return {
                    'answer': "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    'sources': [],
                    'chunks_retrieved': 0,
                    'success': True
                }
            
            # Step 2: Generate response using LLM
            logger.info(f"Generating response with {len(relevant_chunks)} chunks")
            response = self.llm_service.generate_response(question, relevant_chunks)
            
            # Step 3: Format and return result
            return {
                'answer': response['answer'],
                'sources': response['sources'],
                'chunks_retrieved': len(relevant_chunks),
                'context_chunks': [
                    {
                        'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                        'metadata': chunk['metadata']
                    }
                    for chunk in relevant_chunks
                ],
                'success': True
            }
        
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            return {
                'answer': f"An error occurred while processing your query: {str(e)}",
                'sources': [],
                'chunks_retrieved': 0,
                'success': False,
                'error': str(e)
            }