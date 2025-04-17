import csv
import io
from flask import Blueprint, Response, jsonify
from app.config import Config
from .auth import authorize_request

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route('/users', methods=['GET'])
def download_users_csv():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return auth_data

    if auth_data["role"] != "webmaster":
        return {"error": "Unauthorized"}, 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM users")
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    cursor.close()
    conn.close()

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=users.csv"}
    )

@downloads_bp.route('/courses', methods=['GET'])
def download_courses_csv():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return auth_data

    if auth_data["role"] != "webmaster":
        return {"error": "Unauthorized"}, 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.course_id,
            c.course_name,
            u.username AS teacher_username
        FROM 
            courses c
        JOIN 
            users u ON c.teacher_id = u.user_id
    """)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    cursor.close()
    conn.close()

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=courses.csv"}
    )

@downloads_bp.route('/textbook', methods=['GET'])
def download_textbooks_csv():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return auth_data

    if auth_data["role"] != "webmaster":
        return {"error": "Unauthorized"}, 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.textbook_id,
            t.textbook_title,
            t.textbook_author,
            t.textbook_isbn,
            t.textbook_version,
            u.username AS publisher_username
        FROM 
            textbook t
        JOIN 
            users u ON t.publisher_id = u.user_id
    """)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    cursor.close()
    conn.close()

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=textbooks.csv"}
    )

@downloads_bp.route('/questions', methods=['GET'])
def download_questions_csv():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data["role"] not in ("webmaster", "publisher", "teacher"):
        return jsonify({"error": "Unauthorized"}), 403

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Join with Users to get usernames
    cur.execute("""
        SELECT q.*, u.username
        FROM Questions q
        LEFT JOIN Users u ON q.owner_id = u.user_id;
    """)
    questions = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    # Prepare CSV output
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Question ID', 'Type', 'Question Text', 'Answer(s)', 
        'Details', 'Username', 'Attachment'
    ])

    for q in questions:
        qid = q[headers.index('id')]
        qtext = q[headers.index('question_text')]
        qtype = q[headers.index('type')]
        username = q[headers.index('username')]
        attachment_id = q[headers.index('attachment_id')]

        answer = ""
        details = ""
        attachment_info = ""

        # Handle question type answers
        if qtype == 'True/False':
            answer = str(q[headers.index('true_false_answer')])

        elif qtype == 'Multiple Choice':
            cur.execute("""
                SELECT option_text, is_correct 
                FROM QuestionOptions 
                WHERE question_id = %s;
            """, (qid,))
            options = cur.fetchall()
            answer = ", ".join(opt[0] for opt in options if opt[1])
            details = "Options: " + "; ".join(opt[0] for opt in options)

        elif qtype == 'Fill in the Blank':
            cur.execute("""
                SELECT correct_text 
                FROM QuestionFillBlanks 
                WHERE question_id = %s;
            """, (qid,))
            blanks = cur.fetchall()
            answer = ", ".join(b[0] for b in blanks)

        elif qtype == 'Matching':
            cur.execute("""
                SELECT prompt_text, match_text 
                FROM QuestionMatches 
                WHERE question_id = %s;
            """, (qid,))
            pairs = cur.fetchall()
            answer = f"{len(pairs)} pairs"
            details = "; ".join(f"{p[0]} → {p[1]}" for p in pairs)

        # Handle attachment if present
        if attachment_id:
            cur.execute("""
                SELECT name, filepath 
                FROM Attachments 
                WHERE attachments_id = %s;
            """, (attachment_id,))
            attachment = cur.fetchone()
            if attachment:
                try:
                    supabase = Config.get_supabase_client()
                    signed = supabase.storage.from_(Config.ATTACHMENT_BUCKET).create_signed_url(
                        path=attachment[1],
                        expires_in=14400  # 4 hours
                    )
                    attachment_info = f"{attachment[0]} ({signed['signedURL']})"
                except Exception as e:
                    attachment_info = f"{attachment[0]} (URL failed)"

        # Write the row
        writer.writerow([
            qid, qtype, qtext, answer, 
            details, username, attachment_info
        ])

    cur.close()
    conn.close()

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=questions.csv"}
    )

@downloads_bp.route('/tests', methods=['GET'])
def download_tests_csv():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return auth_data

    if auth_data["role"] != "webmaster":
        return {"error": "Unauthorized"}, 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # 1. Get all Final and Published tests + associated teacher username
    cursor.execute("""
        SELECT
            t.tests_id,
            t.name,
            t.status,
            u.username AS teacher_name,
            t.course_id,
            t.filename
        FROM tests t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.status IN ('Final', 'Published')
    """)
    test_rows = cursor.fetchall()

    # 2. Prepare CSV headers
    headers = ['test_id', 'name', 'status', 'teacher_name', 'course_id', 'test_file_url', 'answer_key_file_url']
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    # 3. Get Supabase storage access
    from config import get_supabase_client
    supabase = get_supabase_client()
    test_bucket = "Tests"

    for row in test_rows:
        test_id, name, status, teacher_name, course_id, test_filename = row

        # Test file (already has full path like 'final/test1.pdf')
        test_file_url = None
        if test_filename:
            try:
                signed = supabase.storage.from_(test_bucket).create_signed_url(
                    path=test_filename,
                    expires_in=3600
                )
                test_file_url = signed['signedURL']
            except Exception as e:
                test_file_url = f"ERROR: {e}"

        # Answer key file
        cursor.execute("""
            SELECT filename FROM Answer_Key_Table
            WHERE test_id = %s
        """, (test_id,))
        key_result = cursor.fetchone()
        answer_key_file_url = None

        if key_result and key_result[0]:
            try:
                signed_key = supabase.storage.from_(test_bucket).create_signed_url(
                    path=key_result[0],  # includes 'answer_keys/filename.pdf'
                    expires_in=3600
                )
                answer_key_file_url = signed_key['signedURL']
            except Exception as e:
                answer_key_file_url = f"ERROR: {e}"

        # Add to CSV
        writer.writerow([
            test_id,
            name,
            status,
            teacher_name,
            course_id,
            test_file_url,
            answer_key_file_url
        ])

    output.seek(0)
    cursor.close()
    conn.close()

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=tests.csv"}
    )
