from flask import Flask, render_template, request, redirect, session, jsonify
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
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    db.commit()
    db.close()


init_db()


# ---------------- LANGUAGES ---------------- #

translations = {
    "en": {
        "home": "Home",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "welcome": "Welcome to SkillBridge",
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
        "ai_tutor": "Tutor IA",
        "start_learning": "Comenzar",
    },

    "fr": {
        "home": "Accueil",
        "dashboard": "Tableau",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "login": "Connexion",
        "register": "S’inscrire",
        "welcome": "Bienvenue sur SkillBridge",
        "ai_tutor": "Tuteur IA",
        "start_learning": "Commencer",
    }
}


def get_text():
    lang = session.get("language", "en")
    return translations.get(lang, translations["en"])


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template(
        "index.html",
        text=get_text()
    )


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

        db = get_db()

        existing = db.execute(
            "SELECT * FROM users WHERE username=? OR email=?",
            (username, email)
        ).fetchone()

        if existing:
            db.close()

            return render_template(
                "register.html",
                error="User already exists",
                text=get_text()
            )

        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )

        db.commit()
        db.close()

        return redirect("/login")

    return render_template(
        "register.html",
        text=get_text()
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identifier = request.form.get("identifier")
        password = request.form.get("password")

        db = get_db()

        user = db.execute(
            """
            SELECT * FROM users
            WHERE username=? OR email=?
            """,
            (identifier, identifier)
        ).fetchone()

        db.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = user["username"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid login",
            text=get_text()
        )

    return render_template(
        "login.html",
        text=get_text()
    )


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"],
        text=get_text()
    )


@app.route("/subjects")
def subjects():

    if "user" not in session:
        return redirect("/login")

    subject_list = [
        "Math",
        "Science",
        "Programming",
        "Business",
        "Languages"
    ]

    return render_template(
        "subjects.html",
        subjects=subject_list,
        text=get_text()
    )


@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = [
        {
            "title": f"Introduction to {subject}",
            "content": f"This lesson teaches the fundamentals of {subject}."
        },
        {
            "title": f"Advanced {subject}",
            "content": f"This lesson covers advanced concepts in {subject}."
        }
    ]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons,
        text=get_text()
    )


# ---------------- AI ---------------- #

@app.route("/ai", methods=["POST"])
def ai():

    data = request.get_json()

    message = data.get("message", "").lower()

    responses = {
        "hello": "Hello! I am your SkillBridge AI tutor.",
        "math": "Math improves problem-solving and logical thinking.",
        "science": "Science helps explain the world around us.",
        "python": "Python is one of the easiest and most powerful programming languages."
    }

    answer = responses.get(
        message,
        f"AI Tutor says: {message}"
    )

    return jsonify({
        "response": answer
    })


# ---------------- LANGUAGE ---------------- #

@app.route("/set_language/<language>")
def set_language(language):

    session["language"] = language

    return redirect(request.referrer or "/")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)