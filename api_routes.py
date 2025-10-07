import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import create_document, get_all_documents, get_document_by_id, update_document_status
from document_processor import DocumentProcessor
import json
from datetime import datetime

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get additional metadata
        metadata = request.form.get('metadata', '{}')
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = {}
        
        # Secure filename and save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # Create document record
        document = create_document(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            metadata=json.dumps(metadata_dict)
        )
        
        # Process document asynchronously (in a real app, use Celery or similar)
        try:
            processor = DocumentProcessor()
            result = processor.process_document(file_path, file_type, document.id)
            
            if result['success']:
                # Store chunks in vector database
                vector_store = current_app.vector_store
                chunks_added = vector_store.add_document_chunks(
                    document_id=document.id,
                    chunks=result['chunks'],
                    metadata={
                        'filename': filename,
                        'file_type': file_type,
                        'upload_date': document.upload_date.isoformat()
                    }
                )
                
                if chunks_added:
                    update_document_status(document.id, 'processed', len(result['chunks']))
                    document.metadata = json.dumps(result['metadata'])
                else:
                    update_document_status(document.id, 'error', 0)
            else:
                update_document_status(document.id, 'error', 0)
                document.metadata = json.dumps(result['metadata'])
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            update_document_status(document.id, 'error', 0)
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get all uploaded documents"""
    try:
        documents = get_all_documents()
        return jsonify({
            'documents': [doc.to_dict() for doc in documents],
            'count': len(documents)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': f'Failed to get documents: {str(e)}'}), 500

@api_bp.route('/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    try:
        document = get_document_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({'document': document.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to get document: {str(e)}'}), 500

@api_bp.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and its chunks"""
    try:
        document = get_document_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from vector store
        vector_store = current_app.vector_store
        vector_store.delete_document_chunks(document_id)
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        from database import db
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to delete document: {str(e)}'}), 500

@api_bp.route('/query', methods=['POST'])
def query_documents():
    """Query the RAG system"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        document_ids = data.get('document_ids')  # Optional: filter by specific documents
        max_chunks = data.get('max_chunks', 5)
        max_tokens = data.get('max_tokens', 1000)
        
        if not question.strip():
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Process query through RAG pipeline
        rag_pipeline = current_app.rag_pipeline
        result = rag_pipeline.query(
            question=question,
            document_ids=document_ids,
            max_chunks=max_chunks,
            max_tokens=max_tokens
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@api_bp.route('/documents/<int:document_id>/summary', methods=['GET'])
def get_document_summary(document_id):
    """Get a summary of a specific document"""
    try:
        document = get_document_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        rag_pipeline = current_app.rag_pipeline
        summary = rag_pipeline.get_document_summary(document_id)
        
        return jsonify(summary), 200 if summary['success'] else 500
        
    except Exception as e:
        logger.error(f"Error getting document summary {document_id}: {str(e)}")
        return jsonify({'error': f'Failed to get summary: {str(e)}'}), 500

@api_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        rag_pipeline = current_app.rag_pipeline
        stats = rag_pipeline.get_system_stats()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test vector store
        vector_stats = current_app.vector_store.get_collection_stats()
        
        # Test LLM connection
        llm_test = current_app.llm_client.test_connection()
        
        return jsonify({
            'status': 'healthy',
            'vector_store': 'operational' if 'error' not in vector_stats else 'error',
            'llm': 'operational' if llm_test['success'] else 'error',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500