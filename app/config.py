import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './data/uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
    MAX_DOCUMENTS = 20
    MAX_PAGES_PER_DOCUMENT = 1000
    
    # Vector Database
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './data/vectordb')
    COLLECTION_NAME = 'documents'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/documents.db')
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    
    # Retrieval Configuration
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 5))