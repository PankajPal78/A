import pytest
import json
import tempfile
import os
import io
from unittest.mock import patch, MagicMock
from app import app, db
from models.document import Document

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def sample_document():
    """Create a sample document for testing"""
    doc = Document(
        filename='test.pdf',
        original_filename='test.pdf',
        file_path='/tmp/test.pdf',
        file_size=1024,
        file_type='pdf',
        processing_status='completed',
        total_pages=5,
        total_chunks=10
    )
    return doc

class TestDocumentRoutes:
    
    def test_upload_document_success(self, client):
        """Test successful document upload"""
        with patch('routes.document_routes.document_processor') as mock_processor:
            with patch('routes.document_routes.vector_service') as mock_vector:
                # Mock successful processing
                mock_processor.process_document.return_value = True
                mock_processor.get_document_chunks.return_value = []
                mock_vector.add_document_chunks.return_value = True
                
                # Create a test file
                test_file = (io.BytesIO(b"fake pdf content"), 'test.pdf')
                
                response = client.post('/api/documents/upload', 
                                    data={'file': test_file},
                                    content_type='multipart/form-data')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                assert 'message' in data
                assert 'document' in data
                assert data['document']['original_filename'] == 'test.pdf'
    
    def test_upload_document_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/documents/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_document_invalid_type(self, client):
        """Test upload with invalid file type"""
        test_file = (io.BytesIO(b"content"), 'test.txt')
        
        response = client.post('/api/documents/upload',
                            data={'file': test_file},
                            content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'File type not supported' in data['error']
    
    def test_get_documents(self, client, sample_document):
        """Test getting list of documents"""
        with app.app_context():
            db.session.add(sample_document)
            db.session.commit()
        
        response = client.get('/api/documents/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'documents' in data
        assert 'pagination' in data
        assert len(data['documents']) == 1
    
    def test_get_document_by_id(self, client, sample_document):
        """Test getting specific document"""
        with app.app_context():
            db.session.add(sample_document)
            db.session.commit()
        
        response = client.get(f'/api/documents/{sample_document.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['document']['id'] == sample_document.id
        assert data['document']['filename'] == sample_document.filename
    
    def test_get_document_not_found(self, client):
        """Test getting non-existent document"""
        response = client.get('/api/documents/999')
        assert response.status_code == 404
    
    def test_get_document_chunks(self, client, sample_document):
        """Test getting document chunks"""
        with patch('routes.document_routes.document_processor') as mock_processor:
            mock_chunks = [
                MagicMock(to_dict=lambda: {'id': 1, 'content': 'chunk 1'}),
                MagicMock(to_dict=lambda: {'id': 2, 'content': 'chunk 2'})
            ]
            mock_processor.get_document_chunks.return_value = mock_chunks
            
            with app.app_context():
                db.session.add(sample_document)
                db.session.commit()
            
            response = client.get(f'/api/documents/{sample_document.id}/chunks')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'chunks' in data
            assert len(data['chunks']) == 2
    
    def test_delete_document(self, client, sample_document):
        """Test deleting document"""
        with patch('routes.document_routes.vector_service') as mock_vector:
            with patch('os.path.exists') as mock_exists:
                with patch('os.remove') as mock_remove:
                    mock_vector.delete_document_chunks.return_value = True
                    mock_exists.return_value = True
                    
                    with app.app_context():
                        db.session.add(sample_document)
                        db.session.commit()
                    
                    response = client.delete(f'/api/documents/{sample_document.id}')
                    assert response.status_code == 200
                    
                    data = json.loads(response.data)
                    assert 'message' in data
                    assert 'deleted successfully' in data['message']
    
    def test_get_document_stats(self, client):
        """Test getting document statistics"""
        with app.app_context():
            # Add some test documents
            doc1 = Document(filename='doc1.pdf', original_filename='doc1.pdf',
                          file_path='/tmp/doc1.pdf', file_size=1024, file_type='pdf',
                          processing_status='completed', total_chunks=5)
            doc2 = Document(filename='doc2.pdf', original_filename='doc2.pdf',
                          file_path='/tmp/doc2.pdf', file_size=2048, file_type='pdf',
                          processing_status='failed', total_chunks=0)
            db.session.add_all([doc1, doc2])
            db.session.commit()
        
        response = client.get('/api/documents/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_documents'] == 2
        assert data['processed_documents'] == 1
        assert data['failed_documents'] == 1

class TestQueryRoutes:
    
    def test_ask_question_success(self, client):
        """Test successful question asking"""
        with patch('routes.query_routes.rag_service') as mock_rag:
            mock_response = {
                'response': 'Machine learning is a subset of AI.',
                'metadata': {'context_chunks_used': 2},
                'context_chunks': []
            }
            mock_rag.process_query.return_value = mock_response
            
            response = client.post('/api/query/ask',
                                json={'query': 'What is machine learning?'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] == 'Machine learning is a subset of AI.'
    
    def test_ask_question_no_query(self, client):
        """Test asking question without query"""
        response = client.post('/api/query/ask', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Query is required' in data['error']
    
    def test_ask_question_empty_query(self, client):
        """Test asking question with empty query"""
        response = client.post('/api/query/ask', json={'query': ''})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Query cannot be empty' in data['error']
    
    def test_ask_question_with_parameters(self, client):
        """Test asking question with additional parameters"""
        with patch('routes.query_routes.rag_service') as mock_rag:
            mock_rag.process_query.return_value = {'response': 'Test response', 'metadata': {}, 'context_chunks': []}
            
            response = client.post('/api/query/ask',
                                json={
                                    'query': 'Test query',
                                    'document_ids': [1, 2],
                                    'max_chunks': 3,
                                    'max_tokens': 500
                                })
            
            assert response.status_code == 200
            mock_rag.process_query.assert_called_once_with(
                query='Test query',
                document_ids=[1, 2],
                max_chunks=3,
                max_tokens=500
            )
    
    def test_search_documents(self, client):
        """Test document search"""
        with patch('routes.query_routes.vector_service') as mock_vector:
            mock_results = [
                {'content': 'Test content 1', 'metadata': {}},
                {'content': 'Test content 2', 'metadata': {}}
            ]
            mock_vector.search_similar_chunks.return_value = mock_results
            
            response = client.post('/api/query/search',
                                json={'query': 'test search'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['results']) == 2
            assert data['total_results'] == 2
    
    def test_get_available_documents(self, client):
        """Test getting available documents"""
        with patch('routes.query_routes.rag_service') as mock_rag:
            mock_docs = [{'id': 1, 'filename': 'doc1.pdf'}]
            mock_rag.get_available_documents.return_value = mock_docs
            
            response = client.get('/api/query/available-documents')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data['documents']) == 1
            assert data['documents'][0]['filename'] == 'doc1.pdf'
    
    def test_get_system_stats(self, client):
        """Test getting system statistics"""
        with patch('routes.query_routes.rag_service') as mock_rag:
            mock_stats = {
                'documents': {'total': 5, 'processed': 4, 'failed': 1},
                'vector_database': {'total_chunks': 20}
            }
            mock_rag.get_document_stats.return_value = mock_stats
            
            response = client.get('/api/query/stats')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['documents']['total'] == 5
            assert data['vector_database']['total_chunks'] == 20
    
    def test_test_llm_connection(self, client):
        """Test LLM connection test"""
        with patch('routes.query_routes.llm_service') as mock_llm:
            mock_llm.test_connection.return_value = True
            
            response = client.post('/api/query/test-llm')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'connected'

class TestHealthRoutes:
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get('/api/health/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'RAG API'
    
    def test_detailed_health_check(self, client):
        """Test detailed health check"""
        with patch('routes.health_routes.VectorService') as mock_vector_class:
            with patch('routes.health_routes.LLMService') as mock_llm_class:
                with patch('routes.health_routes.db') as mock_db:
                    # Mock all services as healthy
                    mock_vector = MagicMock()
                    mock_vector.get_collection_stats.return_value = {'total_chunks': 10}
                    mock_vector_class.return_value = mock_vector
                    
                    mock_llm = MagicMock()
                    mock_llm.test_connection.return_value = True
                    mock_llm_class.return_value = mock_llm
                    
                    mock_db.session.execute.return_value = None
                    
                    response = client.get('/api/health/detailed')
                    assert response.status_code == 200
                    
                    data = json.loads(response.data)
                    assert data['status'] == 'healthy'
                    assert 'components' in data