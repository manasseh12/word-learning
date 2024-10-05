import sqlite3

# Path to your database (update this if necessary)
db_path = r"C:\backups_projects\student_activity_projects\gcse_maths_quiz.db"

def insert_test_data():
    try:
        # Connect to the SQLite3 database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Example data to insert
        test_data = [
            (1, 2, 18, 20, 90.0, 1),  # user_id=1, subtopic_id=2, correct_answers=18, total_questions=20, percentage=90%, completed=1
            (2, 3, 15, 20, 75.0, 0),  # user_id=2, subtopic_id=3, correct_answers=15, total_questions=20, percentage=75%, completed=0
            (3, 1, 20, 20, 100.0, 1)  # user_id=3, subtopic_id=1, correct_answers=20, total_questions=20, percentage=100%, completed=1
        ]

        # Insert data into the user_progress table
        insert_query = """
        INSERT INTO user_progress (user_id, subtopic_id, correct_answers, total_questions, percentage, completed)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.executemany(insert_query, test_data)

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the connection
        conn.close()

# Run the function to insert test data
insert_test_data()
