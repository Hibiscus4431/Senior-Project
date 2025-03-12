from flask import Blueprint, request, jsonify, current_app
from auth import authorize_request
from psycopg2 import sql

# Create Blueprint for feedback
feedback_bp = Blueprint('feedback', __name__)

