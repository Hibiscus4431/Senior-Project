from flask import Blueprint, request, jsonify, current_app

api_bp = Blueprint("api", __name__)

# This is a sample route that gets all users from the Supabase table
# it's similar to the one you have is database.py

@api_bp.route("/users", methods=["GET"])
def get_users():
    # Use `current_app` instead of creating a new app instance
    response = current_app.supabase.table("users").select("*").execute()
    return jsonify(response.data)
