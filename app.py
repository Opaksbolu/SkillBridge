from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "skillbridge-secret-key"

# -------------------------
# DATABASE SETUP
# -------------------------

def init_db():
    conn = sqlite3.connect("users.db")
    db = conn.cursor()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        language TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# LANGUAGE SYSTEM
# -------------------------

translations = {
    "English": {
        "welcome": "Welcome to SkillBridge",
        "subtitle": "AI-Powered Learning Platform",
        "login": "Login",
        "register": "Register",
        "subjects": "Choose Your Subject",
        "dashboard": "Dashboard",
        "logout": "Logout",
    },

    "Spanish": {
        "welcome": "Bienvenido a SkillBridge",
        "subtitle": "Plataforma de aprendizaje con IA",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "subjects": "Elige tu materia",
        "dashboard": "Panel",
        "logout": "Cerrar sesión",
    },

    "French": {
        "welcome": "Bienvenue sur SkillBridge",
        "subtitle": "Plateforme d'apprentissage IA",
        "login": "Connexion",
        "register": "S'inscrire",
        "subjects": "Choisissez votre sujet",
        "dashboard": "Tableau de bord",
        "logout": "Déconnexion",
    }
}

# -------------------------
# COURSE DATA
# -------------------------

courses = {
    "Math": [
        "Algebra Basics",
        "Linear Equations",
        "Functions",
        "Graphing",
        "Geometry"
    ],

    "Science": [
        "Cells and Biology",
        "Forces and Motion",
        "Chemistry Basics",
        "Atoms",
        "Energy"
    ],

    "Programming": [
        "Python Basics",
        "Variables",
        "Loops",
        "Functions",
        "Flask Intro"
    ],

    "Spanish": [
        "Greetings",
        "Numbers",
        "Conversation",
        "Grammar",
        "Vocabulary"
    ]
}

# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():
    language = session.get("language", "English")
    text = translations[language]

    return render_template("index.html", text=text)

# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        language = request.form.get("language")

        conn = sqlite3.connect("users.db")
        db = conn.cursor()

        db.execute(
            "INSERT INTO users (username, password, language) VALUES (?, ?, ?)",
            (username, password, language)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        db = conn.cursor()

        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            session["username"] = user["username"]
            session["language"] = user["language"]

            return redirect("/subjects")

        return render_template(
            "login.html",
            error="Invalid login"
        )

    return render_template("login.html")

# -------------------------
# SUBJECTS
# -------------------------

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject")

        return redirect(f"/course/{subject}")

    return render_template(
        "subjects.html",
        subjects=courses.keys()
    )

# -------------------------
# COURSE PAGE
# -------------------------

@app.route("/course/<subject>")
def course(subject):

    if subject not in courses:
        return redirect("/subjects")

    lessons = courses[subject]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    language = session.get("language", "English")
    text = translations[language]

    return render_template(
        "dashboard.html",
        username=session["username"],
        text=text
    )

# -------------------------
# LANGUAGE TOGGLE
# -------------------------

@app.route("/change_language/<language>")
def change_language(language):

    if language in translations:
        session["language"] = language

    return redirect(request.referrer or "/")

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# -------------------------
# RUN APP
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)