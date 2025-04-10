from flask import Blueprint, request, jsonify
from app.config import Config
from .auth import authorize_request
from psycopg2 import sql
from werkzeug.utils import secure_filename
from datetime import datetime
tests_bp = Blueprint('tests', __name__)


######### Finaliing Test Section ##########
"""
The Goal of this route is to finalize a test by:
1. Checking if the test bank exists.
2. Fetching all question_ids from the test bank.
3. Inserting a new test into the tests table.
4. Inserting the question_ids into the test_metadata table.
5. Returning the test_id and the number of questions added.
6. Updating the points_total in the tests table.
7. Returning a success message.
8. Handling errors and rolling back transactions if necessary.
(This route still keeps all question not published so they can be edited)
"""
@tests_bp.route('/finalize', methods=['POST']) #Tested Worked 
def finalize_test():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    data = request.get_json()
    test_bank_id = data.get("test_bank_id")
    name = data.get("name")
    estimated_time = data.get("estimated_time")
    test_instructions = data.get("test_instructions")
    template_id = data.get("template_id")  # can be None
    course_id = data.get("course_id")

    if not test_bank_id or not name or not course_id:
        return jsonify({"error": "Missing required fields: test_bank_id, name, or course_id"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Confirm test bank exists
        cursor.execute("SELECT testbank_id FROM test_bank WHERE testbank_id = %s", (test_bank_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Test bank not found"}), 404

        # Step 2: Fetch questions with default points
        cursor.execute("""
            SELECT q.id, COALESCE(q.default_points, 0)
            FROM test_bank_questions tbq
            JOIN questions q ON tbq.question_id = q.id
            WHERE tbq.test_bank_id = %s
        """, (test_bank_id,))
        questions = cursor.fetchall()  # list of (question_id, default_points)

        if not questions:
            return jsonify({"error": "No questions found in test bank"}), 400

        # Step 3: Insert new test
        cursor.execute("""
            INSERT INTO tests (name, course_id, template_id, user_id, status, estimated_time, test_instrucutions)
            VALUES (%s, %s, %s, %s, 'Final', %s, %s)
            RETURNING tests_id;
        """, (
            name, course_id, template_id, auth_data["user_id"], estimated_time, test_instructions
        ))
        test_id = cursor.fetchone()[0]

        # Step 4: Insert questions into test_metadata with point values
        for question_id, default_points in questions:
            cursor.execute("""
                INSERT INTO test_metadata (test_id, question_id, points)
                VALUES (%s, %s, %s)
            """, (test_id, question_id, default_points))

        # Step 5: Update points_total in the tests table
        cursor.execute("""
            UPDATE tests
            SET points_total = (
            SELECT SUM(points) FROM test_metadata WHERE test_id = %s
            )
            WHERE tests_id = %s
        """, (test_id, test_id))

        conn.commit()

        return jsonify({
            "message": "Test finalized successfully",
            "test_id": test_id,
            "question_count": len(questions)
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


"""
The Goal of this route is to upload attachments to a test by:
1. Checking if the test exists.
2. Uploading the files to Supabase Storage.
3. Inserting the attachment metadata into the database.
4. Returning the attachment_id and file_path for each uploaded file.
"""
@tests_bp.route('/<int:test_id>/upload_attachment', methods=['POST'])
def upload_attachments_to_test(test_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    files = request.files.getlist('file')

    if not files or len(files) == 0:
        return jsonify({"error": "No files found in request"}), 400

    supabase = Config.get_supabase_client()
    conn = Config.get_db_connection()
    cur = conn.cursor()

    uploaded = []

    for file in files:
        if file.filename == '':
            continue

        original_filename = secure_filename(file.filename)
        file_bytes = file.read()
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{user_id}_{timestamp}_{original_filename}"
        supabase_path = f"attachments/{unique_filename}"

        try:
            supabase.storage.from_(Config.ATTACHMENT_BUCKET).upload(
                path=supabase_path,
                file=file_bytes,
                file_options={"content-type": file.content_type}
            )

            cur.execute("""
                INSERT INTO attachments (name, filepath)
                VALUES (%s, %s)
                RETURNING attachments_id;
            """, (original_filename, supabase_path))
            attachment_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO attachments_metadata (attachment_id, reference_type, reference_id)
                VALUES (%s, 'test', %s);
            """, (attachment_id, test_id))

            uploaded.append({
                "attachment_id": attachment_id,
                "file_name": original_filename,
                "file_path": supabase_path
            })

        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"error": f"Upload failed: {str(e)}"}), 500

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "All attachments uploaded successfully",
        "uploaded": uploaded
    }), 201


"""
The Goal of this route is to upload a final PDF for a test by:
1. Checking if the test exists.
2. Uploading the PDF to Supabase Storage.
3. Updating the filename column in the tests table.
4. Returning the file_path of the uploaded PDF.
"""
@tests_bp.route('/<int:test_id>/upload_pdf', methods=['POST']) #Tested Worked 
def upload_final_pdf(test_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if 'file' not in request.files:
        return jsonify({"error": "Missing PDF file"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Clean and build unique filename
    original_filename = secure_filename(file.filename)
    file_bytes = file.read()
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{test_id}_{timestamp}_{original_filename}"
    supabase_path = f"final/{unique_filename}"  # Folder 'final' inside 'Tests' bucket

    try:
        # Upload to Supabase Storage
        supabase = Config.get_supabase_client()
        supabase.storage.from_("Tests").upload(
            path=supabase_path,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        return jsonify({"error": f"Supabase upload failed: {str(e)}"}), 500

    # Update the filename column in tests table
    conn = Config.get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE tests
            SET filename = %s
            WHERE tests_id = %s
        """, (supabase_path, test_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database update failed: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({
        "message": "Test PDF uploaded successfully",
        "file_path": supabase_path
    }), 201



################################### Puplishing Test Section ###################################