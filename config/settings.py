"""
Configuration settings for the RAG application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Upload settings
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'data' / 'uploads'))
MAX_DOCUMENTS = int(os.getenv('MAX_DOCUMENTS', '20'))
MAX_PAGES_PER_DOCUMENT = int(os.getenv('MAX_PAGES_PER_DOCUMENT', '1000'))
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Vector database settings
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', str(BASE_DIR / 'data' / 'vector_db'))
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))

# LLM settings
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1000'))

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/metadata/documents.db')

# Retrieval settings
TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))

# API settings
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_URL.replace('sqlite:///', '')), exist_ok=True)