import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check if the connection is working
if not supabase:
    raise Exception("Failed to connect to Supabase")

# testing connections (checkking all users )
response = supabase.table("users").select("*").execute()
print(response.data)


