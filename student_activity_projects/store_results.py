import sqlite3

# Function to store quiz results in a separate database
def store_quiz_results(user_id, subject, topic, subtopic, score, total_questions, correct_answers, time_taken):
    # Connect to the quiz_results database
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            topic TEXT,
            subtopic TEXT,
            score INTEGER,
            total_questions INTEGER,
            correct_answers INTEGER,
            time_taken INTEGER,
            submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert quiz results into the table
    cursor.execute('''
        INSERT INTO quiz_results (user_id, subject, topic, subtopic, score, total_questions, correct_answers, time_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, subject, topic, subtopic, score, total_questions, correct_answers, time_taken))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

