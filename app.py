from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

# Optional AI import
USE_AI = True
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    USE_AI = False

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# DATABASE
# -------------------------
def get_db():
    return sqlite3.connect("users.db")

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
        username = request.form["username"]
        password = request.form["password"]
        language = request.form["language"]

        db = get_db()
        db.execute("INSERT INTO users (username, password, language) VALUES (?, ?, ?)",
                   (username, password, language))
        db.commit()

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

        if not username or not password:
            return "Missing fields"

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

# -------------------------
# SUBJECT SELECTION
# -------------------------
@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        selected = request.form.getlist("subjects")
        session["subjects"] = selected
        return redirect("/dashboard")

    return render_template("subjects.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    subjects = session.get("subjects", [])

    return render_template("dashboard.html", subjects=subjects)

# -------------------------
# LEARNING PAGE (AI + FALLBACK)
# -------------------------
@app.route("/learn/<subject>", methods=["GET", "POST"])
def learn(subject):
    if "user" not in session:
        return redirect("/login")

    ai_response = None

    if request.method == "POST":
        question = request.form["question"]

        if USE_AI:
            try:
                ai = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful tutor."},
                        {"role": "user", "content": question}
                    ]
                )
                ai_response = ai.choices[0].message.content

            except Exception:
                # Fallback if API fails
                ai_response = f"(Offline Mode) Here's a helpful explanation about {subject}: Focus on fundamentals, practice problems, and consistency."

        else:
            ai_response = f"(Offline Mode) Learning {subject}: Start with basics, watch tutorials, and practice daily."

    return render_template("learn.html", subject=subject, ai_response=ai_response)

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)