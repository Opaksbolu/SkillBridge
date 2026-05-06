from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db():
    return sqlite3.connect("users.db")


# 🔹 CREATE DATABASE (RUN ONCE)
def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        language TEXT
    )
    """)
    db.commit()


init_db()


@app.route("/")
def index():
    return render_template("index.html")


# ======================
# REGISTER
# ======================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        language = request.form.get("language")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (email, password, language) VALUES (?, ?, ?)",
                (email, password, language)
            )
            db.commit()
        except:
            return "User already exists"

        return redirect("/login")

    return render_template("register.html")


# ======================
# LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:
            session["user"] = user[1]
            session["language"] = user[3]
            return redirect("/subjects")
        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")


# ======================
# SUBJECT SELECTION
# ======================
@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        subject = request.form.get("subject")
        session["subject"] = subject
        return redirect("/dashboard")

    return render_template("subjects.html")


# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        subject=session.get("subject"),
        language=session.get("language")
    )


# ======================
# LEARN PAGE (AI SAFE MODE)
# ======================
@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):
    if "user" not in session:
        return redirect("/login")

    ai_response = None

    if request.method == "POST":
        user_input = request.form.get("question")

        # 🔹 SAFE fallback AI (no API needed)
        ai_response = f"""
        Here’s a simple explanation of {subject}:

        {subject} is an important topic. Start with basics,
        practice daily, and build projects.

        Your question: {user_input}
        """

    return render_template(
        "learn.html",
        subject=subject,
        ai_response=ai_response
    )


@app.route("/course/<subject>")
def course(subject):
    if "user" not in session:
        return redirect("/login")

    lessons = [
        f"Introduction to {subject}",
        f"{subject} Basics",
        f"Intermediate {subject}",
        f"Advanced {subject}"
    ]

    return render_template("course.html", subject=subject, lessons=lessons)


# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")