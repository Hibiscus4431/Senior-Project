from flask import Blueprint, request, jsonify, current_app

auth_bp = Blueprint("auth", __name__)


# This is just a sample login function that ChatGPT gave me
# I thought it was neat that Supabase has a built-in authentication system

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Authenticate using Supabase
    response = current_app.supabase.auth.sign_in_with_password({"email": email, "password": password})

    if response.get("error"):
        return jsonify({"error": response["error"]["message"]}), 401

    return jsonify({"message": "Login successful!", "user": response["data"]})
