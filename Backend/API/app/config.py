import os
from dotenv import load_dotenv
from supabase import create_client
# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

 # Initialize Supabase client once (singleton pattern)
SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)

class Config:
    SUPABASE_URL = SUPABASE_URL
    SUPABASE_KEY = SUPABASE_KEY

    #Supabase Storage bucket name 
    QTI_BUCKET = "qti-uploads"
    ATTACHMENT_BUCKET = "attachments"
# PostgreSQL database credentials
    DB_HOST = os.getenv("SUPABASE_DB_HOST")
    DB_NAME = os.getenv("SUPABASE_DB_NAME")
    DB_USER = os.getenv("SUPABASE_DB_USER")
    DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    
    @staticmethod
    def get_supabase_client():
        """Returns a Supabase client."""
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("Supabase credentials are missing!")
        return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        
    @staticmethod
    def get_db_connection():
        """Returns a new database connection (psycopg2)."""
        import psycopg2
        return psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )