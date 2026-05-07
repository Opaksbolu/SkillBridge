from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

# OPTIONAL AI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

app = Flask(__name__)
app.secret_key = "skillbridge_secret_key"

# -------------------------
# DATABASE
# -------------------------

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        language TEXT DEFAULT 'English'
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# LANGUAGES
# -------------------------

LANGUAGES = {
    "English": {
        "welcome": "Welcome",
        "dashboard": "Dashboard",
        "subjects": "Subjects",
        "logout": "Logout",
        "start": "Start Learning",
    },

    "Spanish": {
        "welcome": "Bienvenido",
        "dashboard": "Panel",
        "subjects": "Materias",
        "logout": "Cerrar sesión",
        "start": "Comenzar",
    },

    "French": {
        "welcome": "Bienvenue",
        "dashboard": "Tableau de bord",
        "subjects": "Sujets",
        "logout": "Déconnexion",
        "start": "Commencer",
    }
}

# -------------------------
# COURSE DATA
# -------------------------

COURSES = {
    "Math": {
        "Algebra": [
            "Variables",
            "Equations",
            "Functions",
            "Practice Problems"
        ],

        "Geometry": [
            "Angles",
            "Triangles",
            "Circles"
        ]
    },

    "Science": {
        "Biology": [
            "Cells",
            "DNA",
            "Evolution"
        ],

        "Physics": [
            "Motion",
            "Force",
            "Energy"
        ]
    },

    "Programming": {
        "Python Basics": [
            "Variables",
            "Loops",
            "Functions",
            "Mini Project"
        ],

        "Web Development": [
            "HTML",
            "CSS",
            "Flask"
        ]
    }
}

# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():
    language = session.get("language", "English")
    text = LANGUAGES[language]

    return render_template(
        "index.html",
        text=text,
        language=language
    )

# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()

            return redirect("/login")

        except:
            return render_template(
                "register.html",
                error="User already exists"
            )

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
            error="Invalid login"
        )

    return render_template("login.html")

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    language = session.get("language", "English")
    text = LANGUAGES[language]

    return render_template(
        "dashboard.html",
        user=session["user"],
        text=text,
        language=language
    )

# -------------------------
# SUBJECTS
# -------------------------

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject")

        return redirect(f"/course/{subject}")

    language = session.get("language", "English")
    text = LANGUAGES[language]

    return render_template(
        "subjects.html",
        text=text,
        language=language
    )

# -------------------------
# COURSE PAGE
# -------------------------

@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = COURSES.get(subject, {})

    language = session.get("language", "English")
    text = LANGUAGES[language]

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons,
        text=text,
        language=language
    )

# -------------------------
# AI LEARN PAGE
# -------------------------

@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):

    response = ""

    if request.method == "POST":

        question = request.form.get("question")

        if client:

            try:

                ai = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a tutor for {subject}"
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                )

                response = ai.choices[0].message.content

            except:

                response = f"""
AI temporarily unavailable.

Helpful explanation for {subject}:

Focus on practicing daily and mastering the fundamentals.
"""

        else:

            response = f"""
AI not connected yet.

This is fallback learning mode for {subject}.
"""

    language = session.get("language", "English")
    text = LANGUAGES[language]

    return render_template(
        "learn.html",
        subject=subject,
        response=response,
        text=text,
        language=language
    )

# -------------------------
# LANGUAGE SWITCH
# -------------------------

@app.route("/set_language/<language>")
def set_language(language):

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

if __name__ == "__main__":
    app.run(debug=True)