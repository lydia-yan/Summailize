from flask import Flask
from flask_cors import CORS
from app.api.routes import api

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS, allow all domains and Chrome extension
    CORS(app, resources={r"/api/*": {"origins": ["*", "chrome-extension://bgfhhdhlljldlnmjfpndoeglimej"]}})
    
    # Register API blueprint
    app.register_blueprint(api)
    
    # Define root route for testing service
    @app.route('/')
    def index():
        return "Email summary API service is running!"
    
    return app
