from app.config import Config
from flask import Blueprint, request, jsonify
from .auth import authorize_request
from psycopg2 import sql

testbank_bp = Blueprint('testbanks', __name__)

##############################--------------------Teacher ----------------------------##############################
# CREATE Testbank
# This endpoint allows teachers to create a testbank
@testbank_bp.route('/teacher', methods=['POST'])
def create_teacher_testbank():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can create testbanks here"}), 403

    data = request.get_json()
    testbank_name = data.get("testbank_name")
    course_id = data.get("course_id")

    if not testbank_name or not course_id:
        return jsonify({"error": "Missing testbank_name or course_id"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO Testbank (name, course_id, owner_id)
        VALUES (%s, %s, %s)
        RETURNING testbank_id;
    """)
    cursor.execute(insert_query, (testbank_name, course_id, auth_data["user_id"]))
    testbank_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Testbank created for teacher",
        "testbank_id": testbank_id,
        "course_id": course_id
    }), 201

# GET Teacher Testbanks by course_id
# This endpoint allows teachers to view their testbanks by course_id
# It returns a list of testbanks owned by the teacher for the specified course
@testbank_bp.route('/teacher', methods=['GET'])
def get_teacher_testbanks_by_course():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can view their testbanks"}), 403

    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Missing course_id parameter"}), 400

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT testbank_id, name, course_id
        FROM Testbank
        WHERE owner_id = %s AND course_id = %s
        ORDER BY name;
    """, (user_id, course_id))
    
    rows = cursor.fetchall()
    testbanks = [
        {
            "testbank_id": row[0],
            "name": row[1],
            "course_id": row[2]
        } for row in rows
    ]

    cursor.close()
    conn.close()

    return jsonify({"testbanks": testbanks}), 200

# Add Questions to Testbank 
# This endpoint allows teachers to add questions to their testbanks
# It expects a JSON payload with a list of question_ids
@testbank_bp.route('/<int:testbank_id>/questions', methods=['POST'])
def add_questions_to_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    # Only teachers can use this route
    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can add questions to testbanks"}), 403

    user_id = auth_data["user_id"]
    data = request.get_json()
    question_ids = data.get("question_ids")

    if not question_ids or not isinstance(question_ids, list):
        return jsonify({"error": "question_ids must be a list of integers"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Verify the testbank is owned by the teacher
    cursor.execute("""
        SELECT owner_id FROM Testbank WHERE testbank_id = %s;
    """, (testbank_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # Insert each question_id into testbank_questions
    for qid in question_ids:
        try:
            cursor.execute("""
                INSERT INTO testbank_questions (testbank_id, question_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (testbank_id, qid))
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Failed to insert question {qid}: {str(e)}"}), 500

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Questions added to testbank successfully"}), 201

# GET Questions in Testbank
# This endpoint allows teachers to view all questions in a specific testbank
# It returns a list of questions with their details
# It also enriches the question data with options, matches, and blanks based on the question type
@testbank_bp.route('/<int:testbank_id>/questions', methods=['GET'])
def get_questions_in_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can view questions in testbanks"}), 403

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Confirm ownership
    cur.execute("SELECT owner_id FROM Testbank WHERE testbank_id = %s", (testbank_id,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # Base query: get questions linked to testbank
    cur.execute("""
        SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number
        FROM testbank_questions tbq
        JOIN questions q ON tbq.question_id = q.id
        WHERE tbq.testbank_id = %s;
    """, (testbank_id,))
    
    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # Enrich by type
    for q in questions:
        qid = q['id']
        qtype = q['type']

        if qtype == 'Multiple Choice':
            cur.execute("""
                SELECT option_id, option_text, is_correct
                FROM QuestionOptions
                WHERE question_id = %s;
            """, (qid,))
            options = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

            correct_option = None
            incorrect_options = []

            for option in options:
                if option['is_correct']:
                    correct_option = option
                else:
                    incorrect_options.append(option)

            q['correct_option'] = correct_option
            q['incorrect_options'] = incorrect_options

        elif qtype == 'Matching':
            cur.execute("""
                SELECT match_id, prompt_text, match_text 
                FROM QuestionMatches 
                WHERE question_id = %s;
            """, (qid,))
            q['matches'] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        elif qtype == 'Fill in the Blank':
            cur.execute("""
                SELECT blank_id, correct_text 
                FROM QuestionFillBlanks 
                WHERE question_id = %s;
            """, (qid,))
            q['blanks'] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify({"questions": questions}), 200


######################### ----------------------Publihser ---------------------------------- #########################
@testbank_bp.route('/publisher', methods=['POST'])
def create_publisher_testbank():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "publisher":
        return jsonify({"error": "Only publishers can create testbanks here"}), 403

    data = request.get_json()
    testbank_name = data.get("testbank_name")
    textbook_id = data.get("textbook_id")

    if not testbank_name or not textbook_id:
        return jsonify({"error": "Missing testbank_name or textbook_id"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO Testbank (name, textbook_id, owner_id)
        VALUES (%s, %s, %s)
        RETURNING testbank_id;
    """)
    cursor.execute(insert_query, (testbank_name, textbook_id, auth_data["user_id"]))
    testbank_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Testbank created for publisher",
        "testbank_id": testbank_id,
        "textbook_id": textbook_id
    }), 201


@testbank_bp.route('/publisher', methods=['GET'])
def get_publisher_testbanks_by_textbook():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "publisher":
        return jsonify({"error": "Only publishers can view their testbanks"}), 403

    textbook_id = request.args.get("textbook_id")
    if not textbook_id:
        return jsonify({"error": "Missing textbook_id parameter"}), 400

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT testbank_id, name, textbook_id
        FROM Testbank
        WHERE owner_id = %s AND textbook_id = %s
        ORDER BY name;
    """, (user_id, textbook_id))
    
    rows = cursor.fetchall()
    testbanks = [
        {
            "testbank_id": row[0],
            "name": row[1],
            "textbook_id": row[2]
        } for row in rows
    ]

    cursor.close()
    conn.close()

    return jsonify({"testbanks": testbanks}), 200


