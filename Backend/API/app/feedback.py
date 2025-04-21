from flask import Blueprint, request, jsonify
from .auth import authorize_request
from psycopg2 import sql
from app.config import Config   
import psycopg2.extras
# Create Blueprint for feedback
feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/create', methods=['POST'])
def create_feedback():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    # Since auth_data is not a tuple, it must be a dict with valid user info
    user_id = auth_data.get("user_id")
    role = auth_data.get("role")

    data = request.get_json()

    test_id = data.get("test_id")
    question_id = data.get("question_id")
    comment_field = data.get("comment_field")
    rating = data.get("rating")

    if not (test_id or question_id):
        return jsonify({"error": "Either test_id or question_id must be provided"}), 400

    # Optional: validate rating if present
    if rating is not None:
        try:
            rating = float(rating)
            if rating < 0 or rating > 100:
                return jsonify({"error": "Rating must be between 0 and 100"}), 400
        except ValueError:
            return jsonify({"error": "Invalid rating format"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Feedback (test_id, question_id, comment_field, rating, user_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING feedback_id
    """, (test_id, question_id, comment_field, rating, str(user_id)))

    feedback_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"message": "Feedback created", "feedback_id": feedback_id}), 201

# Get feedback for a specific test
@feedback_bp.route('/test/<int:test_id>', methods=['GET'])
def get_feedback_by_test(test_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT 
            f.comment_field,
            f.rating,
            u.username,
            u.role,
            AVG(f.rating) OVER () AS class_average
        FROM Feedback f
        JOIN Users u ON f.user_id = u.user_id
        WHERE f.test_id = %s
    """, (test_id,))

    feedback = cur.fetchall()
    cur.close()
    conn.close()

    results = {
        "test_id": test_id,
        "class_average": None,
        "feedback": []
    }

    for row in feedback:
        if results["class_average"] is None and row["class_average"] is not None:
            results["class_average"] = float(row["class_average"])

        entry = {
            "username": row["username"],
            "comment": row["comment_field"],
            "role": row["role"]
        }

        if row["rating"] is not None:
            entry["rating"] = float(row["rating"])

        results["feedback"].append(entry)

    return jsonify(results), 200


# Get feedback for a specific question with user info
@feedback_bp.route('/question/<int:question_id>', methods=['GET'])
def get_feedback_by_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT 
            f.comment_field,
            f.rating,
            u.username,
            u.role AS user_role,
            AVG(f.rating) OVER () AS class_average
        FROM Feedback f
        JOIN Users u ON f.user_id = u.user_id
        WHERE f.question_id = %s
    """, (question_id,))
    
    feedback = cur.fetchall()
    cur.close()
    conn.close()

    results = {
        "question_id": question_id,
        "class_average": None,
        "feedback": []
    }

    for row in feedback:
        # Set class average once, if it exists
        if results["class_average"] is None and row["class_average"] is not None:
            results["class_average"] = float(row["class_average"])

        feedback_entry = {
            "username": row["username"],
            "comment": row["comment_field"],
            "role": row["user_role"]
        }

        # Only include rating if it's not null
        if row["rating"] is not None:
            feedback_entry["rating"] = float(row["rating"])

        results["feedback"].append(feedback_entry)

    return jsonify(results), 200


# Update feedback 
@feedback_bp.route('/update/<int:feedback_id>', methods=['PATCH'])
def update_feedback(feedback_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    data = request.get_json()

    comment = data.get("comment_field")
    rating = data.get("rating")

    # Optional: validate rating if provided
    if rating is not None:
        try:
            rating = float(rating)
            if rating < 0 or rating > 100:
                return jsonify({"error": "Rating must be between 0 and 100"}), 400
        except ValueError:
            return jsonify({"error": "Invalid rating format"}), 400

    # Build the update fields dynamically
    fields = []
    values = []

    if comment is not None:
        fields.append("comment_field = %s")
        values.append(comment)
    
    if rating is not None:
        fields.append("rating = %s")
        values.append(rating)

    if not fields:
        return jsonify({"error": "No update fields provided"}), 400

    values.extend([feedback_id, str(user_id)])

    query = f"""
        UPDATE Feedback
        SET {', '.join(fields)}
        WHERE feedback_id = %s AND user_id = %s
        RETURNING feedback_id
    """

    conn = Config.get_db_connection()
    cur = conn.cursor()
    cur.execute(query, values)
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated:
        return jsonify({"message": "Feedback updated"}), 200
    return jsonify({"error": "Feedback not found or unauthorized"}), 403


# Delete feedback
@feedback_bp.route('/delete/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")

    conn = Config.get_db_connection()
    cur = conn.cursor()

    # Add RETURNING clause here
    cur.execute("""
        DELETE FROM Feedback
        WHERE feedback_id = %s AND user_id = %s
        RETURNING feedback_id
    """, (feedback_id, str(user_id)))

    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted:
        return jsonify({"message": "Feedback deleted"}), 200
    return jsonify({"error": "Feedback not found or unauthorized"}), 403

# Get feedback for a specific testbank 
@feedback_bp.route('/<int:testbank_id>/questions-with-feedback', methods=['GET'])
def get_questions_with_feedback_by_testbank(testbank_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT
            q.id AS question_id,
            q.question_text,
            f.comment_field,
            f.rating,
            u.username,
            u.role,
            AVG(f.rating) OVER (PARTITION BY q.id) AS class_average
        FROM test_bank_questions tbq
        JOIN questions q ON tbq.question_id = q.id
        JOIN feedback f ON f.question_id = q.id
        JOIN users u ON f.user_id = u.user_id
        WHERE tbq.test_bank_id = %s
        ORDER BY q.id, f.feedback_id
    """, (testbank_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = {}

    for row in rows:
        qid = row["question_id"]
        if qid not in results:
            results[qid] = {
                "question_id": qid,
                "question_text": row["question_text"],
                "class_average": float(row["class_average"]) if row["class_average"] is not None else None,
                "feedback": []
            }

        feedback_entry = {
            "comment": row["comment_field"],
            "username": row["username"],
            "role": row["role"]
        }

        if row["rating"] is not None:
            feedback_entry["rating"] = float(row["rating"])

        results[qid]["feedback"].append(feedback_entry)

    return jsonify(list(results.values())), 200


# Get feedback to list only questions with feedback
@feedback_bp.route('/questions-with-feedback', methods=['GET'])
def get_all_questions_with_feedback():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT DISTINCT q.id, q.question_text
        FROM questions q
        JOIN feedback f ON f.question_id = q.id
    """)

    questions = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([dict(q) for q in questions]), 200

