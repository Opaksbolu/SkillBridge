from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🌍 LANGUAGE DICTIONARY
translations = {
    "English": {
        "welcome": "Welcome",
        "dashboard": "Dashboard",
        "subjects": "Your Subjects",
        "recommended": "Recommended For You",
        "logout": "Logout"
    },
    "Spanish": {
        "welcome": "Bienvenido",
        "dashboard": "Panel",
        "subjects": "Tus Materias",
        "recommended": "Recomendado Para Ti",
        "logout": "Cerrar sesión"
    },
    "French": {
        "welcome": "Bienvenue",
        "dashboard": "Tableau de bord",
        "subjects": "Vos matières",
        "recommended": "Recommandé pour vous",
        "logout": "Se déconnecter"
    }
}

def get_text(language, key):
    return translations.get(language, translations["English"]).get(key, key)

# 🔹 DB INIT
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
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

# 🏠 HOME
@app.route('/')
def home():
    return render_template('index.html')

# 📝 REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['temp_user'] = request.form
        return redirect(url_for('subjects'))
    return render_template('register.html')

# 📚 SUBJECTS
@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        user = session.get('temp_user')
        subjects = ", ".join(request.form.getlist('subjects'))

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (name, email, password, learning_style, language, grade_level, subjects)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['fullname'],
            user['email'],
            user['password'],
            user['learning_style'],
            user['language'],
            user['grade_level'],
            subjects
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('subjects.html')

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (request.form['email'], request.form['password'])
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))

    return render_template('login.html')

# 🤖 SMART RECOMMENDATIONS
def get_recommendations(style, grade):
    rec = []

    if style == "visual":
        rec += ["Watch videos", "Use diagrams"]
    elif style == "auditory":
        rec += ["Listen to lessons", "Repeat aloud"]
    elif style == "hands_on":
        rec += ["Practice exercises", "Do projects"]

    if "Grade" in grade:
        rec.append("Take quizzes")
    else:
        rec.append("Play learning games")

    return rec

# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id=?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    recommendations = get_recommendations(user[4], user[6])

    text = translations.get(user[5], translations["English"])

    return render_template(
        'dashboard.html',
        user=user,
        recommendations=recommendations,
        text=text
    )

# 📚 LEARN PAGE
@app.route('/learn/<subject>')
def learn(subject):
    return render_template('learn.html', subject=subject)

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)