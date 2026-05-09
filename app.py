from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

DATABASE = "users.db"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LANGUAGE ----------------

translations = {
    "en": {
        "home": "Home",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "login": "Login",
        "register": "Register"
    },
    "es": {
        "home": "Inicio",
        "dashboard": "Panel",
        "subjects": "Materias",
        "logout": "Cerrar sesión",
        "login": "Iniciar sesión",
        "register": "Registrarse"
    },
    "fr": {
        "home": "Accueil",
        "dashboard": "Tableau",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "login": "Connexion",
        "register": "S'inscrire"
    }
}

def get_text():
    lang = session.get("language", "en")
    return translations.get(lang, translations["en"])

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        text=get_text()
    )

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return render_template(
                "register.html",
                error="Please fill all fields",
                text=get_text()
            )

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Email already exists",
                text=get_text()
            )

    return render_template(
        "register.html",
        text=get_text()
    )

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_input = request.form.get("login")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE username = ? OR email = ?
        """, (login_input, login_input))

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid login credentials",
            text=get_text()
        )

    return render_template(
        "login.html",
        text=get_text()
    )

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        text=get_text()
    )

# ---------------- SUBJECTS ----------------

@app.route("/subjects")
def subjects():

    if "user_id" not in session:
        return redirect("/login")

    subjects_list = [
        "Math",
        "Science",
        "Programming",
        "Business",
        "Languages"
    ]

    return render_template(
        "subjects.html",
        subjects=subjects_list,
        text=get_text()
    )

# ---------------- COURSE ----------------

@app.route("/course/<subject>")
def course(subject):

    if "user_id" not in session:
        return redirect("/login")

    lessons = [
        "Introduction",
        "Basics",
        "Intermediate Concepts",
        "Advanced Concepts",
        "Final Quiz"
    ]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons,
        text=get_text()
    )

# ---------------- LEARN ----------------

@app.route("/learn/<subject>/<lesson>")
def learn(subject, lesson):

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "learn.html",
        subject=subject,
        lesson=lesson,
        text=get_text()
    )

# ---------------- AI ----------------

@app.route("/ai", methods=["POST"])
def ai():

    data = request.get_json()

    message = data.get("message", "")
    subject = data.get("subject", "General")

    responses = {
        "math": "Math helps us understand numbers, equations, and logic.",
        "science": "Science explains how the world works through observation and experiments.",
        "programming": "Programming allows us to build software and solve problems with code."
    }

    answer = responses.get(
        subject.lower(),
        f"AI Tutor Response about {subject}: {message}"
    )

    return jsonify({
        "response": answer
    })

# ---------------- LANGUAGE SWITCH ----------------

@app.route("/set_language/<language>")
def set_language(language):

    if language in translations:
        session["language"] = language

    return redirect(request.referrer or "/")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)