from flask import Flask
from supabase import create_client
import os

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object("config")

    # Initialize Supabase client once
    supabase_url = app.config["SUPABASE_URL"]
    supabase_key = app.config["SUPABASE_KEY"]
    app.supabase = create_client(supabase_url, supabase_key)

    # Check if the connection is working
    if not app.supabase:
        raise Exception("Failed to connect to Supabase")

    # Register blueprints (API routes)
    from app.routes import api_bp
    from app.auth import auth_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    return app
