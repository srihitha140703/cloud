from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Configure file upload settings
UPLOAD_FOLDER = '/home/ubuntu/flaskapp/uploads/'  # Replace with the correct path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}
db_path = os.path.join(os.path.dirname(__file__), 'users.db')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database setup function (run once to create the table)
def init_db():
    #db_path = os.path.join(os.path.dirname(__file__), 'users.db')
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                file_name TEXT,
                word_count INTEGER
            )
        """)
        conn.commit()

# Home page (login page)
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database and the password matches
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, pa>
                user = cur.fetchone()

                if user:
                    return redirect(url_for('show_details', username=username))
                else:
                    error = 'Invalid username or password. Please try again.'
        except Exception as e:
            print(e)
            error = 'An error occurred. Please try again.'

    return render_template('login.html', error=error)

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            file = request.files['file']
            word_count = 0
            file_path = None
            filename="Chose not to upload file"
            # Check if username already exists
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                existing_user = cur.fetchone()
                if existing_user:
                    error = "Username already exists."
                    return render_template('register.html', error=error)

            # Check if the file is allowed and save it
            if file and allowed_file(file.filename):
                filename = username + "_" + file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                with open(file_path, 'r') as f:
                    text = f.read()
                    word_count = len(text.split())
                    # Store user information along with file and word count in SQLite
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users (username, password, first_name, last_name, email, file_name, >
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (username, password, first_name, last_name, email, filename, word_count))
                conn.commit()

            return redirect(url_for('show_details', username=username))

        except Exception as e:
            print(e)

    return render_template('register.html')

    # User details page
@app.route('/show/<username>')
def show_details(username):
    user = None
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cur.fetchone()
    except Exception as e:
        print(e)
    
    return render_template('show.html', user=user)

# Route to download uploaded files
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize the database (run this before starting the app)
init_db()
if __name__ == '__main__':
    #init_db()
    app.run(debug=True)

