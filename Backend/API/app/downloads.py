from flask import Blueprint, Response, jsonify
from .auth import authorize_request
from app.config import Config
import csv
import io

# Create the download blueprint
download_bp = Blueprint('downloads', __name__)

# Helper: fetch table rows as CSV
def fetch_table_as_csv(query):
    conn = Config.get_db_connection()
    cursor = conn.cursor()

    cursor.execute(query)
    headers = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)

    return output.getvalue()

# Route to download specific table as CSV
@download_bp.route('/<string:data_type>', methods=['GET'])
def download_table(data_type):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    # Map valid types to SQL queries
    table_queries = {
        "users": "SELECT * FROM users",
        "textbooks": "SELECT * FROM textbooks",
        "courses": "SELECT * FROM courses",
        "questions": "SELECT * FROM questions",
        "tests": "SELECT * FROM tests"
    }

    if data_type == "all":
        return download_all_tables()

    if data_type not in table_queries:
        return jsonify({"error": "Invalid table requested"}), 400

    try:
        csv_data = fetch_table_as_csv(table_queries[data_type])
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={"Content-Disposition": f"attachment; filename={data_type}.csv"}
        )
    except Exception as e:
        print(f"Download failed for {data_type}: {e}")
        return jsonify({"error": "Failed to download data"}), 500

# Special: Combine all tables into one .txt-style CSV dump
def download_all_tables():
    combined_output = io.StringIO()
    tables = ["users", "textbooks", "courses", "questions", "tests"]

    try:
        for table in tables:
            combined_output.write(f"=== {table.upper()} ===\n")
            csv_data = fetch_table_as_csv(f"SELECT * FROM {table}")
            combined_output.write(csv_data + "\n\n")

        return Response(
            combined_output.getvalue(),
            mimetype='text/plain',
            headers={"Content-Disposition": "attachment; filename=all_data.txt"}
        )
    except Exception as e:
        print(f"Download-all failed: {e}")
        return jsonify({"error": "Failed to download all data"}), 500
