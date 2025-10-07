"""
Test configuration and fixtures
"""

import os
import pytest
import tempfile
import shutil
from app import app
from models.document import db
from config.settings import TestingConfig

@pytest.fixture
def client():
    """Create test client"""
    app.config.from_object(TestingConfig)
    
    # Create temporary directories for testing
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['CHROMA_PERSIST_DIRECTORY'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
    
    # Cleanup temporary directories
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    shutil.rmtree(app.config['CHROMA_PERSIST_DIRECTORY'], ignore_errors=True)

@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing"""
    content = """
    This is a sample document for testing the RAG system.
    
    The document contains multiple paragraphs with different topics.
    
    First topic: Machine Learning
    Machine learning is a subset of artificial intelligence that focuses on algorithms
    that can learn and make decisions from data without being explicitly programmed.
    
    Second topic: Natural Language Processing
    Natural language processing (NLP) is a field of AI that focuses on the interaction
    between computers and human language. It involves teaching computers to understand,
    interpret, and generate human language.
    
    Third topic: Vector Databases
    Vector databases are specialized databases designed to store and query high-dimensional
    vectors efficiently. They are commonly used in machine learning applications for
    similarity search and recommendation systems.
    """
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    # For simplicity, we'll create a text file with .pdf extension
    # In a real scenario, you'd create an actual PDF
    content = "This is a sample PDF document for testing."
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)