from flask import Blueprint, request, jsonify
from .auth import authorize_request
from psycopg2 import sql
from app.config import Config
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO 
import json
# Create Blueprint
question_bp = Blueprint('questions', __name__)

# CREATE Question (If the user is a publisher, the question is automatically published)
"""When creating a question that has an attacment linked to it the attaachment must be called first and saved in the frontend using loical storage and then that attachment id is linked to the question"""
@question_bp.route('', methods=['POST'])
def create_question():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    role = auth_data['role']
    # This part needs to be checked in your logic when adding to front end
    if request.content_type.startswith('application/json'):
        data = request.get_json()
    else:
        data = request.form.to_dict()
        for key in ['options', 'matches', 'blanks']:
            if key in data:
                try:
                    data[key] = json.loads(data[key])
                except Exception as e:
                    return jsonify({"error": f"Invalid format for '{key}': {str(e)}"}), 400
                
    conn = Config.get_db_connection()
    cur = conn.cursor()
    # Handle file upload
    attachment_id = None
    if 'file' in request.files:
        file = request.files['file']
        original_filename = secure_filename(file.filename)
        file_bytes = file.read()
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{user_id}_{timestamp}_{original_filename}"
        supabase_path = f"attachments/{unique_filename}"

        try:
        # Upload to Supabase
            supabase = Config.get_supabase_client()
            supabase.storage.from_(Config.ATTACHMENT_BUCKET).upload(
                path=supabase_path,
                file=file_bytes,
                file_options={"content-type": file.content_type}
            )

            # Save to DB and get attachment_id
            cur.execute("""
                INSERT INTO Attachments (name, filepath)
                VALUES (%s, %s)
                RETURNING attachments_id;
            """, (original_filename, supabase_path))
            attachment_id = cur.fetchone()[0]

        except Exception as e:
            return jsonify({"error": f"Failed to upload or save attachment: {str(e)}"}), 500
  
    required_fields = ['question_text', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    # Default values for optional fields
    course_id = data.get('course_id')
    textbook_id = data.get('textbook_id')
    default_points = data.get('default_points', 0)
    est_time = data.get('est_time')
    grading_instructions = data.get('grading_instructions')
    source = data.get('source', 'manual')
    chapter_number = data.get('chapter_number')
    section_number = data.get('section_number')
    true_false_answer = data.get('true_false_answer') if data['type'] == 'True/False' else None
    
    is_published = True if role == 'publisher' else False

    
    # Insert into Questions table
    query = ("""
        INSERT INTO Questions (
            question_text, type, owner_id, true_false_answer, is_published, 
            course_id, textbook_id, default_points, est_time, grading_instructions, 
            attachment_id, source, chapter_number, section_number
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """)
    
    cur.execute(query, (data['question_text'], data['type'], user_id, true_false_answer,is_published, 
                        course_id, textbook_id, default_points, est_time, grading_instructions, 
                        attachment_id, source, chapter_number, section_number))
    question_id = cur.fetchone()[0]
    
    # Insert attachment metadata if provided
    if attachment_id:
        cur.execute("""
            INSERT INTO Attachments_MetaData (attachment_id, reference_id, reference_type)
            VALUES (%s, %s, 'question');
        """, (attachment_id, question_id))

    # Handle different question types
    if data['type'] == 'Multiple Choice':
        if 'options' not in data or not isinstance(data['options'], list) or len(data['options']) < 2:
            return jsonify({"error": "Multiple Choice questions must have at least two answer options."}), 400

        # Insert options into QuestionOptions table
        for option in data['options']:
            cur.execute("""
                INSERT INTO QuestionOptions (question_id, option_text, is_correct) 
                VALUES (%s, %s, %s);
            """, (question_id, option['option_text'], option.get('is_correct', False)))

        # 🔹 Ensure options were inserted before committing
        cur.execute("SELECT COUNT(*) FROM QuestionOptions WHERE question_id = %s;", (question_id,))
        option_count = cur.fetchone()[0]

        if option_count < 2:
            conn.rollback()  # Rollback if options are missing
            return jsonify({"error": "Database validation failed: Not enough options inserted."}), 500

    
    elif data['type'] == 'Fill in the Blank':
        if 'blanks' not in data or not isinstance(data['blanks'], list):
            return jsonify({"error": "Fill in the blank questions require blanks."}), 400
        for blank in data['blanks']:
                cur.execute("INSERT INTO QuestionFillBlanks (question_id, correct_text) VALUES (%s, %s);", 
                (question_id, blank['correct_text']))

    
    elif data['type'] == 'Matching':
        if 'matches' not in data or not isinstance(data['matches'], list):
            return jsonify({"error": "Matching questions require prompt and match pairs."}), 400
        for match in data['matches']:
            cur.execute("INSERT INTO QuestionMatches (question_id, prompt_text, match_text) VALUES (%s, %s, %s);", 
                        (question_id, match['prompt_text'], match['match_text']))
    
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Question created successfully", "question_id": question_id}), 201

# Get Questions (by user_id, published, or canvas) - automatically returns user's questions and published questions gets questions by type and returns what is needed 
"""
When you do this route for the front end there needs to be something added to your front end code 
to send the course_id that is selected then it can show all the questions associated with that course
if that becomes a hassle then dont provide the course id and it will show the questions that are associated with the user"""
@question_bp.route('', methods=['GET'])
def get_questions():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data['user_id']
    role = auth_data['role']
    view_type = request.args.get('view', 'user')  # Default to user's questions
    question_type = request.args.get('type', None)
    course_id_filter = request.args.get('course_id', None)
    textbook_id_filter = request.args.get('textbook_id', None)

    conn = Config.get_db_connection()
    cur = conn.cursor()
    params = []

    # View override for canvas-imported questions
    if view_type == 'canvas':
        query = """
            SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
            FROM Questions q
            LEFT JOIN Courses c ON q.course_id = c.course_id
            LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
            WHERE q.source = 'canvas_qti'
        """

    # Role-based filtering
    else:
        query = """
            SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
            FROM Questions q
            LEFT JOIN Courses c ON q.course_id = c.course_id
            LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
            WHERE q.owner_id = %s
        """
        params.append(user_id)

        if role == 'teacher' and course_id_filter:
            query += " AND q.course_id = %s"
            params.append(course_id_filter)

        elif role == 'publisher' and textbook_id_filter:
            query += " AND q.textbook_id = %s"
            params.append(textbook_id_filter)

    # Optional question type filter
    if question_type:
        query += " AND q.type = %s"
        params.append(question_type)

    # Execute the query
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


# UPDATE Question (only unpublished questions can be updated) - this is a PATCH request
# the only things that can be updated are the question_text, options, blanks, and matches!
@question_bp.route('<int:question_id>', methods=['PATCH'])
def update_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data['user_id']
    data = request.get_json()

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Ensure question exists and is not published
    cur.execute("SELECT owner_id, is_published, type FROM Questions WHERE id = %s;", (question_id,))
    question = cur.fetchone()
    if not question:
        return jsonify({"error": "Question not found."}), 404
    if question[1]:  # is_published == True
        return jsonify({"error": "Published questions cannot be edited."}), 403
    if question[0] != user_id:
        return jsonify({"error": "Unauthorized."}), 403

    question_type = question[2]

    # ✅ General updates (if provided)
    fields_to_update = {
        "question_text": "question_text",
        "default_points": "default_points",
        "est_time": "est_time",
        "chapter_number": "chapter_number",
        "section_number": "section_number",
        "grading_instructions": "grading_instructions",
        "true_false_answer": "true_false_answer"
    }

    for field, column in fields_to_update.items():
        if field in data:
            cur.execute(
                f"UPDATE Questions SET {column} = %s WHERE id = %s;",
                (data[field], question_id)
            )

    # ✅ Type-specific updates

    ## Short Answer
    if question_type == "Short Answer" and "answer" in data:
        cur.execute("UPDATE Questions SET short_answer = %s WHERE id = %s;", (data["answer"], question_id))

    ## Essay
    if question_type == "Essay" and "instructions" in data:
        cur.execute("UPDATE Questions SET grading_instructions = %s WHERE id = %s;", (data["instructions"], question_id))

    ## Multiple Choice
    if question_type == "Multiple Choice" and "options" in data and isinstance(data["options"], list):
        cur.execute("SELECT option_id FROM QuestionOptions WHERE question_id = %s;", (question_id,))
        existing_option_ids = {row[0] for row in cur.fetchall()}

        correct_answer_count = 0

        for option in data["options"]:
            option_id = option.get("option_id")
            if option["is_correct"]:
                correct_answer_count += 1

            if option_id in existing_option_ids:
                cur.execute(
                    "UPDATE QuestionOptions SET option_text = %s, is_correct = %s WHERE option_id = %s;",
                    (option["option_text"], option["is_correct"], option_id)
                )
                existing_option_ids.remove(option_id)
            else:
                cur.execute(
                    "INSERT INTO QuestionOptions (question_id, option_text, is_correct) VALUES (%s, %s, %s);",
                    (question_id, option["option_text"], option["is_correct"])
                )

        if "to_delete" in data:
            for delete_id in data["to_delete"]:
                if delete_id in existing_option_ids:
                    cur.execute("SELECT is_correct FROM QuestionOptions WHERE option_id = %s;", (delete_id,))
                    is_correct = cur.fetchone()
                    if is_correct and is_correct[0]:
                        correct_answer_count -= 1
                    cur.execute("DELETE FROM QuestionOptions WHERE option_id = %s;", (delete_id,))

        if correct_answer_count < 1:
            conn.rollback()
            return jsonify({"error": "Multiple Choice questions must have at least one correct answer."}), 400

    ## Fill in the Blank
    if question_type == "Fill in the Blank" and "blanks" in data and isinstance(data["blanks"], list):
        cur.execute("SELECT blank_id FROM QuestionFillBlanks WHERE question_id = %s;", (question_id,))
        existing_blank_ids = {row[0] for row in cur.fetchall()}

        for blank in data["blanks"]:
            blank_id = blank.get("blank_id")
            if blank_id in existing_blank_ids:
                cur.execute(
                    "UPDATE QuestionFillBlanks SET correct_text = %s WHERE blank_id = %s;",
                    (blank["correct_text"], blank_id))
                existing_blank_ids.remove(blank_id)
            else:
                cur.execute(
                    "INSERT INTO QuestionFillBlanks (question_id, correct_text) VALUES (%s, %s);",
                    (question_id, blank["correct_text"])
                )

        if "to_delete" in data:
            for delete_id in data["to_delete"]:
                if delete_id in existing_blank_ids:
                    cur.execute("DELETE FROM QuestionFillBlanks WHERE blank_id = %s;", (delete_id,))

    ## Matching
    if question_type == "Matching" and "matches" in data and isinstance(data["matches"], list):
        cur.execute("SELECT match_id FROM QuestionMatches WHERE question_id = %s;", (question_id,))
        existing_match_ids = {row[0] for row in cur.fetchall()}

        for match in data["matches"]:
            match_id = match.get("match_id")
            if match_id in existing_match_ids:
                cur.execute(
                    "UPDATE QuestionMatches SET prompt_text = %s, match_text = %s WHERE match_id = %s;",
                    (match["prompt_text"], match["match_text"], match_id)
                )
                existing_match_ids.remove(match_id)
            else:
                cur.execute(
                    "INSERT INTO QuestionMatches (question_id, prompt_text, match_text) VALUES (%s, %s, %s);",
                    (question_id, match["prompt_text"], match["match_text"])
                )

        if "to_delete" in data:
            for delete_id in data["to_delete"]:
                if delete_id in existing_match_ids:
                    cur.execute("DELETE FROM QuestionMatches WHERE match_id = %s;", (delete_id,))

    # ✅ Done: save and close
    conn.commit()
    cur.close()

    return jsonify({"message": "Question updated successfully."}), 200


# DELETE Question
@question_bp.route('<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    user_id = auth_data['user_id']

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Ensure question exists and is owned by the user
    cur.execute("SELECT owner_id, is_published FROM Questions WHERE id = %s;", (question_id,))
    question = cur.fetchone()
    if not question:
        return jsonify({"error": "Question not found."}), 404
    if question[1]: # is_published == True
        return jsonify({"error": "Published questions cannot be deleted."}), 403
    if question[0] != user_id:
        return jsonify({"error": "Unauthorized."}), 403
    
    # Delete related options, blanks, and matches
    cur.execute("DELETE FROM QuestionOptions WHERE question_id = %s;", (question_id,))
    cur.execute("DELETE FROM QuestionFillBlanks WHERE question_id = %s;", (question_id,))
    cur.execute("DELETE FROM QuestionMatches WHERE question_id = %s;", (question_id,))  

    # Delete the main question 
    cur.execute("Delete FROM Questions WHERE id = %s;", (question_id,))

    conn.commit()
    cur.close()

    return jsonify({"message": "Question deleted successfully."}), 200