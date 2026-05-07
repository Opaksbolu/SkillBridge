from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "skillbridge_secret"

DATABASE = "users.db"


# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect(DATABASE)
    db = conn.cursor()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- COURSE DATA ---------------- #

courses = {
    "Math": [
        "Algebra",
        "Geometry",
        "Statistics",
        "Trigonometry"
    ],

    "Science": [
        "Biology",
        "Chemistry",
        "Physics",
        "Earth Science"
    ],

    "Programming": [
        "Python",
        "HTML & CSS",
        "JavaScript",
        "Flask"
    ],

    "Spanish": [
        "Greetings",
        "Numbers",
        "Conversations",
        "Vocabulary"
    ]
}


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

        conn = sqlite3.connect(DATABASE)
        db = conn.cursor()

        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        db = conn.cursor()

        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/subjects")

        return render_template(
            "login.html",
            error="Invalid login"
        )

    return render_template("login.html")


# ---------------- SUBJECTS ---------------- #

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject")

        return redirect(
            url_for(
                "course",
                subject=subject
            )
        )

    return render_template(
        "subjects.html",
        subjects=courses.keys()
    )


# ---------------- COURSE PAGE ---------------- #

@app.route("/course/<subject>")
def course(subject):

    if "user" not in session:
        return redirect("/login")

    lessons = courses.get(subject, [])

    return render_template(
        "course.html",
        subject=subject,
        lessons=lessons
    )


# ---------------- LEARN PAGE ---------------- #

@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):

    if "user" not in session:
        return redirect("/login")

    ai_response = None

    if request.method == "POST":

        question = request.form.get("question")

        ai_response = f"""
AI Tutor is temporarily offline.

Question:
{question}

Recommended Study Tip:
Focus on practicing one concept at a time in {subject}.
"""

    return render_template(
        "learn.html",
        subject=subject,
        ai_response=ai_response
    )


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)