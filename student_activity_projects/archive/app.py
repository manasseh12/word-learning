from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to the main gcse_maths_quiz.db
def connect_db():
    conn = sqlite3.connect('gcse_maths_quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

# Connect to the new quiz_results.db (for quiz result storage)
def connect_new_db():
    conn = sqlite3.connect('quiz_results.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create new database for quiz results
def create_new_database():
    conn = connect_new_db()
    cursor = conn.cursor()

    # Create the table for quiz results if it does not already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            score INTEGER,
            date_taken TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("New database and table for quiz results created.")

# Insert quiz results into the new database
def insert_test_results(username, subject, score):
    conn = connect_new_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO quiz_results (username, subject, score, date_taken)
        VALUES (?, ?, ?, ?)
    ''', (username, subject, score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()
    print("Test results inserted into the new database.")

# Root route that redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash('User account does not exist. Please register.', 'error')
            return redirect(url_for('login'))

        if not check_password_hash(user['password'], password):
            flash('Invalid login. Incorrect password.', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('profile'))

    return render_template('login.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (first_name, last_name, username, email, password) VALUES (?, ?, ?, ?, ?)',
                           (first_name, last_name, username, email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists.")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Profile page to show subjects and quiz attempts
@app.route('/profile')
def profile():
    if 'user_id' in session:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Fetch all subjects
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='users'")
        subjects = cursor.fetchall()

        # Fetch student activities (grouped by subject and attempt)
        cursor.execute('''SELECT subject, topic, subtopic, score, date_time, attempt 
                          FROM student_activities WHERE user_id = ? 
                          ORDER BY subject, date_time DESC''', (session['user_id'],))
        activities = cursor.fetchall()
        conn.close()

        # Organize activities by subject
        student_activities = {}
        for activity in activities:
            subject = activity['subject']
            if subject not in student_activities:
                student_activities[subject] = []
            student_activities[subject].append({
                'topic': activity['topic'],
                'subtopic': activity['subtopic'],
                'score': activity['score'],
                'date_time': activity['date_time'],
                'attempt': activity['attempt']
            })

        return render_template('profile.html', username=session['username'], subjects=subjects, student_activities=student_activities)
    return redirect(url_for('login'))

# Submit quiz and record activities and test results in new database
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    subtopic = request.form.get('subtopic')
    score = request.form.get('score')

    # Insert quiz results into the new database
    insert_test_results(username, subject, int(score))

    flash("Quiz submitted successfully! Results stored.")
    return redirect(url_for('quiz_result_page'))

# Quiz result page
@app.route('/quiz_result_page')
def quiz_result_page():
    return render_template('result.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    # Ensure the new quiz results database is created when the app starts
    create_new_database()
    app.run(debug=True)
