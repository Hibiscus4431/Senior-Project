import psycopg2
import xml.etree.ElementTree as ET
import uuid

# Database connection settings
DB_PARAMS = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

# File paths
QTI_FILE_PATH = "/mnt/data/g8aa81318d31368a82347151de2558aa4.xml"

def connect_db():
    """Establish a database connection"""
    return psycopg2.connect(**DB_PARAMS)

def create_import_entry(file_path, owner_id, test_id):
    """Creates an entry in QTI_Imports to track import status"""
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO QTI_Imports (file_path, status, owner_id, test_id)
    VALUES (%s, 'pending', %s, %s)
    RETURNING import_id;
    """
    cursor.execute(query, (file_path, owner_id, test_id))
    import_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    
    return import_id

def parse_qti_questions(test_id):
    """Parses QTI XML and extracts questions"""
    tree = ET.parse(QTI_FILE_PATH)
    root = tree.getroot()
    namespace = {'qt': 'http://www.imsglobal.org/xsd/ims_qtiasiv1p2'}

    questions = []
    order_num = 1  # Track order in test

    for item in root.findall(".//qt:item", namespace):
        question_id = str(uuid.uuid4())  # Generate a unique ID
        question_text = item.find(".//qt:mattext", namespace).text
        question_type = item.find(".//qt:qtimetadatafield[qt:fieldlabel='question_type']/qt:fieldentry", namespace).text
        points_possible = int(float(item.find(".//qt:qtimetadatafield[qt:fieldlabel='points_possible']/qt:fieldentry", namespace).text))

        # Extract correct answer
        correct_answer_node = item.find(".//qt:respcondition/qt:conditionvar/qt:varequal", namespace)
        correct_answer = correct_answer_node.text if correct_answer_node is not None else None

        # Convert QTI types to match DB types
        type_map = {
            "multiple_choice_question": "Multiple Choice",
            "true_false_question": "True/False",
            "essay_question": "Essay",
            "fill_in_multiple_blanks_question": "Fill in the Blank",  # Updated here
            "matching_question": "Matching"
        }
        question_type_db = type_map.get(question_type, "Short Answer")  # Default to Short Answer if unknown

        questions.append((question_id, test_id, question_text, question_type_db, points_possible, correct_answer, order_num))
        order_num += 1  # Increment order

    return questions

def insert_questions(questions, owner_id):
    """Inserts extracted questions into Questions table"""
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Questions (id, question_text, type, default_points, owner_id, source)
    VALUES (%s, %s, %s, %s, %s, 'canvas_qti')
    RETURNING id;
    """

    question_ids = []
    for question in questions:
        question_id, test_id, text, qtype, points, answer, order_num = question
        cursor.execute(query, (question_id, text, qtype, points, owner_id))
        db_question_id = cursor.fetchone()[0]  # Get the actual question ID
        question_ids.append((test_id, db_question_id, points, order_num))

    conn.commit()
    cursor.close()
    conn.close()

    return question_ids

def insert_test_metadata(test_questions):
    """Links questions to the test in Test_MetaData"""
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO Test_MetaData (test_id, question_id, points, order_num)
    VALUES (%s, %s, %s, %s);
    """
    cursor.executemany(query, test_questions)
    
    conn.commit()
    cursor.close()
    conn.close()

def update_import_status(import_id, status):
    """Updates the status of the QTI import"""
    conn = connect_db()
    cursor = conn.cursor()

    query = "UPDATE QTI_Imports SET status = %s WHERE import_id = %s;"
    cursor.execute(query, (status, import_id))

    conn.commit()
    cursor.close()
    conn.close()

def main(owner_id, test_id):
    """Main function to handle QTI import"""
    
    # Step 1: Log the import
    import_id = create_import_entry(QTI_FILE_PATH, owner_id, test_id)

    try:
        # Step 2: Parse QTI questions
        questions = parse_qti_questions(test_id)

        if not questions:
            raise Exception("No questions found in QTI file.")

        # Step 3: Insert questions into database
        test_questions = insert_questions(questions, owner_id)

        # Step 4: Link questions to test
        insert_test_metadata(test_questions)

        # Step 5: Update import status to 'processed'
        update_import_status(import_id, "processed")

        print("QTI import successful.")
    
    except Exception as e:
        # Step 6: Update import status to 'failed' if error occurs
        update_import_status(import_id, "failed")
        print(f"Import failed: {e}")

if __name__ == "__main__":
    # Example usage
    owner_id = 1  # This should come from the authenticated user
    test_id = 101  # This should be generated when the test is created

    main(owner_id, test_id)
