## This script reads and applies the migration files to your MySQL database hosted on AWS.
import psycopg2
import os 
#from dotenv import load_dotenv

#load_dotenv()
#DATABASE_URL = f"postgresql://{os.getenv('SUPABASE_DB_USER')}:{os.getenv('SUPABASE_DB_PASSWORD')}@{os.getenv('SUPABASE_DB_HOST')}:{os.getenv('SUPABASE_DB_PORT')}/{os.getenv('SUPABASE_DB_NAME')}"
DATABASE_URL = "postgresql://postgres:V3k2WEXmk3kCI4Nn@db.kxhdlyrkvnpqvosxjdus.supabase.co:5432/postgres"

def apply_migrations():
    try:
        # connecting to Supabase Database 
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        #folder containg the migrations files 
        migration_folder = "Migrations"
        if not os.path.exists(migration_folder):
            print ("No migrations folder found. Got to fix this issue!")
            return
        # sorting and appling the migrations files in order 
        migration_files = sorted(os.listdir(migration_folder))

        for file in migration_files:
            if file.endswith(".sql"):
                file_path = os.path.join(migration_folder,file)
                print(f"Applying migrations: {file}")

                with open (file_path, "r") as f:
                    sql = f.read()
                    cur.execute(sql)

                # commit the changes 
                conn.commit()
        print ("All migrations applied successfully.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error applying migrations: {e}")

if __name__ == "__main__":
    apply_migrations()
