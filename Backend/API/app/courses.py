from flask import Blueprint, request, jsonify
from .auth import authorize_request
from psycopg2 import sql
from app.config import Config

# Create Blueprint for courses
course_bp = Blueprint('courses', __name__)

# CREATE Course
#only teachers can create courses
@course_bp.route('', methods=['POST'])
def create_course():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    # Since auth_data is not a tuple, it must be a dict with valid user info
    user_id = auth_data.get("user_id")
    role = auth_data.get("role")

    # Ensure only teachers can create courses
    if role != "teacher":
        return jsonify({"error": "Permission denied"}), 403

    data = request.get_json()
    raw_name = data.get("course_name")
    course_number = data.get("course_number")
    textbook_id = data.get("textbook_id")

    if not raw_name or not textbook_id:
        return jsonify({"error": "Missing course_name or textbook_id"}), 400
    
    course_name = f"{raw_name.strip()} {course_number.strip()}" if course_number else raw_name.strip()

    # Connect to PostgreSQL
    conn = Config.get_db_connection()
    cursor = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO Courses (course_name, teacher_id, textbook_id)
        VALUES (%s, %s, %s) RETURNING course_id;
    """)
    cursor.execute(insert_query, (course_name, user_id, textbook_id))
    course_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Course created successfully", "course_id": course_id}), 201

# GET Courses by teacher_id
@course_bp.route('', methods=['GET'])
def get_courses():
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    role = auth_data.get("role")

    if role != "teacher":
        return jsonify({"error": "Permission denied"}), 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT course_id, course_name, teacher_id, textbook_id FROM Courses WHERE teacher_id = %s;
    """)

    cursor.execute(query, (user_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert tuples to a list of dicts for JSON serialization
    courses_list = [
        {
            "course_id": row[0],
            "course_name": row[1],
            "teacher_id": str(row[2]),  # Convert UUID to string
            "textbook_id": row[3]
        }
        for row in courses
    ]

    return jsonify(courses_list), 200


# GET Course by course_id
@course_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    role = auth_data.get("role")

    if role != "teacher":
        return jsonify({"error": "Permission denied"}), 403

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT course_id, course_name, teacher_id, textbook_id FROM Courses WHERE course_id = %s AND teacher_id = %s;
    """)

    cursor.execute(query, (course_id, user_id))
    course = cursor.fetchone()

    cursor.close()
    conn.close()

    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Convert tuple to dictionary for JSON response
    course_data = {
        "course_id": course[0],
        "course_name": course[1],
        "teacher_id": str(course[2]),
        "textbook_id": course[3]
    }

    return jsonify(course_data), 200


# UPDATE Course by course_id
@course_bp.route('<int:course_id>', methods=['PATCH'])
def update_course(course_id):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    user_id = auth_data.get("user_id")
    role = auth_data.get("role")

    if role != "teacher":
        return jsonify({"error": "Permission denied"}), 403

    data = request.get_json()
    course_name = data.get("course_name")
    textbook_id = data.get("textbook_id")

    if not course_name and not textbook_id:
        return jsonify({"error": "Missing course_name or textbook_id"}), 400

    conn = Config.get_db_connection()
    cursor = conn.cursor()

    # Ensure course exists and is owned by user
    cursor.execute("SELECT * FROM Courses WHERE course_id = %s AND teacher_id = %s", (course_id, user_id))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        conn.close()
        return jsonify({"error": "Course not found"}), 404

    # Dynamically build the update query
    update_fields = []
    values = []

    if course_name:
        update_fields.append("course_name = %s")
        values.append(course_name)
    if textbook_id:
        update_fields.append("textbook_id = %s")
        values.append(textbook_id)

    values.append(course_id)

    update_query = f"""
        UPDATE Courses SET {", ".join(update_fields)}
        WHERE course_id = %s;
    """

    cursor.execute(update_query, tuple(values))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Course updated successfully"}), 200

# DELETE Course by course_id
# we wont have a delete course rn we will delete through supabase



