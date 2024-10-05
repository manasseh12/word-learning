import sqlite3

# Function to calculate and update progress for a user and subtopic
def update_progress(user_id, subtopic_id, correct_answers, db_path):
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
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Function to fetch progress for a user and subtopic
def get_progress(user_id, subtopic_id, db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT percentage, completed FROM user_progress WHERE user_id = ? AND subtopic_id = ?",
        (user_id, subtopic_id)
    )
    progress = cursor.fetchone()
    
    conn.close()
    
    # Return the progress percentage and completion status
    if progress:
        return {"percentage": progress[0], "completed": bool(progress[1])}
    else:
        return {"percentage": 0, "completed": False}
