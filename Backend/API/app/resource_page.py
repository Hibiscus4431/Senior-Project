from flask import Blueprint, request, jsonify
from .auth import authorize_request
from app.config import Config

resources_bp = Blueprint('resources', __name__)

# Get all questions from a course's textbook by a publisher (Tested worked)
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


# Adding questions to the teachers arsenal (Tested worked)
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


# Get all published questions from all users (Tested Worked)
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

        # 🔗 If the question has an attachment, generate signed URL
        if q.get('attachment_id'):
            cur.execute("""
                SELECT name, filepath FROM Attachments WHERE attachments_id = %s;
            """, (q['attachment_id'],))
            attachment = cur.fetchone()
            if attachment:
                try:
                    supabase = Config.get_supabase_client()
                    signed = supabase.storage.from_(Config.ATTACHMENT_BUCKET).create_signed_url(
                        path=attachment[1],
                        expires_in=14400  # 4 hour expiration
                    )
                    q['attachment'] = {
                        "name": attachment[0],
                        "url": signed['signedURL']
                    }
                except Exception as e:
                    q['attachment'] = {
                        "name": attachment[0],
                        "url": None,
                        "error": f"Could not generate signed URL: {str(e)}"
                    }

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


# Get all testbanks by publisher that are published and their questions
@resources_bp.route('/full-testbanks', methods=['GET'])
def get_full_published_testbanks_by_course():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Step 1: Get textbook_id for the course
    cur.execute("SELECT textbook_id FROM Courses WHERE course_id = %s;", (course_id,))
    result = cur.fetchone()
    if not result or result[0] is None:
        return jsonify({"error": "No textbook assigned to this course"}), 404
    textbook_id = result[0]

    # Step 2: Get all published testbanks linked to that textbook
    cur.execute("""
        SELECT testbank_id, name, chapter_number, section_number
        FROM Test_bank
        WHERE textbook_id = %s AND is_published = TRUE;
    """, (textbook_id,))
    testbank_rows = cur.fetchall()

    testbanks = []

    for row in testbank_rows:
        testbank_id, name, chapter, section = row

        # Step 3: Get questions in this testbank
        cur.execute("""
            SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number, q.attachment_id
            FROM test_bank_questions tbq
            JOIN Questions q ON tbq.question_id = q.id
            WHERE tbq.test_bank_id = %s;
        """, (testbank_id,))
        column_names = [desc[0] for desc in cur.description]
        questions = [dict(zip(column_names, qrow)) for qrow in cur.fetchall()]

        # Step 4: Enrich based on type
        for q in questions:
            qid = q["id"]
            qtype = q["type"]

            # 🔗 If the question has an attachment, generate signed URL
            if q.get('attachment_id'):
                cur.execute("""
                    SELECT name, filepath FROM Attachments WHERE attachments_id = %s;
                """, (q['attachment_id'],))
                attachment = cur.fetchone()
                if attachment:
                    try:
                        supabase = Config.get_supabase_client()
                        signed = supabase.storage.from_(Config.ATTACHMENT_BUCKET).create_signed_url(
                            path=attachment[1],
                            expires_in=14400  # 4 hour expiration
                        )
                        q['attachment'] = {
                            "name": attachment[0],
                            "url": signed['signedURL']
                        }
                    except Exception as e:
                        q['attachment'] = {
                            "name": attachment[0],
                            "url": None,
                            "error": f"Could not generate signed URL: {str(e)}"
                        }
                        
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

        testbanks.append({
            "testbank_id": testbank_id,
            "name": name,
            "chapter_number": chapter,
            "section_number": section,
            "questions": questions
        })

    cur.close()
    conn.close()

    return jsonify({"testbanks": testbanks}), 200


