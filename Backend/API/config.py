import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

class Config:
    SUPABASE_URL = SUPABASE_URL
    SUPABASE_KEY = SUPABASE_KEY
