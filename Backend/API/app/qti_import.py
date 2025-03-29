# This is where the QTI import functionality is implemented.
from flask import Blueprint, request, jsonify, current_app
from .auth import authorize_request
from app.config import Config
from werkzeug.utils import secure_filename
from datetime import datetime
from utilities.qti_parser import parse_qti_file_patched
from utilities.file_handler import extract_qti_zip_from_supabase
from io import BytesIO
import os
import shutil

qti_bp = Blueprint('qti', __name__)

# PHASE 1.A - Upload QTI file to Supabase Storage
@qti_bp.route('/upload', methods=['POST'])
def upload_qti_file():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_bytes = BytesIO(file.read())
    # Create a unique file path using user ID and timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    file_path = f"{user_id}/import_{timestamp}_{filename}"

    try:
        supabase = Config.get_supabase_client()

        # Upload to Supabase Storage
        supabase.storage.from_(Config.QTI_BUCKET).upload(
            path=file_path,
            file=file_bytes.read(),
            file_options={"content-type": "application/zip"}
        )

        return jsonify({
            'message': 'File uploaded successfully',
            'file_path': f"{Config.QTI_BUCKET}/{file_path}"
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PHASE 1.B - Create QTI_Imports record (no test_id)
@qti_bp.route('/import', methods=['POST'])
def create_qti_import():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")

    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'Missing file_path'}), 400

    conn = current_app.db_connection
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO QTI_Imports (file_path, status, owner_id)
            VALUES (%s, 'pending', %s)
            RETURNING import_id;
        """, (file_path, user_id))

        import_id = cursor.fetchone()[0]
        conn.commit()

        # Extract ZIP file from Supabase and update file_path to extracted folder
        extract_qti_zip_from_supabase(file_path, import_id)

        return jsonify({
            'message': 'QTI import recorded successfully',
            'import_id': import_id,
            'status': 'pending'
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# PHASE 2 - Process QTI import (this is for testing this route is not meant to be implemented in the frontend)
@qti_bp.route('/parse/<int:import_id>', methods=['GET'])
def parse_qti_import(import_id):
    # Authenticate user
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")

    # Connect to DB
    conn = current_app.db_connection
    cursor = conn.cursor()

    try:
        # Look up the import record for this user
        cursor.execute("""
            SELECT file_path FROM QTI_Imports
            WHERE import_id = %s AND owner_id = %s
        """, (import_id, user_id))

        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Import not found or unauthorized."}), 404

        file_path = result[0]
        #local_file_path = f"./{file_path}/imsmanifest.xml"  # Adjust pathing if needed
        inner_dir = next(os.scandir(file_path)).path
        local_file_path = os.path.join(inner_dir, "imsmanifest.xml")

        # Run the parser
        parsed_data = parse_qti_file_patched(local_file_path)

        shutil.rmtree(file_path, ignore_errors=True)
        return jsonify({
            "import_id": import_id,
            "quiz_title": parsed_data["quiz_title"],
            "time_limit": parsed_data["time_limit"],
            "questions": parsed_data["questions"]
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# PHASE 3 - Save QTI questions to DB
@qti_bp.route('/save/<int:import_id>', methods=['POST'])
def save_qti_questions(import_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    data = request.get_json()
    course_id = data.get("course_id")  # Optional from frontend

    try:
        # DB connection
        conn = Config.get_db_connection()
        cursor = conn.cursor()

        # Get file path for the import
        cursor.execute("""
            SELECT file_path FROM QTI_Imports
            WHERE import_id = %s AND owner_id = %s
        """, (import_id, user_id))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Import not found or unauthorized"}), 404

        # Supabase file path (zip)
        original_supabase_path = result[0].strip()

        # Local extraction path (will contain the folder after unzipping)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        unzipped_folder_path = os.path.join(BASE_DIR, f"qti-uploads/import_{import_id}")
        
        # Re-extract if missing
        if not os.path.exists(unzipped_folder_path):
            print("🛠️ Folder not found locally. Re-extracting from Supabase...")
            unzipped_folder_path = extract_qti_zip_from_supabase(original_supabase_path, import_id)

        
        # Get the inner folder (e.g., group-4-project-quiz-export-3)
        try:
            inner_dir = next(os.scandir(unzipped_folder_path)).path
        except StopIteration:
            return jsonify({"error": "Extracted folder is empty!"}), 500
        
        manifest_path = os.path.join(inner_dir, "imsmanifest.xml")


        # Parse file
        parsed = parse_qti_file_patched(manifest_path)
        quiz_title = parsed["quiz_title"]
        questions = parsed["questions"]

        # ✅ Create test bank
        cursor.execute("""
            INSERT INTO test_bank (owner_id, name, course_id)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (user_id, quiz_title, course_id))
        test_bank_id = cursor.fetchone()[0]

        inserted = []

        for q in questions:
            # Insert into Questions table
            cursor.execute("""
                INSERT INTO Questions (question_text, type, default_points, source, true_false_answer, owner_id, course_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                q["question_text"],
                q["type"],
                q.get("default_points", 1),
                q.get("source", "canvas_qti"),
                q.get("true_false_answer"),
                user_id,
                course_id
            ))

            question_id = cursor.fetchone()[0]

            # ✅ Link to test bank
            cursor.execute("""
                INSERT INTO test_bank_questions (test_bank_id, question_id)
                VALUES (%s, %s)
            """, (test_bank_id, question_id))


            # Save multiple choice options
            if q["type"] == "Multiple Choice":
                for opt in q.get("choices", []):
                    cursor.execute("""
                        INSERT INTO QuestionOptions (question_id, option_text, is_correct)
                        VALUES (%s, %s, %s)
                    """, (question_id, opt.get("option_text", ""), opt.get("is_correct", False)))

            # Save fill-in-the-blank answers
            elif q["type"] == "Fill in the Blank":
                for blank in q.get("blanks", []):
                    cursor.execute("""
                        INSERT INTO QuestionFillBlanks (question_id, correct_text)
                        VALUES (%s, %s)
                    """, (question_id, blank.get("correct_text", "")))
    

            # Save matching options
            elif q["type"] == "Matching":
                for match in q.get("matches", []):
                    cursor.execute("""
                        INSERT INTO QuestionMatches (question_id, prompt_text, match_text)
                        VALUES (%s, %s, %s)
                    """, (
                        question_id,
                        match.get("prompt_text", ""),
                        match.get("match_text", "")
                    ))

            inserted.append(question_id)

        # ✅ Mark import as processed
        cursor.execute("""
            UPDATE QTI_Imports
            SET status = 'processed'
            WHERE import_id = %s
        """, (import_id,))

        conn.commit()

        return jsonify({
            "message": f"{len(inserted)} questions saved and linkes to test bank '{quiz_title}' successfully.",
            "test_bank_id": test_bank_id,
            "question_ids": inserted
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

