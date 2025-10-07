#!/usr/bin/env python3
"""
RAG Document Q&A System
Main Flask application entry point
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///rag_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from models.document import db
db.init_app(app)

# Import routes after app initialization to avoid circular imports
from routes import document_routes, query_routes, health_routes

# Register blueprints
app.register_blueprint(document_routes.bp)
app.register_blueprint(query_routes.bp)
app.register_blueprint(health_routes.bp)

# Setup logging
from utils.helpers import setup_logging, validate_environment
setup_logging(os.getenv('LOG_LEVEL', 'INFO'))

# Create database tables
with app.app_context():
    db.create_all()
    
    # Validate environment
    validation = validate_environment()
    if not validation['valid']:
        print("Environment validation failed:")
        for issue in validation['issues']:
            print(f"  ERROR: {issue}")
    
    if validation['warnings']:
        print("Environment warnings:")
        for warning in validation['warnings']:
            print(f"  WARNING: {warning}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)