from flask import Blueprint, request, jsonify, current_app
from .auth import authorize_request
from psycopg2 import sql

# Create Blueprint
question_bp = Blueprint('questions', __name__)

# CREATE Question
@question_bp.route('', methods=['POST'])
def create_question():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    data = request.get_json()
    required_fields = ['question_text', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    # Default values for optional fields
    course_id = data.get('course_id')
    textbook_id = data.get('textbook_id')
    default_points = data.get('default_points', 0)
    est_time = data.get('est_time')
    grading_instructions = data.get('grading_instructions')
    attachment_id = data.get('attachment_id')
    source = data.get('source', 'manual')
    chapter_number = data.get('chapter_number')
    section_number = data.get('section_number')
    true_false_answer = data.get('true_false_answer') if data['type'] == 'True/False' else None
    
    conn = current_app.db_connection
    cur = conn.cursor()
    
    # Insert into Questions table
    query = sql.SQL("""
        INSERT INTO Questions (
            question_text, type, owner_id, true_false_answer, is_published, 
            course_id, textbook_id, default_points, est_time, grading_instructions, 
            attachment_id, source, chapter_number, section_number
        )
        VALUES (%s, %s, %s, %s, FALSE, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """)
    
    cur.execute(query, (data['question_text'], data['type'], user_id, true_false_answer, 
                        course_id, textbook_id, default_points, est_time, grading_instructions, 
                        attachment_id, source, chapter_number, section_number))
    question_id = cur.fetchone()[0]
    
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
                        (question_id, blank))
    
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

# READ Questions
@question_bp.route('', methods=['GET'])
def get_questions():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    view_type = request.args.get('view', 'user')  # Default to user's questions
    question_type = request.args.get('type', None)  # Optional: question type filter
    conn = current_app.db_connection
    cur = conn.cursor()
    
    if view_type == 'published':
        query = """
        SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.course_id
        LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
        WHERE q.is_published = TRUE;
        """
        params = []
        
    elif view_type == 'canvas':
        query = """
        SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.course_id
        LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
        WHERE q.source = 'canvas_qti';
        """
        params = []
    else:
        query = """
        SELECT q.*, c.course_name AS course_name, t.textbook_title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.course_id
        LEFT JOIN Textbook t ON q.textbook_id = t.textbook_id
        WHERE q.owner_id = %s OR q.is_published = TRUE;
        """
        params = [user_id]
    if question_type:
        query += " AND q.type = %s"
        params.append(question_type)
    
    cur.execute(query, tuple(params))
    column_names = [desc[0] for desc in cur.description]  # Get column names
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]  # Convert to dicts

    cur.close()
    conn.close()
    return jsonify({"questions": questions}), 200

# UPDATE Question
@question_bp.route('<int:question_id>', methods=['PUT'])
def update_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    data = request.get_json()
    
    conn = current_app.db_connection
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
    
    # Update question text if provided
    if "question_text" in data:
        cur.execute("UPDATE Questions SET question_text = %s WHERE id = %s;", 
                    (data["question_text"], question_id))

    # Handle Multiple-Choice Updates
    if question[2] == "Multiple Choice" and "options" in data and isinstance(data["options"], list):
        cur.execute("SELECT option_id FROM QuestionOptions WHERE question_id = %s;", (question_id,))
        existing_option_ids = {row[0] for row in cur.fetchall()}

        correct_answer_count = 0  # Track correct answers

        for option in data["options"]:
            option_id = option.get("option_id")
            if option["is_correct"]:  
                correct_answer_count += 1  # Count correct answers

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
                if option["is_correct"]:  
                    correct_answer_count += 1  # Count newly added correct answer

        # Handle explicit deletions
        if "to_delete" in data and isinstance(data["to_delete"], list):
            for delete_id in data["to_delete"]:
                if delete_id in existing_option_ids:
                    cur.execute("SELECT is_correct FROM QuestionOptions WHERE option_id = %s;", (delete_id,))
                    is_correct = cur.fetchone()
                    if is_correct and is_correct[0]:  
                        correct_answer_count -= 1  # Remove a correct answer from the count

                    cur.execute("DELETE FROM QuestionOptions WHERE option_id = %s;", (delete_id,))

        # Final Check: Ensure at least ONE correct answer exists
        if correct_answer_count < 1:
            conn.rollback()  # Cancel all updates if the condition is not met
            return jsonify({"error": "Multiple Choice questions must have at least one correct answer."}), 400


    # Handle Fill-in-the-Blank Updates
    if question[2] == "Fill in the Blank" and "blanks" in data and isinstance(data["blanks"], list):
        cur.execute("SELECT blank_id FROM QuestionFillBlanks WHERE question_id = %s;", (question_id,))
        existing_blank_ids = {row[0] for row in cur.fetchall()}

        for blank in data["blanks"]:
            blank_id = blank.get("blank_id")
            if blank_id in existing_blank_ids:
                cur.execute(
                    "UPDATE QuestionFillBlanks SET correct_text = %s WHERE blank_id = %s;",
                    (blank["correct_text"], blank_id)
                )
                existing_blank_ids.remove(blank_id)
            else:
                cur.execute(
                    "INSERT INTO QuestionFillBlanks (question_id, correct_text) VALUES (%s, %s);",
                    (question_id, blank["correct_text"])
                )

        if "to_delete" in data and isinstance(data["to_delete"], list):
            for delete_id in data["to_delete"]:
                if delete_id in existing_blank_ids:
                    cur.execute("DELETE FROM QuestionFillBlanks WHERE blank_id = %s;", (delete_id,))

    # Handle Matching Question Updates
    if question[2] == "Matching" and "matches" in data and isinstance(data["matches"], list):
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

        if "to_delete" in data and isinstance(data["to_delete"], list):
            for delete_id in data["to_delete"]:
                if delete_id in existing_match_ids:
                    cur.execute("DELETE FROM QuestionMatches WHERE match_id = %s;", (delete_id,))

    # Commit all changes and close the connection
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

    conn = current_app.db_connection
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


# ADD Attachment to Question
#this needs to be tested for the supabase buckets NOT FINISHED
@question_bp.route('/questions/<int:question_id>/attachment', methods=['POST'])
def upload_attachment(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    
    conn = current_app.config['get_db_connection']()
    cur = conn.cursor()
    
    # Ensure question exists and is owned by the user
    cur.execute("SELECT owner_id FROM Questions WHERE id = %s;", (question_id,))
    question = cur.fetchone()
    if not question:
        return jsonify({"error": "Question not found."}), 404
    if question[0] != user_id:
        return jsonify({"error": "Unauthorized."}), 403
    
    # Handle file upload
    if 'file' not in request.files:
        return jsonify({"error": "No file provided."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    
    filename = secure_filename(file.filename)
    
    # Define Supabase storage path (assuming bucket is set up)
    supabase_client = current_app.config['get_supabase_client']()
    bucket_name = 'attachments'
    file_path = f"questions/{question_id}/{filename}"
    
    # Upload to Supabase Storage
    try:
        res = supabase_client.storage.from_(bucket_name).upload(file_path, file.stream, file.content_type)
        if 'error' in res:
            return jsonify({"error": "File upload failed."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Store attachment metadata in the database
    cur.execute("INSERT INTO Attachments (name, filepath) VALUES (%s, %s) RETURNING attachments_id;", (filename, file_path))
    attachment_id = cur.fetchone()[0]
    
    # Link attachment to the question
    cur.execute("UPDATE Questions SET attachment_id = %s WHERE id = %s;", (attachment_id, question_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({"message": "Attachment uploaded successfully.", "attachment_id": attachment_id}), 201
