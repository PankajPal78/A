"""
Flask API routes for the RAG application
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.models.document import Document
from app.utils.database import get_session
from app.utils.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService
from config.settings import (
    UPLOAD_FOLDER, MAX_DOCUMENTS, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
)
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
document_processor = DocumentProcessor()
vector_store = VectorStoreService()
rag_service = RAGService()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'RAG Document Q&A System'
    }), 200

@api_bp.route('/documents', methods=['POST'])
def upload_document():
    """
    Upload a document for processing
    
    Accepts: multipart/form-data with 'file' field
    Returns: Document metadata
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Check document limit
        session = get_session()
        doc_count = session.query(Document).filter(Document.status != 'failed').count()
        
        if doc_count >= MAX_DOCUMENTS:
            session.close()
            return jsonify({
                'error': f'Maximum document limit ({MAX_DOCUMENTS}) reached. Please delete some documents first.'
            }), 400
        
        # Secure the filename
        original_filename = file.filename
        filename = secure_filename(original_filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            session.close()
            return jsonify({
                'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024):.0f}MB'
            }), 400
        
        # Save file
        file.save(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # Create document record
        document = Document(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            status='processing'
        )
        session.add(document)
        session.commit()
        doc_id = document.id
        
        try:
            # Process document
            logger.info(f"Processing document {doc_id}: {original_filename}")
            chunks, page_count = document_processor.process_document(
                file_path, file_type, doc_id, original_filename
            )
            
            # Add to vector store
            vector_store.add_documents(chunks, doc_id)
            
            # Update document metadata
            document.page_count = page_count
            document.chunk_count = len(chunks)
            document.status = 'indexed'
            session.commit()
            
            logger.info(f"Successfully processed document {doc_id}")
            
            result = document.to_dict()
            session.close()
            return jsonify(result), 201
        
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {str(e)}")
            document.status = 'failed'
            document.error_message = str(e)
            session.commit()
            session.close()
            return jsonify({
                'error': f'Failed to process document: {str(e)}',
                'document_id': doc_id
            }), 500
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents', methods=['GET'])
def list_documents():
    """
    List all uploaded documents with metadata
    
    Query params:
        - status: Filter by status (optional)
        - limit: Limit number of results (optional)
    """
    try:
        session = get_session()
        
        query = session.query(Document)
        
        # Filter by status if provided
        status = request.args.get('status')
        if status:
            query = query.filter(Document.status == status)
        
        # Limit results if provided
        limit = request.args.get('limit', type=int)
        if limit:
            query = query.limit(limit)
        
        # Order by upload date descending
        query = query.order_by(Document.upload_date.desc())
        
        documents = query.all()
        result = [doc.to_dict() for doc in documents]
        
        session.close()
        return jsonify({
            'documents': result,
            'count': len(result)
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get specific document metadata"""
    try:
        session = get_session()
        document = session.query(Document).filter(Document.id == doc_id).first()
        
        if not document:
            session.close()
            return jsonify({'error': 'Document not found'}), 404
        
        result = document.to_dict()
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document and its embeddings"""
    try:
        session = get_session()
        document = session.query(Document).filter(Document.id == doc_id).first()
        
        if not document:
            session.close()
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from vector store
        vector_store.delete_document(doc_id)
        
        # Delete file if it exists
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        session.delete(document)
        session.commit()
        session.close()
        
        logger.info(f"Deleted document {doc_id}")
        return jsonify({'message': 'Document deleted successfully', 'id': doc_id}), 200
    
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/query', methods=['POST'])
def query_documents():
    """
    Query the RAG system
    
    Body: {
        "question": "Your question here",
        "document_id": 1  // optional, to query specific document
        "top_k": 5  // optional, number of chunks to retrieve
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        document_id = data.get('document_id')
        top_k = data.get('top_k', 5)
        
        if not question.strip():
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Process query through RAG pipeline
        result = rag_service.query(question, document_id, top_k)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        session = get_session()
        
        total_docs = session.query(Document).count()
        indexed_docs = session.query(Document).filter(Document.status == 'indexed').count()
        failed_docs = session.query(Document).filter(Document.status == 'failed').count()
        
        total_pages = session.query(Document).filter(
            Document.status == 'indexed'
        ).with_entities(Document.page_count).all()
        total_page_count = sum([p[0] for p in total_pages if p[0]])
        
        total_chunks = session.query(Document).filter(
            Document.status == 'indexed'
        ).with_entities(Document.chunk_count).all()
        total_chunk_count = sum([c[0] for c in total_chunks if c[0]])
        
        vector_stats = vector_store.get_collection_stats()
        
        session.close()
        
        return jsonify({
            'documents': {
                'total': total_docs,
                'indexed': indexed_docs,
                'failed': failed_docs,
                'processing': total_docs - indexed_docs - failed_docs
            },
            'pages': total_page_count,
            'chunks': total_chunk_count,
            'vector_store': vector_stats,
            'limits': {
                'max_documents': MAX_DOCUMENTS,
                'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500