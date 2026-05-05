from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🔹 Initialize DB
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            learning_style TEXT,
            language TEXT,
            grade_level TEXT,
            subjects TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# 🏠 Home
@app.route('/')
def home():
    return render_template('index.html')

# 📝 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['temp_user'] = {
            'name': request.form['fullname'],
            'email': request.form['email'],
            'password': request.form['password'],
            'learning_style': request.form['learning_style'],
            'language': request.form['language'],
            'grade_level': request.form['grade_level']
        }
        return redirect(url_for('subjects'))

    return render_template('register.html')

# 📚 Subjects
@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        subjects = ", ".join(request.form.getlist('subjects'))
        user = session.get('temp_user')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (name, email, password, learning_style, language, grade_level, subjects)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['name'],
            user['email'],
            user['password'],
            user['learning_style'],
            user['language'],
            user['grade_level'],
            subjects
        ))

        conn.commit()
        conn.close()

        session.pop('temp_user', None)
        return redirect(url_for('login'))

    return render_template('subjects.html')

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login"

    return render_template('login.html')

# 🤖 AI-style Recommendation Logic
def get_recommendations(learning_style, grade_level):
    recommendations = []

    if learning_style == "visual":
        recommendations.append("Video-based lessons")
    elif learning_style == "auditory":
        recommendations.append("Audio explanations")
    elif learning_style == "hands_on":
        recommendations.append("Interactive exercises")

    if "Grade" in grade_level:
        recommendations.append("Practice quizzes")
    else:
        recommendations.append("Basic learning games")

    return recommendations

# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, learning_style, language, grade_level, subjects
        FROM users WHERE id=?
    ''', (session['user_id'],))

    user = cursor.fetchone()
    conn.close()

    recommendations = get_recommendations(user[1], user[3])

    return render_template('dashboard.html', user=user, recommendations=recommendations)

# 📚 Learning Page
@app.route('/learn/<subject>')
def learn(subject):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('learn.html', subject=subject)

# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)