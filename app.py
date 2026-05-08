from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

app.secret_key = "skillbridge_secret"

# ---------------- DATABASE ---------------- #

def connect_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    conn = connect_db()

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

# ---------------- LANGUAGES ---------------- #

translations = {
    "en": {
        "welcome": "Welcome",
        "subjects": "Subjects",
        "dashboard": "Dashboard",
        "logout": "Logout",
        "ai": "AI Tutor"
    },

    "es": {
        "welcome": "Bienvenido",
        "subjects": "Materias",
        "dashboard": "Panel",
        "logout": "Cerrar sesión",
        "ai": "Tutor IA"
    },

    "fr": {
        "welcome": "Bienvenue",
        "subjects": "Sujets",
        "dashboard": "Tableau de bord",
        "logout": "Déconnexion",
        "ai": "Tuteur IA"
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
        email = request.form.get("email")
        password = request.form.get("password")

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters"
            )

        hashed_password = generate_password_hash(password)
        db.execute(
    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
    (username, email, hashed_password)
)

        try:

            conn = connect_db()

            conn.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    hashed_password
                )
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:

            return render_template(
                "register.html",
                error="Username or email already exists"
            )

    return render_template("register.html")

# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_input = request.form.get("login")
        password = request.form.get("password")

        conn = connect_db()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE username=? OR email=?
            """,
            (
                login_input,
                login_input
            )
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user"] = user["username"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid credentials"
        )

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
@login_required
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )

# ---------------- SUBJECTS ---------------- #

@app.route("/subjects")
@login_required
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

# ---------------- COURSE ---------------- #

@app.route("/course/<subject>")
@login_required
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = [
        "Introduction",
        "Core Concepts",
        "Practice",
        "Quiz",
        "Project"
    ]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )

# ---------------- LEARN ---------------- #

@app.route("/learn/<subject>")
@login_required
def learn(subject):

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "learn.html",
        subject=subject
    )

# ---------------- AI ---------------- #

@app.route("/ai", methods=["POST"])
@login_required
def ai():

    if "user" not in session:
        return jsonify({
            "response": "Please login first."
        })

    data = request.get_json()

    message = data.get("message", "").lower()

    responses = {
        "hello": "Hello! Welcome to SkillBridge.",
        "math": "Math improves problem solving and logic.",
        "science": "Science helps explain how the world works.",
        "python": "Python is beginner friendly and powerful."
    }

    answer = responses.get(
        message,
        f"AI Tutor says: {message}"
    )

    return jsonify({
        "response": answer
    })

# ---------------- LANGUAGE ---------------- #

@app.route("/set_language/<lang>")
def set_language(lang):

    if lang in translations:
        session["language"] = lang

    return redirect(request.referrer or "/")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)