import sqlite3

# Connect to SQLite3 database (or create it if it doesn't exist)
def connect_db():
    try:
        conn = sqlite3.connect('gcse_maths_quiz.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Create 'users' table
def create_users_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    print("Users table created successfully.")

# Create 'maths' table
def create_maths_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS maths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT
        );
    ''')
    print("Maths table created successfully.")

# Create 'biology' table
def create_biology_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS biology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT
        );
    ''')
    print("Biology table created successfully.")

# Create 'chemistry' table
def create_chemistry_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chemistry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT
        );
    ''')
    print("Chemistry table created successfully.")

# Create 'physics' table
def create_physics_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS physics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT
        );
    ''')
    print("Physics table created successfully.")

# Create 'student_activities' table
def create_student_activities_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS student_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            score INTEGER,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            attempt INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')
    print("Student Activities table created successfully.")

# Create 'user_progress' table to track individual quiz attempts
def create_user_progress(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            topic TEXT,
            subtopic TEXT,
            question_id INTEGER,
            selected_answer TEXT,
            is_correct BOOLEAN,
            attempt_id INTEGER,  -- Field to track individual attempts
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        );
    ''')
    print("User Progress table created successfully.")

# Main function to create all tables
def main():
    conn = connect_db()
    
    if conn:
        # Create tables
        create_users_table(conn)
        create_maths_table(conn)
        create_biology_table(conn)
        create_chemistry_table(conn)
        create_physics_table(conn)
        create_student_activities_table(conn)
        create_user_progress(conn)

        # Commit and close connection
        conn.commit()
        conn.close()
        print("All tables created successfully.")
    else:
        print("Failed to create tables due to database connection issue.")

if __name__ == '__main__':
    main()
