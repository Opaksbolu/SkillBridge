from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    url_for
)

import sqlite3
import os
import re

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# =========================
# APP CONFIG
# =========================

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

DATABASE = "users.db"

# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# =========================
# LANGUAGE SYSTEM
# =========================

translations = {
    "en": {
        "home": "Home",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "welcome": "Welcome to SkillBridge",
        "hero": "Learn skills with AI-powered tutoring.",
        "ai_tutor": "AI Tutor",
        "start_learning": "Start Learning",
    },

    "es": {
        "home": "Inicio",
        "dashboard": "Panel",
        "subjects": "Materias",
        "logout": "Cerrar sesión",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "welcome": "Bienvenido a SkillBridge",
        "hero": "Aprende habilidades con tutoría impulsada por IA.",
        "ai_tutor": "Tutor IA",
        "start_learning": "Comenzar",
    },

    "fr": {
        "home": "Accueil",
        "dashboard": "Tableau de bord",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "login": "Connexion",
        "register": "S'inscrire",
        "welcome": "Bienvenue sur SkillBridge",
        "hero": "Apprenez avec un tutorat alimenté par IA.",
        "ai_tutor": "Tuteur IA",
        "start_learning": "Commencer",
    }
}


@app.context_processor
def inject_language():
    language = session.get("language", "en")

    return {
        "text": translations.get(language, translations["en"]),
        "current_language": language
    }

# =========================
# COURSES
# =========================

courses = {
    "Math": [
        "Algebra Basics",
        "Geometry Fundamentals",
        "Linear Equations",
        "Probability Intro"
    ],

    "Science": [
        "Biology Basics",
        "Physics Motion",
        "Chemistry Reactions",
        "Earth Science"
    ],

    "Programming": [
        "Python Basics",
        "Flask Development",
        "APIs and JSON",
        "Web Development"
    ],

    "Business": [
        "Entrepreneurship",
        "Marketing Basics",
        "Finance Intro",
        "Startup Strategy"
    ]
}

# =========================
# PASSWORD VALIDATION
# =========================

def strong_password(password):
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    return True

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return render_template(
                "register.html",
                error="All fields required"
            )

        if not strong_password(password):
            return render_template(
                "register.html",
                error="Password must contain uppercase, lowercase, number, and 8+ characters"
            )

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()

            conn.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """, (username, email, hashed_password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except Exception as e:
            return render_template(
                "register.html",
                error="Username or email already exists"
            )

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identifier = request.form.get("identifier")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute("""
        SELECT * FROM users
        WHERE username = ?
        OR email = ?
        """, (identifier, identifier)).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = user["username"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid login credentials"
        )

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# =========================
# SUBJECTS
# =========================

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject")

        return redirect(f"/course/{subject}")

    return render_template(
        "subjects.html",
        subjects=courses.keys()
    )


# =========================
# COURSE PAGE
# =========================

@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = courses.get(subject, [])

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )


# =========================
# LEARN PAGE
# =========================

@app.route("/learn/<subject>/<lesson>")
def learn(subject, lesson):

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "learn.html",
        subject=subject,
        lesson=lesson
    )


# =========================
# AI TUTOR
# =========================

@app.route("/ai", methods=["POST"])
def ai():

    data = request.get_json()

    message = data.get("message", "")
    subject = data.get("subject", "General")

    language = session.get("language", "en")

    # SIMPLE FALLBACK AI
    responses = {
        "hello": "Hello! How can I help you learn today?",
        "math": "Math helps build logical thinking and problem solving.",
        "science": "Science helps explain how the world works.",
        "python": "Python is one of the best beginner programming languages."
    }

    answer = responses.get(
        message.lower(),
        f"{subject} AI Tutor: I understand your question about '{message}'."
    )

    # LANGUAGE RESPONSE MOCK
    if language == "es":
        answer = "Tutor IA: " + answer

    elif language == "fr":
        answer = "Tuteur IA: " + answer

    return jsonify({
        "response": answer
    })


# =========================
# LANGUAGE TOGGLE
# =========================

@app.route("/set_language/<language>")
def set_language(language):

    if language in translations:
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