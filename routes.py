from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import logging
from models import Document, DocumentChunk, db
from document_processor import DocumentProcessor
from llm_service import LLMService
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Create blueprints
document_bp = Blueprint('documents', __name__)
query_bp = Blueprint('query', __name__)

# Initialize services
document_processor = DocumentProcessor()
llm_service = LLMService()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Check file size (100MB limit)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large'}), 400
        
        # Generate unique filename
        original_filename = file.filename
        filename = secure_filename(original_filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=os.path.splitext(filename)[1].lower(),
            processing_status='processing'
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Process document in background (in production, use Celery or similar)
        try:
            processing_result = document_processor.process_document(file_path, document.id)
            
            if processing_result['success']:
                document.processing_status = 'completed'
                document.chunk_count = processing_result['chunk_count']
                # Estimate page count (rough approximation)
                document.page_count = max(1, processing_result['chunk_count'] // 3)
            else:
                document.processing_status = 'failed'
                logger.error(f"Document processing failed: {processing_result.get('error')}")
            
            db.session.commit()
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': document.to_dict()
            }), 201
            
        except Exception as e:
            document.processing_status = 'failed'
            db.session.commit()
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': f'Error uploading document: {str(e)}'}), 500

@document_bp.route('/', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        documents = Document.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents.items],
            'total': documents.total,
            'pages': documents.pages,
            'current_page': page
        })
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': f'Error listing documents: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get specific document details"""
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify(document.to_dict())
    
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': f'Error getting document: {str(e)}'}), 500

@document_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and its chunks"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Delete from vector database
        document_processor.delete_document_chunks(document_id)
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'})
    
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500

@document_bp.route('/<int:document_id>/chunks', methods=['GET'])
def get_document_chunks(document_id):
    """Get chunks for a specific document"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        chunks = DocumentChunk.query.filter_by(document_id=document_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'chunks': [chunk.to_dict() for chunk in chunks.items],
            'total': chunks.total,
            'pages': chunks.pages,
            'current_page': page
        })
    
    except Exception as e:
        logger.error(f"Error getting chunks for document {document_id}: {str(e)}")
        return jsonify({'error': f'Error getting chunks: {str(e)}'}), 500

@query_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question using RAG pipeline"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        document_ids = data.get('document_ids', [])  # Optional: filter by specific documents
        max_results = data.get('max_results', 5)
        max_tokens = data.get('max_tokens', 1000)
        
        if not question.strip():
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Search for relevant chunks
        similar_chunks = document_processor.search_similar_chunks(
            question, 
            n_results=max_results,
            document_ids=document_ids if document_ids else None
        )
        
        if not similar_chunks:
            return jsonify({
                'answer': "I couldn't find any relevant information in the uploaded documents to answer your question.",
                'sources': [],
                'context_used': 0
            })
        
        # Generate response using LLM
        response = llm_service.generate_response(
            question, 
            similar_chunks, 
            max_tokens=max_tokens
        )
        
        if response['success']:
            return jsonify({
                'answer': response['response'],
                'sources': response['sources'],
                'context_used': response['context_used'],
                'question': question
            })
        else:
            return jsonify({
                'answer': response['response'],
                'error': response.get('error'),
                'sources': [],
                'context_used': 0
            }), 500
    
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': f'Error processing question: {str(e)}'}), 500

@query_bp.route('/search', methods=['POST'])
def search_documents():
    """Search for relevant chunks without generating a response"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        document_ids = data.get('document_ids', [])
        max_results = data.get('max_results', 10)
        
        # Search for similar chunks
        similar_chunks = document_processor.search_similar_chunks(
            query, 
            n_results=max_results,
            document_ids=document_ids if document_ids else None
        )
        
        return jsonify({
            'query': query,
            'results': similar_chunks,
            'total_results': len(similar_chunks)
        })
    
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return jsonify({'error': f'Error searching documents: {str(e)}'}), 500

@query_bp.route('/test-llm', methods=['GET'])
def test_llm():
    """Test LLM connection"""
    try:
        is_connected = llm_service.test_connection()
        
        return jsonify({
            'llm_connected': is_connected,
            'message': 'LLM connection test completed'
        })
    
    except Exception as e:
        logger.error(f"Error testing LLM: {str(e)}")
        return jsonify({
            'llm_connected': False,
            'error': str(e)
        }), 500