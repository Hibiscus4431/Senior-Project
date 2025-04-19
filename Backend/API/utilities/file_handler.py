import os
import zipfile
import requests
from io import BytesIO
from config import Config

def extract_qti_zip_from_supabase(supabase_path: str, import_id: int) -> str:
    supabase = Config.get_supabase_client()

    # Split the stored path into bucket + key
    bucket, key = supabase_path.split("/", 1)

    # Create a signed URL (expires in 60 seconds)
    signed = supabase.storage.from_(bucket).create_signed_url(
        path=key,
        expires_in=60
    )
    signed_url = signed.get("signedURL")

    if not signed_url:
        raise Exception("Failed to generate signed URL from Supabase.")

    # Download the zip file using the signed URL
    response = requests.get(signed_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download zip file. Status: {response.status_code}")

    zip_data = BytesIO(response.content)

    # Prepare local extraction path
    base_extract_path = os.path.join("qti-uploads", f"import_{import_id}")
    os.makedirs(base_extract_path, exist_ok=True)

    # Extract ZIP contents to local path
    with zipfile.ZipFile(zip_data, "r") as zip_ref:
        zip_ref.extractall(base_extract_path)

    return base_extract_path
