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
@question_bp.route('/questions', methods=['GET'])
def get_questions():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    view_type = request.args.get('view', 'user')  # Default to user's questions
    
    conn = current_app.config['get_db_connection']()
    cur = conn.cursor()
    
    if view_type == 'published':
        query = """
        SELECT q.*, c.name AS course_name, t.title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.id
        LEFT JOIN Textbooks t ON q.textbook_id = t.id
        WHERE q.is_published = TRUE;
        """
        cur.execute(query)
    elif view_type == 'canvas':
        query = """
        SELECT q.*, c.name AS course_name, t.title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.id
        LEFT JOIN Textbooks t ON q.textbook_id = t.id
        WHERE q.source = 'canvas_qti';
        """
        cur.execute(query)
    else:
        query = """
        SELECT q.*, c.name AS course_name, t.title AS textbook_title
        FROM Questions q
        LEFT JOIN Courses c ON q.course_id = c.id
        LEFT JOIN Textbooks t ON q.textbook_id = t.id
        WHERE q.owner_id = %s;
        """
        cur.execute(query, (user_id,))
    column_names = [desc[0] for desc in cur.description]  # Get column names
    questions = [dict(zip(column_names, row)) for row in cur.fetchall()]  # Convert to dicts
    
    cur.close()
    conn.close()
    return jsonify({"questions": questions}), 200

# UPDATE Question
@question_bp.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    user_id = auth_data['user_id']
    data = request.get_json()
    
    conn = current_app.config['get_db_connection']()
    cur = conn.cursor()
    
    # Ensure question exists and is not published
    cur.execute("SELECT owner_id, is_published, type FROM Questions WHERE id = %s;", (question_id,))
    question = cur.fetchone()
    if not question:
        return jsonify({"error": "Question not found."}), 404
    if question[1]:
        return jsonify({"error": "Published questions cannot be edited."}), 403
    if question[0] != user_id:
        return jsonify({"error": "Unauthorized."}), 403
    
    # Update question text if provided
    if 'question_text' in data:
        cur.execute("UPDATE Questions SET question_text = %s WHERE id = %s;", (data['question_text'], question_id))
    
    # Update multiple-choice options
    if question[2] == 'Multiple Choice' and 'options' in data and isinstance(data['options'], list):
        cur.execute("DELETE FROM QuestionOptions WHERE question_id = %s;", (question_id,))
        for option in data['options']:
            cur.execute("INSERT INTO QuestionOptions (question_id, option_text, is_correct) VALUES (%s, %s, %s);", 
                        (question_id, option['option_text'], option['is_correct']))
    
    # Update fill-in-the-blank answers
    if question[2] == 'Fill in the Blank' and 'blanks' in data and isinstance(data['blanks'], list):
        cur.execute("DELETE FROM QuestionFillBlanks WHERE question_id = %s;", (question_id,))
        for blank in data['blanks']:
            cur.execute("INSERT INTO QuestionFillBlanks (question_id, correct_text) VALUES (%s, %s);", 
                        (question_id, blank))
    
    # Update matching question pairs
    if question[2] == 'Matching' and 'matches' in data and isinstance(data['matches'], list):
        cur.execute("DELETE FROM QuestionMatches WHERE question_id = %s;", (question_id,))
        for match in data['matches']:
            cur.execute("INSERT INTO QuestionMatches (question_id, prompt_text, match_text) VALUES (%s, %s, %s);", 
                        (question_id, match['prompt_text'], match['match_text']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Question updated successfully."}), 200

# DELETE Question
#for time being, we are not deleting the questions, we are just marking them as deleted 
# we will just hard delte through supabase

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
