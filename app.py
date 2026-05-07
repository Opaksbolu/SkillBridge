from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

DATABASE = "users.db"

# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# LANGUAGES
# =========================

translations = {

    "English": {
        "welcome": "Welcome to SkillBridge",
        "login": "Login",
        "register": "Register",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "ai_tutor": "AI Tutor",
        "choose_subject": "Choose Subject",
        "ask_ai": "Ask AI",
        "progress": "Progress"
    },

    "Spanish": {
        "welcome": "Bienvenido a SkillBridge",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "dashboard": "Panel",
        "subjects": "Materias",
        "logout": "Cerrar sesión",
        "ai_tutor": "Tutor IA",
        "choose_subject": "Elegir materia",
        "ask_ai": "Preguntar IA",
        "progress": "Progreso"
    },

    "French": {
        "welcome": "Bienvenue sur SkillBridge",
        "login": "Connexion",
        "register": "Inscription",
        "dashboard": "Tableau de bord",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "ai_tutor": "Tuteur IA",
        "choose_subject": "Choisir un sujet",
        "ask_ai": "Demander IA",
        "progress": "Progrès"
    }
}

def get_text():
    language = session.get("language", "English")
    return translations.get(language, translations["English"])

# =========================
# COURSES
# =========================

COURSES = {

    "Math": [
        "Algebra Basics",
        "Geometry",
        "Statistics",
        "Advanced Calculus"
    ],

    "Science": [
        "Biology",
        "Chemistry",
        "Physics",
        "Astronomy"
    ],

    "Programming": [
        "Python",
        "Flask",
        "Databases",
        "APIs"
    ],

    "Spanish": [
        "Greetings",
        "Conversations",
        "Grammar",
        "Fluency"
    ]
}

# =========================
# HOME
# =========================

@app.route("/")
def home():

    text = get_text()

    return render_template(
        "index.html",
        text=text
    )

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    text = get_text()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()

        except:
            return render_template(
                "register.html",
                error="User already exists",
                text=text
            )

        conn.close()

        return redirect("/login")

    return render_template(
        "register.html",
        text=text
    )

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    text = get_text()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = username

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid login",
            text=text
        )

    return render_template(
        "login.html",
        text=text
    )

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    course_progress = {
        "Math": 45,
        "Science": 72,
        "Programming": 20,
        "Spanish": 88
    }

    return render_template(
        "dashboard.html",
        user=session["user"],
        progress=course_progress,
        text=text
    )

# =========================
# SUBJECTS
# =========================

@app.route("/subjects")
def subjects():

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    return render_template(
        "subjects.html",
        courses=COURSES,
        text=text
    )

# =========================
# COURSE PAGE
# =========================

@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    lessons = COURSES.get(subject, [])

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons,
        text=text
    )

# =========================
# AI LEARN PAGE
# =========================

@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    ai_response = None

    if request.method == "POST":

        question = request.form.get("question")

        # FALLBACK AI SYSTEM
        ai_response = f"""
SkillBridge AI Tutor

Subject: {subject}

Question:
{question}

Answer:
This is SkillBridge smart fallback AI mode.

Your AI credits are currently unavailable,
but the tutor system still works without crashing.

Suggested next step:
Continue practicing {subject} fundamentals and
review the lesson modules carefully.
"""

    return render_template(
        "learn.html",
        subject=subject,
        ai_response=ai_response,
        text=text
    )

# =========================
# LANGUAGE SWITCHER
# =========================

@app.route("/set_language/<language>")
def set_language(language):

    session["language"] = language

    return redirect(request.referrer or "/")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)