# This is for teachers to copy a published testbank to their own arsenal (so the testbank and the questions)
@resources_bp.route('/testbanks/copy', methods=['POST'])
def copy_published_testbank_for_teacher():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can copy testbanks"}), 403

    teacher_id = auth_data["user_id"]
    data = request.get_json()
    source_testbank_id = data.get("testbank_id")
    course_id = data.get("course_id")

    if not source_testbank_id or not course_id:
        return jsonify({"error": "Missing testbank_id or course_id"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # 1. Fetch original testbank
    cur.execute("""
        SELECT name, textbook_id, chapter_number, section_number
        FROM test_bank
        WHERE testbank_id = %s AND is_published = TRUE;
    """, (source_testbank_id,))
    original = cur.fetchone()

    if not original:
        return jsonify({"error": "This test bank is not published, and cannot be copied."}), 403

    name, textbook_id, chapter, section = original

    # 2. Insert new testbank for teacher
    cur.execute("""
        INSERT INTO test_bank (owner_id, name, course_id, chapter_number, section_number, is_published)
        VALUES (%s, %s, %s, %s, %s, FALSE)
        RETURNING testbank_id;
    """, (teacher_id, name, course_id, chapter, section))
    new_testbank_id = cur.fetchone()[0]

    # 3. Get question IDs linked to original testbank
    cur.execute("""
        SELECT question_id FROM test_bank_questions WHERE test_bank_id = %s;
    """, (source_testbank_id,))
    question_ids = [row[0] for row in cur.fetchall()]

    copied_qids = []

    for qid in question_ids:
        # Check if teacher already owns this question
        cur.execute("""
            SELECT id FROM Questions
            WHERE id = %s AND owner_id = %s;
        """, (qid, teacher_id))
        existing = cur.fetchone()

        if existing:
            new_qid = existing[0]
        else:
            # Fetch original question
            cur.execute("""
                SELECT id, question_text, type, true_false_answer, default_points, est_time,
                       grading_instructions, source, chapter_number, section_number, attachment_id
                FROM Questions WHERE id = %s;
            """, (qid,))
            q = cur.fetchone()
            if not q:
                continue

            (
                source_question_id, question_text, qtype, tf_answer, points, est_time,
                grading, source, chapter, section, attachment_id
            ) = q

            # Insert copied question
            cur.execute("""
                INSERT INTO Questions (
                    question_text, type, true_false_answer, default_points, est_time,
                    grading_instructions, source, chapter_number, section_number,
                    owner_id, course_id, textbook_id, is_published
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, FALSE)
                RETURNING id;
            """, (
                question_text, qtype, tf_answer, points, est_time,
                grading, source, chapter, section,
                teacher_id, course_id
            ))
            new_qid = cur.fetchone()[0]

            # Copy attachment if exists
            if attachment_id:
                cur.execute("""
                    INSERT INTO Attachments (file_name, file_path, storage_bucket, uploaded_by)
                    SELECT file_name, file_path, storage_bucket, %s
                    FROM Attachments
                    WHERE attachments_id = %s
                    RETURNING attachments_id;
                """, (teacher_id, attachment_id))
                new_attachment_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO Attachments_MetaData (attachments_id, key, value)
                    SELECT %s, key, value
                    FROM Attachments_MetaData
                    WHERE attachments_id = %s;
                """, (new_attachment_id, attachment_id))

                cur.execute("""
                    UPDATE Questions SET attachment_id = %s WHERE id = %s;
                """, (new_attachment_id, new_qid))

            # Copy structure
            if qtype == "Multiple Choice":
                cur.execute("""
                    SELECT option_text, is_correct FROM QuestionOptions WHERE question_id = %s;
                """, (source_question_id,))
                for opt_text, is_correct in cur.fetchall():
                    cur.execute("""
                        INSERT INTO QuestionOptions (question_id, option_text, is_correct)
                        VALUES (%s, %s, %s);
                    """, (new_qid, opt_text, is_correct))

            elif qtype == "Matching":
                cur.execute("""
                    SELECT prompt_text, match_text FROM QuestionMatches WHERE question_id = %s;
                """, (source_question_id,))
                for prompt, match in cur.fetchall():
                    cur.execute("""
                        INSERT INTO QuestionMatches (question_id, prompt_text, match_text)
                        VALUES (%s, %s, %s);
                    """, (new_qid, prompt, match))

            elif qtype == "Fill in the Blank":
                cur.execute("""
                    SELECT correct_text FROM QuestionFillBlanks WHERE question_id = %s;
                """, (source_question_id,))
                for (correct_text,) in cur.fetchall():
                    cur.execute("""
                        INSERT INTO QuestionFillBlanks (question_id, correct_text)
                        VALUES (%s, %s);
                    """, (new_qid, correct_text))

        # Link question to new testbank
        cur.execute("""
            INSERT INTO test_bank_questions (test_bank_id, question_id)
            VALUES (%s, %s);
        """, (new_testbank_id, new_qid))

        copied_qids.append(new_qid)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Testbank copied successfully",
        "new_testbank_id": new_testbank_id,
        "question_ids": copied_qids
    }), 201

############################## Test Routes ########################
@resources_bp.route('/tests/files/<int:test_id>', methods=['GET'])
def get_test_file_signed_url(test_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor()

    try:
        # Get filename from published test
        cur.execute("""
            SELECT filename FROM tests WHERE tests_id = %s AND status = 'Published'
        """, (test_id,))
        row = cur.fetchone()

        if not row or not row[0]:
            return jsonify({"error": "Test file not found or test is not published."}), 404

        file_path = row[0]  # e.g., "published/3_Unit3_Final.pdf"

        # Generate signed URL from Supabase
        supabase = Config.get_supabase_client()
        signed = supabase.storage.from_('Tests').create_signed_url(
            path=file_path,
            expires_in=3600  # 1 hour
        )

        return jsonify({
            "file_url": signed['signedURL'],
            "filename": file_path,
            "expires_in": 3600
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to generate file link: {str(e)}"}), 500

    finally:
        cur.close()
        conn.close()


@resources_bp.route('/tests/<int:test_id>/questions', methods=['GET'])
def get_test_questions(test_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor()

    try:
        # Get all question details for the test
        cur.execute("""
            SELECT q.*
            FROM test_metadata tm
            JOIN questions q ON tm.question_id = q.id
            WHERE tm.test_id = %s
        """, (test_id,))
        questions = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        supabase = Config.get_supabase_client()

        for q in questions:
            qid = q['id']
            qtype = q['type']

            # Attachments (signed URL)
            if q.get('attachment_id'):
                try:
                    cur.execute("""
                        SELECT name, filepath FROM attachments WHERE attachments_id = %s;
                    """, (q['attachment_id'],))
                    attachment = cur.fetchone()
                    if attachment:
                        signed = supabase.storage.from_('attachments').create_signed_url(
                            path=attachment[1],
                            expires_in=14400  # 4 hours
                        )
                        q['attachment'] = {
                            "name": attachment[0],
                            "url": signed['signedURL']
                        }
                except Exception as e:
                    print(f"❌ Error generating signed URL for qid {q['id']}: {e}")

            # Multiple Choice
            if qtype == 'Multiple Choice':
                cur.execute("""
                    SELECT option_id, option_text, is_correct
                    FROM questionoptions
                    WHERE question_id = %s;
                """, (qid,))
                options = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
                q['correct_option'] = next((opt for opt in options if opt['is_correct']), None)
                q['incorrect_options'] = [opt for opt in options if not opt['is_correct']]

            # Matching
            elif qtype == 'Matching':
                cur.execute("""
                    SELECT match_id, prompt_text, match_text
                    FROM questionmatches
                    WHERE question_id = %s;
                """, (qid,))
                q['matches'] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

            # Fill in the Blank
            elif qtype == 'Fill in the Blank':
                cur.execute("""
                    SELECT blank_id, correct_text
                    FROM questionfillblanks
                    WHERE question_id = %s;
                """, (qid,))
                q['blanks'] = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]

        return jsonify({ "questions": questions }), 200

    except Exception as e:
        return jsonify({ "error": f"Failed to fetch test questions: {str(e)}" }), 500

    finally:
        cur.close()
        conn.close()

