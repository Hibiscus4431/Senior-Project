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
    #####################
    chapter_number = data.get("chapter_number")
    section_number = data.get("section_number")
    #####################

    if not testbank_name or not course_id:
        return jsonify({"error": "Missing testbank_name or course_id"}), 400

    #if not testbank_name or not course_id or chapter_number is None or section_number is None:
    #    return jsonify({"error": "Missing testbank_name, course_id, chapter_number, or section_number"}), 400


    conn = Config.get_db_connection()
    cursor = conn.cursor()

    #insert_query = sql.SQL("""
    #    INSERT INTO Test_bank (name, course_id, owner_id)
    #    VALUES (%s, %s, %s)
    #    RETURNING testbank_id;
    #""")
    insert_query = sql.SQL("""
        INSERT INTO Test_bank (name, course_id, owner_id, chapter_number, section_number)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING testbank_id;
    """)


    #cursor.execute(insert_query, (testbank_name, course_id, auth_data["user_id"]))
    cursor.execute(insert_query, (testbank_name, course_id, auth_data["user_id"], chapter_number, section_number))

    testbank_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    #return jsonify({
    #    "message": "Testbank created for teacher",
    #    "testbank_id": testbank_id,
    #    "course_id": course_id
    #}), 201

    return jsonify({
        "message": "Testbank created for teacher",
        "testbank_id": testbank_id,
        "course_id": course_id,
        "chapter_number": chapter_number,
        "section_number": section_number
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
        SELECT testbank_id, name, course_id, chapter_number, section_number, is_published
        FROM Test_bank
        WHERE owner_id = %s AND course_id = %s
        ORDER BY name;
    """, (user_id, course_id))
    
    rows = cursor.fetchall()
    testbanks = [
        {
            "testbank_id": row[0],
            "name": row[1],
            "course_id": row[2],
            "chapter_number": row[3],
            "section_number": row[4],
            "is_published": row[5]
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
        SELECT owner_id FROM Test_bank WHERE testbank_id = %s;
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
                INSERT INTO test_bank_questions (test_bank_id, question_id)
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
    cur.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # Base query: get questions linked to testbank
    #cur.execute("""
    #    SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number
    #    FROM test_bank_questions tbq
    #    JOIN questions q ON tbq.question_id = q.id
    #    WHERE tbq.test_bank_id = %s;
    #""", (testbank_id,))

    ###################
    cur.execute("""
    SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number,
        q.default_points, q.est_time, q.grading_instructions, q.attachment_id
        FROM test_bank_questions tbq
        JOIN questions q ON tbq.question_id = q.id
        WHERE tbq.test_bank_id = %s;
    """, (testbank_id,))
    ###################
    
    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # Enrich by type
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


# UPDATE Teacher Testbank Info (name, chapter, section)
@testbank_bp.route('/teacher/<int:testbank_id>', methods=['PUT'])
def update_teacher_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "teacher":
        return jsonify({"error": "Only teachers can update testbanks"}), 403

    data = request.get_json()
    name = data.get("name")
    chapter_number = data.get("chapter_number")
    section_number = data.get("section_number")

    if not name:
        return jsonify({"error": "Testbank name is required"}), 400

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # Update testbank
    cursor.execute("""
        UPDATE Test_bank
        SET name = %s, chapter_number = %s, section_number = %s
        WHERE testbank_id = %s;
    """, (name, chapter_number, section_number, testbank_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Testbank updated successfully"}), 200


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
    chapter_number = data.get("chapter_number")
    section_number = data.get("section_number")

    if not testbank_name or not textbook_id:
        return jsonify({"error": "Missing testbank_name or textbook_id"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO Test_bank (name, textbook_id, owner_id, chapter_number, section_number)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING testbank_id;
    """)
    cursor.execute(insert_query, (testbank_name, textbook_id, auth_data["user_id"], chapter_number, section_number))
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
        SELECT testbank_id, name, textbook_id, chapter_number, section_number, is_published
        FROM Test_bank
        WHERE owner_id = %s AND textbook_id = %s
        ORDER BY name;
    """, (user_id, textbook_id))
    
    rows = cursor.fetchall()
    testbanks = [
        {
        "testbank_id": row[0],
        "name": row[1],
        "textbook_id": row[2],
        "chapter_number": row[3],
        "section_number": row[4],
        "is_published": row[5]
        } for row in rows
    ]


    cursor.close()
    conn.close()

    return jsonify({"testbanks": testbanks}), 200


@testbank_bp.route('/publisher/<int:testbank_id>/questions', methods=['POST'])
def add_questions_to_testbank_publihser(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "publisher":
        return jsonify({"error": "Only publishers can add to these testbanks"}), 403

    user_id = auth_data["user_id"]
    data = request.get_json()
    question_ids = data.get("question_ids")

    if not question_ids or not isinstance(question_ids, list):
        return jsonify({"error": "question_ids must be a list of integers"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute("SELECT owner_id, is_published FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403
    if result[1]:  # is_published is True
        return jsonify({"error": "Cannot add questions to a published testbank"}), 403

    for qid in question_ids:
        try:
            cursor.execute("""
                INSERT INTO test_bank_questions (test_bank_id, question_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (testbank_id, qid))
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Error adding question {qid}: {str(e)}"}), 500

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Questions added to testbank successfully"}), 201


@testbank_bp.route('/publisher/<int:testbank_id>/questions', methods=['GET'])
def get_questions_in_testbank_publihser(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "publisher":
        return jsonify({"error": "Only publishers can view this testbank"}), 403

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    cur.execute("""
        SELECT q.id, q.question_text, q.type, q.chapter_number, q.section_number, q.attachment_id
        FROM test_bank_questions tbq
        JOIN questions q ON tbq.question_id = q.id
        WHERE tbq.test_bank_id = %s;
    """, (testbank_id,))

    column_names = [desc[0] for desc in cur.description]
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]

    # Enrich as before...
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


@testbank_bp.route('/<int:testbank_id>/publish', methods=['POST'])
def publish_testbank_and_questions(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    role = auth_data.get("role")
    if role not in ["teacher", "publisher"]:
        return jsonify({"error": "Only teachers or publishers can publish testbanks"}), 403

    user_id = auth_data["user_id"]
    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # ✅ Verify the testbank is owned by the user
    cursor.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s;", (testbank_id,))
    result = cursor.fetchone()
    if not result or result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # ✅ Mark the testbank as published
    cursor.execute("""
        UPDATE Test_bank
        SET is_published = TRUE
        WHERE testbank_id = %s;
    """, (testbank_id,))

    # ✅ Mark all questions in the testbank as published
    cursor.execute("""
        UPDATE Questions
        SET is_published = TRUE
        WHERE id IN (
            SELECT question_id
            FROM test_bank_questions
            WHERE test_bank_id = %s
        );
    """, (testbank_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Testbank and all linked questions published successfully."}), 200


#######--------------------Common ----------------------------##############################
@testbank_bp.route('/<int:testbank_id>', methods=['DELETE'])    
def delete_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # ✅ Check ownership and publication status
    cursor.execute("""
        SELECT owner_id, is_published FROM Test_bank
        WHERE testbank_id = %s;
    """, (testbank_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"error": "Testbank not found"}), 404

    owner_id, is_published = result

    if owner_id != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    if is_published:
        return jsonify({"error": "Cannot delete a published testbank"}), 403

    # Delete the testbank
    cursor.execute("DELETE FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Testbank deleted successfully"}), 200


# Removing the question from the testbank
# A buttin or something may need to be provided to delete the question from the testbank 
@testbank_bp.route('/<int:testbank_id>/questions/<int:question_id>', methods=['DELETE'])
def remove_question_from_testbank(testbank_id, question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    role = auth_data.get("role")
    user_id = auth_data.get("user_id")

    if role not in ["teacher", "publisher"]:
        return jsonify({"error": "Unauthorized role"}), 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Check ownership of the testbank
    # OLD: cursor.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    cursor.execute("SELECT owner_id, is_published FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    
    owner_id, is_published = result

    if owner_id != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    if is_published:
        return jsonify({"error": "Cannot remove questions from a published testbank"}), 403

    # Delete the association
    cursor.execute("""
        DELETE FROM test_bank_questions
        WHERE test_bank_id = %s AND question_id = %s;
    """, (testbank_id, question_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Question removed from testbank"}), 200

# UPDATE Publisher Testbank Info (name, chapter, section)
# This endpoint allows publishers to update their testbank information
@testbank_bp.route('/publisher/<int:testbank_id>', methods=['PUT'])
def update_publisher_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    if auth_data.get("role") != "publisher":
        return jsonify({"error": "Only publishers can update testbanks"}), 403

    data = request.get_json()
    name = data.get("name")
    chapter_number = data.get("chapter_number")
    section_number = data.get("section_number")

    if not name:
        return jsonify({"error": "Testbank name is required"}), 400

    user_id = auth_data["user_id"]

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Check that the publisher owns this testbank
    cursor.execute("SELECT owner_id FROM Test_bank WHERE testbank_id = %s", (testbank_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"error": "Testbank not found"}), 404
    if result[0] != user_id:
        return jsonify({"error": "You do not own this testbank"}), 403

    # Update the test bank
    cursor.execute("""
        UPDATE Test_bank
        SET name = %s, chapter_number = %s, section_number = %s
        WHERE testbank_id = %s;
    """, (name, chapter_number, section_number, testbank_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Testbank updated successfully"}), 200
