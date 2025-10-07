import logging
from typing import List, Dict, Any, Optional
import time
from vector_store import VectorStore
from llm_client import LLMClient
from database import log_query

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, vector_store: VectorStore = None, llm_client: LLMClient = None):
        self.vector_store = vector_store or VectorStore()
        self.llm_client = llm_client or LLMClient()
    
    def query(self, question: str, document_ids: Optional[List[int]] = None, 
              max_chunks: int = 5, max_tokens: int = 1000) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            # Step 1: Retrieve relevant chunks
            logger.info("Retrieving relevant chunks...")
            relevant_chunks = self.vector_store.search_similar_chunks(
                query=question,
                n_results=max_chunks,
                document_ids=document_ids
            )
            
            if not relevant_chunks:
                response = {
                    'answer': "I couldn't find any relevant information in the uploaded documents to answer your question.",
                    'sources': [],
                    'metadata': {
                        'chunks_retrieved': 0,
                        'response_time': time.time() - start_time,
                        'error': 'No relevant chunks found'
                    },
                    'success': False
                }
                
                # Log the query
                log_query(question, response['answer'], str(document_ids or []), 
                         time.time() - start_time)
                
                return response
            
            # Step 2: Generate response using LLM
            logger.info("Generating response with LLM...")
            llm_response = self.llm_client.generate_response(
                query=question,
                context_chunks=relevant_chunks,
                max_tokens=max_tokens
            )
            
            if not llm_response['success']:
                response = {
                    'answer': f"Error generating response: {llm_response.get('metadata', {}).get('error', 'Unknown error')}",
                    'sources': [],
                    'metadata': {
                        'chunks_retrieved': len(relevant_chunks),
                        'response_time': time.time() - start_time,
                        'error': 'LLM generation failed'
                    },
                    'success': False
                }
                
                # Log the query
                log_query(question, response['answer'], str(document_ids or []), 
                         time.time() - start_time)
                
                return response
            
            # Step 3: Prepare sources information
            sources = self._prepare_sources(relevant_chunks)
            
            # Step 4: Prepare final response
            response = {
                'answer': llm_response['response'],
                'sources': sources,
                'metadata': {
                    'chunks_retrieved': len(relevant_chunks),
                    'response_time': time.time() - start_time,
                    'llm_metadata': llm_response.get('metadata', {}),
                    'query_processed': True
                },
                'success': True
            }
            
            # Log the query
            log_query(question, response['answer'], str(document_ids or []), 
                     time.time() - start_time)
            
            logger.info(f"Query processed successfully in {time.time() - start_time:.2f} seconds")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            response = {
                'answer': f"An error occurred while processing your query: {str(e)}",
                'sources': [],
                'metadata': {
                    'chunks_retrieved': 0,
                    'response_time': time.time() - start_time,
                    'error': str(e)
                },
                'success': False
            }
            
            # Log the query
            log_query(question, response['answer'], str(document_ids or []), 
                     time.time() - start_time)
            
            return response
    
    def _prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare sources information from chunks"""
        sources = []
        seen_documents = set()
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            document_id = metadata.get('document_id')
            filename = metadata.get('filename', 'Unknown')
            
            if document_id and document_id not in seen_documents:
                source = {
                    'document_id': document_id,
                    'filename': filename,
                    'file_type': metadata.get('file_type', ''),
                    'upload_date': metadata.get('upload_date', ''),
                    'relevance_score': 1 - chunk.get('distance', 0)  # Convert distance to relevance
                }
                sources.append(source)
                seen_documents.add(document_id)
        
        # Sort by relevance score
        sources.sort(key=lambda x: x['relevance_score'], reverse=True)
        return sources
    
    def get_document_summary(self, document_id: int) -> Dict[str, Any]:
        """Get a summary of a specific document"""
        try:
            chunks = self.vector_store.get_document_chunks(document_id)
            
            if not chunks:
                return {
                    'document_id': document_id,
                    'summary': 'No chunks found for this document',
                    'chunk_count': 0,
                    'success': False
                }
            
            # Create a simple summary from chunk texts
            all_text = ' '.join([chunk['text'] for chunk in chunks])
            
            # Truncate for summary (first 500 characters)
            summary = all_text[:500] + "..." if len(all_text) > 500 else all_text
            
            return {
                'document_id': document_id,
                'summary': summary,
                'chunk_count': len(chunks),
                'total_text_length': len(all_text),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting document summary: {str(e)}")
            return {
                'document_id': document_id,
                'summary': f'Error generating summary: {str(e)}',
                'chunk_count': 0,
                'success': False
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            
            return {
                'vector_database': vector_stats,
                'llm_model': 'gemini-pro',
                'status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {
                'error': str(e),
                'status': 'error'
            }