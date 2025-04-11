from flask import Blueprint, Response, jsonify
from .auth import authorize_request
from app.config import Config
import csv
import io

download_bp = Blueprint('downloads', __name__)

def fetch_table_csv(query, params=None):
    conn = Config.get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params or [])
    headers = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)

    return output.getvalue()

@download_bp.route('/<string:data_type>', methods=['GET'])
def download_table(data_type):
    auth_data = authorize_request()
    if isinstance(auth_data, tuple):
        return jsonify(auth_data[0]), auth_data[1]

    table_map = {
        "users": "SELECT * FROM Users",
        "textbooks": "SELECT * FROM Textbook",
        "courses": "SELECT * FROM Courses",
        "questions": "SELECT * FROM Questions",
        "tests": "SELECT * FROM Tests"
    }

    if data_type == "all":
        return download_all_tables(table_map)

    if data_type not in table_map:
        return jsonify({"error": "Invalid download type"}), 400

    try:
        csv_data = fetch_table_csv(table_map[data_type])
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={"Content-Disposition": f"attachment; filename={data_type}.csv"}
        )
    except Exception as e:
        print(f"Download error for {data_type}:", e)
        return jsonify({"error": "Failed to fetch data"}), 500

def download_all_tables(table_map):
    output = io.StringIO()

    for name, query in table_map.items():
        output.write(f"=== {name.upper()} ===\n")
        try:
            csv_section = fetch_table_csv(query)
            output.write(csv_section + "\n\n")
        except Exception as e:
            output.write(f"Failed to load {name}: {str(e)}\n\n")

    return Response(
        output.getvalue(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment; filename=all_data.txt"}
    )
