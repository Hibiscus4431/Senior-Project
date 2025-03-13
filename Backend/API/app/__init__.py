from flask import Flask
from app.config import Config
from app.auth import auth_bp
from app.textbook import textbook_bp
from app.courses import course_bp
from app.questions import question_bp

def create_app():
    app = Flask(__name__)

   # ✅ Initialize Supabase client for authentication
    app.supabase = Config.get_supabase_client()

    # ✅ Initialize PostgreSQL connection for storing user data
    app.db_connection = Config.get_db_connection()

    
    # Import and register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(textbook_bp, url_prefix="/textbooks")
    app.register_blueprint(course_bp, url_prefix="/courses")
    app.register_blueprint(question_bp, url_prefix="/questions")
    
    return app
