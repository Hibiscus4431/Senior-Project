from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.auth import auth_bp
from app.textbook import textbook_bp
from app.courses import course_bp
from app.questions import question_bp
from app.qti_import import qti_bp
from app.testbanks import testbank_bp
from app.feedback import feedback_bp
from app.resource_page import resources_bp
from app.tests import tests_bp
from app.downloads import downloads_bp


def create_app():
    app = Flask(__name__)
    
    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

    # Initialize Supabase client for authentication
    app.supabase = Config.get_supabase_client()

    # Initialize PostgreSQL connection for storing user data
    app.db_connection = Config.get_db_connection()

    # Import and register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(textbook_bp, url_prefix="/textbooks")
    app.register_blueprint(course_bp, url_prefix="/courses")
    app.register_blueprint(question_bp, url_prefix="/questions")
    app.register_blueprint(qti_bp, url_prefix="/qti")
    app.register_blueprint(testbank_bp, url_prefix="/testbanks")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")
    app.register_blueprint(resources_bp, url_prefix="/resources")
    app.register_blueprint(tests_bp, url_prefix="/tests")
    app.register_blueprint(downloads_bp, url_prefix="/download")
    return app
