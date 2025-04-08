from flask import Blueprint, request, jsonify
from .auth import authorize_request
from app.config import Config

resources_bp = Blueprint('resources', __name__)

# Get all questions from a course's textbook by a publisher 
@resources_bp.route('/questions', methods=['GET'])
def get_published_questions_for_course_textbook():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # 1. Get textbook_id from course_id
    cur.execute("SELECT textbook_id FROM Courses WHERE course_id = %s;", (course_id,))
    result = cur.fetchone()
    if not result or result[0] is None:
        return jsonify({"error": "No textbook assigned to this course"}), 404

    textbook_id = result[0]

    # 2. Get published questions from that textbook
    cur.execute("""
        SELECT id, question_text, type, chapter_number, section_number
        FROM Questions
        WHERE textbook_id = %s AND is_published = TRUE;
    """, (textbook_id,))
    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # 3. Enrich by type (reuse your existing logic)
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
            q['correct_option'] = next((o for o in options if o['is_correct']), None)
            q['incorrect_options'] = [o for o in options if not o['is_correct']]

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


# Get all questions from a publisher's testbank
@resources_bp.route('/testbanks/<int:testbank_id>/questions', methods=['GET'])
def get_questions_from_publisher_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Make sure this is a publisher-owned testbank
    cur.execute("""
        SELECT tb.testbank_id
        FROM Test_bank tb
        JOIN Users u ON tb.owner_id = u.id
        WHERE tb.testbank_id = %s AND u.role = 'publisher';
    """, (testbank_id,))
    if not cur.fetchone():
        return jsonify({"error": "Testbank not found or not a publisher testbank"}), 404

    # Fetch questions
    cur.execute("""
        SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number
        FROM test_bank_questions tbq
        JOIN questions q ON tbq.question_id = q.id
        WHERE tbq.test_bank_id = %s;
    """, (testbank_id,))
    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # Enrich questions
    for q in questions:
        qid = q["id"]
        qtype = q["type"]

        if qtype == "Multiple Choice":
            cur.execute("""
                SELECT option_id, option_text, is_correct
                FROM QuestionOptions
                WHERE question_id = %s;
            """, (qid,))
            options = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            q["correct_option"] = next((o for o in options if o["is_correct"]), None)
            q["incorrect_options"] = [o for o in options if not o["is_correct"]]

        elif qtype == "Matching":
            cur.execute("""
                SELECT match_id, prompt_text, match_text
                FROM QuestionMatches
                WHERE question_id = %s;
            """, (qid,))
            q["matches"] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        elif qtype == "Fill in the Blank":
            cur.execute("""
                SELECT blank_id, correct_text
                FROM QuestionFillBlanks
                WHERE question_id = %s;
            """, (qid,))
            q["blanks"] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify({"questions": questions}), 200


#Adding questions to the teachers arsenal (Definitly Not Ready rn)
@resources_bp.route('/questions/copy', methods=['POST'])
def copy_published_question_for_teacher():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can copy questions"}), 403

    teacher_id = auth_data["user_id"]
    data = request.get_json()
    source_question_id = data.get("question_id")
    course_id = data.get("course_id")

    if not source_question_id or not course_id:
        return jsonify({"error": "Missing question_id or course_id"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # 1. Fetch original question
    cur.execute("""
        SELECT question_text, type, true_false_answer, default_points, est_time,
               grading_instructions, source, chapter_number, section_number, attachment_id
        FROM Questions
        WHERE id = %s AND is_published = TRUE;
    """, (source_question_id,))
    original = cur.fetchone()

    if not original:
        return jsonify({"error": "Published question not found"}), 404

    (
        question_text, qtype, tf_answer, points, est_time, grading,
        source, chapter, section, attachment_id
    ) = original

    # 2. Insert new question (no attachment yet)
    cur.execute("""
        INSERT INTO Questions (
            question_text, type, true_false_answer, default_points,
            est_time, grading_instructions, source,
            chapter_number, section_number,
            owner_id, course_id, textbook_id, is_published
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, FALSE)
        RETURNING id;
    """, (
        question_text, qtype, tf_answer, points, est_time, grading,
        source, chapter, section, teacher_id, course_id
    ))
    new_qid = cur.fetchone()[0]

    # 3. If attachment exists, copy it and update the question
    if attachment_id:
        # Copy Attachments table row
        cur.execute("""
            INSERT INTO Attachments (file_name, file_path, storage_bucket, uploaded_by)
            SELECT file_name, file_path, storage_bucket, %s
            FROM Attachments
            WHERE attachments_id = %s
            RETURNING attachments_id;
        """, (teacher_id, attachment_id))
        new_attachment_id = cur.fetchone()[0]

        # Copy metadata
        cur.execute("""
            INSERT INTO Attachments_MetaData (attachments_id, key, value)
            SELECT %s, key, value
            FROM Attachments_MetaData
            WHERE attachments_id = %s;
        """, (new_attachment_id, attachment_id))

        # Update copied question
        cur.execute("""
            UPDATE Questions
            SET attachment_id = %s
            WHERE id = %s;
        """, (new_attachment_id, new_qid))

    # 4. Copy question options or structure based on type
    if qtype == "Multiple Choice":
        cur.execute("""
            SELECT option_text, is_correct
            FROM QuestionOptions
            WHERE question_id = %s;
        """, (source_question_id,))
        options = cur.fetchall()
        for opt_text, is_correct in options:
            cur.execute("""
                INSERT INTO QuestionOptions (question_id, option_text, is_correct)
                VALUES (%s, %s, %s);
            """, (new_qid, opt_text, is_correct))

    elif qtype == "Matching":
        cur.execute("""
            SELECT prompt_text, match_text
            FROM QuestionMatches
            WHERE question_id = %s;
        """, (source_question_id,))
        matches = cur.fetchall()
        for prompt, match in matches:
            cur.execute("""
                INSERT INTO QuestionMatches (question_id, prompt_text, match_text)
                VALUES (%s, %s, %s);
            """, (new_qid, prompt, match))

    elif qtype == "Fill in the Blank":
        cur.execute("""
            SELECT correct_text
            FROM QuestionFillBlanks
            WHERE question_id = %s;
        """, (source_question_id,))
        blanks = cur.fetchall()
        for (correct_text,) in blanks:
            cur.execute("""
                INSERT INTO QuestionFillBlanks (question_id, correct_text)
                VALUES (%s, %s);
            """, (new_qid, correct_text))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Question copied successfully",
        "new_question_id": new_qid
    }), 201


# Get all published questions 
@resources_bp.route('/published', methods=['GET'])
def get_published_questions():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    question_type = request.args.get('type', None)

    conn = Config.get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.course_id
        LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
        WHERE q.is_published = TRUE
    """
    params = []

    if question_type:
        query += " AND q.type = %s"
        params.append(question_type)

    cur.execute(query, tuple(params))
    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # Attach type-specific data
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
            q['correct_option'] = next((opt for opt in options if opt['is_correct']), None)
            q['incorrect_options'] = [opt for opt in options if not opt['is_correct']]

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
