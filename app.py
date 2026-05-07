from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "skillbridge_secret"

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
# LANGUAGE SYSTEM
# =========================

translations = {
    "English": {
        "welcome": "Welcome to SkillBridge",
        "login": "Login",
        "register": "Register",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "start_learning": "Start Learning",
        "choose_subject": "Choose a Subject",
        "ai_tutor": "AI Tutor",
    },

    "Spanish": {
        "welcome": "Bienvenido a SkillBridge",
        "login": "Iniciar sesión",
        "register": "Registrarse",
        "dashboard": "Panel",
        "subjects": "Materias",
        "logout": "Cerrar sesión",
        "start_learning": "Comenzar aprendizaje",
        "choose_subject": "Elegir una materia",
        "ai_tutor": "Tutor IA",
    },

    "French": {
        "welcome": "Bienvenue sur SkillBridge",
        "login": "Connexion",
        "register": "S'inscrire",
        "dashboard": "Tableau de bord",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "start_learning": "Commencer",
        "choose_subject": "Choisir une matière",
        "ai_tutor": "Tuteur IA",
    }
}

def get_text():
    language = session.get("language", "English")
    return translations.get(language, translations["English"])

# =========================
# HOME
# =========================

@app.route("/")
def home():
    text = get_text()
    return render_template("index.html", text=text)

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

    return render_template("register.html", text=text)

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

    return render_template("login.html", text=text)

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    courses = [
        {
            "name": "Math",
            "progress": 40
        },
        {
            "name": "Science",
            "progress": 70
        },
        {
            "name": "Programming",
            "progress": 20
        },
        {
            "name": "Spanish",
            "progress": 90
        }
    ]

    return render_template(
        "dashboard.html",
        user=session["user"],
        courses=courses,
        text=text
    )

# =========================
# SUBJECTS
# =========================

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "user" not in session:
        return redirect("/login")

    text = get_text()

    subject_list = [
        "Math",
        "Science",
        "Programming",
        "Spanish",
        "Business",
        "AI",
        "History"
    ]

    if request.method == "POST":
        subject = request.form.get("subject")
        return redirect(f"/course/{subject}")

    return render_template(
        "subjects.html",
        subjects=subject_list,
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

    lessons = [
        {
            "title": f"Introduction to {subject}",
            "content": f"Learn the basics of {subject}."
        },
        {
            "title": f"Intermediate {subject}",
            "content": f"Build deeper understanding of {subject}."
        },
        {
            "title": f"Advanced {subject}",
            "content": f"Master advanced concepts in {subject}."
        }
    ]

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

        # Fallback AI system
        ai_response = f"""
        SkillBridge AI Tutor:

        You asked about:
        '{question}'

        Here is a smart explanation for {subject}.

        This fallback tutor works even without OpenAI credits.
        """

    return render_template(
        "learn.html",
        subject=subject,
        ai_response=ai_response,
        text=text
    )

# =========================
# LANGUAGE TOGGLE
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