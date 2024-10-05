import sqlite3

# Path to the SQLite3 database
db_path = r"C:\backups_projects\student_activity_projects\gcse_maths_quiz.db"

def reset_user_progress_table_with_username():
    try:
        # Connect to the SQLite3 database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Drop the existing user_progress table
        cursor.execute("DROP TABLE IF EXISTS user_progress")

        # Create a new user_progress table with the username field instead of user_id
        create_query = """
        CREATE TABLE user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            correct_answers INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 20,
            percentage REAL DEFAULT 0.0,
            completed BOOLEAN DEFAULT 0,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        );
        """
        cursor.execute(create_query)
        conn.commit()
        print("New user_progress table with username created successfully.")
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
    finally:
        # Close the database connection
        conn.close()

# Run the function to reset the table with username
reset_user_progress_table_with_username()
