from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from store_results import store_quiz_results  # Assuming this is your function to store results

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Database connection
def connect_db():
    conn = sqlite3.connect('gcse_maths_quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to insert user progress into the user_progress table in gcse_maths_quiz.db
def insert_user_progress(username, subtopic_name, correct_answers, total_questions, percentage):
    db_dir = os.path.dirname(__file__)  # Get the directory where this script is located
    db_path = os.path.join(db_dir, "gcse_maths_quiz.db")  # Construct the path for the database


    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get current date and time
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        # Insert into user_progress table with username
        insert_query = """
        INSERT INTO user_progress (username, subtopic, correct_answers, total_questions, percentage, completed, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        completed = 1 if correct_answers == total_questions else 0
        cursor.execute(insert_query, (username, subtopic_name, correct_answers, total_questions, percentage, completed, current_date, current_time))

        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        conn.close()



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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists.")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Profile page
@app.route('/profile')
def profile():
    if 'user_id' in session:  # Check if the user is logged in
        conn = connect_db()
        cursor = conn.cursor()
        
        # Fetch all subjects except 'users' table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='users'")
        subjects = cursor.fetchall()
        conn.close()
        
        return render_template('profile.html', username=session['username'], subjects=subjects)
    return redirect(url_for('login'))  # Redirect to login page if not logged in

# Get Subtopics for Sidebar (AJAX Route)
@app.route('/get_subtopics/<subject>')
def get_subtopics(subject):
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch subtopics based on subject
    if subject.lower() == 'maths':
        cursor.execute('SELECT DISTINCT subtopic FROM maths')
    elif subject.lower() == 'biology':
        cursor.execute('SELECT DISTINCT subtopic FROM biology')
    elif subject.lower() == 'chemistry':
        cursor.execute('SELECT DISTINCT subtopic FROM chemistry')
    elif subject.lower() == 'physics':
        cursor.execute('SELECT DISTINCT subtopic FROM physics')
    else:
        return "Invalid subject selected", 400

    subtopics = cursor.fetchall()
    conn.close()

    return render_template('subtopics_sidebar.html', subtopics=subtopics)

# Questions page for each subtopic
@app.route('/questions/<subject>/<subtopic>/<int:question_id>', methods=['GET', 'POST'])
def questions(subject, subtopic, question_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch questions based on the subject and subtopic
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
        return redirect(url_for('profile'))

    # Fetch all rows and convert them to dictionaries
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Pass the question data to the questions.html template
    return render_template('questions.html', subject=subject, subtopic=subtopic, questions=questions, current_question=question_id)

# Submit Quiz and Store Results
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    print("Submit quiz route triggered")

    # Get the username from the session instead of user_id
    username = session.get('username')
    if not username:
        print("No username found in session")
        return {'status': 'error', 'message': 'User not logged in'}, 400

    # Get the quiz data from the request
    quiz_data = request.json
    subtopic_name = quiz_data.get('subtopic_name')  # Using subtopic_name instead of subtopic_id
    correct_answers = quiz_data.get('correct_answers')
    total_questions = quiz_data.get('total_questions')

    # Check if the required data is provided
    if not subtopic_name or correct_answers is None or total_questions is None:
        print("Missing quiz data: subtopic_name, correct_answers, or total_questions")
        return redirect(url_for('results_page'))

    try:
        correct_answers = int(correct_answers)
        total_questions = int(total_questions)
    except ValueError:
        print("Error converting correct_answers or total_questions to integer")
        return redirect(url_for('results_page'))

    # Calculate percentage
    percentage = (correct_answers / total_questions) * 100

    # Insert the quiz progress into the user_progress table
    try:
        insert_user_progress(username, subtopic_name, correct_answers, total_questions, percentage)
    except Exception as e:
        print(f"Error inserting user progress: {e}")
        return {'status': 'error', 'message': 'Failed to insert user progress'}, 500

    return {'status': 'success'}, 200




# Helper function to get the subject_id dynamically (you need to implement this function)
def get_subject_id(subject):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject,))
    subject_row = cursor.fetchone()
    conn.close()

    if subject_row:
        return subject_row['id']
    else:
        return None

# Results page
@app.route('/results')
def results_page():
    report = [
        {'question': 'What is 2+2?', 'user_answer': '4', 'is_correct': True, 'correct_answer': '4', 'explanation': '2 + 2 = 4'},
        {'question': 'What is 5+3?', 'user_answer': '7', 'is_correct': False, 'correct_answer': '8', 'explanation': '5 + 3 = 8'}
    ]
    return render_template('result.html', report=report, subtopic='Math Quiz')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
