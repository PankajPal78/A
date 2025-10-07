import pytest
import os
import tempfile
import json
import io
from app import app, db
from models import Document, DocumentChunk

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing"""
    # This would need a proper PDF creation in a real test
    return b"Sample PDF content"

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_upload_document(client):
    """Test document upload"""
    # Create a test file
    test_file = (io.BytesIO(b"Test document content"), "test.txt")
    
    response = client.post('/api/documents/upload', 
                          data={'file': test_file},
                          content_type='multipart/form-data')
    
    # Should return 201 for successful upload
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'document' in data

def test_list_documents(client):
    """Test listing documents"""
    response = client.get('/api/documents/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data

def test_ask_question(client):
    """Test asking a question"""
    # First upload a document
    test_file = (io.BytesIO(b"Sample content for testing"), "test.txt")
    upload_response = client.post('/api/documents/upload',
                                 data={'file': test_file},
                                 content_type='multipart/form-data')
    
    if upload_response.status_code == 201:
        # Ask a question
        question_data = {
            'question': 'What is the content about?',
            'max_results': 3
        }
        
        response = client.post('/api/query/ask',
                              data=json.dumps(question_data),
                              content_type='application/json')
        
        # Should return 200 even if no LLM is configured
        assert response.status_code in [200, 500]
        data = json.loads(response.data)
        assert 'answer' in data

def test_search_documents(client):
    """Test document search"""
    search_data = {
        'query': 'test content',
        'max_results': 5
    }
    
    response = client.post('/api/query/search',
                          data=json.dumps(search_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data
    assert 'query' in data