from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Database connection
def connect_db():
    conn = sqlite3.connect('gcse_maths_quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

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

        # Check if the user exists
        if user is None:
            flash('User account does not exist. Please register.', 'error')
            return redirect(url_for('login'))

        # If the user exists, check the password
        if not check_password_hash(user['password'], password):
            flash('Invalid login. Incorrect password.', 'error')
            return redirect(url_for('login'))

        # If username and password are correct, log the user in
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
            # Redirect to login page after successful registration
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists.")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Profile page with collapsible subjects and student activities
@app.route('/profile')
def profile():
    if 'user_id' in session:  # Check if the user is logged in
        conn = connect_db()
        cursor = conn.cursor()
        
        # Fetch all subjects except 'users' table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='users'")
        subjects = cursor.fetchall()
        
        # Fetch student activities grouped by subject
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
            student_activities[subject].append(activity)
        
        return render_template('profile.html', username=session['username'], subjects=subjects, student_activities=student_activities)
    return redirect(url_for('login'))  # Redirect to login page if not logged in

# Topics page for each subject
@app.route('/topics/<subject>')
def topics(subject):
    conn = connect_db()
    cursor = conn.cursor()

    # Dynamically fetch topics based on the selected subject table
    if subject.lower() == 'maths':
        cursor.execute('SELECT DISTINCT topic FROM maths')
    elif subject.lower() == 'biology':
        cursor.execute('SELECT DISTINCT topic FROM biology')
    elif subject.lower() == 'chemistry':
        cursor.execute('SELECT DISTINCT topic FROM chemistry')
    elif subject.lower() == 'physics':
        cursor.execute('SELECT DISTINCT topic FROM physics')
    else:
        flash('Invalid subject selected.')
        return redirect(url_for('profile'))

    topics = cursor.fetchall()
    conn.close()
    return render_template('topics.html', subject=subject, topics=topics)

# Subtopics page for each topic
@app.route('/subtopics/<subject>/<topic>')
def subtopics(subject, topic):
    conn = connect_db()
    cursor = conn.cursor()

    # Dynamically fetch subtopics based on the subject and topic
    if subject.lower() == 'maths':
        cursor.execute('SELECT DISTINCT subtopic FROM maths WHERE topic = ?', (topic,))
    elif subject.lower() == 'biology':
        cursor.execute('SELECT DISTINCT subtopic FROM biology WHERE topic = ?', (topic,))
    elif subject.lower() == 'chemistry':
        cursor.execute('SELECT DISTINCT subtopic FROM chemistry WHERE topic = ?', (topic,))
    elif subject.lower() == 'physics':
        cursor.execute('SELECT DISTINCT subtopic FROM physics WHERE topic = ?', (topic,))
    else:
        flash('Invalid subject selected.')
        return redirect(url_for('profile'))

    subtopics = cursor.fetchall()
    conn.close()
    return render_template('subtopics.html', subject=subject, topic=topic, subtopics=subtopics)

# Questions page for each subtopic
@app.route('/questions/<subject>/<subtopic>/<int:question_id>', methods=['GET', 'POST'])
def questions(subject, subtopic, question_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Dynamically fetch questions based on the subject and subtopic
    if subject.lower() == 'maths':
        cursor.execute('SELECT * FROM maths WHERE subtopic = ?', (subtopic,))
    elif subject.lower() == 'biology':
        cursor.execute('SELECT * FROM biology WHERE subtopic = ?', (subtopic,))
    elif subject.lower() == 'chemistry':
        cursor.execute('SELECT * FROM chemistry WHERE subtopic = ?', (subtopic,))
    elif subject.lower() == 'physics':
        cursor.execute('SELECT * FROM physics WHERE subtopic = ?', (subtopic,))
    else:
        flash('Invalid subject selected.')
        return redirect(url_for('subjects'))

    # Fetch all rows and convert them to dictionaries
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Pass the question data to the questions.html template
    return render_template('questions.html', subject=subject, subtopic=subtopic, questions=questions, current_question=question_id)

# Submit quiz route to record quiz results
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    user_id = session['user_id']  # Assuming the user is logged in
    subject = request.form['subject']
    topic = request.form['topic']
    subtopic = request.form['subtopic']
    score = request.form['score']

    conn = connect_db()
    cursor = conn.cursor()

    # Fetch previous attempts for this quiz
    cursor.execute('SELECT COUNT(*) FROM student_activities WHERE user_id = ? AND subject = ? AND topic = ? AND subtopic = ?',
                   (user_id, subject, topic, subtopic))
    attempts = cursor.fetchone()[0]
    
    # Insert the new activity into the database
    cursor.execute('INSERT INTO student_activities (user_id, subject, topic, subtopic, score, date_time, attempt) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, subject, topic, subtopic, score, datetime.now(), attempts + 1))
    conn.commit()
    conn.close()

    return redirect(url_for('result_page'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
