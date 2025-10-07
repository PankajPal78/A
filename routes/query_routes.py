"""
Query processing and RAG pipeline routes
"""

import logging
from flask import Blueprint, request, jsonify
from services.rag_pipeline import RAGPipeline
from services.vector_store import VectorStore
from services.llm_service import LLMService
from models.document import Document, QueryLog
from config.settings import get_config

logger = logging.getLogger(__name__)
bp = Blueprint('query', __name__, url_prefix='/api/query')

def get_rag_pipeline():
    """Initialize and return RAG pipeline"""
    config = get_config()
    
    vector_store = VectorStore(
        persist_directory=config.CHROMA_PERSIST_DIRECTORY,
        collection_name=config.COLLECTION_NAME,
        embedding_model=config.EMBEDDING_MODEL
    )
    
    llm_service = LLMService(provider_name=config.LLM_PROVIDER)
    
    rag_pipeline = RAGPipeline(
        vector_store=vector_store,
        llm_service=llm_service,
        top_k=config.TOP_K_RETRIEVAL,
        similarity_threshold=config.SIMILARITY_THRESHOLD
    )
    
    return rag_pipeline

@bp.route('/', methods=['POST'])
def process_query():
    """Process a user query through the RAG pipeline"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query text is required'}), 400
        
        query_text = data['query'].strip()
        
        # Validate query
        rag_pipeline = get_rag_pipeline()
        if not rag_pipeline.validate_query(query_text):
            return jsonify({
                'error': 'Invalid query. Query must be between 3 and 1000 characters.'
            }), 400
        
        # Optional parameters
        document_ids = data.get('document_ids')  # List of specific document IDs
        top_k = data.get('top_k')  # Number of chunks to retrieve
        similarity_threshold = data.get('similarity_threshold')  # Minimum similarity
        
        # Validate document IDs if provided
        if document_ids:
            if not isinstance(document_ids, list):
                return jsonify({'error': 'document_ids must be a list'}), 400
            
            # Check if documents exist
            existing_docs = Document.query.filter(
                Document.id.in_(document_ids),
                Document.status == 'processed'
            ).count()
            
            if existing_docs != len(document_ids):
                return jsonify({
                    'error': 'One or more specified documents not found or not processed'
                }), 400
        
        # Process query
        response = rag_pipeline.query(
            query_text=query_text,
            document_ids=document_ids,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
def get_query_history():
    """Get query history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        rag_pipeline = get_rag_pipeline()
        history = rag_pipeline.get_query_history(limit=limit)
        
        return jsonify({
            'history': history,
            'total_returned': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting query history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_query_stats():
    """Get query and pipeline statistics"""
    try:
        rag_pipeline = get_rag_pipeline()
        stats = rag_pipeline.get_pipeline_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting query stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/config', methods=['GET'])
def get_pipeline_config():
    """Get current pipeline configuration"""
    try:
        config = get_config()
        
        return jsonify({
            'retrieval_config': {
                'top_k': config.TOP_K_RETRIEVAL,
                'similarity_threshold': config.SIMILARITY_THRESHOLD,
                'embedding_model': config.EMBEDDING_MODEL
            },
            'text_processing': {
                'chunk_size': config.CHUNK_SIZE,
                'chunk_overlap': config.CHUNK_OVERLAP
            },
            'llm_config': {
                'provider': config.LLM_PROVIDER
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting pipeline config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/config', methods=['PUT'])
def update_pipeline_config():
    """Update pipeline configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuration data is required'}), 400
        
        rag_pipeline = get_rag_pipeline()
        
        # Update configuration
        top_k = data.get('top_k')
        similarity_threshold = data.get('similarity_threshold')
        
        if top_k is not None:
            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return jsonify({'error': 'top_k must be an integer between 1 and 20'}), 400
        
        if similarity_threshold is not None:
            if not isinstance(similarity_threshold, (int, float)) or similarity_threshold < 0 or similarity_threshold > 1:
                return jsonify({'error': 'similarity_threshold must be a number between 0 and 1'}), 400
        
        rag_pipeline.update_config(
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'new_config': {
                'top_k': rag_pipeline.top_k,
                'similarity_threshold': rag_pipeline.similarity_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating pipeline config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/search', methods=['POST'])
def search_documents():
    """Search for relevant document chunks without generating an answer"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query text is required'}), 400
        
        query_text = data['query'].strip()
        
        # Optional parameters
        document_ids = data.get('document_ids')
        top_k = data.get('top_k', 10)
        similarity_threshold = data.get('similarity_threshold', 0.0)
        
        # Initialize vector store
        config = get_config()
        vector_store = VectorStore(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            collection_name=config.COLLECTION_NAME,
            embedding_model=config.EMBEDDING_MODEL
        )
        
        # Perform search
        results = vector_store.similarity_search(
            query=query_text,
            top_k=top_k,
            document_ids=document_ids,
            similarity_threshold=similarity_threshold
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                'chunk_id': result['id'],
                'text_preview': result['text'][:300] + '...' if len(result['text']) > 300 else result['text'],
                'full_text': result['text'],
                'similarity_score': result['similarity_score'],
                'metadata': result['metadata']
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'query': query_text,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_params': {
                'top_k': top_k,
                'similarity_threshold': similarity_threshold,
                'document_ids': document_ids
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return jsonify({'error': str(e)}), 500