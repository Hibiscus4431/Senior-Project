from flask import Blueprint, request, jsonify, current_app
from .auth import authorize_request
from psycopg2 import sql
from app.config import Config
# Create Blueprint for textbook 
textbook_bp = Blueprint('textbooks', __name__)

# CREATE Textbook
@textbook_bp.route('', methods=['POST'])
def create_textbook():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    publisher_id = auth_data['user_id']
    print("Incoming request data:", request.data)  # Debug step before processing JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON input"}), 400

    required_fields = ['textbook_title', 'textbook_author', 'textbook_version', 'textbook_isbn']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields."}), 400

    conn = Config.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO Textbook (textbook_title, textbook_author, textbook_version, textbook_isbn, publisher_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING textbook_id;
    """, (data['textbook_title'], data['textbook_author'], data['textbook_version'], data['textbook_isbn'], publisher_id))
    
    textbook_id = cur.fetchone()
    if textbook_id is None:
        return jsonify({"error": "Failed to insert textbook"}), 500
    textbook_id = textbook_id[0]  # Now it's safe to access
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Textbook created successfully", "textbook_id": textbook_id}), 201

# GET Textbook by publisher_id (so all the textbooks that a publisher has created)
@textbook_bp.route('', methods=['GET'])
def get_textbooks():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    publisher_id = auth_data['user_id']
    
    conn = Config.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT textbook_id, textbook_title, textbook_author, textbook_version, textbook_isbn
        FROM Textbook
        WHERE publisher_id = %s;
    """, (publisher_id,))
    
    rows = cur.fetchall()
    textbooks = [
        {"id": row[0], "title": row[1], "author": row[2], "version": row[3], "isbn": row[4]}
        for row in rows
    ]
    cur.close()
    conn.close()
    
    return jsonify({"textbooks": textbooks}), 200

# GET Textbook by textbook_id 
@textbook_bp.route('/<int:textbook_id>', methods=['GET'])
def get_textbook(textbook_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT textbook_id, textbook_title, textbook_author, textbook_version, textbook_isbn
        FROM Textbook WHERE textbook_id = %s;
    """, (textbook_id,))
    
    textbook = cur.fetchone()
    cur.close()
    conn.close()
    
    if textbook is None:
        return jsonify({"error": "Textbook not found"}), 404

    return jsonify({
        "textbook_id": textbook[0],
        "title": textbook[1],
        "author": textbook[2],
        "version": textbook[3],
        "isbn": textbook[4]
    }), 200

# UPDATE Textbook by textbook_id
@textbook_bp.route('/<int:textbook_id>', methods=['PATCH'])
def update_textbook(textbook_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]
    
    publisher_id = auth_data['user_id']
    data = request.get_json()

    if not data:
        return jsonify({"error": "No fields provided for update."}), 400

    update_fields = []
    values = []
    
    allowed_fields = ["textbook_title", "textbook_author", "textbook_version", "textbook_isbn"]
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            values.append(data[field])

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update."}), 400

    values.append(textbook_id)
    values.append(publisher_id)

    conn = Config.get_db_connection()
    cur = conn.cursor()

    query = f"""
        UPDATE Textbook
        SET {', '.join(update_fields)}
        WHERE textbook_id = %s AND publisher_id = %s
        RETURNING textbook_id, textbook_title, textbook_author, textbook_version, textbook_isbn;
    """

    cur.execute(query, values)
    updated_textbook = cur.fetchone()
    conn.commit()
    
    cur.close()
    conn.close()
    
    if updated_textbook:
        return jsonify({
            "message": "Textbook updated successfully",
            "textbook": {
                "id": updated_textbook[0],
                "title": updated_textbook[1],
                "author": updated_textbook[2],
                "version": updated_textbook[3],
                "isbn": updated_textbook[4]
            }
        }), 200
    else:
        return jsonify({"error": "Textbook not found or you do not have permission to update it."}), 404

# GET all Textbooks (from all the publishers in the system use for teachers to select textbooks for their courses)
@textbook_bp.route('/all', methods=['GET'])
def get_all_textbooks():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    conn = Config.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT textbook_id, textbook_title, textbook_author, textbook_version, textbook_isbn
        FROM Textbook;
    """)
    
    rows = cur.fetchall()
    cur.close()

    textbooks = [
        {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "version": row[3],
            "isbn": row[4]
        }
        for row in rows
    ]

    return jsonify({"textbooks": textbooks}), 200


# DELETE Textbook by textbook_id
# no delete for textbook becaseu a textbook is linked to course and course is linked to question
# so we can't delete a textbook without deleting the course and the questions



