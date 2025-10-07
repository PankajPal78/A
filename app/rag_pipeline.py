from typing import Dict, List
from app.vector_store import VectorStore
from app.llm_provider import get_llm_provider

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_provider = get_llm_provider()
    
    def query(self, question: str, top_k: int = None) -> Dict:
        """
        Process a query through the RAG pipeline
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.vector_store.search(question, top_k=top_k)
        
        if not retrieved_chunks:
            return {
                'answer': 'No relevant documents found. Please upload documents first.',
                'sources': [],
                'retrieved_chunks': 0
            }
        
        # Step 2: Extract context texts
        context_texts = [chunk['text'] for chunk in retrieved_chunks]
        
        # Step 3: Generate response using LLM
        answer = self.llm_provider.generate_response(question, context_texts)
        
        # Step 4: Prepare sources
        sources = []
        for chunk in retrieved_chunks:
            source = {
                'document_id': chunk['metadata'].get('document_id'),
                'chunk_index': chunk['metadata'].get('chunk_index'),
                'text_preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
            }
            if 'distance' in chunk and chunk['distance'] is not None:
                source['relevance_score'] = 1 - chunk['distance']  # Convert distance to similarity
            sources.append(source)
        
        return {
            'answer': answer,
            'sources': sources,
            'retrieved_chunks': len(retrieved_chunks)
        }