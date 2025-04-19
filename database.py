import sqlite3

def initialize_database():
    conn = sqlite3.connect('student_results.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK (role IN ('student', 'teacher')) NOT NULL,
        full_name TEXT NOT NULL
    )
    ''')
    
    # Create results table with composite primary key
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        std_id TEXT,
        student_name TEXT NOT NULL,
        roll_no TEXT NOT NULL,
        subject TEXT NOT NULL CHECK (subject IN ('MATHS4', 'OS', 'CNND', 'COA', 'AT')),
        marks INTEGER NOT NULL CHECK (marks >= 0 AND marks <= 100),
        added_by TEXT NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (std_id, subject),
        FOREIGN KEY (added_by) REFERENCES users(username),
        FOREIGN KEY (std_id) REFERENCES users(username)
    )
    ''')
    
    # Insert sample users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Teachers
        teachers = [
            ('admin', 'admin123', 'teacher', 'Administrator'),
            ('john', 'john123', 'teacher', 'John Smith')
        ]
        
        # Students - using default password pattern: student123
        students = [
            ('student1', 'student123', 'student', 'Alice Johnson'),
            ('student2', 'student123', 'student', 'Bob Wilson'),
            ('student3', 'student123', 'student', 'Carol White'),
            ('student4', 'student123', 'student', 'David Brown'),
            ('student5', 'student123', 'student', 'Eva Green')
        ]
        
        # Insert all users
        cursor.executemany('INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)', 
                         teachers + students)
        
        # Add some sample results
        sample_results = []
        subjects = ['MATHS4', 'OS', 'CNND', 'COA', 'AT']
        
        # Generate sample results for each student
        for student in students:
            for subject in subjects:
                sample_results.append((
                    student[0],  # std_id (username)
                    student[3],  # student_name (full_name)
                    f"R{student[0][-1]}",  # roll_no (R1, R2, etc.)
                    subject,
                    75,  # default mark
                    'admin'  # added by admin
                ))
        
        # Insert sample results
        cursor.executemany('''
        INSERT INTO results (std_id, student_name, roll_no, subject, marks, added_by)
        VALUES (?,?,?,?,?,?)
        ''', sample_results)
    
    conn.commit()
    conn.close()