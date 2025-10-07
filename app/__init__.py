from flask import Flask
from flask_cors import CORS
from app.config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VECTOR_DB_PATH'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE_URL'].replace('sqlite:///', '')), exist_ok=True)
    
    # Initialize database
    from app.models import init_db
    init_db()
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app