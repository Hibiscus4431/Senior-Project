## This script reads and applies the migration files to your local PostgreSQL test database.
import psycopg2
import os 
from dotenv import load_dotenv

# Load environment variables from .env.test
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))

# Test Statements to verify the environment variables are loaded correctly
print("DB HOST:", os.getenv("LOCAL_DB_HOST"))
print("DB PORT:", os.getenv("LOCAL_DB_PORT")) 
print("DB NAME:", os.getenv("LOCAL_DB_NAME"))
print("DB USER:", os.getenv("LOCAL_DB_USER"))

# Construct the local database URL
DATABASE_URL = f"postgresql://{os.getenv('LOCAL_DB_USER')}:{os.getenv('LOCAL_DB_PASSWORD')}@{os.getenv('LOCAL_DB_HOST')}:{os.getenv('LOCAL_DB_PORT')}/{os.getenv('LOCAL_DB_NAME')}"

def apply_migrations():
    try:
        # Connect to the local test database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Get script's location and point to the test migrations folder
        script_dir = os.path.dirname(os.path.abspath(__file__))  
        migration_folder = os.path.join(script_dir, "Test_Schema")  

        if not os.path.exists(migration_folder):
            print ("No test_migrations folder found! Fix this issue before running.")
            return
        
        # Sorting and applying the migration files in order
        migration_files = sorted(os.listdir(migration_folder))

        for file in migration_files:
            if file.endswith(".sql"):
                file_path = os.path.join(migration_folder, file)
                print(f"Applying migration: {file}")

                with open(file_path, "r") as f:
                    sql = f.read()
                    cur.execute(sql)

                # Commit the changes 
                conn.commit()

        print("✅ All test migrations applied successfully.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error applying test migrations: {e}")

if __name__ == "__main__":
    apply_migrations()
