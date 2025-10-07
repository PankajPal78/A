"""
Document upload and management routes
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.document import Document, db
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from config.settings import get_config

logger = logging.getLogger(__name__)
bp = Blueprint('documents', __name__, url_prefix='/api/documents')

def allowed_file(filename):
    """Check if file extension is allowed"""
    config = get_config()
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        config = get_config()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Supported types: {config.ALLOWED_EXTENSIONS}'
            }), 400
        
        # Check document limit
        document_count = Document.query.count()
        if document_count >= config.MAX_DOCUMENTS:
            return jsonify({
                'error': f'Maximum number of documents ({config.MAX_DOCUMENTS}) reached'
            }), 400
        
        # Generate unique filename
        original_filename = file.filename
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{secure_filename(original_filename)}"
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            status='uploaded'
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Process document in background (or synchronously for now)
        try:
            document.update_status('processing')
            
            # Initialize services
            processor = DocumentProcessor(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )
            
            vector_store = VectorStore(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                collection_name=config.COLLECTION_NAME,
                embedding_model=config.EMBEDDING_MODEL
            )
            
            # Process document
            processing_result = processor.process_document(
                file_path=file_path,
                filename=original_filename,
                file_type=file_extension
            )
            
            # Update document metadata
            document.total_pages = processing_result['page_count']
            document.word_count = processing_result['word_count']
            document.total_chunks = processing_result['chunk_count']
            
            # Store chunks in vector database
            chunk_ids = vector_store.add_documents(
                chunks=processing_result['chunks'],
                document_id=document.id
            )
            
            # Update document with chunk IDs
            document.add_collection_ids(chunk_ids)
            document.update_status('processed')
            
            logger.info(f"Successfully processed document {original_filename} "
                       f"({processing_result['chunk_count']} chunks)")
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': document.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Error processing document {original_filename}: {str(e)}")
            document.update_status('error', str(e))
            
            # Clean up file on processing error
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify({
                'error': f'Error processing document: {str(e)}',
                'document': document.to_dict()
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        
        # Build query
        query = Document.query
        if status_filter:
            query = query.filter(Document.status == status_filter)
        
        # Paginate
        documents = query.order_by(Document.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': documents.total,
                'pages': documents.pages,
                'has_next': documents.has_next,
                'has_prev': documents.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details by ID"""
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify({'document': document.to_dict()})
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and its chunks"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Delete from vector store
        config = get_config()
        vector_store = VectorStore(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            collection_name=config.COLLECTION_NAME,
            embedding_model=config.EMBEDDING_MODEL
        )
        
        deleted_chunks = vector_store.delete_document(document_id)
        
        # Delete file
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.warning(f"Could not delete file {document.file_path}: {str(e)}")
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        logger.info(f"Deleted document {document.original_filename} "
                   f"and {deleted_chunks} chunks")
        
        return jsonify({
            'message': 'Document deleted successfully',
            'deleted_chunks': deleted_chunks
        })
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:document_id>/chunks', methods=['GET'])
def get_document_chunks(document_id):
    """Get all chunks for a specific document"""
    try:
        document = Document.query.get_or_404(document_id)
        
        config = get_config()
        vector_store = VectorStore(
            persist_directory=config.CHROMA_PERSIST_DIRECTORY,
            collection_name=config.COLLECTION_NAME,
            embedding_model=config.EMBEDDING_MODEL
        )
        
        chunks = vector_store.get_document_chunks(document_id)
        
        return jsonify({
            'document_id': document_id,
            'document_name': document.original_filename,
            'total_chunks': len(chunks),
            'chunks': chunks
        })
        
    except Exception as e:
        logger.error(f"Error getting chunks for document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_document_stats():
    """Get document collection statistics"""
    try:
        # Database stats
        total_documents = Document.query.count()
        processed_documents = Document.query.filter(Document.status == 'processed').count()
        processing_documents = Document.query.filter(Document.status == 'processing').count()
        error_documents = Document.query.filter(Document.status == 'error').count()
        
        # Calculate totals
        total_pages = db.session.query(db.func.sum(Document.total_pages)).scalar() or 0
        total_chunks = db.session.query(db.func.sum(Document.total_chunks)).scalar() or 0
        total_words = db.session.query(db.func.sum(Document.word_count)).scalar() or 0
        total_size = db.session.query(db.func.sum(Document.file_size)).scalar() or 0
        
        # Vector store stats
        config = get_config()
        try:
            vector_store = VectorStore(
                persist_directory=config.CHROMA_PERSIST_DIRECTORY,
                collection_name=config.COLLECTION_NAME,
                embedding_model=config.EMBEDDING_MODEL
            )
            vector_stats = vector_store.get_collection_stats()
        except Exception:
            vector_stats = {}
        
        return jsonify({
            'database_stats': {
                'total_documents': total_documents,
                'processed_documents': processed_documents,
                'processing_documents': processing_documents,
                'error_documents': error_documents,
                'total_pages': total_pages,
                'total_chunks': total_chunks,
                'total_words': total_words,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            },
            'vector_store_stats': vector_stats,
            'limits': {
                'max_documents': config.MAX_DOCUMENTS,
                'max_pages_per_document': config.MAX_PAGES_PER_DOCUMENT,
                'allowed_file_types': list(config.ALLOWED_EXTENSIONS)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        return jsonify({'error': str(e)}), 500