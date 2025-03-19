from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__)

def authorize_request():
    """Extracts and verifies the JWT token from the request headers."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Missing or invalid token"}, 401

    try:
        # ✅ Extract token after "Bearer "
        jwt_token = auth_header.split(" ")[1]
        secret_key = os.getenv("JWT_SECRET")

        # ✅ Decode the JWT token
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        return decoded_token  # ✅ Contains user_id & role

    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

# ✅ 1️⃣ Create a User (Backend Only)
@auth_bp.route('/create_user', methods=['POST'])
def create_user():
    """Creates a user in Supabase Auth and stores metadata in PostgreSQL."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if not username or not password or role not in ["teacher", "publisher", "webmaster"]:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # ✅ 1️⃣ Create User in Supabase Auth
        supabase_client = current_app.supabase  # ✅ Using current_app to access Supabase
        response = supabase_client.auth.admin.create_user({
            "email": f"{username}@example.com",  # Supabase requires an email
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "username": username,
                "role": role
            }
        })

        if not response.user:
            return jsonify({"error": "Failed to create user in Supabase"}), 400

        user_id = response.user.id  # Supabase assigns a UUID

        # ✅ 2️⃣ Insert User into PostgreSQL Users Table
        db_conn = current_app.db_connection  # ✅ Using current_app to access PostgreSQL
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO Users (user_id, username, role) VALUES (%s, %s, %s)",
            (user_id, username, role)
        )
        db_conn.commit()
        cursor.close()

        return jsonify({"message": "User created successfully", "user_id": user_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ 2️⃣ User Login (Frontend)
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticates a user and returns a JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # ✅ 1️⃣ Authenticate User with Supabase
        supabase_client = current_app.supabase
        response = supabase_client.auth.sign_in_with_password({
            "email": f"{username}@example.com",
            "password": password
        })

        if not response.session or not response.session.access_token:
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = response.session.access_token

        # ✅ 2️⃣ Retrieve User Metadata from PostgreSQL
        db_conn = current_app.db_connection
        cursor = db_conn.cursor()
        cursor.execute("SELECT user_id, role FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({"error": "User not found in database"}), 404

        user_id, role = user

        # ✅ 3️⃣ Generate JWT Token
        secret_key = os.getenv("JWT_SECRET")  # Use env variable for security
        token_payload = {
            "user_id": str(user_id),
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        token = jwt.encode(token_payload, secret_key, algorithm="HS256")

        return jsonify({"message": "Login successful", "token": token, "user_id": user_id, "role": role})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/protected', methods=['GET'])
def protected():
    """Example of a protected route that requires a valid JWT."""
    auth_data = authorize_request()

    if isinstance(auth_data, tuple):  # ✅ If token is invalid, return error
        return jsonify(auth_data[0]), auth_data[1]

    return jsonify({
        "message": "Access granted",
        "user_id": auth_data["user_id"],
        "role": auth_data["role"]
    })
