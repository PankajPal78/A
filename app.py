"""
Main application entry point
"""
from app import create_app
from config.settings import API_HOST, API_PORT, DEBUG

app = create_app()

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)