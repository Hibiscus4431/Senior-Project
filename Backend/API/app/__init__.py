from flask import Flask
from app.config import Config
from app.auth import auth_bp

def create_app():
    app = Flask(__name__)

   # ✅ Initialize Supabase client for authentication
    app.supabase = Config.get_supabase_client()

    # ✅ Initialize PostgreSQL connection for storing user data
    app.db_connection = Config.get_db_connection()

    
    # Import and register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    return app
