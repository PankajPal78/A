import pytest
import json
import io

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_list_documents_empty(client):
    """Test listing documents when empty"""
    response = client.get('/api/documents')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data
    assert data['total'] == 0

def test_upload_no_file(client):
    """Test upload without file"""
    response = client.post('/api/upload')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_upload_empty_filename(client):
    """Test upload with empty filename"""
    data = {'file': (io.BytesIO(b''), '')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

def test_query_no_question(client):
    """Test query without question"""
    response = client.post('/api/query', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_query_with_question_no_documents(client):
    """Test query when no documents uploaded"""
    response = client.post('/api/query', json={'question': 'What is RAG?'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'answer' in data

def test_get_stats(client):
    """Test getting system statistics"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data
    assert 'vector_store' in data
    assert 'limits' in data

def test_get_nonexistent_document(client):
    """Test getting a document that doesn't exist"""
    response = client.get('/api/documents/999')
    assert response.status_code == 404

def test_delete_nonexistent_document(client):
    """Test deleting a document that doesn't exist"""
    response = client.delete('/api/documents/999')
    assert response.status_code == 404