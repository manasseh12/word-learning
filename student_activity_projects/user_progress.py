import sqlite3

# Function to ensure the user_progress table exists
def ensure_table_exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the `user_progress` table if it doesn't exist
    cursor.execute("""
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
    """)
    
    conn.commit()
    conn.close()

# Function to calculate and update progress for a user and subtopic
def update_progress(user_id, subtopic_id, correct_answers, db_path):
    # Ensure the table exists before updating progress
    ensure_table_exists(db_path)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Calculate the percentage of completion
    total_questions = 20  # As per your setup
    percentage = (correct_answers / total_questions) * 100

    # Mark as completed if 100%
    completed = 1 if percentage == 100 else 0

    # Check if progress already exists for this user and subtopic
    cursor.execute(
        "SELECT id FROM user_progress WHERE user_id = ? AND subtopic_id = ?",
        (user_id, subtopic_id)
    )
    progress_record = cursor.fetchone()

    if progress_record:
        # Update existing progress
        cursor.execute(
            "UPDATE user_progress SET correct_answers = ?, percentage = ?, completed = ? WHERE user_id = ? AND subtopic_id = ?",
            (correct_answers, percentage, completed, user_id, subtopic_id)
        )
    else:
        # Insert new progress
        cursor.execute(
            "INSERT INTO user_progress (user_id, subtopic_id, correct_answers, percentage, completed) VALUES (?, ?, ?, ?, ?)",
            (user_id, subtopic_id, correct_answers, percentage, completed)
        )

    conn.commit()
    conn.close()

# Function to fetch progress for a user and subtopic
def get_progress(user_id, subtopic_id, db_path):
    # Ensure the table exists before fetching progress
    ensure_table_exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT percentage, completed FROM user_progress WHERE user_id = ? AND subtopic_id = ?",
        (user_id, subtopic_id)
    )
    progress = cursor.fetchone()

    conn.close()

    if progress:
        return {"percentage": progress[0], "completed": bool(progress[1])}
    else:
        return {"percentage": 0, "completed": False}
