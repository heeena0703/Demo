from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)

import os

app.secret_key = os.environ.get('SECRET_KEY', 'secret_key')
app.permanent_session_lifetime = timedelta(minutes=15)

# DATABASE CONFIG (use environment variables in production)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_NAME = os.environ.get('DB_NAME', 'virtual_classroom')


def get_db_connection():
    # Try connecting to MySQL first. If it fails (for example MySQL not running
    # locally), fall back to a local sqlite database for quick development.
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3
        )
        return ('mysql', conn)
    except Exception:
        # Fallback: sqlite3 file 'dev.db' in project root
        sqlite_conn = sqlite3.connect('dev.db', check_same_thread=False)
        # Return rows as dict-like objects
        sqlite_conn.row_factory = sqlite3.Row

        # Ensure users table exists in sqlite
        cur = sqlite_conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            );
        ''')
        sqlite_conn.commit()
        return ('sqlite', sqlite_conn)


# HOME
@app.route('/')
def home():
    return render_template('home.html')

# DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # show_images=True so dashboard displays course/profile images only on post-login page
    return render_template('dashboard.html', show_images=True)

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        db_type, conn = get_db_connection()
        try:
            if db_type == 'mysql':
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed_password)
                )
                conn.commit()
                cursor.close()
            else:  # sqlite
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )
                conn.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            # Handle duplicate user error messages for both DBs
            err = str(e)
            if 'UNIQUE constraint failed' in err or '1062' in err:
                flash('Email already exists!', 'danger')
            else:
                flash(f'Error: {err}', 'danger')
        finally:
            # Close only the connection object for sqlite; for MySQL conn.close()
            try:
                conn.close()
            except Exception:
                pass

    return render_template('register.html', show_sidebar=False)


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        db_type, conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if db_type == 'mysql':
                cursor.execute(
                    "SELECT * FROM users WHERE username=%s",
                    (username,)
                )
                user = cursor.fetchone()
                # user is a dict when using pymysql with DictCursor
                user_password = user['password'] if user else None
            else:  # sqlite
                cursor.execute(
                    "SELECT * FROM users WHERE username=?",
                    (username,)
                )
                user = cursor.fetchone()
                user_password = user['password'] if user else None

            if user and user_password and check_password_hash(user_password, password):
                session.permanent = True
                session['username'] = username

                flash('Login successful!', 'success')

                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials!', 'danger')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            try:
                conn.close()
            except Exception:
                pass

    return render_template('login.html', show_sidebar=False)

# PROFILE PAGE
@app.route('/profile')
def profile():

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    return render_template('profile.html', show_images=False)


# # CONTENT PAGE
# @app.route('/content')
# def content():

#     if 'username' not in session:
#         flash('Please login first!', 'warning')
#         return redirect(url_for('login'))

#     courses = [
#         {
#             "title": "Python Programming",
#             "description": "Learn Python from beginner to advanced.",
#             "image": "./static/images/python.jpg",
#             "badge": "Beginner",
#             "link": "python"
#         },
#         {
#             "title": "Web Development",
#             "description": "Master HTML CSS JavaScript and Flask.",
#             "image": "./static/images/webdev.jpg",
#             "badge": "Popular",
#             "link": "web-dev"
#         },
#         {
#             "title": "AWS Cloud",
#             "description": "Learn AWS cloud deployment and services.",
#             "image": "./static/images/awscloude.jpg",
#             "badge": "Advanced",
#             "link": "aws"
#         }
#     ]

#     return render_template('dashboard.html', courses=courses)

# COURSES PAGE
@app.route('/courses')
def courses():

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    courses = [
        {
            "title": "Python Programming",
            "description": "Learn Python from beginner to advanced.",
            "image": "/static/images/python.jpg",
            "badge": "Beginner",
            "link": "python"
        },
        {
            "title": "Web Development",
            "description": "Master HTML CSS JavaScript and Flask.",
            "image": "/static/images/webdev.jpg",
            "badge": "Popular",
            "link": "web-dev"
        },
        {
            "title": "AWS Cloud",
            "description": "Learn AWS cloud deployment and services.",
            "image": "/static/images/awscloude.jpg",
            "badge": "Advanced",
            "link": "aws"
        }
    ]

    return render_template(
        'courses.html',
        courses=courses,
        show_images=False
    )
# ASSIGNMENTS PAGE
@app.route('/assignments')
def assignments():

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    assignments = [
        {
            "title": "Python Mini Project",
            "course": "Python Programming",
            "deadline": "10 June 2026"
        },
        {
            "title": "Portfolio Website",
            "course": "Web Development",
            "deadline": "15 June 2026"
        },
        {
            "title": "AWS Deployment Task",
            "course": "AWS Cloud",
            "deadline": "20 June 2026"
        }
    ]

    return render_template(
        'assignments.html',
        assignments=assignments,
        show_images=False
    )

# CERTIFICATES PAGE
@app.route('/certificates')
def certificates():

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    certificates = [
        {
            "title": "Python Programming",
            "date": "May 2026"
        },
        {
            "title": "Web Development",
            "date": "June 2026"
        }
    ]

    return render_template(
        'certificates.html',
        certificates=certificates,
        show_images=False
    )
# ENROLL
@app.route('/enroll/<course_name>')
def enroll(course_name):

    if 'username' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    flash(f'Successfully enrolled in {course_name}!', 'success')

    return redirect(url_for('dashboard'))


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    flash('Logged out successfully!', 'info')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)