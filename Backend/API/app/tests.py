from flask import Blueprint, jsonify, request, current_app
from app.auth import authorize_request
from app.config import Config

test_bp = Blueprint("test", __name__)

# Still under review/ Not Completed yet
@test_bp.route("/get_tests", methods=["GET"])
def get_tests():
    """Fetches all tests from the database."""
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]  # Return error if authorization fails
    
    try:
        db_conn = Config.get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM tests")  # Adjust columns as needed
        tests = cursor.fetchall()
        cursor.close()
        
        # Convert result to a list of dictionaries
        test_list = [
            {"test_id": row[0], "name": row[4], "status": row[5], "points_total": row[6], "estimated_time": row[7], "filename": row[8], "test_instructions": row[9]}  # Adjust based on table schema
            for row in tests
        ]
        
        return jsonify({"tests": test_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@test_bp.route("/add_test", methods=["POST"])
def add_test():
    """Adds a new test to the database."""
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]  # Return error if authorization fails
    
    user_id = auth_data['user_id']
    data = request.get_json()
    required_fields = ["course_id", "name"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        db_conn = Config.get_db_connection()
        cursor = db_conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO tests (course_id, template_id, user_id, name, status, points_total, estimated_time, filename, test_instrucutions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING tests_id
            """,
            (
                data["course_id"],
                data.get("template_id"),
                user_id,
                data["name"],
                data.get("status", "Draft"),
                data.get("points_total", 0),
                data.get("estimated_time"),
                data.get("filename"),
                data.get("test_instructions"),
            )
        )
        
        test_id = cursor.fetchone()[0]
        db_conn.commit()
        cursor.close()
        
        return jsonify({"message": "Test added successfully", "test_id": test_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500