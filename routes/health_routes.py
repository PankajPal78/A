"""
Health check and system status routes
"""

from flask import Blueprint, jsonify
from services.vector_store import VectorStore
from services.llm_service import LLMService
from config.settings import get_config
import os

bp = Blueprint('health', __name__, url_prefix='/api/health')

@bp.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'RAG Document Q&A System is running',
        'version': '1.0.0'
    })

@bp.route('/status', methods=['GET'])
def system_status():
    """Detailed system status check"""
    try:
        config = get_config()
        
        # Check vector store
        vector_store_status = 'unknown'
        try:
            vector_store = VectorStore(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                collection_name=config.COLLECTION_NAME,
                embedding_model=config.EMBEDDING_MODEL
            )
            vector_stats = vector_store.get_collection_stats()
            vector_store_status = 'healthy'
        except Exception as e:
            vector_store_status = f'error: {str(e)}'
            vector_stats = {}
        
        # Check LLM service
        llm_status = 'unknown'
        llm_info = {}
        try:
            llm_service = LLMService(provider_name=config.LLM_PROVIDER)
            llm_info = llm_service.get_provider_info()
            llm_status = 'healthy'
        except Exception as e:
            llm_status = f'error: {str(e)}'
        
        # Check upload directory
        upload_dir_status = 'healthy' if os.path.exists(config.UPLOAD_FOLDER) else 'missing'
        
        status = {
            'system': 'healthy',
            'components': {
                'vector_store': {
                    'status': vector_store_status,
                    'stats': vector_stats
                },
                'llm_service': {
                    'status': llm_status,
                    'info': llm_info
                },
                'upload_directory': {
                    'status': upload_dir_status,
                    'path': config.UPLOAD_FOLDER
                }
            },
            'configuration': {
                'max_documents': config.MAX_DOCUMENTS,
                'max_pages_per_document': config.MAX_PAGES_PER_DOCUMENT,
                'chunk_size': config.CHUNK_SIZE,
                'chunk_overlap': config.CHUNK_OVERLAP,
                'embedding_model': config.EMBEDDING_MODEL,
                'llm_provider': config.LLM_PROVIDER
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'system': 'error',
            'message': str(e)
        }), 500