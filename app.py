from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LANGUAGE SYSTEM ---------------- #

translations = {
    "en": {
        "welcome": "Welcome to SkillBridge",
        "subjects": "Subjects",
        "ai_tutor": "AI Tutor",
        "dashboard": "Dashboard"
    },
    "es": {
        "welcome": "Bienvenido a SkillBridge",
        "subjects": "Materias",
        "ai_tutor": "Tutor IA",
        "dashboard": "Panel"
    },
    "fr": {
        "welcome": "Bienvenue sur SkillBridge",
        "subjects": "Sujets",
        "ai_tutor": "Tuteur IA",
        "dashboard": "Tableau de bord"
    }
}

@app.context_processor
def inject_language():
    lang = session.get("language", "en")
    return dict(t=translations[lang])

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template(
                "register.html",
                error="Please fill all fields"
            )

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()

            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            return render_template(
                "register.html",
                error="User already exists"
            )

    return render_template("register.html")

# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = username

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid login"
        )

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )

# ---------------- SUBJECTS ---------------- #

@app.route("/subjects", methods=["GET"])
def subjects():

    if "user" not in session:
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
        subjects=subjects_list
    )

# ---------------- COURSE PAGE ---------------- #

@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = [
        "Introduction",
        "Core Concepts",
        "Practice Exercises",
        "Quiz",
        "Final Project"
    ]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )

# ---------------- LEARN PAGE ---------------- #

@app.route("/learn/<subject>")
def learn(subject):

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "learn.html",
        subject=subject
    )

# ---------------- AI TUTOR ---------------- #

@app.route("/ai", methods=["POST"])
def ai():

    if "user" not in session:
        return jsonify({"response": "Please login first."})

    user_message = request.json.get("message", "")

    responses = {
        "math": "Math helps solve real-world problems using logic and numbers.",
        "science": "Science explains how the world works through experiments.",
        "python": "Python is one of the best beginner programming languages.",
    }

    reply = responses.get(
        user_message.lower(),
        f"AI Tutor Response: {user_message}"
    )

    return jsonify({
        "response": reply
    })

# ---------------- LANGUAGE SWITCH ---------------- #

@app.route("/set_language/<lang>")
def set_language(lang):

    if lang in translations:
        session["language"] = lang

    return redirect(request.referrer or "/")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)