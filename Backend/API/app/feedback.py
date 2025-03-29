from flask import Blueprint, request, jsonify
from auth import authorize_request
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

    if not (test_id or question_id):
        return jsonify({"error": "Either test_id or question_id must be provided"}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Feedback (test_id, question_id, comment_field, user_id)
        VALUES (%s, %s, %s, %s)
        RETURNING feedback_id
    """, (test_id, question_id, comment_field, str(user_id)))
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
    cur.execute("SELECT * FROM Feedback WHERE test_id = %s", (test_id,))
    feedback = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(row) for row in feedback]), 200

# Get feedback for a specific question 
@feedback_bp.route('/question/<int:question_id>', methods=['GET'])
def get_feedback_by_question(question_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Feedback WHERE question_id = %s", (question_id,))
    feedback = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(row) for row in feedback]), 200

# Update feedback 
@feedback_bp.route('/update/<int:feedback_id>', methods=['PATCH'])
def update_feedback(feedback_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    comment = request.get_json().get("comment_field")

    conn = Config.get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Feedback
        SET comment_field = %s
        WHERE feedback_id = %s AND user_id = %s
        RETURNING feedback_id
    """, (comment, feedback_id, str(user_id)))
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
    cur.execute("""
        DELETE FROM Feedback
        WHERE feedback_id = %s AND user_id = %s
    """, (feedback_id, str(user_id)))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return jsonify({"message": "Feedback deleted"}), 200
        
    return jsonify({"error": "Feedback not found or unauthorized"}), 403
