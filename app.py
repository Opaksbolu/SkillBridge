from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "secret123"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        language = request.form['language']
        learning_style = request.form['learning_style']
        grade_level = request.form['grade_level']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("""INSERT INTO users 
        (name, email, password, language, learning_style, grade_level)
        VALUES (?, ?, ?, ?, ?, ?)""",
                  (name, email, password, language, learning_style, grade_level))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()

        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/subjects')

    return render_template('login.html')

# ---------------- SUBJECTS ----------------
@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if 'user_id' not in session:
        return redirect('/login')

    subject_list = [
        "Math", "Science", "English", "History",
        "Computer Science", "Biology", "Chemistry",
        "Physics", "Economics", "Art", "Music"
    ]

    if request.method == 'POST':
        selected = request.form.getlist('subjects')
        subjects_str = ",".join(selected)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET subjects=? WHERE id=?",
                  (subjects_str, session['user_id']))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('subjects.html', subjects=subject_list)

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    conn.close()

    return render_template('dashboard.html', user=user)

# ---------------- AI LEARNING PAGE ----------------
@app.route('/learn/<subject>', methods=['GET', 'POST'])
def learn(subject):
    if 'user_id' not in session:
        return redirect('/login')

    response = ""

    if request.method == 'POST':
        question = request.form['question']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT language, learning_style, grade_level FROM users WHERE id=?", (session['user_id'],))
        user = c.fetchone()
        conn.close()

        language, learning_style, grade = user

        prompt = f"""
        You are a helpful tutor.
        
        Teach {subject} to a {grade} student.
        Use {learning_style} learning style.
        Respond in {language}.
        
        Question: {question}
        """

        ai = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert tutor."},
                {"role": "user", "content": prompt}
            ]
        )

        response = ai.choices[0].message.content

    return render_template('learn.html', subject=subject, response=response)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)