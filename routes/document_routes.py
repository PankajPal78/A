from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app import Document
from app import db
from services.document_processor import DocumentProcessor
from services.vector_service import VectorService
import logging

document_bp = Blueprint('documents', __name__)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()
vector_service = VectorService()

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_DOCUMENTS = 20
MAX_PAGES_PER_DOCUMENT = 1000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload a document for processing
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Allowed types: PDF, DOCX'}), 400
        
        # Check document limit
        current_doc_count = Document.query.count()
        if current_doc_count >= MAX_DOCUMENTS:
            return jsonify({'error': f'Maximum number of documents ({MAX_DOCUMENTS}) reached'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
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
            processing_status='pending'
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Process document asynchronously (in a real app, use Celery or similar)
        success = document_processor.process_document(document)
        
        if success:
            # Add chunks to vector database
            chunks = document_processor.get_document_chunks(document.id)
            vector_service.add_document_chunks(document.id, chunks)
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': document.to_dict()
            }), 201
        else:
            return jsonify({
                'message': 'Document uploaded but processing failed',
                'document': document.to_dict()
            }), 202
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@document_bp.route('/', methods=['GET'])
def get_documents():
    """
    Get list of all documents
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        documents = Document.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': documents.total,
                'pages': documents.pages
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': f'Failed to retrieve documents: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get specific document details
    """
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify({'document': document.to_dict()}), 200
    
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to retrieve document: {str(e)}'}), 500

@document_bp.route('/<int:document_id>/chunks', methods=['GET'])
def get_document_chunks(document_id):
    """
    Get chunks for a specific document
    """
    try:
        document = Document.query.get_or_404(document_id)
        chunks = document_processor.get_document_chunks(document_id)
        
        return jsonify({
            'document_id': document_id,
            'chunks': [chunk.to_dict() for chunk in chunks]
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting chunks for document {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to retrieve chunks: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete a document and its chunks
    """
    try:
        document = Document.query.get_or_404(document_id)
        
        # Delete from vector database
        vector_service.delete_document_chunks(document_id)
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to delete document: {str(e)}'}), 500

@document_bp.route('/stats', methods=['GET'])
def get_document_stats():
    """
    Get document processing statistics
    """
    try:
        total_docs = Document.query.count()
        processed_docs = Document.query.filter_by(processing_status='completed').count()
        failed_docs = Document.query.filter_by(processing_status='failed').count()
        pending_docs = Document.query.filter_by(processing_status='pending').count()
        processing_docs = Document.query.filter_by(processing_status='processing').count()
        
        total_chunks = sum(doc.total_chunks for doc in Document.query.filter_by(processing_status='completed').all())
        
        return jsonify({
            'total_documents': total_docs,
            'processed_documents': processed_docs,
            'failed_documents': failed_docs,
            'pending_documents': pending_docs,
            'processing_documents': processing_docs,
            'total_chunks': total_chunks
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        return jsonify({'error': f'Failed to retrieve stats: {str(e)}'}), 500