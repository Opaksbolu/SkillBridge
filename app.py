from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# DATABASE INIT
# -------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    db = conn.cursor()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        language TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        language = request.form.get("language")

        conn = sqlite3.connect("users.db")
        db = conn.cursor()

        db.execute(
            "INSERT INTO users (username, password, language) VALUES (?, ?, ?)",
            (username, password, language)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

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
        db = conn.cursor()

        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = username
            session["language"] = user[3]
            return redirect("/subjects")

    return render_template("login.html")

# -------------------------
# SUBJECTS
# -------------------------
@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "POST":
        subject = request.form.get("subject")
        return redirect(f"/learn/{subject}")

    return render_template("subjects.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])

# -------------------------
# LEARN PAGE (NO AI YET)
# -------------------------
@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):
    content = ""

    if request.method == "POST":
        question = request.form.get("question")

        content = f"""
        📘 {subject} Lesson

        You asked: {question}

        This is a smart placeholder response.
        Real AI will be added later.
        """

    return render_template("learn.html", subject=subject, content=content)

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)