from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

DATABASE = "users.db"


# -------------------------
# DATABASE
# -------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
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


# -------------------------
# LANGUAGE SYSTEM
# -------------------------

translations = {
    "en": {
        "home": "Home",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "welcome": "Welcome to SkillBridge",
        "hero": "AI-powered learning for everyone.",
        "start": "Get Started"
    },

    "es": {
        "home": "Inicio",
        "dashboard": "Panel",
        "subjects": "Materias",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "logout": "Cerrar sesión",
        "welcome": "Bienvenido a SkillBridge",
        "hero": "Aprendizaje impulsado por IA para todos.",
        "start": "Comenzar"
    },

    "fr": {
        "home": "Accueil",
        "dashboard": "Tableau",
        "subjects": "Sujets",
        "login": "Connexion",
        "register": "S'inscrire",
        "logout": "Déconnexion",
        "welcome": "Bienvenue à SkillBridge",
        "hero": "Apprentissage alimenté par l'IA pour tous.",
        "start": "Commencer"
    }
}


def get_text():
    lang = session.get("language", "en")
    return translations.get(lang, translations["en"])


@app.context_processor
def inject_language():
    return dict(t=get_text())


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/set_language/<lang>")
def set_language(lang):
    session["language"] = lang
    return redirect(request.referrer or "/")


# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        try:
            c.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """, (username, email, hashed_password))

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                "register.html",
                error="Email already exists."
            )

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        identifier = request.form.get("identifier")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        c.execute("""
        SELECT * FROM users
        WHERE username=? OR email=?
        """, (identifier, identifier))

        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username/email or password"
        )

    return render_template("login.html")


# -------------------------
# DASHBOARD
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session.get("username")
    )


# -------------------------
# SUBJECTS
# -------------------------

@app.route("/subjects")
def subjects():

    if "user_id" not in session:
        return redirect("/login")

    subjects_list = [
        "Math",
        "Science",
        "Programming",
        "History",
        "Languages",
        "Business"
    ]

    return render_template(
        "subjects.html",
        subjects=subjects_list
    )


# -------------------------
# COURSE PAGE
# -------------------------

@app.route("/course/<subject>")
def course(subject):

    if "user_id" not in session:
        return redirect("/login")

    lessons = [
        f"Introduction to {subject}",
        f"{subject} Fundamentals",
        f"Advanced {subject}",
        f"{subject} Quiz"
    ]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )


# -------------------------
# AI TUTOR
# -------------------------

@app.route("/ai_tutor", methods=["GET", "POST"])
def ai_tutor():

    response = None

    if request.method == "POST":

        question = request.form.get("question")

        response = f"""
        AI Tutor Response:

        You asked:
        "{question}"

        This is currently running in fallback mode.
        OpenAI integration can be added safely later.
        """

    return render_template(
        "ai_tutor.html",
        response=response
    )


# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -------------------------

if __name__ == "__main__":
    app.run(debug=True)