import sqlite3

def connect_db():
    conn = sqlite3.connect('gcse_maths_quiz.db')
    return conn

def record_user_activity(user_id, subject, topic, subtopic, score, attempt):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO student_activities (user_id, subject, topic, subtopic, score, date_time, attempt)
                      VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)''', 
                   (user_id, subject, topic, subtopic, score, attempt))
    conn.commit()
    conn.close()

def get_user_activities(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''SELECT subject, topic, subtopic, score, date_time, attempt 
                      FROM student_activities 
                      WHERE user_id = ? 
                      ORDER BY date_time DESC''', 
                   (user_id,))
    activities = cursor.fetchall()
    conn.close()
    return activities
