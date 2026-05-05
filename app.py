from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# 🌍 TRANSLATIONS
translations = {
    "English": {
        "welcome": "Welcome",
        "subjects": "Your Subjects",
        "recommended": "Recommended For You",
        "logout": "Logout"
    },
    "Spanish": {
        "welcome": "Bienvenido",
        "subjects": "Tus Materias",
        "recommended": "Recomendado Para Ti",
        "logout": "Cerrar sesión"
    }
}

# 🌍 SUBJECT TRANSLATIONS
subject_translations = {
    "English": {
        "Math": "Math",
        "Science": "Science",
        "English": "English",
        "History": "History",
        "Computer Science": "Computer Science"
    },
    "Spanish": {
        "Math": "Matemáticas",
        "Science": "Ciencia",
        "English": "Inglés",
        "History": "Historia",
        "Computer Science": "Informática"
    }
}

# 📚 COURSES
courses = {
    "Math": [
        {"title": "Lesson 1: Numbers", "content": "Learn basic numbers and counting."},
        {"title": "Lesson 2: Addition", "content": "Learn how to add numbers."}
    ],
    "Science": [
        {"title": "Lesson 1: Plants", "content": "Learn about plants."}
    ],
    "English": [
        {"title": "Lesson 1: Alphabet", "content": "Learn A-Z letters."}
    ],
    "History": [
        {"title": "Lesson 1: Ancient World", "content": "Introduction to history."}
    ],
    "Computer Science": [
        {"title": "Lesson 1: Coding", "content": "Introduction to coding."}
    ]
}

# DB INIT
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT, language TEXT, subjects TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        language = request.form["language"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password,language,subjects) VALUES (?,?,?,?,?)",
                  (name, email, password, language, ""))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/subjects")

    return render_template("login.html")

@app.route('/subjects', methods=["GET", "POST"])
def subjects():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        selected = request.form.getlist("subjects")
        selected_str = ", ".join(selected)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("UPDATE users SET subjects=? WHERE id=?", (selected_str, session["user_id"]))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("subjects.html")

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = c.fetchone()
    conn.close()

    language = user[4]
    text = translations.get(language, translations["English"])
    subject_map = subject_translations.get(language, subject_translations["English"])

    raw_subjects = user[5].split(", ") if user[5] else []

    subjects = [
        {"original": s, "translated": subject_map.get(s, s)}
        for s in raw_subjects
    ]

    recommendations = ["Take quizzes", "Practice daily"]

    return render_template("dashboard.html",
                           user=user,
                           subjects=subjects,
                           recommendations=recommendations,
                           text=text)

@app.route('/learn/<subject>')
def learn(subject):
    lessons = courses.get(subject, [])
    return render_template("learn.html", subject=subject, lessons=lessons)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)