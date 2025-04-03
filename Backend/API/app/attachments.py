import os
import time
from flask import Blueprint, request, jsonify
from .auth import authorize_request
from psycopg2 import sql
from app.config import Config   
from werkzeug.utils import secure_filename

attachments_bp = Blueprint("attachments", __name__)

# Create/adding a new attachment to the database
@attachments_bp.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    if 'attachment' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['attachment']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    original_filename = secure_filename(file.filename)
    timestamp = int(time.time())
    unique_filename = f"{user_id}_{timestamp}_{original_filename}"
    filepath = f"{unique_filename}"

    # Upload file to Supabase Storage
    try:
        supabase = Config.get_supabase_client()
        file_bytes = file.read()
        supabase.storage.from_(Config.ATTACHMENT_BUCKET).upload(
            path=filepath,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        return jsonify({"error": f"Upload to Supabase failed: {str(e)}"}), 500

    # Save file metadata to Attachments table
    try:
        conn = Config.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Attachments (name, filepath)
            VALUES (%s, %s)
            RETURNING attachments_id;
        """, (original_filename, filepath))
        attachment_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": f"Database insert failed: {str(e)}"}), 500

    return jsonify({
        "message": "Attachment uploaded successfully.",
        "attachment_id": attachment_id,
        "filename": original_filename,
        "filepath": filepath
    }), 201

# For the sake of the example, we will not implement the rest of the CRUD operations for Attachments.
# Also for the attachment it will only be like with the questions not attachment choices