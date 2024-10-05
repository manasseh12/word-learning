import sqlite3
import os

# Path to the new database
db_path = r"C:\backups_projects\student_activity_projects\student_activity.db"
db_directory = os.path.dirname(db_path)

# Check if the directory exists, create it if not
if not os.path.exists(db_directory):
    try:
        os.makedirs(db_directory)
        print(f"Directory {db_directory} created successfully.")
    except OSError as e:
        print(f"Error creating directory {db_directory}: {e}")
else:
    print(f"Directory {db_directory} already exists.")

# Try to connect to the new database and create table
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the `user_progress` table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subtopic_id INTEGER NOT NULL,
        correct_answers INTEGER DEFAULT 0,
        total_questions INTEGER DEFAULT 20,
        percentage REAL DEFAULT 0.0,
        completed BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (subtopic_id) REFERENCES subtopics(id)
    );
    """
    cursor.execute(create_table_query)

    # Commit the changes
    conn.commit()
    print(f"New student_activity.db created successfully at {db_path} with the user_progress table.")

except sqlite3.Error as e:
    print(f"Error creating database or table: {e}")

finally:
    if conn:
        conn.close()
