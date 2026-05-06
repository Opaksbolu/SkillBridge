from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("users.db")

def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        lesson INTEGER
    )
    """)

    db.commit()

init_db()

# ---------------- COURSES ----------------
courses = {
    "Math": ["Addition", "Subtraction", "Algebra"],
    "English": ["Grammar", "Writing", "Reading"],
    "Science": ["Biology", "Chemistry", "Physics"],
    "Programming": ["Python Basics", "Loops", "Functions"]
}

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        db = get_db()

        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
        except:
            return "User already exists"

        return redirect("/login")

    return render_template("register.html")


# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session["user"] = username
            return redirect("/subjects")

        return "Invalid login"

    return render_template("login.html")


# -------- SUBJECTS --------
@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        subject = request.form.get("subject")
        return redirect(f"/course/{subject}")

    return render_template("subjects.html", courses=courses)


# -------- COURSE PAGE --------
@app.route("/course/<subject>")
def course(subject):
    if "user" not in session:
        return redirect("/login")

    lessons = courses.get(subject, [])
    return render_template("course.html", subject=subject, lessons=lessons)


# -------- LESSON --------
@app.route("/learn/<subject>/<int:lesson_id>", methods=["GET", "POST"])
def learn(subject, lesson_id):
    if "user" not in session:
        return redirect("/login")

    lesson = courses[subject][lesson_id]

    ai_response = None

    if request.method == "POST":
        question = request.form.get("question")

        # SAFE AI (never crashes)
        try:
            ai_response = f"AI Tutor: Explanation for '{question}' in {lesson}. Keep practicing!"
        except:
            ai_response = "AI is temporarily unavailable. Please try again later."

    return render_template(
        "learn.html",
        subject=subject,
        lesson=lesson,
        lesson_id=lesson_id,
        ai_response=ai_response
    )


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)