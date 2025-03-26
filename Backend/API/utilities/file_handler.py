import os, zipfile
from app.config import Config
def extract_qti_zip_from_supabase(file_path, import_id):
    supabase = Config.get_supabase_client()
    bucket, key = file_path.split("/", 1)
    
    # Download ZIP from Supabase
    response = supabase.storage.from_(bucket).download(key)
    
    # Save ZIP locally
    local_dir = f"./qti_uploads/import_{import_id}"
    os.makedirs(local_dir, exist_ok=True)
    zip_path = os.path.join(local_dir, "import.zip")

    with open(zip_path, "wb") as f:
        f.write(response)

    # Extract contents
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(local_dir)

    os.remove(zip_path)
    return local_dir
